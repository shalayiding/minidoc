# Real-Time Data Reporting Platform
## E-commerce Recommendation System

> A unified platform to collect, process, analyze recommendation events and power business + engineering dashboards at 2B+ events/day scale.

| | | | |
|---|---|---|---|
| **Daily Events** 2B+ | **Real-Time Latency** <500ms | **Pipeline Modes** Batch + Stream | **Dashboard Types** BI + Eng |

---

## 1. System Overview

### Core Objectives

- ✅ Ingest and process **2B+ clickstream events per day** from recommendation surfaces
- ✅ Deliver **real-time CTR / CVR / revenue metrics** with sub-second freshness
- ✅ Support both **streaming** (Flink/Kafka) and **batch** (Spark) pipelines
- ✅ Detect **corrupted or missing fields** with automated data quality checks
- ✅ Fire **data quality alerts** when SLAs are breached
- ✅ Power **BI dashboards** for business stakeholders (GMV, CTR, CVR)
- ✅ Enable **historical analysis** with a queryable data warehouse
- ✅ Monitor **ML feature freshness** for recommendation model health

---

## 2. High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         DATA INGESTION                                   │
│  [Mobile SDK] [Web SDK] [Server Events]                                  │
│        │            │           │                                        │
│        └────────────┴───────────┘                                       │
│                     │                                                    │
│             [API Gateway / Kong]                                         │
│                     │                                                    │
│        [Kafka — raw.events — 32 partitions]                              │
└──────────────────────────┬───────────────────────────────────────────────┘
                           │
          ┌────────────────┴────────────────┐
          ▼                                 ▼
┌─────────────────────┐         ┌──────────────────────┐
│  STREAM PIPELINE    │         │   BATCH PIPELINE      │
│  Flink Job 1        │         │   Spark (hourly/daily)│
│  Validation +       │         │   S3 → DW staging     │
│  Enrichment         │         │   → Snowflake/BigQuery│
│         │           │         │         │             │
│  Flink Job 2        │         │   dbt models          │
│  Metric Aggregation │         │   Business Layer      │
└────────┬────────────┘         └──────────┬────────────┘
         │                                  │
   ┌─────┴──────┐                    ┌──────┴──────┐
   ▼            ▼                    ▼             ▼
[Druid]      [Redis]           [BI Dashboard]  [ML Feature
 OLAP         Live              Tableau/        Store]
 Store        Counters          Superset        Feast/Tecton
   │            │                    │             │
   └────────────┘                    └─────────────┘
         │                                  │
[Engineering Dashboard]           [Recommendation Model]
     Grafana
         │
[Alert Manager — PagerDuty / Slack]
```

---

## 3. Data Ingestion Layer

### 3.1 Event Schema

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `event_id` | UUID | Unique event identifier | ✅ |
| `user_id` | STRING | Hashed user identifier | ✅ |
| `item_id` | STRING | Recommended item SKU | ✅ |
| `event_type` | ENUM | impression / click / add_to_cart / purchase | ✅ |
| `timestamp` | INT64 | Unix epoch ms | ✅ |
| `session_id` | STRING | Browser/app session | ✅ |
| `rec_model_ver` | STRING | Model version that served the result | ✅ |
| `position` | INT | Rank position in recommendation list | ✅ |
| `revenue` | FLOAT | Transaction value (purchase only) | ❌ |
| `page_context` | STRING | Homepage / PDP / Cart | ❌ |

### 3.2 Kafka Configuration

| Parameter | Value |
|-----------|-------|
| Topics | `raw.events` / `validated.events` / `dlq.events` |
| Partitions | 32 per topic |
| Retention | 7 days |
| Throughput target | 2.5M events/min peak |
| Replication | 3x |
| Peak events/sec | ~28,000 |
| Avg event size | ~800B |
| Daily raw volume | ~1.8TB |

---

## 4. Stream Processing — Real-Time Pipeline

```
[Kafka raw.events]
       │
       ▼
[Flink Job 1: Validation & Enrichment]
  - Null/type checks on required fields
  - Timestamp drift check (>10min → reject)
  - Enrich user_id → user segment (Redis)
  - Enrich item_id → category/brand (cache)
       │
  ┌────┴────┐
  ▼         ▼
[validated.events]  [dlq.events + failure tag]
  │
  ▼
[Flink Job 2: Metric Aggregation]
  - CTR: 1min / 5min tumbling windows
  - CVR: 5min / 15min tumbling windows
  - Revenue per model: 5min tumbling
  - DLQ rate: 1min tumbling
  │
  ├──→ [Druid — OLAP queries]
  └──→ [Redis — live counters]
```

### Real-Time Metrics

| Metric | Window | Sink | Use Case |
|--------|--------|------|----------|
| CTR (clicks/impressions) | 1min / 5min tumbling | Druid + Redis | Live dashboard |
| CVR (purchases/clicks) | 5min / 15min tumbling | Druid | Conversion monitoring |
| Revenue per model | 5min tumbling | Druid | A/B experiment tracking |
| DLQ rate | 1min tumbling | Redis + Alert | Data quality alerting |
| P99 event latency | 30s sliding | Redis | Eng health monitoring |
| Feature freshness lag | 1min tumbling | Redis | ML model health |

**SLAs:** CTR metric latency < 2min | Stream pipeline uptime 99.9% | DLQ rate < 0.1%

---

## 5. Batch Processing — Historical Pipeline

```
[Kafka raw.events]
       │
       ▼
[S3 / GCS — Raw Data Lake — Parquet/day]
       │
       ▼
[Spark ETL — Hourly + Daily]
       │
       ▼
[Data Warehouse — Snowflake / BigQuery]
       │
       ▼
[dbt Models — Business Layer]
   ├──→ [BI Dashboard — Tableau / Superset]
   └──→ [ML Feature Store — Feast / Tecton]
```

### Batch Schedule

| Time | Job | Description |
|------|-----|-------------|
| T+00:05 | Hourly micro-batch | Spark reads S3 partition, validates schema, writes to DW staging |
| T+01:00 | Hourly aggregation | CTR/CVR/revenue rolled up per hour per model version |
| T+06:00 | Daily full refresh | Recompute 30-day cohort metrics, funnel analysis |
| T+07:00 | ML feature batch | Recompute collaborative-filtering features, write to Feature Store |
| T+08:00 | dbt run | Refresh business-layer models for BI dashboards |

### Data Warehouse Schema (Star Schema)

| Table | Type | Grain | Retention |
|-------|------|-------|-----------|
| `fact_rec_events` | Fact | 1 row per event | 2 years |
| `fact_rec_daily` | Fact (agg) | model × date × category | 3 years |
| `dim_item` | Dimension | 1 row per item | Current |
| `dim_user_segment` | Dimension | 1 row per user tier | Current |
| `dim_model_version` | Dimension | 1 row per model deploy | Permanent |
| `dim_date` | Dimension | 1 row per date | Permanent |

---

## 6. Data Quality & Alerting

### Quality Rule Catalog

#### Schema Checks

| Rule | Threshold | Action |
|------|-----------|--------|
| Null `event_id` rate | > 0.01% | P1 Alert + pause ingestion |
| Null `user_id` rate | > 0.5% | P2 Alert |
| Invalid `event_type` | > 0.1% | P2 Alert + route to DLQ |
| Timestamp drift > 10min | > 1% | P2 Alert |
| Missing revenue on purchase | > 0.01% | P1 Alert |

#### Volume Checks

| Rule | Threshold | Action |
|------|-----------|--------|
| Events/min drop > 50% | vs 7-day avg | P1 Alert |
| Events/min drop > 20% | vs 7-day avg | P2 Alert |
| CTR anomaly (z-score) | > 3 sigma | P2 Alert |
| Zero events > 2min | Any topic | P1 Alert |
| DLQ rate spike | > 0.5% | P2 Alert |

#### Freshness Checks

| Rule | Threshold | Action |
|------|-----------|--------|
| Stream lag behind wall clock | > 5min | P1 Alert |
| Hourly batch delay | > 30min | P2 Alert |
| Daily batch delay | > 2hr | P2 Alert |
| Feature store staleness | > 1hr | P2 Alert |
| DW table not updated | > 2hr | P2 Alert |

> ⚠️ **Alert Routing Policy:** P1 → PagerDuty (page on-call immediately). P2 → `#data-quality` Slack. P3 → Dashboard warning banner only. All alerts auto-attach a runbook link.

---

## 7. Dashboards

### 7.1 Business KPIs

| Metric | Current | Target | Trend |
|--------|---------|--------|-------|
| Overall CTR | 4.2% | 4.5% | ↑ +0.3% |
| CVR | 2.1% | 2.5% | ↑ +0.1% |
| Revenue via Rec | $1.8M/day | $2M/day | ↑ +8% |
| Rec Coverage | 72% | 80% | ↑ +2% |

**CTR by Model Version:**
```
v1.2 ████████████████████░░░░  3.8%
v1.3 █████████████████████░░░  4.1%
v1.4 █████████████████████░░░  4.2%
v1.5 ██████████████████████░░  4.5%
```

**Event Type Distribution:**
```
Impression  ████████████████████████████████████████  82%
Click       ██████                                    12%
AddToCart   ██                                         4%
Purchase    █                                          2%
```

### 7.2 Engineering Health

| Metric | Value | Status |
|--------|-------|--------|
| Kafka Consumer Lag | < 5K msgs | 🟢 OK |
| Flink Checkpoint Interval | 30s | 🟢 OK |
| Spark Job P99 Duration | 22min | 🟡 Watch |
| DLQ Rate (live) | 0.04% | 🟢 OK |
| Kafka Disk Usage | 61% | 🟢 OK |
| Flink TM Memory | 74% | 🟡 Watch |
| Druid Query Cache Hit | 88% | 🟢 OK |
| Redis Memory | 55% | 🟢 OK |

---

## 8. ML Feature Freshness Monitoring

```
[Batch Features — Spark daily] ──┐
                                  ├──→ [Feature Store — Feast/Tecton]
[Stream Features — Flink 1min] ──┘         │               │
                                     [Online Store]   [Offline Store]
                                        Redis            S3 + DW
                                           │               │
                                    [Model Server]   [Training Jobs]
```

### Feature Freshness SLAs

| Feature Group | Update Freq | Max Staleness | Alert Threshold |
|---------------|-------------|---------------|-----------------|
| User interaction history | 1min stream | 5min | > 3min lag |
| Item popularity scores | 5min stream | 15min | > 10min lag |
| User-item affinity matrix | Hourly batch | 2hrs | > 90min lag |
| Collaborative filter embeddings | Daily batch | 26hrs | > 25hr lag |
| User demographic features | Daily batch | 26hrs | > 25hr lag |

**Metrics:** Online feature P99 latency: **3ms** | Freshness SLA met: **99.7%** | Active skew alerts: **0**

> ℹ️ Feature freshness metrics are published to Grafana and compared against a rolling 7-day baseline. Any staleness breach automatically blocks model promotion in the CI/CD pipeline.

---

## 9. Technology Stack

### Ingestion

| Component | Technology | Purpose |
|-----------|------------|---------|
| Event SDK | Custom JS/iOS/Android | Client-side event capture |
| API Gateway | Kong | Rate limiting, auth, routing |
| Message Broker | Apache Kafka | Durable event streaming |
| Schema Registry | Confluent SR (Avro) | Schema enforcement and evolution |

### Processing

| Component | Technology | Purpose |
|-----------|------------|---------|
| Stream Processing | Apache Flink 1.18 | Real-time metrics and validation |
| Batch Processing | Apache Spark 3.5 | Historical aggregation and ETL |
| Orchestration | Apache Airflow | DAG scheduling for batch jobs |
| Transformation | dbt | Business-layer SQL models |

### Storage

| Component | Technology | Purpose |
|-----------|------------|---------|
| Raw Data Lake | S3 / GCS (Parquet) | Immutable event archive |
| OLAP Store | Apache Druid | Sub-second real-time queries |
| Live Counters | Redis Cluster | Real-time metric serving |
| Data Warehouse | Snowflake / BigQuery | Historical analytics and BI |
| Feature Store | Feast + Tecton | ML feature serving and training |

### Dashboards & Alerts

| Component | Technology | Purpose |
|-----------|------------|---------|
| Engineering Board | Grafana | Pipeline health, infra metrics |
| BI Dashboard | Tableau / Superset | Business KPIs and reporting |
| Alerting | PagerDuty + Slack | Incident and quality alerts |
| Data Quality | Great Expectations | Rule-based data validation |
| Tracing | OpenTelemetry + Jaeger | Distributed pipeline tracing |

---

## 10. Scalability & SLA Summary

| Metric | Current | Target | Trend |
|--------|---------|--------|-------|
| Daily Events | 2B+ | 2B | ↑ +5% |
| Peak Throughput | 28K/sec | 30K/sec | ↑ +8% |
| Stream End-to-End Latency | < 500ms | < 500ms | → 0% |
| Batch SLA | < 30min | < 30min | ↓ -5% |
| Ingestion Uptime | 99.99% | 99.99% | → 0% |
| Data Completeness | > 99.9% | 99.9% | ↑ +0.02% |
| DLQ Rate | < 0.1% | < 0.1% | ↓ -0.02% |
| Feature Freshness SLA | 99.7% | 99.5% | ↑ +0.2% |

### Key Design Decisions

1. **Lambda Architecture** — Flink for speed layer (real-time), Spark for batch layer (accuracy), Druid/DW as serving layer satisfies both latency and historical query needs
2. **Schema Registry with Avro** — Enforces schema evolution contracts at ingestion time, preventing downstream breakage from producer changes
3. **DLQ-first validation** — Invalid events are never silently dropped; they're routed to `dlq.events` for replay after fixes, ensuring no data loss
4. **Feature freshness gating** — Model promotion in CI/CD is blocked if any feature group breaches its freshness SLA, preventing stale-feature degradation in production
5. **Tiered alerting (P1/P2/P3)** — Reduces alert fatigue by separating actionable outages (P1) from quality degradation (P2) and monitoring anomalies (P3)

---

> 🚀 **Next Steps:** Phase 1: Deploy Kafka + Flink stream pipeline with validation. Phase 2: Build Spark batch ETL and DW models. Phase 3: Launch BI + Grafana dashboards. Phase 4: Integrate Feature Store with ML model CI/CD.

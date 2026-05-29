# Incident Postmortem — Payment Service Outage

> Severity: P0 · Duration: 47 minutes · Date: 2025-09-12 · Author: Platform Team

| Metric | Value |
|--------|-------|
| Severity | P0 |
| Duration | 47 min |
| Users Affected | ~12,400 |
| Revenue Impact | ~$31K |

> ❌ **Payment processing was completely unavailable from 14:23 to 15:10 UTC on September 12, 2025.** All checkout flows returned 503. Subscription renewals were queued and processed after recovery.

---

## Timeline

1. **14:23 UTC** — Automated alert fired — payment-service p99 latency exceeded 5s threshold
2. **14:26 UTC** — On-call engineer acknowledged alert, began investigation
3. **14:31 UTC** — Identified connection pool exhaustion on payments-db-primary
4. **14:38 UTC** — Attempted connection pool increase — did not resolve, pool exhausted within 90s
5. **14:44 UTC** — Identified root cause: runaway analytics query holding locks on payments table
6. **14:51 UTC** — Killed offending query, connection pool recovered within 60s
7. **14:58 UTC** — Payment service health checks green, traffic restored gradually
8. **15:10 UTC** — Full traffic restored, incident resolved
9. **15:45 UTC** — Postmortem initiated, contributing factors documented

---

## Root Cause

A new analytics report introduced in the v2.4.1 deploy (13:55 UTC) ran a full table scan on `payments` without a query timeout. The query held row-level locks for 28 minutes, causing connection pool exhaustion on the primary database. Payments service workers queued connections until the pool limit was hit, at which point all requests failed with 503.

**Contributing factors:**
1. No query timeout configured on the analytics read replica connection
2. Analytics queries were running against primary instead of replica due to a misconfigured read preference
3. No circuit breaker between analytics service and payments database

```sql
SELECT
    u.id, u.email, p.amount, p.created_at,
    COUNT(r.id) as refund_count
FROM payments p
JOIN users u ON p.user_id = u.id
LEFT JOIN refunds r ON r.payment_id = p.id
WHERE p.created_at > '2024-01-01'
GROUP BY u.id, u.email, p.amount, p.created_at
ORDER BY p.created_at DESC;
-- Missing: statement_timeout, index on payments.created_at, read replica routing
```

---

## Impact Analysis

| Service | Impact | Duration |
|---------|--------|----------|
| Checkout flow | 100% failure — 503 on all requests | 47 min |
| Subscription renewals | Queued, not failed — processed post-recovery | 47 min |
| Payment history API | Read-only, unaffected | — |
| Refund processing | Blocked — recovered automatically | 47 min |
| Fraud detection | Unaffected — separate database | — |

**Affected transaction types:** Checkout 61% · Subscription Renewal 28% · Manual Charge 11%

---

## Action Items

| Action | Owner | Priority | Due |
|--------|-------|----------|-----|
| Add statement_timeout=30s to all analytics queries | @data-eng | P0 | 2025-09-13 |
| Route analytics queries to read replica | @platform | P0 | 2025-09-14 |
| Add circuit breaker between analytics and payments DB | @platform | P1 | 2025-09-20 |
| Set up PagerDuty alert for connection pool >80% | @platform | P1 | 2025-09-18 |
| Add load test for analytics queries in CI | @data-eng | P2 | 2025-09-30 |
| Document query review checklist for PRs touching payments | @eng-lead | P2 | 2025-10-01 |

---

## What Went Well

- [x] Alert fired within 3 minutes of degradation starting
- [x] On-call response time was under 5 minutes
- [x] Subscription renewals were queued rather than dropped — no data loss
- [x] Runbook for database connection issues was accurate and actionable
- [x] Communication to customers sent within 15 minutes of detection

> ✅ No data loss. All queued transactions processed successfully within 8 minutes of recovery. Customer-facing status page updated within 12 minutes of detection.

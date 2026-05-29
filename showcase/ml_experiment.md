# ML Experiment Log — Churn Prediction v3

> Project: Customer Retention · Run ID: exp-2025-0912 · Author: @ml-team

| Metric | Value | Trend |
|--------|-------|-------|
| Best AUC-ROC | 0.923 | +3.1% |
| F1 Score | 0.871 | +2.4% |
| Precision | 0.889 | — |
| Recall | 0.854 | — |

> 🏆 **Best model: XGBoost with SMOTE + feature selection.** Outperforms production baseline (v2 LightGBM) by +3.1% AUC-ROC. Recommended for A/B test deployment targeting high-risk segment (top 15% churn probability).

---

## Model Comparison

| Model | AUC-ROC | F1 | Precision | Recall | Train Time | Notes |
|-------|---------|----|-----------|--------|------------|-------|
| Logistic Regression (baseline) | 0.831 | 0.802 | 0.819 | 0.786 | 12s | — |
| Random Forest | 0.874 | 0.838 | 0.851 | 0.825 | 4m 2s | — |
| LightGBM v2 (production) | 0.892 | 0.847 | 0.863 | 0.832 | 1m 18s | current prod |
| XGBoost default | 0.901 | 0.858 | 0.872 | 0.844 | 2m 44s | — |
| **XGBoost + SMOTE + FS** | **0.923** | **0.871** | **0.889** | **0.854** | 3m 12s | **winner** |
| Neural Net (MLP) | 0.908 | 0.861 | 0.874 | 0.849 | 18m 5s | not worth cost |

---

## Top Features — XGBoost + SMOTE

| Rank | Feature | Importance | Description |
|------|---------|------------|-------------|
| 1 | days_since_last_login | 0.182 | Recency signal — strongest predictor |
| 2 | support_tickets_30d | 0.147 | Friction indicator |
| 3 | feature_adoption_score | 0.134 | Engagement breadth |
| 4 | mrr_change_90d | 0.118 | Expansion/contraction signal |
| 5 | api_calls_trend_30d | 0.096 | Usage velocity |
| 6 | seats_utilization_pct | 0.089 | Team adoption |
| 7 | nps_score_last | 0.074 | Satisfaction signal |
| 8 | contract_months_remaining | 0.068 | Renewal proximity |
| 9 | onboarding_completion_pct | 0.052 | Early health indicator |
| 10 | billing_failure_count_90d | 0.040 | Payment health |

Feature category contribution: Engagement 41% · Financial 27% · Support 19% · Satisfaction 13%

---

## Training Details

**Dataset**
- Training samples: 84,210
- Test samples: 21,053
- Churn rate (raw): 8.3%
- Churn rate (SMOTE): 30%

**Hyperparameters**
- n_estimators: 450
- max_depth: 6
- learning_rate: 0.05
- subsample: 0.8

```python
from xgboost import XGBClassifier
from imblearn.over_sampling import SMOTE
from sklearn.feature_selection import SelectFromModel

# SMOTE for class imbalance
sm = SMOTE(sampling_strategy=0.3, random_state=42)
X_train_res, y_train_res = sm.fit_resample(X_train, y_train)

# Feature selection via LightGBM importance
selector = SelectFromModel(lgb_model, threshold="1.25*mean")
X_train_sel = selector.transform(X_train_res)

# Final XGBoost
model = XGBClassifier(
    n_estimators=450,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    eval_metric="auc",
    early_stopping_rounds=20,
)
model.fit(X_train_sel, y_train_res,
          eval_set=[(X_val_sel, y_val)])
```

---

## Deployment Plan

1. **Week 1** — Shadow mode deployment — score all customers daily, no action taken
2. **Week 2** — A/B test — top 15% churn risk: 50% get proactive CS outreach
3. **Week 3** — Review A/B results — measure 30-day retention lift
4. **Week 4** — Full rollout if lift >5% reduction in churn rate

**Success Criteria**
- [ ] 30-day churn rate in treatment group reduced by ≥5% vs control
- [ ] False positive rate (flagged as churn risk, did not churn) stays below 25%
- [ ] No increase in CS team escalation rate from over-triggering
- [ ] Model inference latency p99 < 50ms in production

> ℹ️ Experiment tracking in MLflow: run ID `exp-2025-0912`. Model artifact registered as `churn-prediction-v3` in staging. Promotion to production requires data science lead approval.

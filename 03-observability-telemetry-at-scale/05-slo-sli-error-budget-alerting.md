# 🎯 SLI, SLO & Error Budget Engineering (The SRE Mathematics)

> **Senior/Staff Interview Scope**: Mathematical definitions of SLI/SLO/SLA, Error Budgets, Google SRE Multi-Window Multi-Burn-Rate alerting formulas, alert fatigue elimination, and Error Budget Policy governance.

---

## 1. Core Mathematical Definitions

$$\text{SLI (Service Level Indicator)} = \frac{\text{Good Events}}{\text{Total Valid Events}} \times 100\%$$

$$\text{Error Budget} = 100\% - \text{SLO}$$

### Example Calculation:
- **Service**: Payment API.
- **SLO Target**: $99.9\%$ successful requests ($< 500\text{ms}$ latency) over a **30-day rolling window**.
- **Total Requests**: 100,000,000 requests / month.
- **Error Budget**: $0.1\% \times 100,000,000 = 100,000\text{ allowed bad requests}$.

---

## 2. Why Naive Threshold Alerting Fails

- **Naive Rule**: `alert if error_rate > 1% for 5 minutes`
  - **Flaw 1 (False Positives)**: High error rate during low traffic (e.g. 2 out of 4 requests fail at 3 AM) pages the on-call engineer despite burning negligible error budget.
  - **Flaw 2 (Slow Burn undetected)**: An error rate of 0.2% on a 99.9% SLO consumes 200% of the monthly error budget over 2 weeks, but will NEVER trigger the 1% alert!

---

## 3. Google SRE Multi-Window Multi-Burn-Rate Alerting

A **Burn Rate of 1.0** means the error budget will be consumed in exactly the SLO window period (30 days). A **Burn Rate of 14.4** burns 2% of the budget in 1 hour and will consume the entire monthly budget in 50 hours.

```mermaid
flowchart TD
    subgraph Multi_Window_Multi_Burn_Rate["Google SRE Alerting Formula"]
        ShortWindow["Short Window (e.g. 5m / 30m)<br/>Confirms the outage is STILL happening NOW"]
        LongWindow["Long Window (e.g. 1h / 6h)<br/>Confirms significant error budget has burned"]
        
        ShortWindow & LongWindow --> AND_Condition{"Both Windows Active?"}
        AND_Condition -->|Burn Rate > 14.4 (1h)| PageP0["🚨 PAGER / P1 Incident<br/>(Burns 2% budget in 1 hour)"]
        AND_Condition -->|Burn Rate > 6.0 (6h)| TicketP2["🎫 TICKET / P2 Notification<br/>(Burns 5% budget in 6 hours)"]
        AND_Condition -->|No (Transient spike ended)| AutoResolve["Auto-resolve / Suppressed"]
    end
```

### Production PromQL Multi-Burn-Rate Alert Rule
```yaml
groups:
  - name: payment-service-slo-alerts
    rules:
      # P1 Page: 14.4x Burn Rate (1h long window + 5m short window)
      - alert: PaymentServiceErrorBudgetFastBurn
        expr: |
          (
            sum(rate(http_requests_total{service="payment", status=~"5.*"}[1h]))
            /
            sum(rate(http_requests_total{service="payment"}[1h]))
          ) > (14.4 * (1 - 0.999))
          AND
          (
            sum(rate(http_requests_total{service="payment", status=~"5.*"}[5m]))
            /
            sum(rate(http_requests_total{service="payment"}[5m]))
          ) > (14.4 * (1 - 0.999))
        for: 2m
        labels:
          severity: page
          tier: p1
        annotations:
          summary: "Payment API burning error budget at 14.4x rate (100% budget gone in 50h)"

      # P2 Ticket: 6x Burn Rate (6h long window + 30m short window)
      - alert: PaymentServiceErrorBudgetSlowBurn
        expr: |
          (
            sum(rate(http_requests_total{service="payment", status=~"5.*"}[6h]))
            /
            sum(rate(http_requests_total{service="payment"}[6h]))
          ) > (6.0 * (1 - 0.999))
          AND
          (
            sum(rate(http_requests_total{service="payment", status=~"5.*"}[30m]))
            /
            sum(rate(http_requests_total{service="payment"}[30m]))
          ) > (6.0 * (1 - 0.999))
        for: 15m
        labels:
          severity: ticket
          tier: p2
        annotations:
          summary: "Payment API burning error budget at 6x rate (100% budget gone in 5 days)"
```

---

## 4. Error Budget Policy & Governance

When an error budget is exhausted (< 0% remaining in a 30-day window):
1. **Feature Freeze**: Non-critical feature releases are halted.
2. **Prioritize Reliability**: 100% of engineering sprints are redirected to bug fixes, circuit breakers, and automated testing.
3. **Restoration Criteria**: Normal release velocity resumes only after error budget trends positive over a 14-day trailing period.

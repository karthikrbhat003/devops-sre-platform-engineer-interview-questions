#!/usr/bin/env python3
"""
AWS CloudWatch / Cost Explorer Anomaly Detector
- Queries AWS Cost Explorer API for daily cost spikes per service.
- Flags any service exceeding 25% cost jump over 7-day moving average.
"""

import boto3
from datetime import datetime, timedelta
from typing import List, Dict, Any

def get_daily_costs(days: int = 8) -> List[Dict[str, Any]]:
    """Fetches daily unblended costs grouped by SERVICE from AWS Cost Explorer."""
    client = boto3.client("ce", region_name="us-east-1")
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=days)

    response = client.get_cost_and_usage(
        TimePeriod={
            "Start": start_date.strftime("%Y-%m-%d"),
            "End": end_date.strftime("%Y-%m-%d"),
        },
        Granularity="DAILY",
        Metrics=["UnblendedCost"],
        GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
    )
    return response.get("ResultsByTime", [])

def detect_anomalies(results: List[Dict[str, Any]], spike_threshold_pct: float = 25.0):
    service_history = {}

    for day_data in results:
        date_str = day_data["TimePeriod"]["Start"]
        for group in day_data.get("Groups", []):
            service_name = group["Keys"][0]
            amount = float(group["Metrics"]["UnblendedCost"]["Amount"])
            if service_name not in service_history:
                service_history[service_name] = []
            service_history[service_name].append((date_str, amount))

    print(f"🔍 Analyzing AWS Cost Trends (Alert Threshold: +{spike_threshold_pct}% vs 7-day baseline)...")
    anomalies = []

    for service, points in service_history.items():
        if len(points) < 2:
            continue
        latest_date, latest_cost = points[-1]
        historical_costs = [amt for _, amt in points[:-1]]
        avg_cost = sum(historical_costs) / len(historical_costs)

        if avg_cost > 10.0: # Filter out noise below $10/day
            pct_change = ((latest_cost - avg_cost) / avg_cost) * 100
            if pct_change >= spike_threshold_pct:
                anomalies.append({
                    "service": service,
                    "date": latest_date,
                    "latest_cost": latest_cost,
                    "avg_cost": avg_cost,
                    "pct_change": pct_change,
                })

    if not anomalies:
        print("✅ No cost anomalies detected across any AWS services.")
        return

    print("\n🚨 AWS COST ANOMALIES DETECTED:")
    for a in sorted(anomalies, key=lambda x: x["pct_change"], reverse=True):
        print(f"  • {a['service']:<30} | Latest: ${a['latest_cost']:,.2f} | 7d-Avg: ${a['avg_cost']:,.2f} | Spike: +{a['pct_change']:.1f}%")

if __name__ == "__main__":
    # Mock data demonstration mode if AWS credentials not configured locally
    print("Running AWS Cost Anomaly Detector module demo...")
    mock_data = [
        {"TimePeriod": {"Start": "2026-08-27"}, "Groups": [{"Keys": ["Amazon Elastic Compute Cloud - Compute"], "Metrics": {"UnblendedCost": {"Amount": "100.0"}}}]},
        {"TimePeriod": {"Start": "2026-08-28"}, "Groups": [{"Keys": ["Amazon Elastic Compute Cloud - Compute"], "Metrics": {"UnblendedCost": {"Amount": "105.0"}}}]},
        {"TimePeriod": {"Start": "2026-08-29"}, "Groups": [{"Keys": ["Amazon Elastic Compute Cloud - Compute"], "Metrics": {"UnblendedCost": {"Amount": "102.0"}}}]},
        {"TimePeriod": {"Start": "2026-08-30"}, "Groups": [{"Keys": ["Amazon Elastic Compute Cloud - Compute"], "Metrics": {"UnblendedCost": {"Amount": "210.0"}}}]}, # 100%+ spike
    ]
    detect_anomalies(mock_data, spike_threshold_pct=25.0)

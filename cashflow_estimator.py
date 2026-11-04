#!/usr/bin/env python3
"""
MSME AI Cash Flow Estimator
Starter script for estimating liquidity gaps and working capital needs
using mock UPI transaction and GST insights data for Indian MSMEs.

Focus: Practical demo of cash-flow analysis to address delayed payments
and working capital stress.

Run: python cashflow_estimator.py
"""

from datetime import datetime, timedelta
from collections import defaultdict
import statistics

# Mock data representing typical MSME UPI inflows/outflows and GST-related insights
# In a real tool, this would come from UPI statement CSV exports or GST portal data
MOCK_TRANSACTIONS = [
    {"date": "2026-10-01", "type": "inflow", "amount": 150000, "category": "customer_payment", "description": "UPI from Retailer A"},
    {"date": "2026-10-05", "type": "outflow", "amount": 45000, "category": "supplier", "description": "Raw material payment"},
    {"date": "2026-10-10", "type": "inflow", "amount": 80000, "category": "customer_payment", "description": "Partial payment - delayed invoice"},
    {"date": "2026-10-12", "type": "outflow", "amount": 25000, "category": "gst", "description": "GST payment"},
    {"date": "2026-10-15", "type": "outflow", "amount": 60000, "category": "salary", "description": "Staff salaries"},
    {"date": "2026-10-20", "type": "inflow", "amount": 200000, "category": "customer_payment", "description": "Large order settlement"},
    {"date": "2026-10-22", "type": "outflow", "amount": 90000, "category": "supplier", "description": "Inventory replenishment"},
    {"date": "2026-10-25", "type": "outflow", "amount": 15000, "category": "gst", "description": "Additional GST"},
    {"date": "2026-10-28", "type": "inflow", "amount": 45000, "category": "customer_payment", "description": "Small retailer UPI"},
    {"date": "2026-11-01", "type": "outflow", "amount": 30000, "category": "utility", "description": "Rent and utilities"},
]

# Simulated delayed receivables (common MSME issue)
DELAYED_RECEIVABLES = [
    {"invoice_date": "2026-09-15", "amount": 120000, "days_overdue": 50, "customer": "Distributor X"},
    {"invoice_date": "2026-09-28", "amount": 75000, "days_overdue": 37, "customer": "Retail Chain Y"},
]

def parse_date(date_str):
    """Convert date string to datetime object."""
    return datetime.strptime(date_str, "%Y-%m-%d")

def calculate_cash_flow(transactions):
    """
    Calculate net cash flow, category-wise summaries, and basic metrics.
    Returns totals and a simple projection base.
    """
    inflows = 0
    outflows = 0
    category_summary = defaultdict(lambda: {"in": 0, "out": 0})
    daily_net = defaultdict(int)

    for txn in transactions:
        amount = txn["amount"]
        cat = txn["category"]
        day = txn["date"]

        if txn["type"] == "inflow":
            inflows += amount
            category_summary[cat]["in"] += amount
            daily_net[day] += amount
        else:
            outflows += amount
            category_summary[cat]["out"] += amount
            daily_net[day] -= amount

    net_cash_flow = inflows - outflows
    avg_daily_net = statistics.mean(daily_net.values()) if daily_net else 0

    return {
        "total_inflows": inflows,
        "total_outflows": outflows,
        "net_cash_flow": net_cash_flow,
        "category_summary": dict(category_summary),
        "avg_daily_net": avg_daily_net,
        "transaction_count": len(transactions),
    }

def estimate_working_capital(cash_flow, delayed_receivables, projection_days=30):
    """
    Estimate working capital needs based on current net position,
    delayed receivables, and simple projection.
    This is a rule-based starter; real AI would use time-series forecasting.
    """
    total_delayed = sum(r["amount"] for r in delayed_receivables)
    avg_overdue_days = statistics.mean(r["days_overdue"] for r in delayed_receivables) if delayed_receivables else 0

    # Simple projection: assume current avg daily net continues, adjusted for delayed recovery
    projected_net = cash_flow["avg_daily_net"] * projection_days
    # Conservative: assume only 60% of delayed receivables recover within projection window
    recoverable = total_delayed * 0.6

    # Working capital buffer: cover projected outflows + safety margin for delays
    estimated_buffer = max(0, -projected_net) + (total_delayed * 0.3)  # 30% risk buffer on delayed

    return {
        "total_delayed_receivables": total_delayed,
        "average_overdue_days": round(avg_overdue_days, 1),
        "projected_30day_net": round(projected_net, 2),
        "estimated_recoverable": round(recoverable, 2),
        "recommended_working_capital_buffer": round(estimated_buffer, 2),
        "risk_level": "High" if avg_overdue_days > 45 else "Medium" if avg_overdue_days > 30 else "Low",
    }

def generate_report(cash_flow, wc_estimate):
    """Print a clear, professional report."""
    print("=" * 60)
    print("MSME AI CASH FLOW ESTIMATOR - STARTER DEMO")
    print("Focus: Indian MSME Liquidity & Working Capital")
    print("=" * 60)
    print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"Transactions Analyzed: {cash_flow['transaction_count']}")
    print()

    print("CASH FLOW SUMMARY (Recent Period)")
    print(f"  Total Inflows:     ₹{cash_flow['total_inflows']:,.0f}")
    print(f"  Total Outflows:    ₹{cash_flow['total_outflows']:,.0f}")
    print(f"  Net Cash Flow:     ₹{cash_flow['net_cash_flow']:,.0f}")
    print(f"  Avg Daily Net:     ₹{cash_flow['avg_daily_net']:,.0f}")
    print()

    print("CATEGORY BREAKDOWN")
    for cat, vals in cash_flow["category_summary"].items():
        net = vals["in"] - vals["out"]
        print(f"  {cat.capitalize():<18} In: ₹{vals['in']:>10,.0f} | Out: ₹{vals['out']:>10,.0f} | Net: ₹{net:>10,.0f}")
    print()

    print("WORKING CAPITAL & DELAYED PAYMENTS ESTIMATE")
    print(f"  Delayed Receivables: ₹{wc_estimate['total_delayed_receivables']:,.0f}")
    print(f"  Avg Overdue Days:    {wc_estimate['average_overdue_days']}")
    print(f"  Risk Level:          {wc_estimate['risk_level']}")
    print(f"  Projected 30-day Net: ₹{wc_estimate['projected_30day_net']:,.0f}")
    print(f"  Est. Recoverable:    ₹{wc_estimate['estimated_recoverable']:,.0f}")
    print(f"  Recommended Buffer:  ₹{wc_estimate['recommended_working_capital_buffer']:,.0f}")
    print()

    print("KEY INSIGHTS & NEXT STEPS")
    if wc_estimate["risk_level"] == "High":
        print("  • High delayed payment risk detected. Prioritize collections and consider TReDS for early payment.")
    print("  • Integrate real UPI/GST data for accurate forecasting.")
    print("  • Extend with AI models for seasonal pattern detection and predictive alerts.")
    print("  • Explore Account Aggregator or bank statement APIs for live data.")
    print()
    print("This is a starter demo. Replace mock data and add ML for production use.")
    print("=" * 60)

def main():
    """Main execution function."""
    print("Starting MSME Cash Flow Analysis...\n")

    cash_flow = calculate_cash_flow(MOCK_TRANSACTIONS)
    wc_estimate = estimate_working_capital(cash_flow, DELAYED_RECEIVABLES)
    generate_report(cash_flow, wc_estimate)

if __name__ == "__main__":
    main()

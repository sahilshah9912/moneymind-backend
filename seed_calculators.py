"""
seed_calculators.py — Defines all 50 calculators with real, working formulas.
Run once via: python seed_calculators.py  (adds/updates rows in calculators table)

Each calculator dict matches the Calculator model fields.
Formulas use formula_steps (named intermediate variables) for readability + a final
output mapping. All formulas use only the safe operators/functions in formula_engine.py.
"""

CALCULATORS = [

    # ═══════════════════════════ LOANS (8) — incl. 2 featured ═══════════════════════════
    {
        "slug": "home-loan-emi", "name": "Home Loan EMI Planner", "category": "Loans",
        "icon": "🏠", "description": "Calculate monthly EMI for a fresh home loan.",
        "is_featured": True, "featured_order": 1, "sort_order": 1,
        "inputs": [
            {"key": "loan_amount", "label": "Loan Amount", "type": "number", "default": 5000000, "min": 100000, "max": 100000000, "unit": "₹", "step": 50000},
            {"key": "annual_rate", "label": "Interest Rate", "type": "number", "default": 8.5, "min": 5, "max": 20, "unit": "%", "step": 0.05},
            {"key": "tenure_years", "label": "Loan Tenure", "type": "number", "default": 20, "min": 1, "max": 30, "unit": "years", "step": 1},
        ],
        "formula_steps": [
            {"var": "tenure_months", "expr": "tenure_years * 12"},
            {"var": "r", "expr": "annual_rate / 12 / 100"},
            {"var": "emi", "expr": "(loan_amount * r * (1+r)**tenure_months) / ((1+r)**tenure_months - 1)"},
            {"var": "total_payment", "expr": "emi * tenure_months"},
            {"var": "total_interest", "expr": "total_payment - loan_amount"},
        ],
        "formula": "emi",
        "outputs": [
            {"key": "emi", "label": "Monthly EMI", "format": "currency"},
            {"key": "total_interest", "label": "Total Interest Payable", "format": "currency"},
            {"key": "total_payment", "label": "Total Amount Payable", "format": "currency"},
        ],
        "constants": {},
    },
    {
        "slug": "loan-prepayment-impact", "name": "Loan Prepayment Impact", "category": "Loans",
        "icon": "💳", "description": "See how much time/interest you save with extra payments.",
        "is_featured": False, "sort_order": 2,
        "inputs": [
            {"key": "outstanding_principal", "label": "Outstanding Principal", "type": "number", "default": 4000000, "min": 10000, "max": 100000000, "unit": "₹", "step": 10000},
            {"key": "annual_rate", "label": "Interest Rate", "type": "number", "default": 8.5, "min": 5, "max": 20, "unit": "%", "step": 0.05},
            {"key": "remaining_months", "label": "Remaining Tenure", "type": "number", "default": 180, "min": 1, "max": 360, "unit": "months", "step": 1},
            {"key": "extra_monthly", "label": "Extra Monthly Payment", "type": "number", "default": 10000, "min": 0, "max": 1000000, "unit": "₹", "step": 1000},
        ],
        "formula_steps": [
            {"var": "r", "expr": "annual_rate / 12 / 100"},
            {"var": "emi", "expr": "(outstanding_principal * r * (1+r)**remaining_months) / ((1+r)**remaining_months - 1)"},
            {"var": "new_emi", "expr": "emi + extra_monthly"},
            {"var": "new_tenure_months", "expr": "log((new_emi)/(new_emi - outstanding_principal*r)) / log(1+r)"},
            {"var": "months_saved", "expr": "remaining_months - new_tenure_months"},
            {"var": "old_total_interest", "expr": "emi*remaining_months - outstanding_principal"},
            {"var": "new_total_interest", "expr": "new_emi*new_tenure_months - outstanding_principal"},
            {"var": "interest_saved", "expr": "old_total_interest - new_total_interest"},
        ],
        "formula": "interest_saved",
        "outputs": [
            {"key": "months_saved", "label": "Months Saved", "format": "number"},
            {"key": "interest_saved", "label": "Interest Saved", "format": "currency"},
            {"key": "new_tenure_months", "label": "New Tenure (months)", "format": "number"},
        ],
        "constants": {},
    },
    {
        "slug": "loan-refinance-comparator", "name": "Loan Refinance / Balance Transfer", "category": "Loans",
        "icon": "🔄", "description": "Compare your current loan vs a refinanced lower-rate loan.",
        "is_featured": False, "featured_order": 0, "sort_order": 3,
        "inputs": [
            {"key": "outstanding_principal", "label": "Outstanding Principal", "type": "number", "default": 4000000, "min": 10000, "max": 100000000, "unit": "₹", "step": 10000},
            {"key": "old_rate", "label": "Current Interest Rate", "type": "number", "default": 9.5, "min": 5, "max": 20, "unit": "%", "step": 0.05},
            {"key": "new_rate", "label": "New Offer Rate", "type": "number", "default": 8.3, "min": 5, "max": 20, "unit": "%", "step": 0.05},
            {"key": "remaining_months", "label": "Remaining Tenure", "type": "number", "default": 180, "min": 1, "max": 360, "unit": "months", "step": 1},
            {"key": "processing_fee", "label": "Refinance Processing Fee", "type": "number", "default": 15000, "min": 0, "max": 500000, "unit": "₹", "step": 1000},
        ],
        "formula_steps": [
            {"var": "r_old", "expr": "old_rate / 12 / 100"},
            {"var": "r_new", "expr": "new_rate / 12 / 100"},
            {"var": "emi_old", "expr": "(outstanding_principal * r_old * (1+r_old)**remaining_months) / ((1+r_old)**remaining_months - 1)"},
            {"var": "emi_new", "expr": "(outstanding_principal * r_new * (1+r_new)**remaining_months) / ((1+r_new)**remaining_months - 1)"},
            {"var": "monthly_saving", "expr": "emi_old - emi_new"},
            {"var": "total_old_interest", "expr": "emi_old*remaining_months - outstanding_principal"},
            {"var": "total_new_interest", "expr": "emi_new*remaining_months - outstanding_principal"},
            {"var": "net_lifetime_saving", "expr": "total_old_interest - total_new_interest - processing_fee"},
        ],
        "formula": "net_lifetime_saving",
        "outputs": [
            {"key": "emi_old", "label": "Current EMI", "format": "currency"},
            {"key": "emi_new", "label": "New EMI", "format": "currency"},
            {"key": "monthly_saving", "label": "Monthly Saving", "format": "currency"},
            {"key": "net_lifetime_saving", "label": "Net Lifetime Saving (after fees)", "format": "currency"},
        ],
        "constants": {},
    },
    {
        "slug": "car-loan-emi", "name": "Car Loan EMI Planner", "category": "Loans",
        "icon": "🚗", "description": "EMI for new or used car loans.",
        "is_featured": False, "sort_order": 4,
        "inputs": [
            {"key": "loan_amount", "label": "Loan Amount", "type": "number", "default": 800000, "min": 50000, "max": 10000000, "unit": "₹", "step": 10000},
            {"key": "annual_rate", "label": "Interest Rate", "type": "number", "default": 9.5, "min": 5, "max": 18, "unit": "%", "step": 0.05},
            {"key": "tenure_years", "label": "Tenure", "type": "number", "default": 5, "min": 1, "max": 8, "unit": "years", "step": 1},
        ],
        "formula_steps": [
            {"var": "tenure_months", "expr": "tenure_years * 12"},
            {"var": "r", "expr": "annual_rate / 12 / 100"},
            {"var": "emi", "expr": "(loan_amount * r * (1+r)**tenure_months) / ((1+r)**tenure_months - 1)"},
            {"var": "total_interest", "expr": "emi*tenure_months - loan_amount"},
        ],
        "formula": "emi",
        "outputs": [
            {"key": "emi", "label": "Monthly EMI", "format": "currency"},
            {"key": "total_interest", "label": "Total Interest", "format": "currency"},
        ],
        "constants": {},
    },
    {
        "slug": "personal-loan-emi", "name": "Personal Loan EMI Planner", "category": "Loans",
        "icon": "💵", "description": "EMI for unsecured personal loans.",
        "is_featured": False, "sort_order": 5,
        "inputs": [
            {"key": "loan_amount", "label": "Loan Amount", "type": "number", "default": 300000, "min": 10000, "max": 5000000, "unit": "₹", "step": 5000},
            {"key": "annual_rate", "label": "Interest Rate", "type": "number", "default": 13, "min": 8, "max": 28, "unit": "%", "step": 0.1},
            {"key": "tenure_years", "label": "Tenure", "type": "number", "default": 3, "min": 1, "max": 7, "unit": "years", "step": 1},
        ],
        "formula_steps": [
            {"var": "tenure_months", "expr": "tenure_years * 12"},
            {"var": "r", "expr": "annual_rate / 12 / 100"},
            {"var": "emi", "expr": "(loan_amount * r * (1+r)**tenure_months) / ((1+r)**tenure_months - 1)"},
            {"var": "total_interest", "expr": "emi*tenure_months - loan_amount"},
        ],
        "formula": "emi",
        "outputs": [
            {"key": "emi", "label": "Monthly EMI", "format": "currency"},
            {"key": "total_interest", "label": "Total Interest", "format": "currency"},
        ],
        "constants": {},
    },
    {
        "slug": "education-loan-emi", "name": "Education Loan EMI Planner", "category": "Loans",
        "icon": "🎓", "description": "EMI for education loans with optional moratorium.",
        "is_featured": False, "sort_order": 6,
        "inputs": [
            {"key": "loan_amount", "label": "Loan Amount", "type": "number", "default": 1500000, "min": 50000, "max": 10000000, "unit": "₹", "step": 10000},
            {"key": "annual_rate", "label": "Interest Rate", "type": "number", "default": 10.5, "min": 6, "max": 16, "unit": "%", "step": 0.1},
            {"key": "tenure_years", "label": "Repayment Tenure", "type": "number", "default": 10, "min": 1, "max": 15, "unit": "years", "step": 1},
        ],
        "formula_steps": [
            {"var": "tenure_months", "expr": "tenure_years * 12"},
            {"var": "r", "expr": "annual_rate / 12 / 100"},
            {"var": "emi", "expr": "(loan_amount * r * (1+r)**tenure_months) / ((1+r)**tenure_months - 1)"},
            {"var": "total_interest", "expr": "emi*tenure_months - loan_amount"},
        ],
        "formula": "emi",
        "outputs": [
            {"key": "emi", "label": "Monthly EMI", "format": "currency"},
            {"key": "total_interest", "label": "Total Interest", "format": "currency"},
        ],
        "constants": {},
    },
    {
        "slug": "loan-eligibility", "name": "Loan Eligibility Planner", "category": "Loans",
        "icon": "✅", "description": "Estimate max loan amount based on income.",
        "is_featured": False, "sort_order": 7,
        "inputs": [
            {"key": "monthly_income", "label": "Net Monthly Income", "type": "number", "default": 100000, "min": 10000, "max": 5000000, "unit": "₹", "step": 5000},
            {"key": "existing_emi", "label": "Existing Monthly EMIs", "type": "number", "default": 0, "min": 0, "max": 1000000, "unit": "₹", "step": 1000},
            {"key": "annual_rate", "label": "Interest Rate", "type": "number", "default": 8.5, "min": 5, "max": 20, "unit": "%", "step": 0.05},
            {"key": "tenure_years", "label": "Tenure", "type": "number", "default": 20, "min": 1, "max": 30, "unit": "years", "step": 1},
        ],
        "formula_steps": [
            {"var": "max_emi_allowed", "expr": "monthly_income * 0.5 - existing_emi"},
            {"var": "tenure_months", "expr": "tenure_years * 12"},
            {"var": "r", "expr": "annual_rate / 12 / 100"},
            {"var": "max_loan", "expr": "max_emi_allowed * ((1+r)**tenure_months - 1) / (r * (1+r)**tenure_months)"},
        ],
        "formula": "max_loan",
        "outputs": [
            {"key": "max_emi_allowed", "label": "Max EMI You Can Afford", "format": "currency"},
            {"key": "max_loan", "label": "Estimated Max Loan Eligibility", "format": "currency"},
        ],
        "constants": {"emi_to_income_ratio": 0.5},
    },
    {
        "slug": "gold-loan-emi", "name": "Gold Loan EMI Planner", "category": "Loans",
        "icon": "🪙", "description": "EMI for loans against gold.",
        "is_featured": False, "sort_order": 8,
        "inputs": [
            {"key": "loan_amount", "label": "Loan Amount", "type": "number", "default": 200000, "min": 10000, "max": 5000000, "unit": "₹", "step": 5000},
            {"key": "annual_rate", "label": "Interest Rate", "type": "number", "default": 10, "min": 7, "max": 18, "unit": "%", "step": 0.1},
            {"key": "tenure_years", "label": "Tenure", "type": "number", "default": 1, "min": 1, "max": 3, "unit": "years", "step": 1},
        ],
        "formula_steps": [
            {"var": "tenure_months", "expr": "tenure_years * 12"},
            {"var": "r", "expr": "annual_rate / 12 / 100"},
            {"var": "emi", "expr": "(loan_amount * r * (1+r)**tenure_months) / ((1+r)**tenure_months - 1)"},
        ],
        "formula": "emi",
        "outputs": [{"key": "emi", "label": "Monthly EMI", "format": "currency"}],
        "constants": {},
    },

    # ═══════════════════════════ INSURANCE (5) — incl. 1 featured ═══════════════════════════
    {
        "slug": "term-life-coverage-need", "name": "Term Life Coverage Need", "category": "Insurance",
        "icon": "🛡️", "description": "How much life cover do you actually need?",
        "is_featured": False, "sort_order": 9,
        "inputs": [
            {"key": "annual_income", "label": "Annual Income", "type": "number", "default": 1200000, "min": 100000, "max": 50000000, "unit": "₹", "step": 50000},
            {"key": "outstanding_loans", "label": "Outstanding Loans", "type": "number", "default": 3000000, "min": 0, "max": 100000000, "unit": "₹", "step": 50000},
            {"key": "years_to_cover", "label": "Years of Income to Replace", "type": "number", "default": 15, "min": 5, "max": 30, "unit": "years", "step": 1},
            {"key": "existing_cover", "label": "Existing Life Cover", "type": "number", "default": 0, "min": 0, "max": 100000000, "unit": "₹", "step": 50000},
        ],
        "formula_steps": [
            {"var": "income_replacement", "expr": "annual_income * years_to_cover"},
            {"var": "total_need", "expr": "income_replacement + outstanding_loans - existing_cover"},
        ],
        "formula": "total_need",
        "outputs": [{"key": "total_need", "label": "Additional Cover Needed", "format": "currency"}],
        "constants": {},
    },
    {
        "slug": "health-insurance-gap", "name": "Health Insurance Coverage Gap", "category": "Insurance",
        "icon": "🏥", "description": "Check if your health cover matches likely costs.",
        "is_featured": False, "sort_order": 10,
        "inputs": [
            {"key": "city_tier", "label": "City Tier (1=Metro, 2=Tier-2, 3=Tier-3)", "type": "number", "default": 1, "min": 1, "max": 3, "unit": "", "step": 1},
            {"key": "family_size", "label": "Family Size", "type": "number", "default": 4, "min": 1, "max": 10, "unit": "members", "step": 1},
            {"key": "current_cover", "label": "Current Health Cover", "type": "number", "default": 500000, "min": 0, "max": 20000000, "unit": "₹", "step": 50000},
        ],
        "formula_steps": [
            {"var": "base_per_person", "expr": "1000000 - (city_tier-1)*250000"},
            {"var": "recommended_cover", "expr": "base_per_person + (family_size-1)*200000"},
            {"var": "gap", "expr": "recommended_cover - current_cover"},
        ],
        "formula": "gap",
        "outputs": [
            {"key": "recommended_cover", "label": "Recommended Cover", "format": "currency"},
            {"key": "gap", "label": "Coverage Gap", "format": "currency"},
        ],
        "constants": {},
    },
    {
        "slug": "critical-illness-cover", "name": "Critical Illness Cover Estimator", "category": "Insurance",
        "icon": "💊", "description": "Estimate adequate critical illness cover.",
        "is_featured": False, "sort_order": 11,
        "inputs": [
            {"key": "annual_income", "label": "Annual Income", "type": "number", "default": 1200000, "min": 100000, "max": 50000000, "unit": "₹", "step": 50000},
            {"key": "existing_cover", "label": "Existing Critical Illness Cover", "type": "number", "default": 0, "min": 0, "max": 20000000, "unit": "₹", "step": 50000},
        ],
        "formula_steps": [
            {"var": "recommended", "expr": "annual_income * 3"},
            {"var": "gap", "expr": "recommended - existing_cover"},
        ],
        "formula": "gap",
        "outputs": [
            {"key": "recommended", "label": "Recommended Cover (3x income)", "format": "currency"},
            {"key": "gap", "label": "Coverage Gap", "format": "currency"},
        ],
        "constants": {"income_multiple": 3},
    },
    {
        "slug": "vehicle-insurance-estimator", "name": "Vehicle Insurance Premium Estimator", "category": "Insurance",
        "icon": "🚙", "description": "Rough estimate of annual vehicle insurance premium.",
        "is_featured": False, "sort_order": 12,
        "inputs": [
            {"key": "vehicle_value", "label": "Vehicle's Current (IDV) Value", "type": "number", "default": 600000, "min": 50000, "max": 10000000, "unit": "₹", "step": 10000},
            {"key": "vehicle_age", "label": "Vehicle Age", "type": "number", "default": 2, "min": 0, "max": 15, "unit": "years", "step": 1},
            {"key": "ncb_pct", "label": "No-Claim Bonus", "type": "number", "default": 20, "min": 0, "max": 50, "unit": "%", "step": 5},
        ],
        "formula_steps": [
            {"var": "base_premium_pct", "expr": "3.5 - (vehicle_age*0.1)"},
            {"var": "base_premium", "expr": "vehicle_value * base_premium_pct / 100"},
            {"var": "estimated_premium", "expr": "base_premium * (1 - ncb_pct/100)"},
        ],
        "formula": "estimated_premium",
        "outputs": [{"key": "estimated_premium", "label": "Estimated Annual Premium", "format": "currency"}],
        "constants": {},
    },
    {
        "slug": "insurance-optimizer", "name": "Insurance Premium vs Coverage Optimizer", "category": "Insurance",
        "icon": "⚖️", "description": "Find the most coverage-efficient mix of term + health cover for your budget.",
        "is_featured": True, "featured_order": 2, "sort_order": 13,
        "inputs": [
            {"key": "annual_income", "label": "Annual Income", "type": "number", "default": 1200000, "min": 100000, "max": 50000000, "unit": "₹", "step": 50000},
            {"key": "monthly_budget", "label": "Monthly Premium Budget", "type": "number", "default": 3000, "min": 500, "max": 100000, "unit": "₹", "step": 500},
            {"key": "family_size", "label": "Family Size", "type": "number", "default": 4, "min": 1, "max": 10, "unit": "members", "step": 1},
            {"key": "outstanding_loans", "label": "Outstanding Loans", "type": "number", "default": 3000000, "min": 0, "max": 100000000, "unit": "₹", "step": 50000},
        ],
        "formula_steps": [
            {"var": "ideal_term_cover", "expr": "annual_income*15 + outstanding_loans"},
            {"var": "ideal_health_cover", "expr": "1000000 + (family_size-1)*200000"},
            {"var": "annual_budget", "expr": "monthly_budget * 12"},
            {"var": "term_premium_est", "expr": "ideal_term_cover / 1000000 * 600"},
            {"var": "health_premium_est", "expr": "ideal_health_cover / 500000 * 8000"},
            {"var": "total_ideal_premium", "expr": "term_premium_est + health_premium_est"},
            {"var": "coverage_efficiency_pct", "expr": "min(100, (annual_budget/total_ideal_premium)*100)"},
        ],
        "formula": "coverage_efficiency_pct",
        "outputs": [
            {"key": "ideal_term_cover", "label": "Ideal Term Cover", "format": "currency"},
            {"key": "ideal_health_cover", "label": "Ideal Health Cover", "format": "currency"},
            {"key": "total_ideal_premium", "label": "Estimated Annual Premium Needed", "format": "currency"},
            {"key": "coverage_efficiency_pct", "label": "Your Budget Covers", "format": "percent"},
        ],
        "constants": {},
    },

    # ═══════════════════════════ INVESTMENTS / WEALTH (8) — incl. 1 featured (multi-mode) ═══════════════════════════
    {
        "slug": "sip-future-value", "name": "SIP Future Value Planner", "category": "Investments",
        "icon": "📈", "description": "Project the future value of a monthly SIP.",
        "is_featured": False, "sort_order": 14,
        "inputs": [
            {"key": "monthly_sip", "label": "Monthly SIP Amount", "type": "number", "default": 10000, "min": 500, "max": 1000000, "unit": "₹", "step": 500},
            {"key": "annual_return", "label": "Expected Annual Return", "type": "number", "default": 12, "min": 1, "max": 30, "unit": "%", "step": 0.5},
            {"key": "years", "label": "Investment Duration", "type": "number", "default": 15, "min": 1, "max": 40, "unit": "years", "step": 1},
        ],
        "formula_steps": [
            {"var": "months", "expr": "years * 12"},
            {"var": "r", "expr": "annual_return / 12 / 100"},
            {"var": "future_value", "expr": "monthly_sip * (((1+r)**months - 1) / r) * (1+r)"},
            {"var": "total_invested", "expr": "monthly_sip * months"},
            {"var": "wealth_gained", "expr": "future_value - total_invested"},
        ],
        "formula": "future_value",
        "outputs": [
            {"key": "future_value", "label": "Future Value", "format": "currency"},
            {"key": "total_invested", "label": "Total Invested", "format": "currency"},
            {"key": "wealth_gained", "label": "Wealth Gained", "format": "currency"},
        ],
        "constants": {},
    },
    {
        "slug": "lumpsum-future-value", "name": "Lumpsum Future Value Planner", "category": "Investments",
        "icon": "💰", "description": "Project growth of a one-time investment.",
        "is_featured": False, "sort_order": 15,
        "inputs": [
            {"key": "principal", "label": "Lumpsum Amount", "type": "number", "default": 500000, "min": 1000, "max": 100000000, "unit": "₹", "step": 10000},
            {"key": "annual_return", "label": "Expected Annual Return", "type": "number", "default": 12, "min": 1, "max": 30, "unit": "%", "step": 0.5},
            {"key": "years", "label": "Duration", "type": "number", "default": 15, "min": 1, "max": 40, "unit": "years", "step": 1},
        ],
        "formula_steps": [
            {"var": "future_value", "expr": "principal * (1 + annual_return/100)**years"},
            {"var": "wealth_gained", "expr": "future_value - principal"},
        ],
        "formula": "future_value",
        "outputs": [
            {"key": "future_value", "label": "Future Value", "format": "currency"},
            {"key": "wealth_gained", "label": "Wealth Gained", "format": "currency"},
        ],
        "constants": {},
    },
    {
        "slug": "sip-vs-lumpsum", "name": "SIP vs Lumpsum Comparator", "category": "Investments",
        "icon": "⚔️", "description": "Compare investing via SIP vs all at once.",
        "is_featured": False, "sort_order": 16,
        "inputs": [
            {"key": "total_amount", "label": "Total Amount to Invest", "type": "number", "default": 1200000, "min": 10000, "max": 100000000, "unit": "₹", "step": 10000},
            {"key": "annual_return", "label": "Expected Annual Return", "type": "number", "default": 12, "min": 1, "max": 30, "unit": "%", "step": 0.5},
            {"key": "years", "label": "Duration", "type": "number", "default": 10, "min": 1, "max": 40, "unit": "years", "step": 1},
        ],
        "formula_steps": [
            {"var": "lumpsum_fv", "expr": "total_amount * (1 + annual_return/100)**years"},
            {"var": "months", "expr": "years * 12"},
            {"var": "monthly_sip", "expr": "total_amount / months"},
            {"var": "r", "expr": "annual_return / 12 / 100"},
            {"var": "sip_fv", "expr": "monthly_sip * (((1+r)**months - 1) / r) * (1+r)"},
            {"var": "difference", "expr": "lumpsum_fv - sip_fv"},
        ],
        "formula": "difference",
        "outputs": [
            {"key": "lumpsum_fv", "label": "Lumpsum Future Value", "format": "currency"},
            {"key": "sip_fv", "label": "SIP Future Value (same total)", "format": "currency"},
            {"key": "difference", "label": "Difference (Lumpsum - SIP)", "format": "currency"},
        ],
        "constants": {},
    },
    {
        "slug": "step-up-sip-planner", "name": "Step-up SIP Planner", "category": "Investments",
        "icon": "📊", "description": "SIP that increases every year — project final value.",
        "is_featured": False, "sort_order": 17,
        "inputs": [
            {"key": "initial_monthly_sip", "label": "Starting Monthly SIP", "type": "number", "default": 10000, "min": 500, "max": 1000000, "unit": "₹", "step": 500},
            {"key": "annual_stepup_pct", "label": "Annual Step-up", "type": "number", "default": 10, "min": 0, "max": 50, "unit": "%", "step": 1},
            {"key": "annual_return", "label": "Expected Annual Return", "type": "number", "default": 12, "min": 1, "max": 30, "unit": "%", "step": 0.5},
            {"key": "years", "label": "Duration", "type": "number", "default": 15, "min": 1, "max": 40, "unit": "years", "step": 1},
        ],
        # Approximation: treat as growing annuity using year-wise lumpsum-equivalent compounding
        "formula_steps": [
            {"var": "r_annual", "expr": "annual_return / 100"},
            {"var": "g", "expr": "annual_stepup_pct / 100"},
            {"var": "yearly_invested_y1", "expr": "initial_monthly_sip * 12"},
            # Future value of a growing annuity (annual compounding approximation)
            {"var": "future_value", "expr": "yearly_invested_y1 * (((1+r_annual)**years - (1+g)**years) / (r_annual - g)) * (1+r_annual)"},
        ],
        "formula": "future_value",
        "outputs": [
            {"key": "future_value", "label": "Estimated Future Value", "format": "currency"},
        ],
        "constants": {},
    },
    {
        "slug": "goal-based-sip", "name": "Goal-based SIP (Reverse Planner)", "category": "Investments",
        "icon": "🎯", "description": "How much SIP do you need monthly to hit a target corpus?",
        "is_featured": False, "sort_order": 18,
        "inputs": [
            {"key": "target_amount", "label": "Target Corpus", "type": "number", "default": 5000000, "min": 50000, "max": 500000000, "unit": "₹", "step": 50000},
            {"key": "annual_return", "label": "Expected Annual Return", "type": "number", "default": 12, "min": 1, "max": 30, "unit": "%", "step": 0.5},
            {"key": "years", "label": "Time to Goal", "type": "number", "default": 10, "min": 1, "max": 40, "unit": "years", "step": 1},
        ],
        "formula_steps": [
            {"var": "months", "expr": "years * 12"},
            {"var": "r", "expr": "annual_return / 12 / 100"},
            {"var": "required_sip", "expr": "target_amount / ((((1+r)**months - 1) / r) * (1+r))"},
        ],
        "formula": "required_sip",
        "outputs": [{"key": "required_sip", "label": "Required Monthly SIP", "format": "currency"}],
        "constants": {},
    },
    {
        "slug": "ppf-maturity", "name": "PPF Maturity Planner", "category": "Investments",
        "icon": "🏦", "description": "Project PPF maturity value (15-year default).",
        "is_featured": False, "sort_order": 19,
        "inputs": [
            {"key": "annual_contribution", "label": "Annual Contribution", "type": "number", "default": 150000, "min": 500, "max": 150000, "unit": "₹", "step": 5000},
            {"key": "interest_rate", "label": "PPF Interest Rate", "type": "number", "default": 7.1, "min": 5, "max": 10, "unit": "%", "step": 0.1},
            {"key": "years", "label": "Duration", "type": "number", "default": 15, "min": 15, "max": 50, "unit": "years", "step": 1},
        ],
        "formula_steps": [
            {"var": "r", "expr": "interest_rate / 100"},
            {"var": "maturity_value", "expr": "annual_contribution * (((1+r)**years - 1) / r) * (1+r)"},
            {"var": "total_invested", "expr": "annual_contribution * years"},
            {"var": "interest_earned", "expr": "maturity_value - total_invested"},
        ],
        "formula": "maturity_value",
        "outputs": [
            {"key": "maturity_value", "label": "Maturity Value", "format": "currency"},
            {"key": "interest_earned", "label": "Interest Earned", "format": "currency"},
        ],
        "constants": {},
    },
    {
        "slug": "fd-rd-maturity", "name": "FD / RD Maturity Planner", "category": "Investments",
        "icon": "🧾", "description": "Maturity value for Fixed or Recurring Deposits.",
        "is_featured": False, "sort_order": 20,
        "inputs": [
            {"key": "deposit_type", "label": "Type (1=FD, 2=RD)", "type": "number", "default": 1, "min": 1, "max": 2, "unit": "", "step": 1},
            {"key": "amount", "label": "Deposit Amount (FD lumpsum / RD monthly)", "type": "number", "default": 200000, "min": 500, "max": 50000000, "unit": "₹", "step": 5000},
            {"key": "annual_rate", "label": "Interest Rate", "type": "number", "default": 7, "min": 3, "max": 10, "unit": "%", "step": 0.1},
            {"key": "years", "label": "Tenure", "type": "number", "default": 5, "min": 1, "max": 10, "unit": "years", "step": 1},
        ],
        "formula_steps": [
            {"var": "r_q", "expr": "annual_rate / 4 / 100"},
            {"var": "n_q", "expr": "years * 4"},
            {"var": "fd_maturity", "expr": "amount * (1+r_q)**n_q"},
            {"var": "months", "expr": "years * 12"},
            {"var": "r_m", "expr": "annual_rate / 12 / 100"},
            {"var": "rd_maturity", "expr": "amount * (((1+r_m)**months - 1) / r_m) * (1+r_m)"},
            {"var": "maturity_value", "expr": "fd_maturity if deposit_type < 1.5 else rd_maturity"},
        ],
        "formula": "maturity_value",
        "outputs": [{"key": "maturity_value", "label": "Maturity Value", "format": "currency"}],
        "constants": {},
    },
    {
        "slug": "wealth-manager", "name": "Wealth Manager (SIP + Goal Planner)", "category": "Investments",
        "icon": "💎", "description": "All-in-one: see your SIP's future value and what's needed for your goal.",
        "is_featured": True, "featured_order": 3, "sort_order": 21,
        "inputs": [
            {"key": "monthly_sip", "label": "Current/Planned Monthly SIP", "type": "number", "default": 15000, "min": 500, "max": 1000000, "unit": "₹", "step": 500},
            {"key": "annual_return", "label": "Expected Annual Return", "type": "number", "default": 12, "min": 1, "max": 30, "unit": "%", "step": 0.5},
            {"key": "years", "label": "Investment Horizon", "type": "number", "default": 15, "min": 1, "max": 40, "unit": "years", "step": 1},
            {"key": "goal_amount", "label": "Your Goal Amount (optional)", "type": "number", "default": 5000000, "min": 0, "max": 500000000, "unit": "₹", "step": 50000},
        ],
        "formula_steps": [
            {"var": "months", "expr": "years * 12"},
            {"var": "r", "expr": "annual_return / 12 / 100"},
            {"var": "future_value", "expr": "monthly_sip * (((1+r)**months - 1) / r) * (1+r)"},
            {"var": "total_invested", "expr": "monthly_sip * months"},
            {"var": "wealth_gained", "expr": "future_value - total_invested"},
            {"var": "goal_gap", "expr": "goal_amount - future_value"},
            {"var": "required_sip_for_goal", "expr": "goal_amount / ((((1+r)**months - 1) / r) * (1+r))"},
        ],
        "formula": "future_value",
        "outputs": [
            {"key": "future_value", "label": "Projected Future Value", "format": "currency"},
            {"key": "wealth_gained", "label": "Wealth Gained", "format": "currency"},
            {"key": "goal_gap", "label": "Gap vs Your Goal", "format": "currency"},
            {"key": "required_sip_for_goal", "label": "SIP Needed to Hit Goal", "format": "currency"},
        ],
        "constants": {},
    },

    # ═══════════════════════════ RETIREMENT (4) ═══════════════════════════
    {
        "slug": "retirement-corpus-needed", "name": "Retirement Corpus Needed", "category": "Retirement",
        "icon": "🌅", "description": "How big a corpus do you need to retire comfortably?",
        "is_featured": True, "featured_order": 4, "sort_order": 22,
        "inputs": [
            {"key": "current_monthly_expense", "label": "Current Monthly Expense", "type": "number", "default": 50000, "min": 5000, "max": 1000000, "unit": "₹", "step": 1000},
            {"key": "years_to_retirement", "label": "Years to Retirement", "type": "number", "default": 25, "min": 1, "max": 45, "unit": "years", "step": 1},
            {"key": "years_in_retirement", "label": "Years in Retirement", "type": "number", "default": 25, "min": 5, "max": 40, "unit": "years", "step": 1},
            {"key": "inflation_rate", "label": "Inflation Rate", "type": "number", "default": 6, "min": 2, "max": 12, "unit": "%", "step": 0.5},
            {"key": "post_retirement_return", "label": "Post-Retirement Return", "type": "number", "default": 7, "min": 2, "max": 15, "unit": "%", "step": 0.5},
        ],
        "formula_steps": [
            {"var": "future_monthly_expense", "expr": "current_monthly_expense * (1 + inflation_rate/100)**years_to_retirement"},
            {"var": "future_annual_expense", "expr": "future_monthly_expense * 12"},
            {"var": "real_return", "expr": "(post_retirement_return - inflation_rate) / 100"},
            {"var": "corpus_needed", "expr": "future_annual_expense * ((1 - (1+real_return)**(-years_in_retirement)) / real_return)"},
        ],
        "formula": "corpus_needed",
        "outputs": [
            {"key": "future_monthly_expense", "label": "Monthly Expense at Retirement", "format": "currency"},
            {"key": "corpus_needed", "label": "Retirement Corpus Needed", "format": "currency"},
        ],
        "constants": {},
    },
    {
        "slug": "nps-maturity", "name": "NPS Maturity & Annuity Estimator", "category": "Retirement",
        "icon": "📜", "description": "Project NPS corpus and estimated monthly pension.",
        "is_featured": False, "sort_order": 23,
        "inputs": [
            {"key": "monthly_contribution", "label": "Monthly NPS Contribution", "type": "number", "default": 5000, "min": 500, "max": 200000, "unit": "₹", "step": 500},
            {"key": "annual_return", "label": "Expected Annual Return", "type": "number", "default": 10, "min": 4, "max": 15, "unit": "%", "step": 0.5},
            {"key": "years_to_retirement", "label": "Years to Retirement", "type": "number", "default": 25, "min": 1, "max": 45, "unit": "years", "step": 1},
            {"key": "annuity_pct", "label": "% Used for Annuity at Retirement", "type": "number", "default": 40, "min": 40, "max": 100, "unit": "%", "step": 5},
            {"key": "annuity_rate", "label": "Annuity Rate", "type": "number", "default": 6, "min": 3, "max": 10, "unit": "%", "step": 0.5},
        ],
        "formula_steps": [
            {"var": "months", "expr": "years_to_retirement * 12"},
            {"var": "r", "expr": "annual_return / 12 / 100"},
            {"var": "corpus", "expr": "monthly_contribution * (((1+r)**months - 1) / r) * (1+r)"},
            {"var": "annuity_corpus", "expr": "corpus * annuity_pct / 100"},
            {"var": "lumpsum_withdrawal", "expr": "corpus - annuity_corpus"},
            {"var": "monthly_pension", "expr": "annuity_corpus * annuity_rate / 100 / 12"},
        ],
        "formula": "corpus",
        "outputs": [
            {"key": "corpus", "label": "Total NPS Corpus at Retirement", "format": "currency"},
            {"key": "lumpsum_withdrawal", "label": "Lumpsum You Can Withdraw", "format": "currency"},
            {"key": "monthly_pension", "label": "Estimated Monthly Pension", "format": "currency"},
        ],
        "constants": {},
    },
    {
        "slug": "epf-maturity", "name": "EPF Maturity Estimator", "category": "Retirement",
        "icon": "🏛️", "description": "Project EPF corpus at retirement.",
        "is_featured": False, "sort_order": 24,
        "inputs": [
            {"key": "basic_monthly_salary", "label": "Basic Monthly Salary", "type": "number", "default": 40000, "min": 5000, "max": 1000000, "unit": "₹", "step": 1000},
            {"key": "current_epf_balance", "label": "Current EPF Balance", "type": "number", "default": 500000, "min": 0, "max": 50000000, "unit": "₹", "step": 10000},
            {"key": "annual_rate", "label": "EPF Interest Rate", "type": "number", "default": 8.25, "min": 6, "max": 10, "unit": "%", "step": 0.05},
            {"key": "years_to_retirement", "label": "Years to Retirement", "type": "number", "default": 20, "min": 1, "max": 40, "unit": "years", "step": 1},
        ],
        "formula_steps": [
            {"var": "monthly_contribution", "expr": "basic_monthly_salary * 0.24"},
            {"var": "months", "expr": "years_to_retirement * 12"},
            {"var": "r", "expr": "annual_rate / 12 / 100"},
            {"var": "future_contributions_value", "expr": "monthly_contribution * (((1+r)**months - 1) / r) * (1+r)"},
            {"var": "existing_balance_growth", "expr": "current_epf_balance * (1+r)**months"},
            {"var": "total_corpus", "expr": "future_contributions_value + existing_balance_growth"},
        ],
        "formula": "total_corpus",
        "outputs": [{"key": "total_corpus", "label": "EPF Corpus at Retirement", "format": "currency"}],
        "constants": {"employee_employer_combined_pct": 0.24},
    },
    {
        "slug": "retirement-drawdown", "name": "Retirement Income Drawdown Planner", "category": "Retirement",
        "icon": "📉", "description": "How long will your retirement corpus last at a given withdrawal rate?",
        "is_featured": False, "sort_order": 25,
        "inputs": [
            {"key": "corpus", "label": "Retirement Corpus", "type": "number", "default": 20000000, "min": 100000, "max": 500000000, "unit": "₹", "step": 100000},
            {"key": "monthly_withdrawal", "label": "Monthly Withdrawal Needed", "type": "number", "default": 150000, "min": 5000, "max": 5000000, "unit": "₹", "step": 5000},
            {"key": "annual_return", "label": "Expected Return During Retirement", "type": "number", "default": 7, "min": 2, "max": 15, "unit": "%", "step": 0.5},
        ],
        "formula_steps": [
            {"var": "r", "expr": "annual_return / 12 / 100"},
            {"var": "monthly_interest", "expr": "corpus * r"},
            {"var": "depletes", "expr": "1 if monthly_withdrawal > monthly_interest else 0"},
            {"var": "months_corpus_lasts", "expr": "(log(monthly_withdrawal / (monthly_withdrawal - corpus*r)) / log(1+r)) if depletes > 0.5 else 999"},
            {"var": "years_corpus_lasts", "expr": "months_corpus_lasts / 12"},
        ],
        "formula": "years_corpus_lasts",
        "outputs": [{"key": "years_corpus_lasts", "label": "Corpus Will Last (Years)", "format": "number"}],
        "constants": {},
    },

    # ═══════════════════════════ TAX (6) ═══════════════════════════
    {
        "slug": "old-vs-new-tax-regime", "name": "Old vs New Tax Regime Comparator", "category": "Tax",
        "icon": "🧾", "description": "Simplified comparison of tax liability under both regimes (FY24-25 slabs).",
        "is_featured": False, "sort_order": 26,
        "inputs": [
            {"key": "annual_income", "label": "Gross Annual Income", "type": "number", "default": 1200000, "min": 250000, "max": 100000000, "unit": "₹", "step": 50000},
            {"key": "deductions_80c_etc", "label": "Total Deductions (80C, HRA, etc - Old Regime)", "type": "number", "default": 200000, "min": 0, "max": 1000000, "unit": "₹", "step": 10000},
        ],
        # Simplified slab approximation (effective-rate style, not exact slab-by-slab, flagged for admin to tune via constants)
        "formula_steps": [
            {"var": "taxable_old", "expr": "max(0, annual_income - deductions_80c_etc - 50000)"},
            {"var": "taxable_new", "expr": "max(0, annual_income - 75000)"},
            {"var": "tax_old", "expr": "max(0, (taxable_old-250000)*0.05) + max(0,(taxable_old-500000)*0.15) + max(0,(taxable_old-1000000)*0.10)"},
            {"var": "tax_new", "expr": "max(0, (taxable_new-300000)*0.05) + max(0,(taxable_new-700000)*0.05) + max(0,(taxable_new-1000000)*0.10) + max(0,(taxable_new-1200000)*0.05)"},
            {"var": "better_regime_saving", "expr": "tax_old - tax_new"},
        ],
        "formula": "better_regime_saving",
        "outputs": [
            {"key": "tax_old", "label": "Estimated Tax — Old Regime", "format": "currency"},
            {"key": "tax_new", "label": "Estimated Tax — New Regime", "format": "currency"},
            {"key": "better_regime_saving", "label": "Saving by Choosing New (if positive)", "format": "currency"},
        ],
        "constants": {},
    },
    {
        "slug": "hra-exemption", "name": "HRA Exemption Planner", "category": "Tax",
        "icon": "🏘️", "description": "Calculate your tax-exempt HRA amount.",
        "is_featured": False, "sort_order": 27,
        "inputs": [
            {"key": "basic_salary_annual", "label": "Annual Basic Salary", "type": "number", "default": 600000, "min": 50000, "max": 10000000, "unit": "₹", "step": 10000},
            {"key": "hra_received_annual", "label": "Annual HRA Received", "type": "number", "default": 240000, "min": 0, "max": 5000000, "unit": "₹", "step": 5000},
            {"key": "rent_paid_annual", "label": "Annual Rent Paid", "type": "number", "default": 300000, "min": 0, "max": 5000000, "unit": "₹", "step": 5000},
            {"key": "is_metro", "label": "Metro City (1=Yes, 0=No)", "type": "number", "default": 1, "min": 0, "max": 1, "unit": "", "step": 1},
        ],
        "formula_steps": [
            {"var": "rent_minus_10pct_basic", "expr": "max(0, rent_paid_annual - 0.1*basic_salary_annual)"},
            {"var": "pct_of_basic", "expr": "basic_salary_annual * (0.5 if is_metro > 0.5 else 0.4)"},
            {"var": "exempt_hra", "expr": "min(hra_received_annual, rent_minus_10pct_basic, pct_of_basic)"},
            {"var": "taxable_hra", "expr": "hra_received_annual - exempt_hra"},
        ],
        "formula": "exempt_hra",
        "outputs": [
            {"key": "exempt_hra", "label": "Tax-Exempt HRA", "format": "currency"},
            {"key": "taxable_hra", "label": "Taxable HRA", "format": "currency"},
        ],
        "constants": {},
    },
    {
        "slug": "section-80c-optimizer", "name": "Section 80C Optimizer", "category": "Tax",
        "icon": "📋", "description": "See how much of your ₹1.5L 80C limit is left to use.",
        "is_featured": False, "sort_order": 28,
        "inputs": [
            {"key": "epf_contribution", "label": "EPF Contribution (Annual)", "type": "number", "default": 50000, "min": 0, "max": 300000, "unit": "₹", "step": 5000},
            {"key": "ppf_contribution", "label": "PPF Contribution", "type": "number", "default": 50000, "min": 0, "max": 150000, "unit": "₹", "step": 5000},
            {"key": "elss_investment", "label": "ELSS Mutual Funds", "type": "number", "default": 0, "min": 0, "max": 300000, "unit": "₹", "step": 5000},
            {"key": "life_insurance_premium", "label": "Life Insurance Premium", "type": "number", "default": 20000, "min": 0, "max": 300000, "unit": "₹", "step": 1000},
            {"key": "tax_slab_pct", "label": "Your Tax Slab", "type": "number", "default": 30, "min": 0, "max": 30, "unit": "%", "step": 5},
        ],
        "formula_steps": [
            {"var": "total_used", "expr": "min(150000, epf_contribution + ppf_contribution + elss_investment + life_insurance_premium)"},
            {"var": "remaining_limit", "expr": "max(0, 150000 - total_used)"},
            {"var": "tax_saved_so_far", "expr": "total_used * tax_slab_pct / 100"},
            {"var": "additional_tax_saving_possible", "expr": "remaining_limit * tax_slab_pct / 100"},
        ],
        "formula": "remaining_limit",
        "outputs": [
            {"key": "total_used", "label": "80C Limit Used", "format": "currency"},
            {"key": "remaining_limit", "label": "Remaining 80C Limit", "format": "currency"},
            {"key": "tax_saved_so_far", "label": "Tax Saved So Far", "format": "currency"},
            {"key": "additional_tax_saving_possible", "label": "Additional Tax Saving Possible", "format": "currency"},
        ],
        "constants": {"section_80c_limit": 150000},
    },
    {
        "slug": "capital-gains-tax", "name": "Capital Gains Tax Planner", "category": "Tax",
        "icon": "📈", "description": "Estimate LTCG/STCG tax on equity or debt investments.",
        "is_featured": False, "sort_order": 29,
        "inputs": [
            {"key": "purchase_value", "label": "Purchase Value", "type": "number", "default": 500000, "min": 1000, "max": 100000000, "unit": "₹", "step": 5000},
            {"key": "sale_value", "label": "Sale Value", "type": "number", "default": 800000, "min": 1000, "max": 100000000, "unit": "₹", "step": 5000},
            {"key": "holding_months", "label": "Holding Period", "type": "number", "default": 18, "min": 1, "max": 600, "unit": "months", "step": 1},
            {"key": "asset_type", "label": "Type (1=Equity, 2=Debt)", "type": "number", "default": 1, "min": 1, "max": 2, "unit": "", "step": 1},
        ],
        "formula_steps": [
            {"var": "gain", "expr": "sale_value - purchase_value"},
            {"var": "is_long_term", "expr": "1 if (holding_months >= 12 and asset_type < 1.5) or (holding_months >= 36 and asset_type >= 1.5) else 0"},
            {"var": "ltcg_equity_exempt", "expr": "min(gain, 125000) if (is_long_term > 0.5 and asset_type < 1.5) else 0"},
            {"var": "taxable_gain", "expr": "max(0, gain - ltcg_equity_exempt)"},
            {"var": "tax_rate_pct", "expr": "12.5 if (is_long_term > 0.5 and asset_type < 1.5) else (20 if asset_type < 1.5 else 20)"},
            {"var": "tax_payable", "expr": "taxable_gain * tax_rate_pct / 100"},
        ],
        "formula": "tax_payable",
        "outputs": [
            {"key": "gain", "label": "Total Gain", "format": "currency"},
            {"key": "tax_payable", "label": "Estimated Tax Payable", "format": "currency"},
        ],
        "constants": {},
    },
    {
        "slug": "advance-tax-estimator", "name": "Advance Tax Estimator", "category": "Tax",
        "icon": "📅", "description": "Estimate quarterly advance tax installments.",
        "is_featured": False, "sort_order": 30,
        "inputs": [
            {"key": "estimated_annual_tax", "label": "Estimated Total Annual Tax", "type": "number", "default": 150000, "min": 0, "max": 10000000, "unit": "₹", "step": 5000},
            {"key": "tds_already_deducted", "label": "TDS Already Deducted", "type": "number", "default": 50000, "min": 0, "max": 10000000, "unit": "₹", "step": 5000},
        ],
        "formula_steps": [
            {"var": "remaining_tax", "expr": "max(0, estimated_annual_tax - tds_already_deducted)"},
            {"var": "q1_jun15", "expr": "remaining_tax * 0.15"},
            {"var": "q2_sep15", "expr": "remaining_tax * 0.30"},
            {"var": "q3_dec15", "expr": "remaining_tax * 0.30"},
            {"var": "q4_mar15", "expr": "remaining_tax * 0.25"},
        ],
        "formula": "remaining_tax",
        "outputs": [
            {"key": "remaining_tax", "label": "Total Advance Tax Payable", "format": "currency"},
            {"key": "q1_jun15", "label": "By 15 Jun (15%)", "format": "currency"},
            {"key": "q2_sep15", "label": "By 15 Sep (cumulative 45%)", "format": "currency"},
            {"key": "q3_dec15", "label": "By 15 Dec (cumulative 75%)", "format": "currency"},
            {"key": "q4_mar15", "label": "By 15 Mar (cumulative 100%)", "format": "currency"},
        ],
        "constants": {},
    },
    {
        "slug": "tds-on-fd", "name": "TDS on FD Interest Planner", "category": "Tax",
        "icon": "🏦", "description": "Estimate TDS deducted on your FD interest income.",
        "is_featured": False, "sort_order": 31,
        "inputs": [
            {"key": "annual_fd_interest", "label": "Total Annual FD Interest (all banks)", "type": "number", "default": 60000, "min": 0, "max": 10000000, "unit": "₹", "step": 1000},
            {"key": "has_pan", "label": "PAN Submitted to Bank (1=Yes, 0=No)", "type": "number", "default": 1, "min": 0, "max": 1, "unit": "", "step": 1},
        ],
        "formula_steps": [
            {"var": "tds_threshold", "expr": "40000"},
            {"var": "taxable_interest_for_tds", "expr": "max(0, annual_fd_interest - tds_threshold)"},
            {"var": "tds_rate_pct", "expr": "10 if has_pan > 0.5 else 20"},
            {"var": "tds_deducted", "expr": "taxable_interest_for_tds * tds_rate_pct / 100"},
        ],
        "formula": "tds_deducted",
        "outputs": [{"key": "tds_deducted", "label": "Estimated TDS Deducted", "format": "currency"}],
        "constants": {},
    },

    # ═══════════════════════════ BUDGETING / EXPENSE (6) — incl. 1 featured ═══════════════════════════
    {
        "slug": "monthly-budget-planner", "name": "Monthly Expense Planner (50-30-20)", "category": "Budgeting",
        "icon": "🧮", "description": "Split your income into Needs / Wants / Savings.",
        "is_featured": True, "featured_order": 5, "sort_order": 32,
        "inputs": [
            {"key": "monthly_income", "label": "Monthly Take-Home Income", "type": "number", "default": 80000, "min": 5000, "max": 5000000, "unit": "₹", "step": 1000},
        ],
        "formula_steps": [
            {"var": "needs_budget", "expr": "monthly_income * 0.5"},
            {"var": "wants_budget", "expr": "monthly_income * 0.3"},
            {"var": "savings_budget", "expr": "monthly_income * 0.2"},
        ],
        "formula": "savings_budget",
        "outputs": [
            {"key": "needs_budget", "label": "Needs (50%)", "format": "currency"},
            {"key": "wants_budget", "label": "Wants (30%)", "format": "currency"},
            {"key": "savings_budget", "label": "Savings (20%)", "format": "currency"},
        ],
        "constants": {"needs_pct": 0.5, "wants_pct": 0.3, "savings_pct": 0.2},
    },
    {
        "slug": "emergency-fund-planner", "name": "Emergency Fund Planner", "category": "Budgeting",
        "icon": "🆘", "description": "How big should your emergency fund be?",
        "is_featured": False, "featured_order": 0, "sort_order": 33,
        "inputs": [
            {"key": "monthly_expenses", "label": "Total Monthly Expenses", "type": "number", "default": 50000, "min": 5000, "max": 1000000, "unit": "₹", "step": 1000},
            {"key": "job_stability", "label": "Job Stability (1=Very Stable, 3=Unstable/Freelance)", "type": "number", "default": 2, "min": 1, "max": 3, "unit": "", "step": 1},
            {"key": "current_emergency_fund", "label": "Current Emergency Fund", "type": "number", "default": 100000, "min": 0, "max": 10000000, "unit": "₹", "step": 5000},
        ],
        "formula_steps": [
            {"var": "months_recommended", "expr": "3 + (job_stability-1)*1.5"},
            {"var": "target_fund", "expr": "monthly_expenses * months_recommended"},
            {"var": "gap", "expr": "target_fund - current_emergency_fund"},
        ],
        "formula": "gap",
        "outputs": [
            {"key": "months_recommended", "label": "Recommended Months of Cover", "format": "number"},
            {"key": "target_fund", "label": "Target Emergency Fund", "format": "currency"},
            {"key": "gap", "label": "Amount Still Needed", "format": "currency"},
        ],
        "constants": {},
    },
    {
        "slug": "salary-inhand-calculator", "name": "Salary Breakup / In-hand Planner", "category": "Budgeting",
        "icon": "💼", "description": "Estimate your monthly in-hand salary from CTC.",
        "is_featured": False, "sort_order": 34,
        "inputs": [
            {"key": "annual_ctc", "label": "Annual CTC", "type": "number", "default": 1200000, "min": 200000, "max": 100000000, "unit": "₹", "step": 50000},
            {"key": "employer_pf_pct", "label": "Employer PF Contribution", "type": "number", "default": 12, "min": 0, "max": 12, "unit": "%", "step": 1},
        ],
        "formula_steps": [
            {"var": "basic_annual", "expr": "annual_ctc * 0.4"},
            {"var": "employer_pf_annual", "expr": "basic_annual * employer_pf_pct / 100"},
            {"var": "employee_pf_annual", "expr": "basic_annual * 0.12"},
            {"var": "gross_annual", "expr": "annual_ctc - employer_pf_annual"},
            {"var": "approx_tax_annual", "expr": "max(0,(gross_annual-700000))*0.1"},
            {"var": "net_annual", "expr": "gross_annual - employee_pf_annual - approx_tax_annual"},
            {"var": "monthly_inhand", "expr": "net_annual / 12"},
        ],
        "formula": "monthly_inhand",
        "outputs": [{"key": "monthly_inhand", "label": "Estimated Monthly In-Hand", "format": "currency"}],
        "constants": {},
    },
    {
        "slug": "inflation-impact-expenses", "name": "Inflation Impact on Expenses", "category": "Budgeting",
        "icon": "📉", "description": "See how today's expenses grow with inflation.",
        "is_featured": False, "sort_order": 35,
        "inputs": [
            {"key": "current_monthly_expense", "label": "Current Monthly Expense", "type": "number", "default": 50000, "min": 5000, "max": 1000000, "unit": "₹", "step": 1000},
            {"key": "inflation_rate", "label": "Inflation Rate", "type": "number", "default": 6, "min": 2, "max": 15, "unit": "%", "step": 0.5},
            {"key": "years", "label": "Years Ahead", "type": "number", "default": 10, "min": 1, "max": 40, "unit": "years", "step": 1},
        ],
        "formula_steps": [
            {"var": "future_expense", "expr": "current_monthly_expense * (1+inflation_rate/100)**years"},
        ],
        "formula": "future_expense",
        "outputs": [{"key": "future_expense", "label": "Future Monthly Expense", "format": "currency"}],
        "constants": {},
    },
    {
        "slug": "debt-to-income-ratio", "name": "Debt-to-Income Ratio Planner", "category": "Budgeting",
        "icon": "⚖️", "description": "Check how much of your income goes to debt.",
        "is_featured": False, "sort_order": 36,
        "inputs": [
            {"key": "monthly_income", "label": "Monthly Income", "type": "number", "default": 80000, "min": 5000, "max": 5000000, "unit": "₹", "step": 1000},
            {"key": "total_monthly_emi", "label": "Total Monthly EMI/Debt Payments", "type": "number", "default": 25000, "min": 0, "max": 5000000, "unit": "₹", "step": 1000},
        ],
        "formula_steps": [
            {"var": "dti_ratio", "expr": "(total_monthly_emi / monthly_income) * 100"},
        ],
        "formula": "dti_ratio",
        "outputs": [{"key": "dti_ratio", "label": "Debt-to-Income Ratio", "format": "percent"}],
        "constants": {"healthy_threshold_pct": 40},
    },
    {
        "slug": "subscription-spend-audit", "name": "Subscription / Recurring Spend Audit", "category": "Budgeting",
        "icon": "🔁", "description": "See the real annual cost of your monthly subscriptions.",
        "is_featured": False, "sort_order": 37,
        "inputs": [
            {"key": "total_monthly_subscriptions", "label": "Total Monthly Subscription Spend", "type": "number", "default": 2000, "min": 0, "max": 100000, "unit": "₹", "step": 100},
        ],
        "formula_steps": [
            {"var": "annual_cost", "expr": "total_monthly_subscriptions * 12"},
            {"var": "ten_year_cost_invested", "expr": "total_monthly_subscriptions * (((1+0.01)**120 - 1) / 0.01) * 1.01"},
        ],
        "formula": "annual_cost",
        "outputs": [
            {"key": "annual_cost", "label": "Annual Subscription Cost", "format": "currency"},
            {"key": "ten_year_cost_invested", "label": "If Invested Instead (10yr @ 12%)", "format": "currency"},
        ],
        "constants": {},
    },

    # ═══════════════════════════ LIFE GOALS (8) ═══════════════════════════
    {
        "slug": "child-education-corpus", "name": "Child Education Corpus Planner", "category": "Life Goals",
        "icon": "🎓", "description": "Plan for your child's future education costs.",
        "is_featured": False, "sort_order": 38,
        "inputs": [
            {"key": "current_education_cost", "label": "Current Cost of Target Course", "type": "number", "default": 2000000, "min": 100000, "max": 50000000, "unit": "₹", "step": 50000},
            {"key": "years_to_goal", "label": "Years Until Needed", "type": "number", "default": 15, "min": 1, "max": 25, "unit": "years", "step": 1},
            {"key": "education_inflation", "label": "Education Inflation Rate", "type": "number", "default": 10, "min": 4, "max": 15, "unit": "%", "step": 0.5},
            {"key": "expected_return", "label": "Expected Investment Return", "type": "number", "default": 12, "min": 1, "max": 20, "unit": "%", "step": 0.5},
        ],
        "formula_steps": [
            {"var": "future_cost", "expr": "current_education_cost * (1+education_inflation/100)**years_to_goal"},
            {"var": "months", "expr": "years_to_goal * 12"},
            {"var": "r", "expr": "expected_return / 12 / 100"},
            {"var": "required_sip", "expr": "future_cost / ((((1+r)**months - 1) / r) * (1+r))"},
        ],
        "formula": "future_cost",
        "outputs": [
            {"key": "future_cost", "label": "Future Cost of Education", "format": "currency"},
            {"key": "required_sip", "label": "Monthly SIP Needed", "format": "currency"},
        ],
        "constants": {},
    },
    {
        "slug": "wedding-budget-planner", "name": "Wedding Budget Planner", "category": "Life Goals",
        "icon": "💍", "description": "Break down a wedding budget by category.",
        "is_featured": False, "sort_order": 39,
        "inputs": [
            {"key": "total_budget", "label": "Total Wedding Budget", "type": "number", "default": 1500000, "min": 100000, "max": 50000000, "unit": "₹", "step": 50000},
        ],
        "formula_steps": [
            {"var": "venue_catering", "expr": "total_budget * 0.40"},
            {"var": "decor", "expr": "total_budget * 0.15"},
            {"var": "attire_jewellery", "expr": "total_budget * 0.20"},
            {"var": "photography", "expr": "total_budget * 0.08"},
            {"var": "misc_contingency", "expr": "total_budget * 0.17"},
        ],
        "formula": "venue_catering",
        "outputs": [
            {"key": "venue_catering", "label": "Venue & Catering (40%)", "format": "currency"},
            {"key": "decor", "label": "Decor (15%)", "format": "currency"},
            {"key": "attire_jewellery", "label": "Attire & Jewellery (20%)", "format": "currency"},
            {"key": "photography", "label": "Photography (8%)", "format": "currency"},
            {"key": "misc_contingency", "label": "Misc & Contingency (17%)", "format": "currency"},
        ],
        "constants": {},
    },
    {
        "slug": "home-down-payment-planner", "name": "Home Down Payment Planner", "category": "Life Goals",
        "icon": "🏡", "description": "SIP needed to save your home down payment.",
        "is_featured": False, "sort_order": 40,
        "inputs": [
            {"key": "home_value", "label": "Expected Home Value", "type": "number", "default": 8000000, "min": 500000, "max": 200000000, "unit": "₹", "step": 100000},
            {"key": "down_payment_pct", "label": "Down Payment %", "type": "number", "default": 20, "min": 10, "max": 50, "unit": "%", "step": 5},
            {"key": "years_to_goal", "label": "Years to Save", "type": "number", "default": 5, "min": 1, "max": 20, "unit": "years", "step": 1},
            {"key": "expected_return", "label": "Expected Return", "type": "number", "default": 10, "min": 1, "max": 20, "unit": "%", "step": 0.5},
        ],
        "formula_steps": [
            {"var": "down_payment_needed", "expr": "home_value * down_payment_pct / 100"},
            {"var": "months", "expr": "years_to_goal * 12"},
            {"var": "r", "expr": "expected_return / 12 / 100"},
            {"var": "required_sip", "expr": "down_payment_needed / ((((1+r)**months - 1) / r) * (1+r))"},
        ],
        "formula": "required_sip",
        "outputs": [
            {"key": "down_payment_needed", "label": "Down Payment Needed", "format": "currency"},
            {"key": "required_sip", "label": "Monthly SIP Required", "format": "currency"},
        ],
        "constants": {},
    },
    {
        "slug": "car-purchase-affordability", "name": "Car Purchase Affordability", "category": "Life Goals",
        "icon": "🚘", "description": "How expensive a car can you comfortably afford?",
        "is_featured": True, "featured_order": 6, "sort_order": 41,
        "inputs": [
            {"key": "annual_income", "label": "Annual Income", "type": "number", "default": 1200000, "min": 200000, "max": 50000000, "unit": "₹", "step": 50000},
            {"key": "existing_emi", "label": "Existing Monthly EMIs", "type": "number", "default": 0, "min": 0, "max": 1000000, "unit": "₹", "step": 1000},
        ],
        "formula_steps": [
            {"var": "max_car_value", "expr": "annual_income * 0.5 - existing_emi*12"},
        ],
        "formula": "max_car_value",
        "outputs": [{"key": "max_car_value", "label": "Recommended Max Car Value", "format": "currency"}],
        "constants": {"income_multiple": 0.5},
    },
    {
        "slug": "vacation-fund-planner", "name": "Vacation Fund Planner", "category": "Life Goals",
        "icon": "✈️", "description": "Monthly saving needed for your next big trip.",
        "is_featured": False, "sort_order": 42,
        "inputs": [
            {"key": "trip_cost", "label": "Estimated Trip Cost", "type": "number", "default": 200000, "min": 5000, "max": 5000000, "unit": "₹", "step": 5000},
            {"key": "months_to_trip", "label": "Months Until Trip", "type": "number", "default": 12, "min": 1, "max": 60, "unit": "months", "step": 1},
        ],
        "formula_steps": [
            {"var": "monthly_saving_needed", "expr": "trip_cost / months_to_trip"},
        ],
        "formula": "monthly_saving_needed",
        "outputs": [{"key": "monthly_saving_needed", "label": "Monthly Saving Needed", "format": "currency"}],
        "constants": {},
    },
    {
        "slug": "home-renovation-cost", "name": "Home Renovation Cost Estimator", "category": "Life Goals",
        "icon": "🔨", "description": "Estimate renovation cost by area and finish level.",
        "is_featured": False, "sort_order": 43,
        "inputs": [
            {"key": "area_sqft", "label": "Area to Renovate", "type": "number", "default": 1000, "min": 100, "max": 10000, "unit": "sq.ft", "step": 50},
            {"key": "finish_level", "label": "Finish Level (1=Basic, 2=Mid, 3=Premium)", "type": "number", "default": 2, "min": 1, "max": 3, "unit": "", "step": 1},
        ],
        "formula_steps": [
            {"var": "rate_per_sqft", "expr": "800 + (finish_level-1)*900"},
            {"var": "estimated_cost", "expr": "area_sqft * rate_per_sqft"},
        ],
        "formula": "estimated_cost",
        "outputs": [{"key": "estimated_cost", "label": "Estimated Renovation Cost", "format": "currency"}],
        "constants": {},
    },
    {
        "slug": "rent-vs-buy", "name": "Rent vs Buy Comparator", "category": "Life Goals",
        "icon": "🏠", "description": "Compare the financial outcome of renting vs buying over time.",
        "is_featured": False, "sort_order": 44,
        "inputs": [
            {"key": "home_price", "label": "Home Purchase Price", "type": "number", "default": 8000000, "min": 500000, "max": 200000000, "unit": "₹", "step": 100000},
            {"key": "monthly_rent", "label": "Equivalent Monthly Rent", "type": "number", "default": 30000, "min": 1000, "max": 1000000, "unit": "₹", "step": 1000},
            {"key": "down_payment_pct", "label": "Down Payment %", "type": "number", "default": 20, "min": 10, "max": 100, "unit": "%", "step": 5},
            {"key": "loan_rate", "label": "Home Loan Rate", "type": "number", "default": 8.5, "min": 5, "max": 15, "unit": "%", "step": 0.1},
            {"key": "years", "label": "Years to Compare", "type": "number", "default": 10, "min": 1, "max": 30, "unit": "years", "step": 1},
        ],
        "formula_steps": [
            {"var": "down_payment", "expr": "home_price * down_payment_pct / 100"},
            {"var": "loan_amount", "expr": "home_price - down_payment"},
            {"var": "r", "expr": "loan_rate / 12 / 100"},
            {"var": "tenure_months", "expr": "years * 12"},
            {"var": "emi", "expr": "(loan_amount * r * (1+r)**tenure_months) / ((1+r)**tenure_months - 1)"},
            {"var": "total_buy_cost", "expr": "down_payment + emi*tenure_months"},
            {"var": "total_rent_cost", "expr": "monthly_rent * tenure_months * 1.3"},
            {"var": "buy_minus_rent", "expr": "total_buy_cost - total_rent_cost"},
        ],
        "formula": "buy_minus_rent",
        "outputs": [
            {"key": "total_buy_cost", "label": "Total Cost of Buying", "format": "currency"},
            {"key": "total_rent_cost", "label": "Total Cost of Renting (est. w/ rent escalation)", "format": "currency"},
            {"key": "buy_minus_rent", "label": "Difference (Buy - Rent)", "format": "currency"},
        ],
        "constants": {"rent_escalation_factor": 1.3},
    },
    {
        "slug": "sabbatical-fund-planner", "name": "Sabbatical / Career Break Fund Planner", "category": "Life Goals",
        "icon": "🌴", "description": "How much you need saved for a planned career break.",
        "is_featured": False, "sort_order": 45,
        "inputs": [
            {"key": "monthly_expenses", "label": "Monthly Expenses During Break", "type": "number", "default": 50000, "min": 5000, "max": 1000000, "unit": "₹", "step": 1000},
            {"key": "break_months", "label": "Length of Break", "type": "number", "default": 6, "min": 1, "max": 36, "unit": "months", "step": 1},
            {"key": "buffer_pct", "label": "Safety Buffer", "type": "number", "default": 20, "min": 0, "max": 50, "unit": "%", "step": 5},
        ],
        "formula_steps": [
            {"var": "base_fund", "expr": "monthly_expenses * break_months"},
            {"var": "total_fund_needed", "expr": "base_fund * (1 + buffer_pct/100)"},
        ],
        "formula": "total_fund_needed",
        "outputs": [{"key": "total_fund_needed", "label": "Total Fund Needed", "format": "currency"}],
        "constants": {},
    },

    # ═══════════════════════════ NET WORTH & MISC (5) ═══════════════════════════
    {
        "slug": "net-worth-tracker", "name": "Net Worth Planner", "category": "Net Worth",
        "icon": "📒", "description": "Calculate your current net worth.",
        "is_featured": False, "sort_order": 46,
        "inputs": [
            {"key": "total_assets", "label": "Total Assets (savings, investments, property)", "type": "number", "default": 5000000, "min": 0, "max": 1000000000, "unit": "₹", "step": 50000},
            {"key": "total_liabilities", "label": "Total Liabilities (loans, debts)", "type": "number", "default": 2000000, "min": 0, "max": 1000000000, "unit": "₹", "step": 50000},
        ],
        "formula_steps": [
            {"var": "net_worth", "expr": "total_assets - total_liabilities"},
        ],
        "formula": "net_worth",
        "outputs": [{"key": "net_worth", "label": "Your Net Worth", "format": "currency"}],
        "constants": {},
    },
    {
        "slug": "cagr-calculator", "name": "CAGR Planner", "category": "Net Worth",
        "icon": "📐", "description": "Calculate Compound Annual Growth Rate between two values.",
        "is_featured": False, "sort_order": 47,
        "inputs": [
            {"key": "initial_value", "label": "Initial Value", "type": "number", "default": 100000, "min": 100, "max": 100000000, "unit": "₹", "step": 1000},
            {"key": "final_value", "label": "Final Value", "type": "number", "default": 250000, "min": 100, "max": 1000000000, "unit": "₹", "step": 1000},
            {"key": "years", "label": "Number of Years", "type": "number", "default": 5, "min": 1, "max": 50, "unit": "years", "step": 1},
        ],
        "formula_steps": [
            {"var": "cagr_pct", "expr": "((final_value / initial_value)**(1/years) - 1) * 100"},
        ],
        "formula": "cagr_pct",
        "outputs": [{"key": "cagr_pct", "label": "CAGR", "format": "percent"}],
        "constants": {},
    },
    {
        "slug": "inflation-adjusted-fv", "name": "Inflation-Adjusted Future Value", "category": "Net Worth",
        "icon": "🔮", "description": "What today's money will really be worth in the future.",
        "is_featured": False, "sort_order": 48,
        "inputs": [
            {"key": "current_amount", "label": "Current Amount", "type": "number", "default": 1000000, "min": 1000, "max": 1000000000, "unit": "₹", "step": 10000},
            {"key": "inflation_rate", "label": "Inflation Rate", "type": "number", "default": 6, "min": 1, "max": 15, "unit": "%", "step": 0.5},
            {"key": "years", "label": "Years Ahead", "type": "number", "default": 10, "min": 1, "max": 50, "unit": "years", "step": 1},
        ],
        "formula_steps": [
            {"var": "real_value_future", "expr": "current_amount / (1+inflation_rate/100)**years"},
        ],
        "formula": "real_value_future",
        "outputs": [{"key": "real_value_future", "label": "Real Value in Future (today's purchasing power)", "format": "currency"}],
        "constants": {},
    },
    {
        "slug": "compound-interest", "name": "Compound Interest Planner", "category": "Net Worth",
        "icon": "🧮", "description": "Classic compound interest calculator with flexible compounding frequency.",
        "is_featured": False, "sort_order": 49,
        "inputs": [
            {"key": "principal", "label": "Principal Amount", "type": "number", "default": 100000, "min": 1000, "max": 100000000, "unit": "₹", "step": 5000},
            {"key": "annual_rate", "label": "Annual Interest Rate", "type": "number", "default": 8, "min": 1, "max": 20, "unit": "%", "step": 0.25},
            {"key": "years", "label": "Duration", "type": "number", "default": 10, "min": 1, "max": 50, "unit": "years", "step": 1},
            {"key": "compounds_per_year", "label": "Compounding Frequency per Year", "type": "number", "default": 4, "min": 1, "max": 365, "unit": "times", "step": 1},
        ],
        "formula_steps": [
            {"var": "future_value", "expr": "principal * (1 + (annual_rate/100)/compounds_per_year)**(compounds_per_year*years)"},
            {"var": "interest_earned", "expr": "future_value - principal"},
        ],
        "formula": "future_value",
        "outputs": [
            {"key": "future_value", "label": "Future Value", "format": "currency"},
            {"key": "interest_earned", "label": "Interest Earned", "format": "currency"},
        ],
        "constants": {},
    },
    {
        "slug": "credit-score-improvement", "name": "Credit Score Improvement Estimator", "category": "Net Worth",
        "icon": "📶", "description": "Rough estimate of credit score impact from key actions.",
        "is_featured": False, "sort_order": 50,
        "inputs": [
            {"key": "current_score", "label": "Current Credit Score", "type": "number", "default": 650, "min": 300, "max": 900, "unit": "", "step": 10},
            {"key": "credit_utilization_pct", "label": "Current Credit Utilization", "type": "number", "default": 60, "min": 0, "max": 100, "unit": "%", "step": 5},
            {"key": "missed_payments_last_year", "label": "Missed Payments (Last 12 months)", "type": "number", "default": 1, "min": 0, "max": 12, "unit": "", "step": 1},
        ],
        "formula_steps": [
            {"var": "utilization_penalty", "expr": "max(0, credit_utilization_pct - 30) * 1.5"},
            {"var": "missed_payment_penalty", "expr": "missed_payments_last_year * 40"},
            {"var": "potential_score_if_fixed", "expr": "min(900, current_score + utilization_penalty*0.5 + missed_payment_penalty*0.5)"},
            {"var": "potential_improvement", "expr": "potential_score_if_fixed - current_score"},
        ],
        "formula": "potential_improvement",
        "outputs": [
            {"key": "potential_improvement", "label": "Potential Score Improvement", "format": "number"},
            {"key": "potential_score_if_fixed", "label": "Estimated Score if Fixed", "format": "number"},
        ],
        "constants": {},
    },
]


def seed(db_session):
    """Insert or update all 50 calculators. Call from main.py startup or a one-off script."""
    from models import Calculator
    for calc_def in CALCULATORS:
        existing = db_session.query(Calculator).filter_by(slug=calc_def["slug"]).first()
        if existing:
            for k, v in calc_def.items():
                setattr(existing, k, v)
        else:
            db_session.add(Calculator(**calc_def))
    db_session.commit()
    print(f"Seeded {len(CALCULATORS)} calculators.")


if __name__ == "__main__":
    from database import SessionLocal, init_db
    init_db()  # creates tables if they don't exist yet — main.py normally does this on app startup,
               # but this script can run standalone (e.g. as a one-off Render shell command)
    db = SessionLocal()
    seed(db)
    db.close()

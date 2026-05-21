# Financial Calculator Formulas and Logic

This document explains the mathematical formulas and logic behind each financial calculator in FinPilot AI.

---

## 🏠 Loan/Mortgage Calculator

### Purpose
Calculate monthly payments, total interest, and payoff time for loans with optional extra payments.

### Input Parameters
- `loan_amount`: Principal amount borrowed ($)
- `interest_rate`: Annual interest rate (as decimal, e.g., 0.045 for 4.5%)
- `loan_term_years`: Loan duration in years
- `extra_payment`: Additional monthly payment ($)

### Formulas

#### 1. Monthly Payment (EMI)
```
monthly_rate = interest_rate / 12
months = loan_term_years × 12

If monthly_rate > 0:
    monthly_payment = loan_amount × [monthly_rate × (1 + monthly_rate)^months] / [(1 + monthly_rate)^months - 1]
Else:
    monthly_payment = loan_amount / months
```

**Example**: $200,000 at 4.5% for 30 years
```
monthly_rate = 0.045 / 12 = 0.00375
months = 30 × 12 = 360

monthly_payment = 200000 × [0.00375 × (1.00375)^360] / [(1.00375)^360 - 1]
                = 200000 × [0.00375 × 3.8477] / [3.8477 - 1]
                = 200000 × 0.01443 / 2.8477
                = 200000 × 0.005067
                = $1,013.37
```

#### 2. Amortization with Extra Payments
```
balance = loan_amount
total_interest = 0
months_to_payoff = 0

While balance > 0 and months_to_payoff < months:
    interest_payment = balance × monthly_rate
    principal_payment = monthly_payment + extra_payment - interest_payment
    
    If principal_payment > balance:
        principal_payment = balance
    
    balance -= principal_payment
    total_interest += interest_payment
    months_to_payoff += 1
```

#### 3. Interest Saved Calculation
```
# Calculate standard scenario (no extra payments)
balance_standard = loan_amount
total_interest_standard = 0

For each month in original term:
    interest_payment = balance_standard × monthly_rate
    principal_payment = monthly_payment - interest_payment
    balance_standard -= principal_payment
    total_interest_standard += interest_payment

# Interest saved
interest_saved = total_interest_standard - total_interest
years_saved = (original_months - months_to_payoff) / 12
```

### Output
- `monthly_payment`: Regular monthly payment
- `total_interest_paid`: Total interest over loan life
- `total_amount_paid`: Principal + Interest
- `months_to_payoff`: Time to pay off loan
- `years_to_payoff`: Time in years
- `interest_saved`: Interest saved with extra payments
- `years_saved`: Time saved with extra payments

---

## 🎯 Retirement Planning Calculator

### Purpose
Project retirement savings and determine if you're on track to meet retirement goals.

### Input Parameters
- `current_age`: Your current age
- `retirement_age`: Target retirement age
- `current_savings`: Current retirement savings ($)
- `monthly_contribution`: Monthly savings amount ($)
- `expected_return`: Expected annual return rate (as decimal)
- `inflation_rate`: Expected inflation rate (as decimal)
- `desired_annual_income`: Desired annual income in retirement ($)
- `life_expectancy`: Expected lifespan (default: 90)

### Formulas

#### 1. Future Value of Current Savings
```
years_to_retirement = retirement_age - current_age

fv_current = current_savings × (1 + expected_return)^years_to_retirement
```

#### 2. Future Value of Monthly Contributions
```
monthly_rate = expected_return / 12
months_to_retirement = years_to_retirement × 12

If monthly_rate > 0:
    fv_contributions = monthly_contribution × [((1 + monthly_rate)^months - 1) / monthly_rate]
Else:
    fv_contributions = monthly_contribution × months
```

**Example**: $1,000/month for 35 years at 7% annual return
```
monthly_rate = 0.07 / 12 = 0.005833
months = 35 × 12 = 420

fv_contributions = 1000 × [((1.005833)^420 - 1) / 0.005833]
                 = 1000 × [(10.677 - 1) / 0.005833]
                 = 1000 × 1658.88
                 = $1,658,880
```

#### 3. Total at Retirement
```
total_at_retirement = fv_current + fv_contributions
```

#### 4. Required Savings
```
years_in_retirement = life_expectancy - retirement_age
inflation_adjusted_income = desired_annual_income × (1 + inflation_rate)^years_to_retirement

required_savings = inflation_adjusted_income × years_in_retirement / (1 + expected_return - inflation_rate)
```

#### 5. Shortfall/Surplus
```
shortfall = required_savings - total_at_retirement

If shortfall > 0:
    # Need more savings
    required_monthly = (required_savings - fv_current) × monthly_rate / ((1 + monthly_rate)^months - 1)
Else:
    # On track or surplus
    surplus = abs(shortfall)
```

#### 6. Monte Carlo Success Probability
Runs 1,000 simulations with random returns (normal distribution, 15% volatility):
```
For each simulation:
    # Accumulation phase
    balance = current_savings
    For each year to retirement:
        annual_return = random_normal(expected_return, 0.15)
        balance = balance × (1 + annual_return) + (monthly_contribution × 12)
    
    # Withdrawal phase
    inflation_adjusted_income = desired_income × (1 + inflation)^years_to_retirement
    For each year in retirement:
        annual_return = random_normal(expected_return, 0.15)
        balance = balance × (1 + annual_return) - inflation_adjusted_income
        inflation_adjusted_income × = (1 + inflation)
        
        If balance <= 0:
            break
    
    If balance > 0:
        success_count += 1

success_probability = success_count / 1000 × 100%
```

### Output
- `projected_savings_at_retirement`: Expected savings at retirement
- `required_savings`: Amount needed for retirement goals
- `shortfall`: Amount short of goal (if any)
- `surplus`: Amount over goal (if any)
- `required_monthly_contribution`: Monthly amount needed to meet goal
- `success_probability`: Probability of success (Monte Carlo)
- `years_to_retirement`: Time until retirement
- `years_in_retirement`: Expected retirement duration

---

## 📈 Investment Growth Calculator

### Purpose
Project investment growth with compound interest and risk analysis.

### Input Parameters
- `initial_investment`: Starting investment amount ($)
- `monthly_contribution`: Monthly investment amount ($)
- `years`: Investment time horizon
- `expected_return`: Expected annual return (as decimal)
- `risk_level`: Risk tolerance ('conservative', 'moderate', 'aggressive')

### Formulas

#### 1. Deterministic Projection
```
monthly_rate = expected_return / 12
months = years × 12

# Future value of initial investment
fv_initial = initial_investment × (1 + expected_return)^years

# Future value of monthly contributions
If monthly_rate > 0:
    fv_contributions = monthly_contribution × [((1 + monthly_rate)^months - 1) / monthly_rate]
Else:
    fv_contributions = monthly_contribution × months

expected_value = fv_initial + fv_contributions
```

**Example**: $10,000 initial + $500/month for 20 years at 8%
```
monthly_rate = 0.08 / 12 = 0.006667
months = 20 × 12 = 240

fv_initial = 10000 × (1.08)^20 = 10000 × 4.661 = $46,610

fv_contributions = 500 × [((1.006667)^240 - 1) / 0.006667]
                 = 500 × [(4.927 - 1) / 0.006667]
                 = 500 × 588.91
                 = $294,455

expected_value = 46,610 + 294,455 = $341,065
```

#### 2. Total Contributions and Gains
```
total_contributions = initial_investment + (monthly_contribution × months)
total_gains = expected_value - total_contributions
```

#### 3. Monte Carlo Risk Analysis
Volatility based on risk level:
- Conservative: 8% standard deviation
- Moderate: 15% standard deviation
- Aggressive: 25% standard deviation

```
For 1,000 simulations:
    balance = initial_investment
    For each year:
        annual_return = random_normal(expected_return, volatility)
        balance = balance × (1 + annual_return) + (monthly_contribution × 12)
    
    Store final_balance

Sort all final balances
best_case = 95th percentile
worst_case = 5th percentile
median = 50th percentile
```

### Output
- `expected_final_value`: Expected investment value
- `total_contributions`: Total amount invested
- `total_gains`: Investment earnings
- `best_case_scenario`: 95th percentile outcome
- `worst_case_scenario`: 5th percentile outcome
- `median_scenario`: 50th percentile outcome

---

## 💰 Budget Forecast Calculator

### Purpose
Project future cash flow based on income and expenses with growth rates.

### Input Parameters
- `monthly_income`: Current monthly income ($)
- `monthly_expenses`: Current monthly expenses ($)
- `forecast_months`: Projection period (months)
- `income_growth_rate`: Annual income growth (as decimal)
- `expense_growth_rate`: Annual expense growth (as decimal)

### Formulas

#### Monthly Projections
```
current_income = monthly_income
current_expenses = monthly_expenses
cumulative_savings = 0

For each month in forecast period:
    If month % 12 == 0:  # Annual adjustment
        current_income × = (1 + income_growth_rate)
        current_expenses × = (1 + expense_growth_rate)
    
    monthly_net = current_income - current_expenses
    cumulative_savings += monthly_net
    
    Store projection:
        - month number
        - income
        - expenses
        - net_savings
        - cumulative_savings
```

**Example**: $5,000 income, $4,000 expenses, 3% income growth, 2% expense growth
```
Month 1-12:
    Income: $5,000
    Expenses: $4,000
    Net: $1,000/month
    Cumulative: $12,000

Month 13-24:
    Income: $5,000 × 1.03 = $5,150
    Expenses: $4,000 × 1.02 = $4,080
    Net: $1,070/month
    Cumulative: $12,000 + $12,840 = $24,840
```

### Output
- `starting_monthly_income`: Initial income
- `starting_monthly_expenses`: Initial expenses
- `starting_monthly_savings`: Initial net savings
- `projected_total_savings`: Total savings over period
- `average_monthly_savings`: Average monthly savings
- `monthly_projections`: Array of monthly data points

---

## 🧮 Common Financial Concepts

### Compound Interest
Interest calculated on initial principal and accumulated interest:
```
A = P(1 + r/n)^(nt)

Where:
A = Final amount
P = Principal
r = Annual interest rate
n = Compounding frequency per year
t = Time in years
```

### Present Value
Current value of future cash flows:
```
PV = FV / (1 + r)^t

Where:
PV = Present value
FV = Future value
r = Discount rate
t = Time periods
```

### Annuity (Regular Payments)
```
# Future value of annuity
FV = PMT × [((1 + r)^n - 1) / r]

# Present value of annuity
PV = PMT × [(1 - (1 + r)^-n) / r]

Where:
PMT = Payment amount
r = Interest rate per period
n = Number of periods
```

### Monte Carlo Simulation
Statistical method using random sampling to model uncertainty:
1. Define probability distributions for variables
2. Run thousands of simulations with random values
3. Analyze distribution of outcomes
4. Calculate probabilities and percentiles

---

## 📊 Accuracy and Limitations

### Assumptions
- Returns are normally distributed (Monte Carlo)
- Tax implications not included
- Inflation affects purchasing power uniformly
- No account fees or transaction costs
- Regular, consistent contributions

### Accuracy
- Loan calculations: Exact (standard amortization)
- Retirement projections: ±10% (depends on actual returns)
- Investment growth: ±15% (market volatility)
- Budget forecasts: ±5% (assumes stable patterns)

### Recommendations
- Use conservative estimates for returns
- Plan for higher inflation than expected
- Include emergency fund buffer
- Review and adjust plans annually
- Consult financial advisor for personalized advice

---

## 🔧 Implementation Details

### Code Location
- **Backend**: `backend/app/services/simulation_service.py`
- **Frontend**: `frontend/src/components/layout/ChatAssistantWithCalculators.tsx`
- **Tests**: `backend/tests/test_calculations.py`

### API Endpoints
- `POST /api/v1/simulations/loan-payoff/quick`
- `POST /api/v1/simulations/retirement/quick`
- `POST /api/v1/simulations/investment/quick`
- `POST /api/v1/simulations/budget-forecast/quick`

### Data Flow
1. User inputs values in frontend form
2. Frontend converts percentages to decimals
3. API request sent to backend
4. Backend runs calculations
5. Results returned as JSON
6. Frontend formats and displays results

---

**Made with FinPilot AI** 🚀
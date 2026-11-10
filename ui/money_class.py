"""Interactive South African financial literacy lessons using practice scenarios."""

import json
from math import ceil
from pathlib import Path

import streamlit as st


RULES_PATH = Path(__file__).resolve().parents[1] / "config" / "za_money_rules.json"
MONEY_MODULES = {
    "payslip": "Payslip decoder",
    "budget": "Budget simulator",
    "credit": "Debt and credit",
    "saving": "Saving tools",
    "investing": "Investing and shares",
    "tax": "Tax basics",
}
PAYSLIP = {
    "Gross pay": (10000, "Pay before employee deductions. Gross pay and total cost to company can differ."),
    "PAYE": (-850, "Employees’ tax withheld by your employer and paid to SARS. The actual amount depends on taxable pay and your circumstances."),
    "UIF": (-100, "The employee contribution to unemployment insurance. Your employer also contributes where UIF applies."),
    "Pension": (-550, "This example includes an employee contribution to a retirement fund. Actual contributions depend on the fund and employment terms."),
    "SDL": (100, "The Skills Development Levy is an employer cost where applicable. It does not reduce an employee’s net pay."),
    "Net pay": (8500, "The take-home amount after the employee deductions in this example."),
}
BUDGET_ITEMS = {
    "Rent": 3400,
    "Transport": 1000,
    "Mobile data": 300,
    "Food": 1850,
    "Emergency savings": 900,
    "Other costs": 550,
}
BUDGET_ESSENTIALS = ("Rent", "Transport", "Mobile data", "Food")
BUDGET_SHOCKS = {900: "R900 appliance repair", 450: "R450 urgent transport", 1200: "R1,200 medical bill"}
NET_INCOME = PAYSLIP["Net pay"][0]
PRACTICE_ASSETS = {
    "Example manufacturer share": (50, {"Price falls": 40, "Price stays flat": 50, "Price rises": 60}),
    "Example broad-market ETF": (80, {"Price falls": 74, "Price stays flat": 80, "Price rises": 88}),
}


def rand(amount):
    return f"{'-' if amount < 0 else ''}R{abs(amount):,.2f}".removesuffix(".00")


def check_concept(module, question, choices, correct, explanation, complete):
    st.divider()
    with st.form(f"money_check_{module}"):
        answer = st.radio(question, choices, index=None)
        submitted = st.form_submit_button("Check understanding")
    if submitted and answer == correct:
        complete(module)
        st.success(f"{explanation} Module complete.")
    elif submitted and answer is not None:
        st.info(f"{explanation} Give it another try.")
    elif submitted:
        st.info("Choose an answer first.")


def render_payslip(rules, complete, ask_tex):
    st.caption("Fictional training payslip. The deduction amounts are supplied for the exercise.")
    st.metric("Take-home pay", rand(NET_INCOME))
    line = st.selectbox("Tap a payslip line to decode it", PAYSLIP)
    amount, meaning = PAYSLIP[line]
    st.markdown(f"**{line} · {rand(amount)}**")
    st.write(meaning)
    payroll = rules["payroll"]
    if line == "UIF":
        st.caption(f"The employee UIF rate is {payroll['uif_employee_percent']}% of applicable remuneration up to the contribution ceiling.")
    elif line == "SDL":
        st.caption(f"The SDL employer rate is {payroll['sdl_employer_percent']}% where the employer is liable.")
    st.markdown(f"[SARS payroll rates and rules]({payroll['source']})")
    st.button(
        f"Ask Tex about {line}",
        icon=":material/chat:",
        on_click=ask_tex,
        args=(f"Teach me what {line} means on this fictional South African payslip. "
              f"Use this lesson fact: {meaning} Use fictional amounts and avoid estimating my tax.",),
    )
    check_concept(
        "payslip", "Which amount belongs in your spending plan?",
        ["Gross pay", "Net pay", "Gross pay plus SDL"],
        "Net pay", "Net pay is the amount that actually reaches your account.", complete,
    )


def budget_result(amounts, surprise):
    remaining = NET_INCOME - sum(amounts.values())
    after_surprise = remaining - surprise
    checks = {
        "Budgeted for rent, transport, data and food": all(amounts[item] > 0 for item in BUDGET_ESSENTIALS),
        "Spending and saving fit within income": remaining >= 0,
        "Set aside money for emergencies within the budget": remaining >= 0 and amounts["Emergency savings"] > 0,
        "Surprise fits the remaining unallocated cash": after_surprise >= 0,
    }
    return remaining, after_surprise, checks


def render_budget(complete):
    st.write(f"Build a month on **{rand(NET_INCOME)} take-home pay**. Include a surprise expense to test the plan.")
    previous_amounts, previous_surprise = st.session_state.get("money_budget_plan", (BUDGET_ITEMS, 900))
    with st.form("money_budget"):
        amounts = {
            label: st.number_input(
                f"{label} (R)", min_value=0, max_value=30000, value=default, step=50, key=f"money_budget_{label}",
            )
            for label, default in previous_amounts.items()
        }
        surprise = st.selectbox(
            "Surprise expense", BUDGET_SHOCKS, index=list(BUDGET_SHOCKS).index(previous_surprise),
            format_func=BUDGET_SHOCKS.get, key="money_budget_surprise",
        )
        submitted = st.form_submit_button("Test my month", type="primary")
    if submitted:
        st.session_state["money_budget_plan"] = (amounts, surprise)
    if "money_budget_plan" in st.session_state:
        remaining, after_surprise, checks = budget_result(*st.session_state["money_budget_plan"])
        if submitted and remaining >= 0 and all(amounts[item] > 0 for item in BUDGET_ESSENTIALS):
            complete("budget")
        st.caption("Results for your last tested plan")
        cols = st.columns(3)
        cols[0].metric("Plan score", f"{sum(checks.values())} / {len(checks)}")
        cols[1].metric("Cash left", rand(remaining))
        cols[2].metric("After surprise", rand(after_surprise))
        for label, achieved in checks.items():
            st.write(f"{'✓' if achieved else '○'} {label}")
        st.caption("The surprise uses unallocated cash first. An existing emergency fund is a separate buffer.")


def render_credit(complete):
    st.write(
        "A store account is credit. Compare the total repayment, fees and rate before signing. "
        "A credit report records items such as accounts and payment history. Lenders can use that information "
        "when deciding whether to lend. Query errors with the credit bureau."
    )
    st.write(
        "Unregistered lenders, sometimes called mashonisas, can use high charges or pressure. "
        "Check credit providers through the National Credit Regulator and keep your bank card and PIN private."
    )
    st.markdown("[National Credit Regulator](https://www.ncr.org.za/)")
    with st.container(border=True):
        st.markdown("**See how a balance compounds**")
        principal = st.number_input("Starting practice balance (R)", 100, 50000, 2000, 100, key="money_credit_principal")
        rate = st.slider("Example annual interest (%)", 0, 45, 24, key="money_credit_rate")
        months = st.slider("Months with no repayments", 1, 36, 12, key="money_credit_months")
        balance = principal * (1 + rate / 1200) ** months
        st.metric("Example balance", rand(balance), f"{rand(balance - principal)} interest", delta_color="inverse")
        st.caption("Monthly compounding only. Real credit agreements can include fees, repayments and different interest terms.")
    check_concept(
        "credit", "Why does the interest amount grow month by month in this example?",
        ["Interest is added to the balance", "The interest rate goes up each month", "The starting balance is replaced with the annual rate"],
        "Interest is added to the balance",
        "Each new month charges interest on the balance, including interest already added.", complete,
    )


def render_savings(rules, complete):
    st.write(
        "**Emergency fund.** Keep accessible savings for shocks. **Stokvel.** A group saves together under agreed rules. "
        "Check how money is kept, who can withdraw and how members see the records."
    )
    st.write(
        "**Retirement funds.** Pension and provident funds help build long-term retirement savings. "
        "Check your employer’s contributions, fund fees, investment options and access rules."
    )
    tfi = rules["tax_free_investments"]
    st.write(
        f"**Tax-free investments.** SARS lists an annual contribution limit of {rand(tfi['annual_limit_zar'])} "
        f"from {tfi['effective_from']} and a lifetime limit of {rand(tfi['lifetime_limit_zar'])}. "
        "Limits apply across eligible accounts. Replacing a withdrawal generally counts as a new contribution."
    )
    st.markdown(f"[SARS tax-free investment limits]({tfi['source']}) · [FSCA retirement-fund verification](https://www.fsca.co.za/Retirement-Fund-Verifications/)")
    with st.container(border=True):
        st.markdown("**Build a practice emergency fund**")
        essentials = st.number_input("Monthly essentials (R)", 500, 50000, 6000, 100, key="money_saving_costs")
        target_months = st.slider("Months of essentials to cover", 1, 6, 3, key="money_saving_months")
        deposit = st.number_input("Monthly saving (R)", 50, 20000, 750, 50, key="money_saving_deposit")
        st.metric("Example target", rand(essentials * target_months))
        st.caption(f"At that saving pace it takes about {ceil(essentials * target_months / deposit)} months, excluding interest.")
    check_concept(
        "saving", "Which quality matters most for money set aside for an urgent bill?",
        ["Easy access when needed", "The longest possible lock-in", "Exposure to a single company"],
        "Easy access when needed", "An emergency fund should be accessible when something goes wrong.", complete,
    )


def trade_result(price, exit_price, quantity, fee):
    buy_total = price * quantity + fee
    sale_total = exit_price * quantity - fee
    return buy_total, sale_total, sale_total - buy_total


def render_investing(complete):
    st.write(
        "A **share** is a small ownership stake in a company. Its price can fall and dividends can change or stop. "
        "A broad-market **ETF** holds a basket of investments, which can spread some risk. It can still lose value."
    )
    st.write(
        "**Who does what?** Banks take deposits and provide credit. Insurers cover agreed risks. "
        "Fund managers run investment portfolios. Brokers place orders. The JSE is an exchange where listed investments trade, "
        "and the FSCA oversees market conduct."
    )
    st.write(
        "**How a purchase works.** Check the provider’s authorisation and the broker’s JSE membership where applicable. "
        "Compare fees, choose a quantity, review the estimated cost, then choose an order type. "
        "A market order seeks execution at the available price. A limit order sets a price boundary and might not fill."
    )
    st.markdown("[JSE investing lessons](https://www.jse.co.za/learn-how-to-invest) · [FSCA provider register](https://www.fsca.co.za/FSB-Search/)")
    with st.container(border=True):
        st.markdown("**Paper-trading practice**")
        st.caption("Use R1,000 in imaginary cash. Prices and products are fictional. The exercise assumes immediate fills and a flat fee each way.")
        asset = st.selectbox("Fictional investment", PRACTICE_ASSETS)
        price, outcomes = PRACTICE_ASSETS[asset]
        fee = 10
        quantity = st.slider("Units to buy", 1, (1000 - fee) // price, 5, key=f"money_trade_qty_{price}")
        outcome = st.selectbox("Later market scenario", outcomes)
        buy_total, sale_total, profit = trade_result(price, outcomes[outcome], quantity, fee)
        st.caption(f"Entry {rand(price)} per unit · Exit {rand(outcomes[outcome])} per unit · {rand(fee)} fee each way")
        cols = st.columns(3)
        cols[0].metric("Buy cost", rand(buy_total))
        cols[1].metric("Sale proceeds", rand(sale_total))
        cols[2].metric("Gain or loss", rand(profit))
        st.caption("Before tax and dividends. All activity uses practice money.")
    check_concept(
        "investing", "If the price stays flat in this simulation, why can the trade still lose money?",
        ["Buy and sell fees reduce the result", "Every ETF loses money by design", "The entry price doubles at checkout"],
        "Buy and sell fees reduce the result", "Paying a fee on both sides means a flat price can still produce a loss.", complete,
    )


def render_tax(complete):
    st.write(
        "**eFiling.** SARS’s online service lets you review assessments, submit returns and manage tax records. "
        "Keep your IRP5 or IT3(a) and any relevant supporting documents. Review an auto-assessment for missing or incorrect information."
    )
    st.write(
        "**When to file.** Check SARS’s current filing season and whether you need to submit a return. "
        "Different deadlines can apply to provisional and non-provisional taxpayers. Income from freelance or contract work "
        "can create additional obligations depending on how you are paid and your circumstances."
    )
    st.write(
        "**Tax directive.** A formal instruction from SARS can tell a payer how much tax to withhold for a specific payment or situation. "
        "A fixed-percentage directive applies in some eligible cases. Check which rules apply to your type of work."
    )
    st.markdown(
        "[SARS filing season](https://www.sars.gov.za/types-of-tax/personal-income-tax/filing-season/) · "
        "[SARS tax directive guide](https://www.sars.gov.za/guide-to-the-tax-directive-functionality-on-efiling/)"
    )
    check_concept(
        "tax", "You receive an auto-assessment with missing income. What should you do first?",
        ["Review it on eFiling and check SARS’s correction process", "Ignore it because it is automatic", "Pay someone from a social-media message"],
        "Review it on eFiling and check SARS’s correction process",
        "Check the assessment and official correction steps through SARS before relying on the result.", complete,
    )


def render_money_class(complete, ask_tex):
    st.header("Money Class", anchor=False)
    st.caption("South African money skills for your first payslip and beyond. Use the fictional figures to practise.")
    with RULES_PATH.open(encoding="utf-8") as file:
        rules = json.load(file)
    module = st.selectbox("Choose a money lesson", MONEY_MODULES, format_func=MONEY_MODULES.get, key="money_module")
    st.subheader(MONEY_MODULES[module], anchor=False)
    if module == "payslip":
        render_payslip(rules, complete, ask_tex)
    elif module == "budget":
        render_budget(complete)
    elif module == "credit":
        render_credit(complete)
    elif module == "saving":
        render_savings(rules, complete)
    elif module == "investing":
        render_investing(complete)
    elif module == "tax":
        render_tax(complete)
    st.caption(f"Published rule figures reviewed {rules['reviewed_on']}. Check the linked official source for the latest rules.")

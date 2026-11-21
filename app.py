import json
from datetime import date

import streamlit as st


st.set_page_config(page_title="Smart Loan Eligibility Checker", page_icon="🏦", layout="centered")


def calculate_emi(principal, annual_rate, months):
    """Return monthly EMI using the standard reducing-balance formula."""
    monthly_rate = annual_rate / 12 / 100
    if monthly_rate == 0:
        return principal / months
    factor = (1 + monthly_rate) ** months
    return principal * monthly_rate * factor / (factor - 1)


def assess_loan(monthly_income, existing_emi, loan_amount, annual_rate, months, credit_score,
                max_foir, min_credit_score):
    proposed_emi = calculate_emi(loan_amount, annual_rate, months)
    total_emi = existing_emi + proposed_emi
    foir = total_emi / monthly_income * 100 if monthly_income else 100
    affordable_emi = max(0, monthly_income * max_foir / 100 - existing_emi)
    max_supported_loan = 0
    if affordable_emi > 0:
        # Invert the EMI formula to estimate principal supported by the available EMI.
        monthly_rate = annual_rate / 12 / 100
        if monthly_rate == 0:
            max_supported_loan = affordable_emi * months
        else:
            max_supported_loan = affordable_emi * ((1 + monthly_rate) ** months - 1) / (
                monthly_rate * (1 + monthly_rate) ** months
            )

    reasons = []
    if credit_score < min_credit_score:
        reasons.append(f"Credit score is below the configured threshold of {min_credit_score}.")
    if foir > max_foir:
        reasons.append(f"Estimated total EMI uses {foir:.1f}% of monthly income, above the configured {max_foir:.0f}% limit.")
    eligible = not reasons
    return {
        "status": "Meets the configured pre-check" if eligible else "Needs review / does not meet configured pre-check",
        "proposed_emi": proposed_emi,
        "total_emi": total_emi,
        "foir": foir,
        "affordable_emi": affordable_emi,
        "max_supported_loan": max_supported_loan,
        "reasons": reasons or ["The entered values meet the configured pre-check rules."],
    }


st.title("🏦 Smart Loan Eligibility Checker")
st.write("Estimate whether a loan request fits simple, configurable affordability rules. The result is an educational pre-check, not a credit decision or loan offer.")

with st.sidebar:
    st.header("Demo policy settings")
    st.caption("These are example thresholds. Real lenders use their own approved policies and verify all information.")
    max_foir = st.slider("Maximum EMI-to-income ratio (%)", min_value=20, max_value=80, value=50, step=5)
    min_credit_score = st.number_input("Minimum credit score for this demo", min_value=300, max_value=900, value=650, step=10)
    st.markdown("---")
    st.caption("No information is sent to a bank. Avoid entering real personal or account information in a classroom demo.")

st.subheader("Applicant and loan details")
with st.form("loan_form"):
    applicant = st.text_input("Applicant name or demo ID", placeholder="Example: Applicant 001")
    col1, col2 = st.columns(2)
    with col1:
        monthly_income = st.number_input("Monthly net income", min_value=0.0, value=50000.0, step=5000.0)
        existing_emi = st.number_input("Existing monthly loan payments (EMIs)", min_value=0.0, value=5000.0, step=1000.0)
        credit_score = st.number_input("Credit score", min_value=300, max_value=900, value=720, step=10)
    with col2:
        loan_amount = st.number_input("Requested loan amount", min_value=1.0, value=500000.0, step=25000.0)
        annual_rate = st.number_input("Annual interest rate (%)", min_value=0.0, max_value=60.0, value=10.5, step=0.25)
        months = st.selectbox("Loan term", [12, 24, 36, 48, 60, 84, 120, 180, 240], index=4, format_func=lambda n: f"{n} months ({n // 12} years)")
    submitted = st.form_submit_button("Check affordability", type="primary", use_container_width=True)

if submitted:
    if monthly_income <= 0:
        st.error("Enter a monthly income greater than zero to calculate affordability.")
    else:
        result = assess_loan(monthly_income, existing_emi, loan_amount, annual_rate, months, credit_score, max_foir, min_credit_score)
        st.session_state["loan_result"] = result
        st.session_state["loan_inputs"] = {
            "applicant": applicant or "Not provided",
            "monthly_income": monthly_income,
            "existing_emi": existing_emi,
            "credit_score": credit_score,
            "loan_amount": loan_amount,
            "annual_rate": annual_rate,
            "term_months": months,
            "max_foir_percent": max_foir,
            "minimum_credit_score": min_credit_score,
        }

if "loan_result" in st.session_state:
    result = st.session_state["loan_result"]
    inputs = st.session_state["loan_inputs"]
    st.divider()
    st.subheader("Pre-check result")
    if not result["reasons"] or result["reasons"] == ["The entered values meet the configured pre-check rules."]:
        st.success(f"{result['status']}")
    else:
        st.warning(result["status"])

    c1, c2, c3 = st.columns(3)
    c1.metric("Estimated monthly EMI", f"{result['proposed_emi']:,.2f}")
    c2.metric("Total monthly EMI", f"{result['total_emi']:,.2f}")
    c3.metric("EMI / income", f"{result['foir']:.1f}%")
    st.markdown("**What affected this result**")
    for reason in result["reasons"]:
        st.write(f"- {reason}")
    st.write(f"Estimated EMI capacity under the configured ratio: **{result['affordable_emi']:,.2f} per month**")
    st.write(f"Approximate loan amount supported by that EMI capacity: **{result['max_supported_loan']:,.2f}**")
    st.caption("Estimates assume a fixed annual interest rate and equal monthly repayments. Actual rates, fees, eligibility rules, income verification, and lender review can change the outcome.")

    report = {
        "report_date": date.today().isoformat(),
        "applicant_demo_id": inputs["applicant"],
        "inputs": inputs,
        "estimated_results": result,
        "notice": "Educational pre-check only. Not an approval, rejection, legal determination, or loan offer. Final assessment requires authorised lender review.",
    }
    st.download_button("Download result as JSON", data=json.dumps(report, indent=2), file_name="loan_eligibility_precheck.json", mime="application/json")

st.divider()
st.caption("Prototype limitations: this demo uses only the entered income, existing EMI, requested amount, term, interest rate, and a sample credit-score threshold. It does not access credit bureaus, verify identity or income, or apply any jurisdiction-specific lending law.")

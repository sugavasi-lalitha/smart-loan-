# Smart Loan Eligibility Checker

A beginner-friendly Python and Streamlit project that estimates loan affordability using monthly income, existing loan payments, requested loan amount, interest rate, and loan term.

## Features

- Estimates the new loan’s monthly EMI.
- Adds existing monthly EMIs to calculate total monthly loan payments.
- Calculates the EMI-to-income ratio.
- Checks the entered values against adjustable demo thresholds for credit score and EMI-to-income ratio.
- Estimates an affordable EMI and approximate loan amount under the selected demo rules.
- Lets you download a JSON summary of the result.

## Run the app

Install Python 3 and open a terminal in the project folder. On Ubuntu or WSL:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

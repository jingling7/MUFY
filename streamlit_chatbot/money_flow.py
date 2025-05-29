import streamlit as st
from datetime import date
import pandas as pd

st.set_page_config(page_title="Money Flow Tracker", layout="centered")
st.title("💰 Money Flow Tracker")

# Initialize transaction data in session state
if "transactions" not in st.session_state:
    st.session_state.transactions = []

# Function to add a new transaction
def add_transaction(t_type, amount, category, payment_method, t_date):
    st.session_state.transactions.append({
        "Type": t_type,
        "Amount": amount,
        "Category": category,
        "Payment Method": payment_method,
        "Date": t_date
    })

# --- Input form ---
with st.form("add_transaction_form", clear_on_submit=True):
    t_type = st.selectbox("Type", ["Income", "Expense"])
    amount = st.number_input("Amount", min_value=0.01, format="%.2f")
    category = st.text_input("Category (e.g., Salary, Food, Rent)")

    payment_method = st.selectbox("Payment Method", 
                                  ["Cash", "Credit Card", "Debit Card", "Bank Transfer", "Other"])
    if payment_method == "Other":
        payment_method = st.text_input("Please specify payment method")

    t_date = st.date_input("Date", value=date.today())
    submitted = st.form_submit_button("Add Transaction")

    if submitted:
        if amount <= 0:
            st.error("Amount must be positive!")
        elif category.strip() == "":
            st.error("Please enter a category.")
        elif payment_method.strip() == "":
            st.error("Please specify payment method.")
        else:
            add_transaction(t_type, amount, category.strip(), payment_method.strip(), t_date)
            st.success(f"Added {t_type.lower()}: {amount} in category '{category}' via {payment_method}")

# --- Show transactions ---
st.header("📋 Transactions")

if st.session_state.transactions:
    df = pd.DataFrame(st.session_state.transactions)
    df = df.sort_values(by="Date", ascending=False)

    st.dataframe(df)

    # Calculate summary
    total_income = df[df["Type"] == "Income"]["Amount"].sum()
    total_expense = df[df["Type"] == "Expense"]["Amount"].sum()
    balance = total_income - total_expense

    st.markdown(f"### Summary")
    st.markdown(f"- Total Income: 💵 **${total_income:.2f}**")
    st.markdown(f"- Total Expense: 🛒 **${total_expense:.2f}**")
    st.markdown(f"- **Balance: ${balance:.2f}**")
else:
    st.info("No transactions yet. Add your first transaction above!")


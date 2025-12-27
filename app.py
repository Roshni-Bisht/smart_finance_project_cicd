# app.py
import streamlit as st
from datetime import date
from streamlit_option_menu import option_menu
import pandas as pd
import plotly.express as px
import os, json
from pandas.errors import EmptyDataError


# ---------- Files for persistence ----------
DATA_FILE = "expenses.csv"
ACCOUNTS_FILE = "accounts.json"
LOGIN_FILE = "login.json"

# ---------- Utility functions ----------
def load_accounts():
    if os.path.exists(ACCOUNTS_FILE):
        try:
            with open(ACCOUNTS_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def save_accounts(accounts):
    with open(ACCOUNTS_FILE, "w") as f:
        json.dump(accounts, f)

def load_login():
    if os.path.exists(LOGIN_FILE):
        try:
            with open(LOGIN_FILE, "r") as f:
                return json.load(f)
        except:
            return None
    return None

def save_login(user):
    with open(LOGIN_FILE, "w") as f:
        json.dump(user, f)

def clear_login():
    if os.path.exists(LOGIN_FILE):
        os.remove(LOGIN_FILE)

# ---------- Session Defaults ----------
if "accounts" not in st.session_state:
    st.session_state.accounts = load_accounts()

if "user" not in st.session_state:
    st.session_state.user = load_login()
    st.session_state.logged_in = bool(st.session_state.user)

if "show_signup" not in st.session_state:
    st.session_state.show_signup = False

if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["Type", "Amount", "Category", "Date", "Note"])

# ----------------- Authentication -----------------
def login_page():
    col1, col2 = st.columns([1, 1])
    with col1:
        try:
            st.markdown("## Hi, Welcome Back")
            st.markdown("Sign in to Smart Finance!")
            st.image("Images/signup_hero.png")
        except:
            st.warning("signup_hero.png not found")
        
    with col2:
        st.caption("Enter your details below.")
        email = st.text_input("Email address", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login", use_container_width=True):
            found = next((acc for acc in st.session_state.accounts if acc["email"] == email), None)
            if found and password == found.get("password"):
                st.session_state.logged_in = True
                st.session_state.user = found
                save_login(found)  # persist login
                st.success(f"Welcome back, {found['first_name']}!")
                st.rerun()
            else:
                st.error("Invalid credentials or user not found.")

        st.markdown("Don't have an account?")
        if st.button("Sign Up"):
            st.session_state.show_signup = True
            st.rerun()

def signup_page():
    col1, col2 = st.columns([1, 1])
    with col1:
        try:
            st.markdown("## Manage your expenses more effectively")
            st.image("Images/login_hero.png")
        except:
            st.warning("login_hero.png not found")
        
    with col2:
        st.markdown("### ✨ Create your account")
        st.caption("Fill details below to register.")
        fname = st.text_input("First Name", key="signup_fname")
        lname = st.text_input("Last Name", key="signup_lname")
        email = st.text_input("Email address", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_pass")

        if st.button("Register", use_container_width=True):
            if fname and lname and email and password:
                new_acc = {
                    "first_name": fname,
                    "last_name": lname,
                    "email": email,
                    "password": password,
                    "date_joined": date.today().strftime("%Y-%m-%d")
                }
                st.session_state.accounts.append(new_acc)
                save_accounts(st.session_state.accounts)
                st.session_state.user = new_acc
                st.session_state.logged_in = True
                save_login(new_acc)  # persist login
                st.success(f"Account created for {fname} {lname}!")
                st.rerun()
            else:
                st.error("Please fill all fields.")

        st.markdown("Already have an account?")
        if st.button("Login"):
            st.session_state.show_signup = False
            st.rerun()

# ---------- Redirect if not logged in ----------
if not st.session_state.logged_in:
    if st.session_state.show_signup:
        signup_page()
    else:
        login_page()
    st.stop()

# ---------- Load Expenses Data ----------
BASE_DIR = os.path.dirname(__file__) if "__file__" in globals() else os.getcwd()
DATA_FILE = os.path.join(BASE_DIR, "expenses.csv")

if os.path.exists(DATA_FILE):
    try:
        df = pd.read_csv(DATA_FILE, parse_dates=["Date"])
        expected = ["Type", "Amount", "Category", "Date", "Note"]
        for c in expected:
            if c not in df.columns:
                df[c] = None
        df = df[expected]
    except EmptyDataError:
        df = pd.DataFrame(columns=["Type", "Amount", "Category", "Date", "Note"])
    except Exception as e:
        st.error(f"Error reading {DATA_FILE}: {e}")
        df = pd.DataFrame(columns=["Type", "Amount", "Category", "Date", "Note"])
else:
    df = pd.DataFrame(columns=["Type", "Amount", "Category", "Date", "Note"])

if "Date" in df.columns:
    try:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    except:
        pass
st.session_state.data = df

data = st.session_state.data

# ----------------- Dashboard -----------------
def dashboard():
    st.subheader("Overview")

    incomes = data[data["Type"] == "Income"]["Amount"].sum()
    expenses = data[data["Type"] == "Expense"]["Amount"].sum()
    invest = data[data["Type"] == "Investment"]["Amount"].sum() \
             if "Investment" in data["Type"].unique() else 0
    balance = incomes - expenses - invest

    st.markdown("""<style>.metric-card{border:1px solid #e5e7eb;border-radius:12px;padding:14px;text-align:center;background:#fff;box-shadow:0 2px 6px rgba(0,0,0,0.05);} 
    .metric-value{font-size:1.3rem;font-weight:600;} .metric-label{color:#6b7280;font-size:0.9rem;margin-top:4px;}</style>""", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"<div class='metric-card'>💰<div class='metric-value'>₹{incomes:,.2f}</div><div class='metric-label'>Income</div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='metric-card'>📉<div class='metric-value'>₹{expenses:,.2f}</div><div class='metric-label'>Spent</div></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='metric-card'>📊<div class='metric-value'>₹{invest:,.2f}</div><div class='metric-label'>Invest</div></div>", unsafe_allow_html=True)
    with c4:
        st.markdown(f"<div class='metric-card'>🟢<div class='metric-value'>₹{balance:,.2f}</div><div class='metric-label'>Balance</div></div>", unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Report")
    col_left, col_right = st.columns([5, 1])
    with col_right:
        st.date_input("📅", date.today(), label_visibility="collapsed")

        left, right = st.columns([1, 2])

        with left:
          df_expense = data[data["Type"] == "Expense"] if not data.empty else pd.DataFrame()
          if not df_expense.empty:
             donut = px.pie(
             df_expense,
             values="Amount",
             names="Category",
             hole=0.5,
             title="Expense Breakdown",
             color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(donut, use_container_width=True)

        with right:
          if not data.empty and "Date" in data.columns:
            df_monthly = data.copy()
            df_monthly["Date"] = pd.to_datetime(df_monthly["Date"], errors="coerce")
            df_monthly = df_monthly.dropna(subset=["Date"])
        if not df_monthly.empty:
            df_monthly["Month"] = df_monthly["Date"].dt.strftime("%b")
            monthly = df_monthly.groupby("Month", sort=False)["Amount"].sum().reset_index()

            # Create line chart
            line_chart = px.line(
                monthly,
                x="Month",
                y="Amount",
                title="Activity",
                markers=True
            )
            line_chart.update_traces(line=dict(shape="spline", width=3, color="#0077ff"))
            line_chart.update_layout(
                yaxis_title=None,
                xaxis_title=None,
                showlegend=False,
                plot_bgcolor="white",
                margin=dict(l=10, r=10, t=40, b=10)
            )
            st.plotly_chart(line_chart, use_container_width=True)
    

    
            # solve erroers# app.py

#
# ---------- Utility functions ----------
def load_accounts():
    if os.path.exists(ACCOUNTS_FILE):
        try:
            with open(ACCOUNTS_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def save_accounts(accounts):
    with open(ACCOUNTS_FILE, "w") as f:
        json.dump(accounts, f)

def load_login():
    if os.path.exists(LOGIN_FILE):
        try:
            with open(LOGIN_FILE, "r") as f:
                return json.load(f)
        except:
            return None
    return None

def save_login(user):
    with open(LOGIN_FILE, "w") as f:
        json.dump(user, f)

def clear_login():
    if os.path.exists(LOGIN_FILE):
        os.remove(LOGIN_FILE)

# ---------- Session Defaults ----------
if "accounts" not in st.session_state:
    st.session_state.accounts = load_accounts()

if "user" not in st.session_state:
    st.session_state.user = load_login()
    st.session_state.logged_in = bool(st.session_state.user)

if "show_signup" not in st.session_state:
    st.session_state.show_signup = False

if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["Type", "Amount", "Category", "Date", "Note"])

# ----------------- Authentication -----------------
def login_page():
    col1, col2 = st.columns([1, 1])
    with col1:
        try:
            st.markdown("## Hi, Welcome Back")
            st.markdown("Sign in to Smart Finance!")
            st.image("Images/signup_hero.png")
        except:
            st.warning("signup_hero.png not found")
        
    with col2:
        st.caption("Enter your details below.")
        email = st.text_input("Email address", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login", use_container_width=True):
            found = next((acc for acc in st.session_state.accounts if acc["email"] == email), None)
            if found and password == found.get("password"):
                st.session_state.logged_in = True
                st.session_state.user = found
                save_login(found)  # persist login
                st.success(f"Welcome back, {found['first_name']}!")
                st.rerun()
            else:
                st.error("Invalid credentials or user not found.")

        st.markdown("Don't have an account?")
        if st.button("Sign Up"):
            st.session_state.show_signup = True
            st.rerun()

def signup_page():
    col1, col2 = st.columns([1, 1])
    with col1:
        try:
            st.markdown("## Manage your expenses more effectively")
            st.image("Images/login_hero.png")
        except:
            st.warning("login_hero.png not found")
        
    with col2:
        st.markdown("### ✨ Create your account")
        st.caption("Fill details below to register.")
        fname = st.text_input("First Name", key="signup_fname")
        lname = st.text_input("Last Name", key="signup_lname")
        email = st.text_input("Email address", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_pass")

        if st.button("Register", use_container_width=True):
            if fname and lname and email and password:
                new_acc = {
                    "first_name": fname,
                    "last_name": lname,
                    "email": email,
                    "password": password,
                    "date_joined": date.today().strftime("%Y-%m-%d")
                }
                st.session_state.accounts.append(new_acc)
                save_accounts(st.session_state.accounts)
                st.session_state.user = new_acc
                st.session_state.logged_in = True
                save_login(new_acc)  # persist login
                st.success(f"Account created for {fname} {lname}!")
                st.rerun()
            else:
                st.error("Please fill all fields.")

        st.markdown("Already have an account?")
        if st.button("Login"):
            st.session_state.show_signup = False
            st.rerun()

# ---------- Redirect if not logged in ----------
if not st.session_state.logged_in:
    if st.session_state.show_signup:
        signup_page()
    else:
        login_page()
    st.stop()

# ---------- Load Expenses Data ----------
BASE_DIR = os.path.dirname(__file__) if "__file__" in globals() else os.getcwd()
DATA_FILE = os.path.join(BASE_DIR, "expenses.csv")

if os.path.exists(DATA_FILE):
    try:
        df = pd.read_csv(DATA_FILE, parse_dates=["Date"])
        expected = ["Type", "Amount", "Category", "Date", "Note"]
        for c in expected:
            if c not in df.columns:
                df[c] = None
        df = df[expected]
    except EmptyDataError:
        df = pd.DataFrame(columns=["Type", "Amount", "Category", "Date", "Note"])
    except Exception as e:
        st.error(f"Error reading {DATA_FILE}: {e}")
        df = pd.DataFrame(columns=["Type", "Amount", "Category", "Date", "Note"])
else:
    df = pd.DataFrame(columns=["Type", "Amount", "Category", "Date", "Note"])

if "Date" in df.columns:
    try:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    except:
        pass
st.session_state.data = df

data = st.session_state.data

# ----------------- Dashboard -----------------
def dashboard():
    st.subheader("Overview")

    incomes = data[data["Type"] == "Income"]["Amount"].sum()
    expenses = data[data["Type"] == "Expense"]["Amount"].sum()
    invest = data[data["Type"] == "Investment"]["Amount"].sum() \
             if "Investment" in data["Type"].unique() else 0
    balance = incomes - expenses - invest

    st.markdown("""<style>.metric-card{border:1px solid #e5e7eb;border-radius:12px;padding:14px;text-align:center;background:#fff;box-shadow:0 2px 6px rgba(0,0,0,0.05);} 
    .metric-value{font-size:1.3rem;font-weight:600;} .metric-label{color:#6b7280;font-size:0.9rem;margin-top:4px;}</style>""", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"<div class='metric-card'>💰<div class='metric-value'>₹{incomes:,.2f}</div><div class='metric-label'>Income</div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='metric-card'>📉<div class='metric-value'>₹{expenses:,.2f}</div><div class='metric-label'>Spent</div></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='metric-card'>📊<div class='metric-value'>₹{invest:,.2f}</div><div class='metric-label'>Invest</div></div>", unsafe_allow_html=True)
    with c4:
        st.markdown(f"<div class='metric-card'>🟢<div class='metric-value'>₹{balance:,.2f}</div><div class='metric-label'>Balance</div></div>", unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Report")
    col_left, col_right = st.columns([5, 1])
    with col_right:
        st.date_input("📅", date.today(), label_visibility="collapsed")

    left, right = st.columns([1, 2])
    with left:
        df_expense = data[data["Type"] == "Expense"] if not data.empty else pd.DataFrame()
        if not df_expense.empty:
            donut = px.pie(df_expense, values="Amount", names="Category",
                           hole=0.5, title="Expense Breakdown",
                           color_discrete_sequence=px.colors.qualitative.Set2)
            st.plotly_chart(donut, use_container_width=True)
    with right:
        if not data.empty and "Date" in data.columns:
            df_monthly = data.copy()
            df_monthly["Date"] = pd.to_datetime(df_monthly["Date"], errors="coerce")
            df_monthly = df_monthly.dropna(subset=["Date"])
            if not df_monthly.empty:
                df_monthly["Month"] = df_monthly["Date"].dt.strftime("%b")
                monthly = df_monthly.groupby("Month", sort=False)["Amount"].sum().reset_index()


    with right:
        if not data.empty and "Date" in data.columns:
            df_monthly = data.copy()
            df_monthly["Date"] = pd.to_datetime(df_monthly["Date"], errors="coerce")
            df_monthly = df_monthly.dropna(subset=["Date"])
            df_expense = df_monthly[df_monthly["Type"] == "Expense"]  # Only expenses

        if not df_expense.empty:
            # Extract month number and name
            df_expense["MonthNum"] = df_expense["Date"].dt.month
            df_expense["Month"] = df_expense["Date"].dt.strftime("%b")

            # Group by month number to ensure calendar order
            monthly = df_expense.groupby(["MonthNum", "Month"], sort=True)["Amount"].sum().reset_index()
            monthly = monthly.sort_values("MonthNum")  # Ascending order Jan → Dec

            # Plot line chart
            line_chart = px.line(
                monthly,
                x="Month",
                y="Amount",
                title="Monthly Expenses",
                markers=True,
                color_discrete_sequence=["#2527a2"]  # Change to your exact color
            )

            # Make line smooth like your image
            line_chart.update_traces(line=dict(shape="spline", width=3))

            # Layout styling to match dashboard
            line_chart.update_layout(
                yaxis_title=None,
                xaxis_title=None,
                showlegend=False,
                plot_bgcolor="white",
                margin=dict(l=10, r=10, t=40, b=10),
                xaxis=dict(tickmode="linear")
            )

            st.plotly_chart(line_chart, use_container_width=True)

    # # ---------- Expense Form ----------
    # st.markdown("---")
    # st.subheader("➕ Add Expense (bottom)")

    # expense_name = st.text_input("Expense Name", key="expense_name")
    # expense_amount = st.number_input("Amount", min_value=0.0, format="%.2f", key="expense_amount")
    # expense_category = st.selectbox("Category", ["Food", "Rent", "Entertainment", "Transport", "Other"], key="expense_category")
    # expense_date = st.date_input("Date", date.today(), key="expense_date")

    # col1, col2 = st.columns(2)
    # with col1:
    #     if st.button("Save Expense"):
    #         new_expense = {
    #             "Type": "Expense",
    #             "Amount": float(expense_amount),
    #             "Category": expense_category,
    #             "Date": pd.to_datetime(expense_date).date(),
    #             "Note": expense_name
    #         }
    #         st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new_expense])], ignore_index=True)
    #         try:
    #             df_to_save = st.session_state.data.copy()
    #             df_to_save["Date"] = pd.to_datetime(df_to_save["Date"], errors="coerce").dt.date
    #             df_to_save.to_csv(DATA_FILE, index=False)
    #             st.success(f"Added {expense_name} - ₹{expense_amount}")
    #         except Exception as e:
    #             st.error(f"Error saving file: {e}")
    #         st.rerun()

    # with col2:
    #     if st.button("Clear"):
    #         for k in ("expense_name", "expense_amount", "expense_category", "expense_date"):
    #             if k in st.session_state:
    #                 del st.session_state[k]
    #         st.rerun()

# ----------------- Other Pages -----------------

def income_page():
    st.title("💰 Income")

    df_income = st.session_state.data[st.session_state.data["Type"] == "Income"]

    total_income = len(df_income)
    total_amount = df_income["Amount"].sum()

    # --- Same style as Dashboard summary boxes ---
    st.markdown("""
    <style>
    .metric-card {
        border:1px solid #e5e7eb;
        border-radius:12px;
        padding:14px;
        text-align:center;
        background:#fff;
        box-shadow:0 2px 6px rgba(0,0,0,0.05);
    }
    .metric-value {
        font-size:1.3rem;
        font-weight:600;
    }
    .metric-label {
        color:#6b7280;
        font-size:0.9rem;
        margin-top:4px;
    }
    </style>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            f"<div class='metric-card'>📊<div class='metric-value'>{total_income}</div><div class='metric-label'>Total Incomes</div></div>",
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"<div class='metric-card'>💰<div class='metric-value'>₹{total_amount:,.2f}</div><div class='metric-label'>Total Amount</div></div>",
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # --- Filter by Month ---
    st.subheader("Income Records")
    selected_month = st.selectbox(
        "Filter by Month",
        ["All"] + sorted(df_income["Date"].dt.strftime("%B").unique().tolist())
        if not df_income.empty else ["All"],
    )

    filtered_income = df_income.copy()
    if selected_month != "All":
        filtered_income = filtered_income[filtered_income["Date"].dt.strftime("%B") == selected_month]

    # --- Show Table with Edit/Delete ---
    if not filtered_income.empty:
        st.markdown("### Income Records")
        for idx, row in filtered_income.iterrows():
            with st.container():
                c1, c2, c3, c4, c5, c6 = st.columns([2,2,2,2,2,1])
                with c1: st.write(row["Note"])  # Name
                with c2: st.write(f"₹{row['Amount']:,.2f}")  # Amount
                with c3: st.write(row["Date"].strftime("%b %d, %Y"))  # Date
                with c4: st.write(row["Category"])  # Category
                with c5: st.write(row.get("ExtraNote",""))  # Optional Notes
                with c6:
                    edit = st.button("✏️", key=f"edit_income_{idx}")
                    delete = st.button("🗑️", key=f"del_income_{idx}")

                if edit:
                    st.session_state.edit_income_idx = idx

                if delete:
                    st.session_state.data.drop(idx, inplace=True)
                    st.session_state.data.to_csv(DATA_FILE, index=False)
                    st.success("Income deleted!")
                    st.rerun()
    else:
        st.info("No income records found.")

    st.markdown("---")

    # --- Add / Edit Form ---
    if "edit_income_idx" in st.session_state:
        st.subheader("✏️ Edit Income")
        idx = st.session_state.edit_income_idx
        row = st.session_state.data.loc[idx]

        name = st.text_input("Income Name", value=row["Note"], key="edit_income_name")
        amount = st.number_input("Amount", min_value=0.0, value=float(row["Amount"]), key="edit_income_amount")
        category = st.selectbox("Category", ["Salary","Business","Other"], index=0, key="edit_income_category")
        date_in = st.date_input("Date", value=row["Date"], key="edit_income_date")

        if st.button("Update Income"):
            st.session_state.data.loc[idx] = {
                "Type": "Income",
                "Amount": amount,
                "Category": category,
                "Date": pd.to_datetime(date_in),
                "Note": name
            }
            st.session_state.data.to_csv(DATA_FILE, index=False)
            st.success("Income updated successfully!")
            del st.session_state.edit_income_idx
            st.rerun()

    else:
        st.subheader("➕ Add Income")
        name = st.text_input("Income Name", key="new_income_name")
        amount = st.number_input("Amount", min_value=0.0, key="new_income_amount")
        category = st.selectbox("Category", ["Salary","Business","Other"], key="new_income_category")
        date_in = st.date_input("Date", date.today(), key="new_income_date")

        if st.button("Save Income"):
            new_income = {
                "Type": "Income",
                "Amount": amount,
                "Category": category,
                "Date": pd.to_datetime(date_in),
                "Note": name
            }
            st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new_income])], ignore_index=True)
            st.session_state.data.to_csv(DATA_FILE, index=False)
            st.success(f"Added income: {name} - ₹{amount:,.2f}")
            st.rerun()
#------------------------------------------------------------------------------------------------

def expenses_page():
    st.title("💸 Expenses")

    df_expense = st.session_state.data[st.session_state.data["Type"] == "Expense"]

    total_expenses = len(df_expense)
    total_amount = df_expense["Amount"].sum()

    # --- Summary cards like Dashboard ---
    st.markdown("""
    <style>
    .metric-card {
        border:1px solid #e5e7eb;
        border-radius:12px;
        padding:14px;
        text-align:center;
        background:#fff;
        box-shadow:0 2px 6px rgba(0,0,0,0.05);
    }
    .metric-value {
        font-size:1.3rem;
        font-weight:600;
    }
    .metric-label {
        color:#6b7280;
        font-size:0.9rem;
        margin-top:4px;
    }
    </style>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            f"<div class='metric-card'>📊<div class='metric-value'>{total_expenses}</div><div class='metric-label'>Total Expenses</div></div>",
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"<div class='metric-card'>💰<div class='metric-value'>₹{total_amount:,.2f}</div><div class='metric-label'>Total Amount</div></div>",
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # --- Filters ---
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_name = st.text_input("🔍 Filter by Name", key="filter_expense_name")
    with col2:
        filter_category = st.selectbox(
            "Category",
            ["All"] + sorted(df_expense["Category"].dropna().unique().tolist())
            if not df_expense.empty else ["All"],
            key="filter_expense_category"
        )
    with col3:
        filter_month = st.selectbox(
            "📅 Filter by Month",
            ["All"] + sorted(df_expense["Date"].dt.strftime("%B").unique().tolist())
            if not df_expense.empty else ["All"],
            key="filter_expense_month"
        )

    filtered = df_expense.copy()
    if filter_name:
        filtered = filtered[filtered["Note"].str.contains(filter_name, case=False, na=False)]
    if filter_category != "All":
        filtered = filtered[filtered["Category"] == filter_category]
    if filter_month != "All":
        filtered = filtered[filtered["Date"].dt.strftime("%B") == filter_month]

    # --- Show full table with edit/delete buttons ---
    if not filtered.empty:
        st.markdown("### Expense Records")
        for idx, row in filtered.iterrows():
            cols = st.columns([2, 2, 2, 2, 2, 1])
            cols[0].write(row["Note"])
            cols[1].write(f"₹{row['Amount']:,.2f}")
            cols[2].write(row["Date"].strftime("%b %d, %Y"))
            cols[3].write(row["Category"])
            cols[4].write(row.get("PaidVia",""))
            edit_btn = cols[5].button("✏️", key=f"edit_expense_{idx}")
            del_btn = cols[5].button("🗑️", key=f"del_expense_{idx}")

            if edit_btn:
                st.session_state.edit_expense_idx = idx
            if del_btn:
                st.session_state.data.drop(idx, inplace=True)
                st.session_state.data.to_csv(DATA_FILE, index=False)
                st.success("Expense deleted!")
                st.rerun()
    else:
        st.info("No expense records found.")

    st.markdown("---")

    # --- Add / Edit Expense Form ---
    if "edit_expense_idx" in st.session_state:
        st.subheader("✏️ Edit Expense")
        idx = st.session_state.edit_expense_idx
        row = st.session_state.data.loc[idx]

        name = st.text_input("Expense Name", value=row["Note"], key="edit_expense_name")
        amount = st.number_input("Amount", min_value=0.0, value=float(row["Amount"]), key="edit_expense_amount")
        category = st.selectbox("Category", ["Food","Rent","Entertainment","Transport","Other"], index=0, key="edit_expense_category")
        date_in = st.date_input("Date", value=row["Date"], key="edit_expense_date")
        paid_via = st.text_input("Paid Via", value=row.get("PaidVia",""), key="edit_expense_paid")
        notes = st.text_area("Notes", value=row.get("ExtraNote",""), key="edit_expense_notes")

        if st.button("Update Expense"):
            st.session_state.data.loc[idx] = {
                "Type": "Expense",
                "Amount": amount,
                "Category": category,
                "Date": pd.to_datetime(date_in),
                "Note": name,
                "PaidVia": paid_via,
                "ExtraNote": notes
            }
            st.session_state.data.to_csv(DATA_FILE, index=False)
            st.success("Expense updated successfully!")
            del st.session_state.edit_expense_idx
            st.rerun()

    else:
        st.subheader("➕ Add Expense")
        name = st.text_input("Expense Name", key="new_expense_name")
        amount = st.number_input("Amount", min_value=0.0, key="new_expense_amount")
        category = st.selectbox("Category", ["Food","Rent","Entertainment","Transport","Other"], key="new_expense_category")
        date_in = st.date_input("Date", date.today(), key="new_expense_date")
        paid_via = st.text_input("Paid Via", key="new_expense_paid")
        notes = st.text_area("Notes", key="new_expense_notes")

        if st.button("Save Expense"):
            new_expense = {
                "Type": "Expense",
                "Amount": amount,
                "Category": category,
                "Date": pd.to_datetime(date_in),
                "Note": name,
                "PaidVia": paid_via,
                "ExtraNote": notes
            }
            st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new_expense])], ignore_index=True)
            st.session_state.data.to_csv(DATA_FILE, index=False)
            st.success(f"Added expense: {name} - ₹{amount:,.2f}")
            st.rerun()

def savings_page():
    st.title("💹 Investments")

    df_invest = st.session_state.data[st.session_state.data["Type"] == "Investment"]

    total_investments = len(df_invest)
    total_amount = df_invest["Amount"].sum() if not df_invest.empty else 0

    # --- Summary Cards ---
    st.markdown("""
    <style>
    .metric-card {
        border:1px solid #e5e7eb;
        border-radius:12px;
        padding:14px;
        text-align:center;
        background:#fff;
        box-shadow:0 2px 6px rgba(0,0,0,0.05);
    }
    .metric-value {
        font-size:1.3rem;
        font-weight:600;
    }
    .metric-label {
        color:#6b7280;
        font-size:0.9rem;
        margin-top:4px;
    }
    </style>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            f"<div class='metric-card'>📊<div class='metric-value'>{total_investments}</div><div class='metric-label'>Total Investments</div></div>",
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"<div class='metric-card'>💰<div class='metric-value'>₹{total_amount:,.2f}</div><div class='metric-label'>Total Amount</div></div>",
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # --- Filter by Month ---
    selected_month = st.selectbox(
        "📅 Filter by Month",
        ["All"] + sorted(df_invest["Date"].dt.strftime("%B").unique().tolist()) if not df_invest.empty else ["All"]
    )

    filtered = df_invest.copy()
    if selected_month != "All":
        filtered = filtered[filtered["Date"].dt.strftime("%B") == selected_month]

    # --- Show Table with Edit/Delete ---
    if not filtered.empty:
        st.markdown("### Investment Records")
        for idx, row in filtered.iterrows():
            cols = st.columns([2,1,1,1,2,1,2,1])
            cols[0].write(row["Note"])  # Name
            cols[1].write(row.get("Units",""))  # Units
            cols[2].write(f"₹{row.get('SinglePrice',0):,.2f}")  # Single Stock Price
            cols[3].write(f"₹{row['Amount']:,.2f}")  # Total Amount
            cols[4].write(row["Date"].strftime("%b %d, %Y"))  # Bought Date
            cols[5].write(row["Category"])  # Category
            cols[6].write(row.get("ExtraNote",""))  # Notes
            edit_btn = cols[7].button("✏️", key=f"edit_invest_{idx}")
            del_btn = cols[7].button("🗑️", key=f"del_invest_{idx}")

            if edit_btn:
                st.session_state.edit_invest_idx = idx
            if del_btn:
                st.session_state.data.drop(idx, inplace=True)
                st.session_state.data.to_csv(DATA_FILE, index=False)
                st.success("Investment deleted!")
                st.rerun()
    else:
        st.info("No investment records found.")

    st.markdown("---")

    # --- Add / Edit Investment Form ---
    if "edit_invest_idx" in st.session_state:
        st.subheader("✏️ Edit Investment")
        idx = st.session_state.edit_invest_idx
        row = st.session_state.data.loc[idx]

        name = st.text_input("Investment Name", value=row["Note"], key="edit_invest_name")
        units = st.number_input("Units", min_value=0.0, value=float(row.get("Units",0)), key="edit_invest_units")
        single_price = st.number_input("Single Stock Price", min_value=0.0, value=float(row.get("SinglePrice",0)), key="edit_invest_price")
        total_amount_input = units * single_price
        category = st.selectbox("Category", ["Indian Stock","Crypto Currency","Mutual Funds","Other"], index=0, key="edit_invest_category")
        date_in = st.date_input("Bought Date", value=row["Date"], key="edit_invest_date")
        notes = st.text_area("Notes", value=row.get("ExtraNote",""), key="edit_invest_notes")

        if st.button("Update Investment"):
            st.session_state.data.loc[idx] = {
                "Type": "Investment",
                "Amount": total_amount_input,
                "Category": category,
                "Date": pd.to_datetime(date_in),
                "Note": name,
                "Units": units,
                "SinglePrice": single_price,
                "ExtraNote": notes
            }
            st.session_state.data.to_csv(DATA_FILE, index=False)
            st.success("Investment updated successfully!")
            del st.session_state.edit_invest_idx
            st.rerun()
    else:
        st.subheader("➕ Add Investment")
        name = st.text_input("Investment Name", key="new_invest_name")
        units = st.number_input("Units", min_value=0.0, key="new_invest_units")
        single_price = st.number_input("Single Stock Price", min_value=0.0, key="new_invest_price")
        total_amount_input = units * single_price
        category = st.selectbox("Category", ["Indian Stock","Crypto Currency","Mutual Funds","Other"], key="new_invest_category")
        date_in = st.date_input("Bought Date", date.today(), key="new_invest_date")
        notes = st.text_area("Notes", key="new_invest_notes")

        if st.button("Save Investment"):
            new_invest = {
                "Type": "Investment",
                "Amount": total_amount_input,
                "Category": category,
                "Date": pd.to_datetime(date_in),
                "Note": name,
                "Units": units,
                "SinglePrice": single_price,
                "ExtraNote": notes
            }
            st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new_invest])], ignore_index=True)
            st.session_state.data.to_csv(DATA_FILE, index=False)
            st.success(f"Added investment: {name} - ₹{total_amount_input:,.2f}")
            st.rerun()
def goals_page():
    st.title("🎯 Goals")
    st.info("This is your goals page. You can add financial goals here.")


def settings_page():
    st.title("⚙️ Settings")
    st.markdown("---")
    st.markdown("### 👤 Your Profile")

    if "profile" not in st.session_state:
        st.session_state.profile = {
            "First Name": "John",
            "Last Name": "Doe",
            "Username": st.session_state.user.get("first_name", "User"),
            "Email": st.session_state.user.get("email", "user@email.com"),
            "Photo": None
        }

    profile = st.session_state.profile
    edit_mode = st.checkbox("✏️ Edit Profile")

    if edit_mode:
        with st.form("profile_form", clear_on_submit=False):
            uploaded_photo = st.file_uploader("Upload Profile Photo", type=["jpg", "png", "jpeg"])
            if uploaded_photo:
                profile["Photo"] = uploaded_photo.getvalue()

            fname = st.text_input("First Name", value=profile["First Name"])
            lname = st.text_input("Last Name", value=profile["Last Name"])
            uname = st.text_input("Username", value=profile["Username"], disabled=True)
            email = st.text_input("Email", value=profile["Email"])
            submitted = st.form_submit_button("💾 Save Changes")
            if submitted:
                st.session_state.profile.update({
                    "First Name": fname,
                    "Last Name": lname,
                    "Email": email,
                })
                st.success("✅ Profile updated successfully!")
                st.rerun()
    else:
        st.markdown(
            """
            <style>
            .details-card {
                border: 1px solid #e5e7eb;
                border-radius: 12px;
                padding: 16px;
                background: #fff;
                box-shadow: 0 2px 6px rgba(0,0,0,0.05);
            }
            .details-grid {
                display: grid;
                grid-template-columns: 1fr 2fr;
                row-gap: 10px;
                column-gap: 20px;
            }
            .details-label { font-weight: 600; color: #374151; }
            .details-value { color: #111827; }
            </style>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<div class='details-card'>", unsafe_allow_html=True)

        # Profile photo
        if profile.get("Photo"):
            st.image(profile["Photo"], width=100, caption="Profile Photo")

        st.markdown(
            f"""
            <div class="details-grid">
                <div class="details-label">First Name</div><div class="details-value">{profile['First Name']}</div>
                <div class="details-label">Last Name</div><div class="details-value">{profile['Last Name']}</div>
                <div class="details-label">Username</div><div class="details-value">{profile['Username']}</div>
                <div class="details-label">Email</div><div class="details-value">{profile['Email']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")

    # --- Theme Switch ---
    dark_mode = st.toggle("🌙 Theme", key="dark_mode")

    if dark_mode:
        st.markdown(
            """
            <style>
            body, .stApp {
                background-color: #111827;
                color: #f9fafb;
            }
            .metric-card, .details-card {
                background: #1f2937 !important;
                color: #f9fafb !important;
            }
            .details-label {
                color: #d1d5db !important;
            }
            .details-value {
                color: #f9fafb !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
    st.markdown("---")

    # --- Plans ---
    st.subheader("📦 Subscription Plan")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            """
            <div class="metric-card">
            <h4>Basic (Free)</h4>
            <p><b>$0</b> per month</p>
            <ul>
                <li>Trend visualisation with charts</li>
                <li>Add up to 100 entries per account</li>
                <li>Track subscription billing dates</li>
                <li>Choose preferred currency display</li>
                <li>Email support available</li>
            </ul>
            <b>✅ Current plan</b>
            </div>
            """, unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            """
            <div class="metric-card">
            <h4>Premium</h4>
            <p><b>$20</b> per year</p>
            <ul>
                <li>Everything in Basic plan</li>
                <li>Add up to 2000 entries per account</li>
                <li>Advanced trend visualisation</li>
                <li>Export data as CSV</li>
                <li>Priority support</li>
            </ul>
            <button style="padding:8px 16px;background:#25a244;color:white;border:none;border-radius:8px;">Go Premium</button>
            </div>
            """, unsafe_allow_html=True
        )

    st.markdown("---")

    # --- Delete Account ---
    st.error("⚠️ Permanently delete your account and all its data.")
    if st.button("🗑️ Delete Account"):
        st.session_state.accounts = [a for a in st.session_state.accounts if a["email"] != st.session_state.user["email"]]
        save_accounts(st.session_state.accounts)
        clear_login()
        st.session_state.logged_in = False
        st.success("Account deleted successfully!")
        st.rerun()

# ----------------- Main App -----------------
with st.sidebar:
    choice = option_menu(
        "Smart Finance",
        ["Dashboard", "Income", "Expenses", "Investment", "Settings", "Logout"],
        icons=["speedometer", "wallet2", "cash-coin", "piggy-bank", "gear", "box-arrow-right"],
        menu_icon="app-indicator",
        default_index=0,
    )

if choice == "Dashboard":
    dashboard()
elif choice == "Income":
    income_page()
elif choice == "Expenses":
    expenses_page()
elif choice == "Investment":
    savings_page()
elif choice == "Settings":
    settings_page()
elif choice == "Logout":
    st.session_state.logged_in = False
    st.session_state.user = None
    clear_login()
    st.success("You have been logged out.")

                
    # ---------- Expense Form ----------
    st.markdown("---")
    st.subheader("➕ Add Expense (bottom)")

    expense_name = st.text_input("Expense Name", key="expense_name")
    expense_amount = st.number_input("Amount", min_value=0.0, format="%.2f", key="expense_amount")
    expense_category = st.selectbox("Category", ["Food", "Rent", "Entertainment", "Transport", "Other"], key="expense_category")
    expense_date = st.date_input("Date", date.today(), key="expense_date")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Save Expense"):
            new_expense = {
                "Type": "Expense",
                "Amount": float(expense_amount),
                "Category": expense_category,
                "Date": pd.to_datetime(expense_date).date(),
                "Note": expense_name
            }
            st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new_expense])], ignore_index=True)
            try:
                df_to_save = st.session_state.data.copy()
                df_to_save["Date"] = pd.to_datetime(df_to_save["Date"], errors="coerce").dt.date
                df_to_save.to_csv(DATA_FILE, index=False)
                st.success(f"Added {expense_name} - ₹{expense_amount}")
            except Exception as e:
                st.error(f"Error saving file: {e}")
            st.rerun()

    with col2:
        if st.button("Clear"):
            for k in ("expense_name", "expense_amount", "expense_category", "expense_date"):
                if k in st.session_state:
                    del st.session_state[k]
            st.rerun()

# ----------------- Other Pages -----------------

def income_page():
    st.title("💰 Income")

    df_income = st.session_state.data[st.session_state.data["Type"] == "Income"]

    total_income = len(df_income)
    total_amount = df_income["Amount"].sum()

    # --- Same style as Dashboard summary boxes ---
    st.markdown("""
    <style>
    .metric-card {
        border:1px solid #e5e7eb;
        border-radius:12px;
        padding:14px;
        text-align:center;
        background:#fff;
        box-shadow:0 2px 6px rgba(0,0,0,0.05);
    }
    .metric-value {
        font-size:1.3rem;
        font-weight:600;
    }
    .metric-label {
        color:#6b7280;
        font-size:0.9rem;
        margin-top:4px;
    }
    </style>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            f"<div class='metric-card'>📊<div class='metric-value'>{total_income}</div><div class='metric-label'>Total Incomes</div></div>",
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"<div class='metric-card'>💰<div class='metric-value'>₹{total_amount:,.2f}</div><div class='metric-label'>Total Amount</div></div>",
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # --- Filter by Month ---
    st.subheader("Income Records")
    selected_month = st.selectbox(
        "Filter by Month",
        ["All"] + sorted(df_income["Date"].dt.strftime("%B").unique().tolist())
        if not df_income.empty else ["All"],
    )

    filtered_income = df_income.copy()
    if selected_month != "All":
        filtered_income = filtered_income[filtered_income["Date"].dt.strftime("%B") == selected_month]

    # --- Show Table with Edit/Delete ---
    if not filtered_income.empty:
        st.markdown("### Income Records")
        for idx, row in filtered_income.iterrows():
            with st.container():
                c1, c2, c3, c4, c5, c6 = st.columns([2,2,2,2,2,1])
                with c1: st.write(row["Note"])  # Name
                with c2: st.write(f"₹{row['Amount']:,.2f}")  # Amount
                with c3: st.write(row["Date"].strftime("%b %d, %Y"))  # Date
                with c4: st.write(row["Category"])  # Category
                with c5: st.write(row.get("ExtraNote",""))  # Optional Notes
                with c6:
                    edit = st.button("✏️", key=f"edit_income_{idx}")
                    delete = st.button("🗑️", key=f"del_income_{idx}")

                if edit:
                    st.session_state.edit_income_idx = idx

                if delete:
                    st.session_state.data.drop(idx, inplace=True)
                    st.session_state.data.to_csv(DATA_FILE, index=False)
                    st.success("Income deleted!")
                    st.rerun()
    else:
        st.info("No income records found.")

    st.markdown("---")

    # --- Add / Edit Form ---
    if "edit_income_idx" in st.session_state:
        st.subheader("✏️ Edit Income")
        idx = st.session_state.edit_income_idx
        row = st.session_state.data.loc[idx]

        name = st.text_input("Income Name", value=row["Note"], key="edit_income_name")
        amount = st.number_input("Amount", min_value=0.0, value=float(row["Amount"]), key="edit_income_amount")
        category = st.selectbox("Category", ["Salary","Business","Other"], index=0, key="edit_income_category")
        date_in = st.date_input("Date", value=row["Date"], key="edit_income_date")

        if st.button("Update Income"):
            st.session_state.data.loc[idx] = {
                "Type": "Income",
                "Amount": amount,
                "Category": category,
                "Date": pd.to_datetime(date_in),
                "Note": name
            }
            st.session_state.data.to_csv(DATA_FILE, index=False)
            st.success("Income updated successfully!")
            del st.session_state.edit_income_idx
            st.rerun()

    else:
        st.subheader("➕ Add Income")
        name = st.text_input("Income Name", key="new_income_name")
        amount = st.number_input("Amount", min_value=0.0, key="new_income_amount")
        category = st.selectbox("Category", ["Salary","Business","Other"], key="new_income_category")
        date_in = st.date_input("Date", date.today(), key="new_income_date")

        if st.button("Save Income"):
            new_income = {
                "Type": "Income",
                "Amount": amount,
                "Category": category,
                "Date": pd.to_datetime(date_in),
                "Note": name
            }
            st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new_income])], ignore_index=True)
            st.session_state.data.to_csv(DATA_FILE, index=False)
            st.success(f"Added income: {name} - ₹{amount:,.2f}")
            st.rerun()
#------------------------------------------------------------------------------------------------

def expenses_page():
    st.title("💸 Expenses")

    df_expense = st.session_state.data[st.session_state.data["Type"] == "Expense"]

    total_expenses = len(df_expense)
    total_amount = df_expense["Amount"].sum()

    # --- Summary cards like Dashboard ---
    st.markdown("""
    <style>
    .metric-card {
        border:1px solid #e5e7eb;
        border-radius:12px;
        padding:14px;
        text-align:center;
        background:#fff;
        box-shadow:0 2px 6px rgba(0,0,0,0.05);
    }
    .metric-value {
        font-size:1.3rem;
        font-weight:600;
    }
    .metric-label {
        color:#6b7280;
        font-size:0.9rem;
        margin-top:4px;
    }
    </style>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            f"<div class='metric-card'>📊<div class='metric-value'>{total_expenses}</div><div class='metric-label'>Total Expenses</div></div>",
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"<div class='metric-card'>💰<div class='metric-value'>₹{total_amount:,.2f}</div><div class='metric-label'>Total Amount</div></div>",
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # --- Filters ---
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_name = st.text_input("🔍 Filter by Name", key="filter_expense_name")
    with col2:
        filter_category = st.selectbox(
            "Category",
            ["All"] + sorted(df_expense["Category"].dropna().unique().tolist())
            if not df_expense.empty else ["All"],
            key="filter_expense_category"
        )
    with col3:
        filter_month = st.selectbox(
            "📅 Filter by Month",
            ["All"] + sorted(df_expense["Date"].dt.strftime("%B").unique().tolist())
            if not df_expense.empty else ["All"],
            key="filter_expense_month"
        )

    filtered = df_expense.copy()
    if filter_name:
        filtered = filtered[filtered["Note"].str.contains(filter_name, case=False, na=False)]
    if filter_category != "All":
        filtered = filtered[filtered["Category"] == filter_category]
    if filter_month != "All":
        filtered = filtered[filtered["Date"].dt.strftime("%B") == filter_month]

    # --- Show full table with edit/delete buttons ---
    if not filtered.empty:
        st.markdown("### Expense Records")
        for idx, row in filtered.iterrows():
            cols = st.columns([2, 2, 2, 2, 2, 1])
            cols[0].write(row["Note"])
            cols[1].write(f"₹{row['Amount']:,.2f}")
            cols[2].write(row["Date"].strftime("%b %d, %Y"))
            cols[3].write(row["Category"])
            cols[4].write(row.get("PaidVia",""))
            edit_btn = cols[5].button("✏️", key=f"edit_expense_{idx}")
            del_btn = cols[5].button("🗑️", key=f"del_expense_{idx}")

            if edit_btn:
                st.session_state.edit_expense_idx = idx
            if del_btn:
                st.session_state.data.drop(idx, inplace=True)
                st.session_state.data.to_csv(DATA_FILE, index=False)
                st.success("Expense deleted!")
                st.rerun()
    else:
        st.info("No expense records found.")

    st.markdown("---")

    # --- Add / Edit Expense Form ---
    if "edit_expense_idx" in st.session_state:
        st.subheader("✏️ Edit Expense")
        idx = st.session_state.edit_expense_idx
        row = st.session_state.data.loc[idx]

        name = st.text_input("Expense Name", value=row["Note"], key="edit_expense_name")
        amount = st.number_input("Amount", min_value=0.0, value=float(row["Amount"]), key="edit_expense_amount")
        category = st.selectbox("Category", ["Food","Rent","Entertainment","Transport","Other"], index=0, key="edit_expense_category")
        date_in = st.date_input("Date", value=row["Date"], key="edit_expense_date")
        paid_via = st.text_input("Paid Via", value=row.get("PaidVia",""), key="edit_expense_paid")
        notes = st.text_area("Notes", value=row.get("ExtraNote",""), key="edit_expense_notes")

        if st.button("Update Expense"):
            st.session_state.data.loc[idx] = {
                "Type": "Expense",
                "Amount": amount,
                "Category": category,
                "Date": pd.to_datetime(date_in),
                "Note": name,
                "PaidVia": paid_via,
                "ExtraNote": notes
            }
            st.session_state.data.to_csv(DATA_FILE, index=False)
            st.success("Expense updated successfully!")
            del st.session_state.edit_expense_idx
            st.rerun()

    else:
        st.subheader("➕ Add Expense")
        name = st.text_input("Expense Name", key="new_expense_name")
        amount = st.number_input("Amount", min_value=0.0, key="new_expense_amount")
        category = st.selectbox("Category", ["Food","Rent","Entertainment","Transport","Other"], key="new_expense_category")
        date_in = st.date_input("Date", date.today(), key="new_expense_date")
        paid_via = st.text_input("Paid Via", key="new_expense_paid")
        notes = st.text_area("Notes", key="new_expense_notes")

        if st.button("Save Expense"):
            new_expense = {
                "Type": "Expense",
                "Amount": amount,
                "Category": category,
                "Date": pd.to_datetime(date_in),
                "Note": name,
                "PaidVia": paid_via,
                "ExtraNote": notes
            }
            st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new_expense])], ignore_index=True)
            st.session_state.data.to_csv(DATA_FILE, index=False)
            st.success(f"Added expense: {name} - ₹{amount:,.2f}")
            st.rerun()

def savings_page():
    st.title("💹 Investments")

    df_invest = st.session_state.data[st.session_state.data["Type"] == "Investment"]

    total_investments = len(df_invest)
    total_amount = df_invest["Amount"].sum() if not df_invest.empty else 0

    # --- Summary Cards ---
    st.markdown("""
    <style>
    .metric-card {
        border:1px solid #e5e7eb;
        border-radius:12px;
        padding:14px;
        text-align:center;
        background:#fff;
        box-shadow:0 2px 6px rgba(0,0,0,0.05);
    }
    .metric-value {
        font-size:1.3rem;
        font-weight:600;
    }
    .metric-label {
        color:#6b7280;
        font-size:0.9rem;
        margin-top:4px;
    }
    </style>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            f"<div class='metric-card'>📊<div class='metric-value'>{total_investments}</div><div class='metric-label'>Total Investments</div></div>",
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"<div class='metric-card'>💰<div class='metric-value'>₹{total_amount:,.2f}</div><div class='metric-label'>Total Amount</div></div>",
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # --- Filter by Month ---
    selected_month = st.selectbox(
        "📅 Filter by Month",
        ["All"] + sorted(df_invest["Date"].dt.strftime("%B").unique().tolist()) if not df_invest.empty else ["All"]
    )

    filtered = df_invest.copy()
    if selected_month != "All":
        filtered = filtered[filtered["Date"].dt.strftime("%B") == selected_month]

    # --- Show Table with Edit/Delete ---
    if not filtered.empty:
        st.markdown("### Investment Records")
        for idx, row in filtered.iterrows():
            cols = st.columns([2,1,1,1,2,1,2,1])
            cols[0].write(row["Note"])  # Name
            cols[1].write(row.get("Units",""))  # Units
            cols[2].write(f"₹{row.get('SinglePrice',0):,.2f}")  # Single Stock Price
            cols[3].write(f"₹{row['Amount']:,.2f}")  # Total Amount
            cols[4].write(row["Date"].strftime("%b %d, %Y"))  # Bought Date
            cols[5].write(row["Category"])  # Category
            cols[6].write(row.get("ExtraNote",""))  # Notes
            edit_btn = cols[7].button("✏️", key=f"edit_invest_{idx}")
            del_btn = cols[7].button("🗑️", key=f"del_invest_{idx}")

            if edit_btn:
                st.session_state.edit_invest_idx = idx
            if del_btn:
                st.session_state.data.drop(idx, inplace=True)
                st.session_state.data.to_csv(DATA_FILE, index=False)
                st.success("Investment deleted!")
                st.rerun()
    else:
        st.info("No investment records found.")

    st.markdown("---")

    # --- Add / Edit Investment Form ---
    if "edit_invest_idx" in st.session_state:
        st.subheader("✏️ Edit Investment")
        idx = st.session_state.edit_invest_idx
        row = st.session_state.data.loc[idx]

        name = st.text_input("Investment Name", value=row["Note"], key="edit_invest_name")
        units = st.number_input("Units", min_value=0.0, value=float(row.get("Units",0)), key="edit_invest_units")
        single_price = st.number_input("Single Stock Price", min_value=0.0, value=float(row.get("SinglePrice",0)), key="edit_invest_price")
        total_amount_input = units * single_price
        category = st.selectbox("Category", ["Indian Stock","Crypto Currency","Mutual Funds","Other"], index=0, key="edit_invest_category")
        date_in = st.date_input("Bought Date", value=row["Date"], key="edit_invest_date")
        notes = st.text_area("Notes", value=row.get("ExtraNote",""), key="edit_invest_notes")

        if st.button("Update Investment"):
            st.session_state.data.loc[idx] = {
                "Type": "Investment",
                "Amount": total_amount_input,
                "Category": category,
                "Date": pd.to_datetime(date_in),
                "Note": name,
                "Units": units,
                "SinglePrice": single_price,
                "ExtraNote": notes
            }
            st.session_state.data.to_csv(DATA_FILE, index=False)
            st.success("Investment updated successfully!")
            del st.session_state.edit_invest_idx
            st.rerun()
    else:
        st.subheader("➕ Add Investment")
        name = st.text_input("Investment Name", key="new_invest_name")
        units = st.number_input("Units", min_value=0.0, key="new_invest_units")
        single_price = st.number_input("Single Stock Price", min_value=0.0, key="new_invest_price")
        total_amount_input = units * single_price
        category = st.selectbox("Category", ["Indian Stock","Crypto Currency","Mutual Funds","Other"], key="new_invest_category")
        date_in = st.date_input("Bought Date", date.today(), key="new_invest_date")
        notes = st.text_area("Notes", key="new_invest_notes")

        if st.button("Save Investment"):
            new_invest = {
                "Type": "Investment",
                "Amount": total_amount_input,
                "Category": category,
                "Date": pd.to_datetime(date_in),
                "Note": name,
                "Units": units,
                "SinglePrice": single_price,
                "ExtraNote": notes
            }
            st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new_invest])], ignore_index=True)
            st.session_state.data.to_csv(DATA_FILE, index=False)
            st.success(f"Added investment: {name} - ₹{total_amount_input:,.2f}")
            st.rerun()
def goals_page():
    st.title("🎯 Goals")
    st.info("This is your goals page. You can add financial goals here.")


def settings_page():
    st.title("⚙️ Settings")
    st.markdown("---")
    st.markdown("### 👤 Your Profile")

    if "profile" not in st.session_state:
        st.session_state.profile = {
            "First Name": "John",
            "Last Name": "Doe",
            "Username": st.session_state.user.get("first_name", "User"),
            "Email": st.session_state.user.get("email", "user@email.com"),
            "Photo": None
        }

    profile = st.session_state.profile
    edit_mode = st.checkbox("✏️ Edit Profile")

    if edit_mode:
        with st.form("profile_form", clear_on_submit=False):
            uploaded_photo = st.file_uploader("Upload Profile Photo", type=["jpg", "png", "jpeg"])
            if uploaded_photo:
                profile["Photo"] = uploaded_photo.getvalue()

            fname = st.text_input("First Name", value=profile["First Name"])
            lname = st.text_input("Last Name", value=profile["Last Name"])
            uname = st.text_input("Username", value=profile["Username"], disabled=True)
            email = st.text_input("Email", value=profile["Email"])
            submitted = st.form_submit_button("💾 Save Changes")
            if submitted:
                st.session_state.profile.update({
                    "First Name": fname,
                    "Last Name": lname,
                    "Email": email,
                })
                st.success("✅ Profile updated successfully!")
                st.rerun()
    else:
        st.markdown(
            """
            <style>
            .details-card {
                border: 1px solid #e5e7eb;
                border-radius: 12px;
                padding: 16px;
                background: #fff;
                box-shadow: 0 2px 6px rgba(0,0,0,0.05);
            }
            .details-grid {
                display: grid;
                grid-template-columns: 1fr 2fr;
                row-gap: 10px;
                column-gap: 20px;
            }
            .details-label { font-weight: 600; color: #374151; }
            .details-value { color: #111827; }
            </style>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<div class='details-card'>", unsafe_allow_html=True)

        # Profile photo
        if profile.get("Photo"):
            st.image(profile["Photo"], width=100, caption="Profile Photo")

        st.markdown(
            f"""
            <div class="details-grid">
                <div class="details-label">First Name</div><div class="details-value">{profile['First Name']}</div>
                <div class="details-label">Last Name</div><div class="details-value">{profile['Last Name']}</div>
                <div class="details-label">Username</div><div class="details-value">{profile['Username']}</div>
                <div class="details-label">Email</div><div class="details-value">{profile['Email']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")

    # --- Theme Switch ---
    dark_mode = st.toggle("🌙 Theme", key="dark_mode")

    if dark_mode:
        st.markdown(
            """
            <style>
            body, .stApp {
                background-color: #111827;
                color: #f9fafb;
            }
            .metric-card, .details-card {
                background: #1f2937 !important;
                color: #f9fafb !important;
            }
            .details-label {
                color: #d1d5db !important;
            }
            .details-value {
                color: #f9fafb !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
    st.markdown("---")

    # --- Plans ---
    st.subheader("📦 Subscription Plan")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            """
            <div class="metric-card">
            <h4>Basic (Free)</h4>
            <p><b>$0</b> per month</p>
            <ul>
                <li>Trend visualisation with charts</li>
                <li>Add up to 100 entries per account</li>
                <li>Track subscription billing dates</li>
                <li>Choose preferred currency display</li>
                <li>Email support available</li>
            </ul>
            <b>✅ Current plan</b>
            </div>
            """, unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            """
            <div class="metric-card">
            <h4>Premium</h4>
            <p><b>$20</b> per year</p>
            <ul>
                <li>Everything in Basic plan</li>
                <li>Add up to 2000 entries per account</li>
                <li>Advanced trend visualisation</li>
                <li>Export data as CSV</li>
                <li>Priority support</li>
            </ul>
            <button style="padding:8px 16px;background:#25a244;color:white;border:none;border-radius:8px;">Go Premium</button>
            </div>
            """, unsafe_allow_html=True
        )

    st.markdown("---")

    # --- Delete Account ---
    st.error("⚠️ Permanently delete your account and all its data.")
    if st.button("🗑️ Delete Account"):
        st.session_state.accounts = [a for a in st.session_state.accounts if a["email"] != st.session_state.user["email"]]
        save_accounts(st.session_state.accounts)
        clear_login()
        st.session_state.logged_in = False
        st.success("Account deleted successfully!")
        st.rerun()

# ----------------- Main App -----------------
with st.sidebar:
    choice = option_menu(
        "Smart Finance",
        ["Dashboard", "Income", "Expenses", "Investment", "Settings", "Logout"],
        icons=["speedometer", "wallet2", "cash-coin", "piggy-bank", "gear", "box-arrow-right"],
        menu_icon="app-indicator",
        default_index=0,
        
    )

if choice == "Dashboard":
    dashboard()
elif choice == "Income":
    income_page()
elif choice == "Expenses":
    expenses_page()
elif choice == "Investment":
    savings_page()
elif choice == "Settings":
    settings_page()
elif choice == "Logout":
    st.session_state.logged_in = False
    st.session_state.user = None
    clear_login()
    st.success("You have been logged out.")

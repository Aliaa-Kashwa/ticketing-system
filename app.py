import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Pro-Heater Support System", layout="wide", page_icon="🎫")

DB_FILE = "database.csv"
ADMIN_PASSWORD = "admin123" # Change this to your preferred password

# --- DATA FUNCTIONS ---
def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["ID", "Timestamp", "Employee Name", "Department", "Issue Category", "Description", "Priority", "Status"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

# --- UI HEADER ---
st.title("🏗️ Pro-Heater Application Support System")
st.markdown("---")

# --- APP TABS ---
tab1, tab2, tab3 = st.tabs(["🆕 Submit Ticket", "📊 Analytics Dashboard", "🔐 Admin Control"])

# --- TAB 1: SUBMIT TICKET ---
with tab1:
    st.header("Submit a Technical Request")
    with st.form("ticket_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            emp_name = st.text_input("Employee Full Name")
            dept = st.selectbox("Department", ["Production", "Quality", "Maintenance", "HR", "Sales", "IT", "Finance"])
        with col2:
            category = st.selectbox("Issue Category", ["Software Bug", "Data Request", "System Access", "Heater Configuration", "Other"])
            priority = st.select_slider("Priority Level", options=["Low", "Medium", "High"])
        
        description = st.text_area("Detailed Description of the Problem")
        submit = st.form_submit_button("Submit Request")

        if submit:
            if emp_name and description:
                df = load_data()
                new_id = len(df) + 1001
                new_data = {
                    "ID": new_id,
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Employee Name": emp_name,
                    "Department": dept,
                    "Issue Category": category,
                    "Description": description,
                    "Priority": priority,
                    "Status": "Pending"
                }
                df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
                save_data(df)
                st.success(f"Ticket #{new_id} has been submitted successfully!")
            else:
                st.error("Please fill in all required fields.")

# --- TAB 2: ANALYTICS ---
with tab2:
    st.header("Support Insights")
    df = load_data()
    if not df.empty:
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Total Tickets", len(df))
        col_m2.metric("Pending Issues", len(df[df['Status'] == 'Pending']))
        col_m3.metric("Resolved Issues", len(df[df['Status'] == 'Resolved']))

        c1, c2 = st.columns(2)
        with c1:
            fig_status = px.pie(df, names='Status', title='Tickets by Status', hole=0.4)
            st.plotly_chart(fig_status)
        with c2:
            fig_dept = px.bar(df['Department'].value_counts(), title='Tickets by Department')
            st.plotly_chart(fig_dept)
    else:
        st.info("No data available yet.")

# --- TAB 3: ADMIN CONTROL ---
with tab3:
    st.header("Admin Management Panel")
    pwd = st.text_input("Enter Admin Password", type="password")
    
    if pwd == ADMIN_PASSWORD:
        st.success("Access Granted")
        df = load_data()
        if not df.empty:
            st.subheader("Manage Active Tickets")
            
            # Update Status Section
            with st.expander("Update Ticket Status"):
                t_id = st.number_input("Enter Ticket ID", min_value=1001, step=1)
                new_status = st.selectbox("New Status", ["Pending", "In Progress", "Resolved", "Cancelled"])
                if st.button("Update Status"):
                    df.loc[df['ID'] == t_id, 'Status'] = new_status
                    save_data(df)
                    st.success(f"Ticket #{t_id} updated to {new_status}")
                    st.rerun()

            st.dataframe(df.sort_values(by="Timestamp", ascending=False), use_container_width=True)
            
            if st.button("Clear All Data (Danger)"):
                if os.path.exists(DB_FILE):
                    os.remove(DB_FILE)
                    st.rerun()
        else:
            st.info("No tickets to manage.")
    elif pwd != "":
        st.error("Incorrect Password")
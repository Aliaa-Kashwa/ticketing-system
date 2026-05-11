import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Ticketing System", layout="wide", page_icon="🎫")

# --- 2. HIDE STREAMLIT STYLE ---
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden; display: none !important;}
            header {visibility: hidden; display: none !important;}
            .stAppDeployButton {display: none !important;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- 3. ONEDRIVE EXCEL CONFIGURATION ---
# تم تعديل المسار بناءً على هيكلة الـ OneDrive الخاصة بكِ
EXCEL_PATH = r"C:\Users\afaisal\OneDrive - GROUPE ATLANTIC\Documents\Ticketing System\Ticketing_System_DB.xlsx"
COLUMNS_LIST = ["ID", "Timestamp", "Employee Name", "Department", "Issue Category", "Description", "Priority", "Status"]

def load_data():
    if not os.path.exists(EXCEL_PATH):
        # إنشاء ملف جديد لو مش موجود
        df = pd.DataFrame(columns=COLUMNS_LIST)
        df.to_excel(EXCEL_PATH, index=False)
        return df
    
    try:
        df = pd.read_excel(EXCEL_PATH)
        # تأكيد أنواع البيانات (Casting)
        if not df.empty:
            df['ID'] = pd.to_numeric(df['ID'], errors='coerce').fillna(0).astype(int)
            df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
        return df
    except Exception as e:
        st.error(f"Error loading Excel from OneDrive: {e}")
        return pd.DataFrame(columns=COLUMNS_LIST)

def save_data(df_to_save):
    try:
        # التأكد من ترتيب الأعمدة قبل الحفظ
        df_to_save = df_to_save[COLUMNS_LIST]
        df_to_save.to_excel(EXCEL_PATH, index=False)
        return True
    except PermissionError:
        st.error("❌ عذراً: ملف الإكسيل مفتوح حالياً. يرجى إغلاقه لتتمكن من حفظ البيانات.")
        return False
    except Exception as e:
        st.error(f"Error saving to OneDrive: {e}")
        return False

# إعدادات الأدمن
ADMIN_PASSWORD = "aliaa123" 

# --- 4. UI HEADER ---
st.title("🏗️ Ticketing System")
st.markdown("---")

# --- 5. APP TABS ---
tab1, tab2, tab3 = st.tabs(["🆕 Submit Ticket", "📊 Analytics Dashboard", "🔐 Admin Control"])

# --- TAB 1: SUBMIT TICKET ---
with tab1:
    st.header("Submit a Technical Request")
    with st.form("ticket_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            emp_name = st.text_input("Employee Name")
            dept = st.selectbox("Department", ["Production", "Quality", "Maintenance", "HR", "Purchasing", "IT", "Finance", "R&D", "CI", "HSE", "Logistics"])
        with col2:
            category = st.selectbox("Issue Category", ["Software Bug", "Data Request", "System Access", "Other"])
            priority = st.select_slider("Priority Level", options=["Low", "Medium", "High"])
        
        description = st.text_area("Detailed Description")
        submit = st.form_submit_button("Submit Request")

        if submit:
            if emp_name and description:
                df = load_data()
                new_id = 1001 if df.empty else int(df['ID'].max()) + 1
                
                new_row = pd.DataFrame([{
                    "ID": int(new_id),
                    "Timestamp": datetime.now(),
                    "Employee Name": emp_name,
                    "Department": dept,
                    "Issue Category": category,
                    "Description": description,
                    "Priority": priority,
                    "Status": "Pending"
                }])
                
                updated_df = pd.concat([df, new_row], ignore_index=True)
                if save_data(updated_df):
                    st.success(f"Ticket #{new_id} saved! ✅")
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
            fig_status = px.pie(df, names='Status', title='Status Overview', hole=0.4)
            st.plotly_chart(fig_status)
        with c2:
            dept_counts = df['Department'].value_counts().reset_index()
            fig_dept = px.bar(dept_counts, x='Department', y='count', title='Tickets per Department')
            st.plotly_chart(fig_dept)
    else:
        st.info("No data found in OneDrive file.")

# --- TAB 3: ADMIN CONTROL ---
with tab3:
    st.header("Admin Management")
    pwd = st.text_input("Password", type="password")
    if pwd == ADMIN_PASSWORD:
        df = load_data()
        if not df.empty:
            t_id = st.number_input("Enter Ticket ID to Update", min_value=1001, step=1)
            new_status = st.selectbox("New Status", ["Pending", "In Progress", "Resolved", "Cancelled"])
            if st.button("Update Status"):
                if t_id in df['ID'].values:
                    df.loc[df['ID'] == t_id, 'Status'] = new_status
                    if save_data(df):
                        st.success("Updated!")
                        st.rerun()
            st.dataframe(df.sort_values(by="ID", ascending=False), use_container_width=True)
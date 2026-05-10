import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Ticketing System", layout="wide", page_icon="🎫")

# --- 2. THE ULTIMATE HIDE (CSS) ---
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden; display: none !important;}
            header {visibility: hidden; display: none !important;}
            div[data-testid="stToolbar"] {display: none !important;}
            div[data-testid="stStatusWidget"] {display: none !important;}
            .stAppDeployButton {display: none !important;}
            [data-testid="stConnectionStatus"] {display: none !important;}
            [data-testid="stDecoration"] {display: none !important;}
            .st-emotion-cache-1kyx601 {display: none !important;} 
            .st-emotion-cache-v609y2 {display: none !important;}
            .block-container {
                padding-top: 1rem;
                padding-bottom: 0rem;
                padding-left: 1rem;
                padding-right: 1rem;
            }
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- 3. GOOGLE SHEETS CONNECTION ---
# ضعي رابط ملفك هنا بين علامتي التنصيص
SHEET_URL = "https://docs.google.com/spreadsheets/d/18aAMNSGmi_AIcQSLPoSroiVt-0C8GgRClOOOmMKhThg/edit?gid=0#gid=0"

conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    # هنا قمنا بإضافة الرابط مباشرة داخل الدالة لتجنب خطأ الـ Secrets
    return conn.read(spreadsheet=SHEET_URL, ttl="0")

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
        
        description = st.text_area("Detailed Description of the Problem")
        submit = st.form_submit_button("Submit Request")

        if submit:
            if emp_name and description:
                df = load_data()
                # توليد ID جديد بناءً على آخر ID موجود
                new_id = 1001 if df.empty else df['ID'].max() + 1
                
                new_data = pd.DataFrame([{
                    "ID": int(new_id),
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Employee Name": emp_name,
                    "Department": dept,
                    "Issue Category": category,
                    "Description": description,
                    "Priority": priority,
                    "Status": "Pending"
                }])
                
                # تحديث شيت جوجل بالبيانات الجديدة
                updated_df = pd.concat([df, new_data], ignore_index=True)
                conn.update(data=updated_df)
                st.success(f"Ticket #{new_id} has been submitted successfully! ✅")
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
            # معالجة البيانات للرسم البياني للأقسام
            dept_counts = df['Department'].value_counts().reset_index()
            dept_counts.columns = ['Department', 'count']
            fig_dept = px.bar(dept_counts, x='Department', y='count', title='Tickets by Department')
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
                    if t_id in df['ID'].values:
                        df.loc[df['ID'] == t_id, 'Status'] = new_status
                        conn.update(data=df)
                        st.success(f"Ticket #{t_id} updated to {new_status}")
                        st.rerun()
                    else:
                        st.error("Ticket ID not found.")

            st.dataframe(df.sort_values(by="Timestamp", ascending=False), use_container_width=True)
            
            # ملاحظة: زر مسح البيانات سيقوم بمسح كل شيء من جوجل شيت
            if st.button("Clear All Data (Danger)"):
                empty_df = pd.DataFrame(columns=["ID", "Timestamp", "Employee Name", "Department", "Issue Category", "Description", "Priority", "Status"])
                conn.update(data=empty_df)
                st.rerun()
        else:
            st.info("No tickets to manage.")
    elif pwd != "":
        st.error("Incorrect Password")
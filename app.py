import streamlit as st
import pandas as pd
from datetime import datetime
import os

# إعدادات الصفحة
st.set_page_config(page_title="Support Ticket System", layout="wide")

# اسم ملف قاعدة البيانات البسيطة
DB_FILE = "tickets.csv"

# دالة لتحميل البيانات
def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["ID", "Date", "Employee", "Department", "Issue", "Priority", "Status"])

# واجهة المستخدم
st.title("🎫 نظام الدعم الفني للموظفين")

# قائمة جانبية لإضافة تذكرة جديدة
with st.sidebar:
    st.header("إضافة طلب دعم جديد")
    with st.form("ticket_form", clear_on_submit=True):
        emp_name = st.text_input("اسم الموظف")
        dept = st.selectbox("القسم", ["HR", "Finance", "Sales", "IT", "Management"])
        issue = st.text_area("وصف المشكلة التقنية")
        priority = st.select_slider("درجة الأهمية", options=["Low", "Medium", "High"])
        submit = st.form_submit_button("إرسال التذكرة")

        if submit:
            df = load_data()
            new_id = len(df) + 1
            new_ticket = {
                "ID": new_id,
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Employee": emp_name,
                "Department": dept,
                "Issue": issue,
                "Priority": priority,
                "Status": "Open"
            }
            df = pd.concat([df, pd.DataFrame([new_ticket])], ignore_index=True)
            df.to_csv(DB_FILE, index=False)
            st.success(f"تم تسجيل التذكرة بنجاح رقم {new_id}")

# عرض التذاكر الحالية في الصفحة الرئيسية
st.header("📋 سجل طلبات الدعم المفتوحة")
df_display = load_data()

if not df_display.empty:
    # فلترة سريعة
    status_filter = st.multiselect("تصفية حسب الحالة", options=["Open", "In Progress", "Closed"], default=["Open", "In Progress"])
    filtered_df = df_display[df_display["Status"].isin(status_filter)]
    
    # عرض الجدول بشكل تفاعلي
    st.dataframe(filtered_df, use_container_width=True)
    
    # تحديث حالة تذكرة
    st.divider()
    st.subheader("تحديث حالة طلب")
    col1, col2 = st.columns(2)
    with col1:
        t_id = st.number_input("رقم التذكرة لتحديثها", min_value=1, step=1)
    with col2:
        new_status = st.selectbox("الحالة الجديدة", ["Open", "In Progress", "Closed"])
    
    if st.button("تحديث"):
        df_display.loc[df_display['ID'] == t_id, 'Status'] = new_status
        df_display.to_csv(DB_FILE, index=False)
        st.rerun()
else:
    st.info("لا توجد تذاكر مسجلة حالياً.")
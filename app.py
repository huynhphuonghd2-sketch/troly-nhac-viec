import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Trợ Lý Nhắc Việc Thông Minh", page_icon="⏰", layout="centered")

st.title("🤖 Trợ Lý Nhắc Việc Cá Nhân (Calendar Edition)")

# Kết nối Google Sheets bằng st-gsheets-connection chuẩn
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        return conn.read(worksheet="Sheet1", ttl="0s")
    except Exception:
        return pd.DataFrame(columns=["ID", "Nội dung", "Ngày", "Giờ", "Trạng thái"])

df = load_data()

with st.form("task_form", clear_on_submit=True):
    task_name = st.text_input("📝 Nội dung công việc cần làm:")
    col1, col2 = st.columns(2)
    with col1:
        task_date = st.date_input("📅 Ngày")
    with col2:
        task_time = st.time_input("⏰ Giờ")
    
    submit = st.form_submit_button("🚀 Lưu Lịch & Tạo Thông Báo Điện Thoại")

if submit:
    if task_name.strip():
        # 1. Lưu vào Google Sheets
        new_id = len(df) + 1 if not df.empty else 1
        new_row = pd.DataFrame([{
            "ID": new_id,
            "Nội dung": task_name,
            "Ngày": str(task_date),
            "Giờ": str(task_time),
            "Trạng thái": "Chưa xong"
        }])
        updated_df = pd.concat([df, new_row], ignore_index=True)
        
        # Cập nhật dữ liệu kèm theo chỉ định worksheet="Sheet1"
        conn.update(worksheet="Sheet1", data=updated_df)
        
        # 2. Tạo link Google Calendar Quick Add
        start_dt = datetime.combine(task_date, task_time)
        start_str = start_dt.strftime("%Y%m%dT%H%M00")
        
        cal_url = f"https://calendar.google.com/calendar/render?action=TEMPLATE&text={task_name}&dates={start_str}/{start_str}&details=Nhắc+nhở+từ+Trợ+Lý+Nhắc+Việc+Cá+Nhân"
        
        st.success("✅ Đã lưu công việc vào Google Sheets thành công!")
        
        # Hiển thị nút bấm đồng bộ lịch
        st.markdown(
            f'<a href="{cal_url}" target="_blank" style="display: inline-block; padding: 0.75em 1em; background-color: #4285F4; color: white; text-decoration: none; border-radius: 4px; font-weight: bold; text-align: center; width: 100%;">📅 Bấm vào đây để đồng bộ lịch báo thức lên Điện Thoại ngay!</a>',
            unsafe_allow_html=True
        )
        st.info("💡 Mẹo: Khi bấm vào nút trên, ứng dụng Lịch trên điện thoại sẽ tự động mở ra, bạn chỉ cần bấm **Lưu** là điện thoại sẽ tự động hẹn giờ báo thức chính xác!")
        
    else:
        st.warning("⚠️ Vui lòng nhập nội dung công việc!")

st.divider()
st.subheader("📋 Danh sách công việc đã lưu")
st.dataframe(df, use_container_width=True)
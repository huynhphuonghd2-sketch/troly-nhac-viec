import streamlit as st
import json
import os
from datetime import datetime

# Cấu hình giao diện tối ưu cho màn hình điện thoại
st.set_page_config(
    page_title="Trợ Lý Của Tôi", 
    page_icon="🤖", 
    layout="centered"
)

DATA_FILE = "my_tasks.json"

def load_tasks():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_tasks(tasks):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=4)

# Giao diện ứng dụng trên điện thoại
st.title("🤖 Trợ Lý Nhắc Việc")
st.caption("Ứng dụng di động cá nhân do bạn tự làm bằng Python")

with st.form("task_form_mobile", clear_on_submit=True):
    # Mẹo: Khi bấm vào ô này trên điện thoại, hãy bấm nút micro trên bàn phím để nói!
    title = st.text_input("📝 Nội dung công việc cần làm:")
    
    col1, col2 = st.columns(2)
    with col1:
        d = st.date_input("📅 Ngày")
    with col2:
        t = st.time_input("⏰ Giờ")
        
    submitted = st.form_submit_button("🚀 Lưu Lịch Nhắc", use_container_width=True)
    if submitted and title:
        task_time_str = f"{d} {t.strftime('%H:%M')}"
        tasks = load_tasks()
        tasks.append({
            "title": title,
            "time": task_time_str,
            "sent": False
        })
        save_tasks(tasks)
        st.success(f"Đã lưu thành công công việc!")

st.divider()
st.subheader("📋 Lịch trình đã lưu")

tasks = load_tasks()
if tasks:
    for task in tasks:
        status = "🔔 Đã xong" if task.get("sent") else "⏳ Đang chờ"
        st.markdown(f"• **{task['title']}**\n  ⏰ _{task['time']}_ | _{status}_")
    
    if st.button("🗑️ Xóa toàn bộ danh sách"):
        save_tasks([])
        st.rerun()
else:
    st.info("Chưa có công việc nào được lên lịch.")
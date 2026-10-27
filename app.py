from datetime import datetime, timedelta
import pytz
from google.oauth2.service_account import Credentials
import gspread
import streamlit as st

# Thiết lập múi giờ Việt Nam (GMT+7)
vietnam_tz = pytz.timezone("Asia/Ho_Chi_Minh")
now_vn = datetime.now(vietnam_tz)

st.set_page_config(
    page_title="Trợ Lý Nhắc Việc", page_icon="📅", layout="centered"
)

st.title("📅 TRỢ LÝ CỦA THẮNG")


# Hàm kết nối Google Sheets bảo mật bằng gspread
@st.cache_resource
def init_connection():
  creds_dict = dict(st.secrets["connections"]["gsheets"])
  scopes = [
      "https://www.googleapis.com/auth/spreadsheets",
      "https://www.googleapis.com/auth/drive",
  ]
  creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
  gc = gspread.authorize(creds)

  spreadsheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
  sheet = gc.open_by_url(spreadsheet_url).sheet1
  return sheet


try:
  sheet = init_connection()
except Exception as e:
  st.error(f"Lỗi kết nối Google Sheets: {e}")
  st.stop()

# Form nhập liệu công việc
st.subheader("📝 Nội dung công việc cần làm:")
task_content = st.text_input(
    "Nhập nội dung công việc",
    label_visibility="collapsed",
    placeholder="Ví dụ: Họp triển khai vận tải...",
)

col1, col2 = st.columns(2)
with col1:
  selected_date = st.date_input("📅 Ngày", value=now_vn.date())
with col2:
  selected_time = st.time_input("⏰ Giờ", value=now_vn.time())

if st.button("🚀 Lưu Lịch & Tạo Thông Báo Điện Thoại", type="primary"):
  if task_content.strip() == "":
    st.warning("Vui lòng nhập nội dung công việc!")
  else:
    try:
      all_records = sheet.get_all_records()
      next_id = len(all_records) + 1

      date_str = selected_date.strftime("%Y-%m-%d")
      time_str = selected_time.strftime("%H:%M:%S")

      # Ghi dòng mới vào Google Sheets
      sheet.append_row([next_id, task_content, date_str, time_str, "Chưa xong"])
      st.success("Đã lưu công việc vào Google Sheets thành công!")

      # Tạo link đồng bộ Google Calendar
      start_dt = vietnam_tz.localize(
          datetime.combine(selected_date, selected_time)
      )
      end_dt = start_dt + timedelta(hours=1)

      start_iso = start_dt.strftime("%Y%m%dT%H%M%S")
      end_iso = end_dt.strftime("%Y%m%dT%H%M%S")

      cal_url = (
          "https://calendar.google.com/calendar/render?action=TEMPLATE"
          f"&text={task_content.replace(' ', '%20')}"
          f"&dates={start_iso}/{end_iso}"
          "&details=Được%20tạo%20tự%20động%20từ%20Trợ%20Lý%20Nhắc%20Việc"
      )

      st.markdown(
          f"### [📅 Bấm vào đây để đồng bộ lịch ngay trên Điện"
          f" Thoại]({cal_url})"
      )

    except Exception as e:
      st.error(f"Đã xảy ra lỗi khi lưu dữ liệu: {e}")

# Hiển thị danh sách công việc đã lưu
st.divider()
st.subheader("📋 Danh sách công việc đã lưu")
try:
  data = sheet.get_all_records()
  if data:
    st.dataframe(data, use_container_width=True)
  else:
    st.info("Chưa có công việc nào được lưu trên Google Sheet.")
except Exception as e:
  st.error(f"Không thể tải danh sách công việc: {e}")
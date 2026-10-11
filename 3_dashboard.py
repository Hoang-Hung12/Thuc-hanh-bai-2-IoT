import streamlit as st
import pandas as pd
from pymongo import MongoClient
import time

# Cấu hình trang
st.set_page_config(page_title="IoT Dashboard - B23DCCN366", layout="wide")
st.title("📊 Giám Sát Dữ Liệu IoT - Bài Thực Hành 2")
st.subheader("Sinh viên: Hoàng Xuân Hưng - B23DCCN366")

# Kết nối MongoDB (sử dụng chuỗi kết nối chuẩn của bạn)
client_db = MongoClient("mongodb+srv://admin:Hung12345@cluster0.75kfu92.mongodb.net/?appName=Cluster0")
db = client_db["iot_database"]

# Khung chứa nội dung tự động cập nhật
placeholder = st.empty()

# Vòng lặp cập nhật dữ liệu Real-time
while True:
    # Lấy 30 bản ghi mới nhất từ database
    cursor = db["sensor_data"].find().sort("timestamp", -1).limit(30)
    df = pd.DataFrame(list(cursor))
    
    with placeholder.container():
        if not df.empty:
            # Đảo ngược dòng thời gian để vẽ đồ thị từ trái sang phải
            df = df.iloc[::-1] 
            
            # Khối 1: Hiển thị 3 chỉ số mới nhất
            col1, col2, col3 = st.columns(3)
            latest = df.iloc[-1]
            col1.metric("Nhiệt độ", f"{latest['temperature']} °C")
            col2.metric("Độ ẩm", f"{latest['humidity']} %")
            col3.metric("Khoảng cách", f"{latest['distance_cm']} cm")
            
            # Khối 2: Vẽ biểu đồ đường
            st.subheader("📈 Biểu đồ thời gian thực")
            st.line_chart(df.set_index("timestamp")[["temperature", "humidity", "distance_cm"]])
            
            # Khối 3: Hiển thị bảng dữ liệu
            st.write("📋 Dữ liệu thô mới nhất:")
            st.dataframe(df.tail(10))
            
    # Dừng 2 giây trước khi tải dữ liệu mới
    time.sleep(2)
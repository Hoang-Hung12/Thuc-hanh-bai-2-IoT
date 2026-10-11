import pandas as pd
from pymongo import MongoClient
from sklearn.preprocessing import MinMaxScaler

# 1. Kết nối MongoDB bằng chuỗi của bạn
client_db = MongoClient("mongodb+srv://admin:Hung12345@cluster0.75kfu92.mongodb.net/?appName=Cluster0")
db = client_db["iot_database"]
collection = db["sensor_data"]

# Đọc dữ liệu từ DB vào Pandas DataFrame
cursor = collection.find()
df = pd.DataFrame(list(cursor))

if not df.empty:
    df.set_index('timestamp', inplace=True)
    df.drop(columns=['_id'], inplace=True, errors='ignore')
    
    print("--- DỮ LIỆU THÔ BAN ĐẦU (5 dòng đầu) ---")
    print(df.head())

    # 2. Làm sạch: Điền giá trị thiếu (Missing values) bằng giá trị ngay trước đó
    df = df.ffill()

    # 3. Lọc nhiễu (Outliers) cho khoảng cách bằng phương pháp khoảng tứ phân vị (IQR)
    Q1 = df['distance_cm'].quantile(0.25)
    Q3 = df['distance_cm'].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    df_clean = df[(df['distance_cm'] >= lower_bound) & (df['distance_cm'] <= upper_bound)].copy()

    # 4. Resampling: Gom nhóm và tính trung bình mỗi 30 giây
    df_resampled = df_clean.resample('30s').mean().dropna()

    # 5. Chuẩn hóa (Min-Max Scaling) đưa các chỉ số về thang đo [0, 1] cho AI dễ học
    scaler = MinMaxScaler()
    columns_to_scale = ['temperature', 'humidity', 'distance_cm']
    df_resampled[columns_to_scale] = scaler.fit_transform(df_resampled[columns_to_scale])

    print("\n--- DỮ LIỆU SAU KHI TIỀN XỬ LÝ (LỌC NHIỄU & CHUẨN HÓA) ---")
    print(df_resampled.head())
    
    # 6. Lưu dữ liệu sạch vào một bảng (collection) mới
    db["sensor_data_cleaned"].insert_many(df_resampled.reset_index().to_dict('records'))
    print("\n[THÀNH CÔNG] Đã lưu dữ liệu sạch vào collection 'sensor_data_cleaned'")
else:
    print("Chưa có dữ liệu trong DB! Hãy để file 1 chạy thêm một lúc.")
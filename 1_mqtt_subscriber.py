import json
import paho.mqtt.client as mqtt
from pymongo import MongoClient
from datetime import datetime

# 1. Kết nối MongoDB

client_db = MongoClient("mongodb+srv://admin:Hung12345@cluster0.75kfu92.mongodb.net/?appName=Cluster0") 
db = client_db["iot_database"]
collection = db["sensor_data"]

# 2. Cấu hình MQTT
MQTT_BROKER = "test.mosquitto.org"
MQTT_PORT = 1883
MQTT_TOPIC = "ptit/b23dccn366/sensors"

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT Broker with result code {rc}")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    try:
        # Nhận chuỗi JSON từ ESP32
        payload = msg.payload.decode("utf-8")
        data = json.loads(payload)
        
        # Thêm timestamp của hệ thống máy chủ (Server timestamp)
        data["timestamp"] = datetime.now()
        
        # Lưu vào MongoDB
        collection.insert_one(data)
        print(f"Đã lưu DB: T={data['temperature']}°C, H={data['humidity']}%, D={data['distance_cm']}cm")
    except Exception as e:
        print("Lỗi tiền xử lý ban đầu:", e)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_forever()
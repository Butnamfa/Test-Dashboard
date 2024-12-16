import pymysql  
import pandas as pd

def get_connection():
    """เชื่อมต่อกับฐานข้อมูล MySQL บน Railway"""
    connection = pymysql.connect(
        host="autorack.proxy.rlwy.net",
        port=25949,
        user="root",
        password="TFjOleWgujKggEAEMLPMgaoUJLxDyJWx",
        database="railway",
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection

# ทดสอบการเชื่อมต่อ
try:
    connection = get_connection()
    print("เชื่อมต่อสำเร็จ")
    connection.close()
except Exception as e:
    print(f"เกิดข้อผิดพลาด: {e}")

def get_data_from_db():
    """ดึงข้อมูลจากฐานข้อมูล"""
    connection = get_connection()
    cursor = connection.cursor()

    # คำสั่ง SQL ที่ใช้ดึงข้อมูล
    query = """
    SELECT `Menu`, `Order Time`, `Serve Time`, `Price`, `Category`, 
           `Kitchen Staff`, `Drinks Staff`, `Day Of Week`
    FROM test_data;
    """
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    connection.close()

    # แปลงข้อมูลเป็น DataFrame
    df = pd.DataFrame(result)
    df.columns = ["Menu", "Order Time", "Serve Time", "Price", "Category", 
                  "Kitchen Staff", "Drinks Staff", "Day Of Week"]

    # แปลงเวลาเป็น datetime
    df['Order Time'] = pd.to_datetime(df['Order Time'], errors='coerce')
    df['Serve Time'] = pd.to_datetime(df['Serve Time'], errors='coerce')

    # คำนวณเวลารออาหาร
    df['Wait Time'] = (df['Serve Time'] - df['Order Time']).dt.total_seconds() / 60
    
    df = df.dropna(subset=['Wait Time', 'Menu'])

    # คำนวณยอดขายเมนูยอดนิยม
    menu_sales = df.groupby('Menu').size().reset_index(name='Order Count')

    # เวลารออาหารเฉลี่ยตามช่วงเวลา
    avg_wait_time_by_hour = df.groupby(df['Order Time'].dt.hour)['Wait Time'].mean()

    # เมนูยอดนิยมตามช่วงเวลา
    top_menu_by_hour = df.groupby([df['Order Time'].dt.hour, 'Menu']).size().reset_index(name='Order Count')
    top_menu_by_hour = top_menu_by_hour.loc[top_menu_by_hour.groupby('Order Time')['Order Count'].idxmax()]

    # การใช้งานพนักงานในครัวและบาร์
    staff_workload = df.groupby(df['Order Time'].dt.hour).agg({
        'Kitchen Staff': 'sum',
        'Drinks Staff': 'sum'
    }).reset_index()

    return df, avg_wait_time_by_hour, menu_sales, top_menu_by_hour, staff_workload

import streamlit as st
import matplotlib.pyplot as plt
from query import get_data_from_db


st.set_page_config(layout="wide")
st.title("Restaurant Analytics Dashboard")

# ดึงข้อมูลจากฐานข้อมูล
menu_data, avg_wait_time_by_hour, menu_sales, top_menu_by_hour, staff_workload = get_data_from_db()

if menu_data is not None:
    row1_col1, row1_col2 = st.columns(2)  
    with row1_col1:
        # กราฟ 1: Top Selling Menu Items
        st.subheader("Top Selling Menu Items")
        st.bar_chart(menu_sales.set_index('Menu')['Order Count'], use_container_width=True) 

    with row1_col2:
        # กราฟ 2: Staff vs. Serve Time
        st.subheader("Staff vs. Serve Time")
        fig1, ax1 = plt.subplots(figsize=(12, 6)) 
        ax1.scatter(menu_data['Kitchen Staff'], menu_data['Wait Time'], label='Kitchen Staff', color='blue')
        ax1.scatter(menu_data['Drinks Staff'], menu_data['Wait Time'], label='Drinks Staff', color='green')
        ax1.set_xlabel('Number of Staff')
        ax1.set_ylabel('Wait Time (minutes)')
        ax1.set_title('Staff vs. Serve Time')
        ax1.legend()
        st.pyplot(fig1)

    row2_col1, row2_col2 = st.columns(2)
    with row2_col1:
        # กราฟ 3: Staff Workload 
        st.subheader("Staff Workload")
        fig2, ax2 = plt.subplots(figsize=(12, 6))
        ax2.bar(staff_workload['Order Time'], staff_workload['Kitchen Staff'], label='Kitchen Staff', color='blue')
        ax2.bar(staff_workload['Order Time'], staff_workload['Drinks Staff'], label='Drinks Staff', color='green',
                bottom=staff_workload['Kitchen Staff'])
        ax2.set_title('Staff Workload Analysis')
        ax2.set_xlabel('Hour of Day')
        ax2.set_ylabel('Number of Staff')
        ax2.legend()
        st.pyplot(fig2)

    with row2_col2:
        # กราฟ 4: Order Pattern by Day and Hour
        st.subheader("Order Pattern by Day and Hour")
        order_pattern = menu_data.groupby([menu_data['Day Of Week'], menu_data['Order Time'].dt.hour]).size().unstack()
        st.write(order_pattern.style.background_gradient(cmap='coolwarm'))

    row3_col1, row3_col2 = st.columns(2)
    with row3_col1:
        # กราฟ 5: Order Pattern Over Time
        st.subheader("Order Pattern Over Time")
        order_pattern_time = menu_data.groupby(menu_data['Order Time'].dt.date).size()
        st.line_chart(order_pattern_time, use_container_width=True)

    with row3_col2:
        # กราฟ 6: Serve Time Analysis by Menu 
        st.subheader("Serve Time by Menu")
        if 'Menu' in menu_data.columns and 'Wait Time' in menu_data.columns:
            avg_wait_time_per_menu = menu_data.groupby('Menu')['Wait Time'].mean().sort_values()
            st.line_chart(avg_wait_time_per_menu, use_container_width=True)
        else:
            st.warning("Required columns 'Menu' and 'Wait Time' are missing in the dataset.")

else:
    st.error("Failed to retrieve data from the database.")

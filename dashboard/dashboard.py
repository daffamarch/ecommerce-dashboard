import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


st.set_page_config(page_title="E-Commerce Performance Dashboard", layout="wide")

st.title("📊 E-Commerce Business Performance Dashboard")
st.markdown("---")


try:
    df = pd.read_csv("main_data.csv")
except FileNotFoundError:
    try:
        df = pd.read_csv("dashboard/main_data.csv")
    except Exception:
        st.error("❌ Berkas 'main_data.csv' tidak ditemukan! Pastikan file berada di direktori yang tepat.")
        st.stop()


df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])

min_date = df['order_purchase_timestamp'].min().date()
max_date = df['order_purchase_timestamp'].max().date()


with st.sidebar:
    st.markdown("## 🛒 **E-Commerce Menu**")
    st.header("Filter Rentang Waktu")
    
    date_range = st.date_input(
        label='Pilih Alokasi Tanggal',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
    
    
    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        start_date, end_date = date_range
    elif isinstance(date_range, (list, tuple)) and len(date_range) == 1:
        start_date = end_date = date_range[0]
    else:
        start_date = end_date = min_date


filtered_df = df[(df['order_purchase_timestamp'].dt.date >= start_date) & 
                 (df['order_purchase_timestamp'].dt.date <= end_date)]


col1, col2, col3 = st.columns(3)
with col1:
    total_orders = filtered_df['order_id'].nunique()
    st.metric(label="🛍️ Total Orders", value=f"{total_orders:,}")
with col2:
    total_revenue = filtered_df['price'].sum()
    st.metric(label="💰 Total Revenue", value=f"${total_revenue:,.2f}")
with col3:
    total_customers = filtered_df['customer_unique_id'].nunique()
    st.metric(label="👥 Active Customers", value=f"{total_customers:,}")

st.markdown("---")

tab1, tab2 = st.tabs(["📈 Performa Produk (2017)", "👥 Analisis Segmentasi RFM (Q1 2018)"])


with tab1:
    st.subheader("Kategori Produk Pencetak Revenue Terbesar & Terkecil")
    
    
    df_2017 = df[df['order_purchase_timestamp'].dt.year == 2017]
    
    if not df_2017.empty:
        product_revenue = df_2017.groupby('product_category_name_english')['price'].sum().reset_index()
        product_revenue = product_revenue.sort_values(by='price', ascending=False)
        
        
        fig, ax = plt.subplots(nrows=2, ncols=1, figsize=(12, 10))
        
        
        sns.barplot(
            x="price", 
            y="product_category_name_english", 
            data=product_revenue.head(5), 
            hue="product_category_name_english",
            palette="Blues_r", 
            legend=False,
            ax=ax[0]
        )
        ax[0].set_title("Top 5 Kategori Produk Berdasarkan Revenue (2017)", fontsize=14, fontweight="bold", pad=10)
        ax[0].set_xlabel("Total Pendapatan ($)", fontsize=11)
        ax[0].set_ylabel("Kategori Produk", fontsize=11)
        
        
        sns.barplot(
            x="price", 
            y="product_category_name_english", 
            data=product_revenue.tail(5), 
            hue="product_category_name_english",
            palette="Reds", 
            legend=False,
            ax=ax[1]
        )
        ax[1].set_title("Bottom 5 Kategori Produk Berdasarkan Revenue (2017)", fontsize=14, fontweight="bold", pad=10)
        ax[1].set_xlabel("Total Pendapatan ($)", fontsize=11)
        ax[1].set_ylabel("Kategori Produk", fontsize=11)
        
        plt.tight_layout()
        st.pyplot(fig)
    else:
        st.warning("⚠️ Data transaksi untuk tahun 2017 tidak ditemukan.")


with tab2:
    st.subheader("Karakteristik Loyalitas Pelanggan (Analisis Lanjutan)")
    
    
    df_q1_2018 = df[(df['order_purchase_timestamp'] >= '2018-01-01') & 
                    (df['order_purchase_timestamp'] <= '2018-03-31 23:59:59')]
    
    if not df_q1_2018.empty:
        rfm_freq = df_q1_2018.groupby('customer_unique_id')['order_id'].nunique().reset_index()
        rfm_freq.columns = ['customer_id', 'frequency']
        
        
        def segment_customer(freq):
            if freq > 2: 
                return "Top Loyal Customer"
            elif freq == 2: 
                return "Repeat Customer"
            else: 
                return "One-Time Buyer"
            
        rfm_freq['customer_segment'] = rfm_freq['frequency'].apply(segment_customer)
        segment_counts = rfm_freq['customer_segment'].value_counts().reset_index()
        segment_counts.columns = ['Segmen_Pelanggan', 'Jumlah_Pelanggan']
        segment_counts['Persentase (%)'] = (segment_counts['Jumlah_Pelanggan'] / segment_counts['Jumlah_Pelanggan'].sum()) * 100
        
        fig, ax = plt.subplots(figsize=(10, 4))
        
        sns.barplot(
            x='Persentase (%)', 
            y='Segmen_Pelanggan', 
            data=segment_counts, 
            hue='Segmen_Pelanggan',
            palette="magma", 
            legend=False,
            ax=ax
        )
        
        
        for p in ax.patches:
            width = p.get_width()
            if width > 0:
                ax.text(width + 1.5, p.get_y() + p.get_height() / 2, f'{width:.2f}%', 
                        ha='left', va='center', fontsize=10, fontweight='bold')
                    
        ax.set_title("Proporsi Segmentasi Loyalitas Pelanggan (Q1 2018)", fontsize=12, fontweight="bold")
        ax.set_xlabel("Persentase dari Total Populasi (%)")
        ax.set_ylabel("Segmen Bisnis")
        ax.set_xlim(0, 115) 
        
        plt.tight_layout()
        st.pyplot(fig)
    else:
        st.warning("⚠️ Data transaksi untuk periode Q1 2018 tidak ditemukan.")

st.markdown("---")
st.caption("Copyright © 2026 | Muhammad Daffa Marchdiansyah - Proyek Final Analisis Data E-Commerce")
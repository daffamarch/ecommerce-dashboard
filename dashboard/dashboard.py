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
        st.error(" Berkas 'main_data.csv' tidak ditemukan! Pastikan file berada di direktori yang tepat.")
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


tab1, tab2, tab3 = st.tabs(["📈 Performa Produk", "👥 Analisis Eksplorasi Pertanyaan 2", "📊 Segmentasi Lanjutan (RFM)"])


with tab1:
    st.subheader("Kategori Produk Pencetak Revenue Terbesar & Terkecil")
    
    df_2017 = filtered_df[filtered_df['order_purchase_timestamp'].dt.year == 2017]
    
    if not df_2017.empty:
        product_revenue_2017 = df_2017.groupby('product_category_name_english')['price'].sum().reset_index()
        product_revenue_2017 = product_revenue_2017[product_revenue_2017['price'] > 50000]
        product_revenue_2017 = product_revenue_2017.sort_values(by='price', ascending=False)
        
        top_5 = product_revenue_2017.head(5)
        bottom_5 = product_revenue_2017.tail(5)
        
        fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(20, 6))
        colors_top = ["#003f5c", "#7f7f7f", "#7f7f7f", "#7f7f7f", "#7f7f7f"]
        colors_bottom = ["#7f7f7f", "#7f7f7f", "#7f7f7f", "#7f7f7f", "#d45087"]
        
        sns.barplot(x="price", y="product_category_name_english", data=top_5, palette=colors_top, ax=ax[0])
        ax[0].set_title("Top 5 Kategori Produk Berdasarkan Total Revenue (> $50,000 di Tahun 2017)", fontsize=13, fontweight="bold")
        ax[0].set_xlabel("Total Pendapatan ($)", fontsize=11)
        ax[0].set_ylabel("Kategori Produk (English)", fontsize=11)
        
        sns.barplot(x="price", y="product_category_name_english", data=bottom_5, palette=colors_bottom, ax=ax[1])
        ax[1].set_title("Bottom 5 Kategori Produk Berdasarkan Total Revenue (Tahun 2017)", fontsize=13, fontweight="bold")
        ax[1].set_xlabel("Total Pendapatan ($)", fontsize=11)
        ax[1].set_ylabel("")
        ax[1].invert_xaxis()
        
        plt.tight_layout()
        st.pyplot(fig)
    else:
        st.warning("⚠️ Data transaksi tahun 2017 tidak ditemukan pada rentang filter saat ini.")

with tab2:
    st.subheader("Distribusi Frekuensi Belanja & Peta Spasial Geografis Demografi")
    
    df_q1_2018 = filtered_df[(filtered_df['order_purchase_timestamp'] >= '2018-01-01') & 
                             (filtered_df['order_purchase_timestamp'] <= '2018-03-31 23:59:59')]
    
    if not df_q1_2018.empty:
        rfm_freq = df_q1_2018.groupby('customer_unique_id')['order_id'].nunique().reset_index()
        rfm_freq.columns = ['customer_unique_id', 'frequency']
        
        frequency_counts = rfm_freq['frequency'].value_counts().reset_index()
        frequency_counts.columns = ['Jumlah_Transaksi', 'Jumlah_Pelanggan']
        
        fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(22, 7))
        
    
        sns.barplot(x='Jumlah_Transaksi', y='Jumlah_Pelanggan', data=frequency_counts, color='#003f5c', ax=ax[0])
        ax[0].set_yscale('log')
        ax[0].set_title("Distribusi Volume Frekuensi Belanja Pelanggan (Q1 2018)", fontsize=13, fontweight="bold")
        ax[0].set_xlabel("Frekuensi Transaksi yang Dilakukan (Kali)", fontsize=11)
        ax[0].set_ylabel("Jumlah Konsumen Unik (Skala Log)", fontsize=11)
        ax[0].grid(axis='y', linestyle='--', alpha=0.5)
        
        
        if 'geolocation_lng' in df_q1_2018.columns and 'geolocation_lat' in df_q1_2018.columns:
            
            geo_sample = df_q1_2018.dropna(subset=['geolocation_lng', 'geolocation_lat'])
            if len(geo_sample) > 3500:
                geo_sample = geo_sample.sample(n=3500, random_state=42)
                
            scatter = ax[1].scatter(geo_sample['geolocation_lng'], geo_sample['geolocation_lat'], 
                                    c=geo_sample['customer_zip_code_prefix'], cmap='coolwarm', alpha=0.5, s=10)
            
            ax[1].set_xlim(-70, -35)
            ax[1].set_ylim(-30, 5)
            ax[1].set_title("Peta Spasial Distribusi Lokasi Geografis Demografi Pelanggan (Geospatial Insights)", fontsize=13, fontweight="bold")
            ax[1].set_xlabel("Longitude (Garis Bujur)", fontsize=11)
            ax[1].set_ylabel("Latitude (Garis Lintang)", fontsize=11)
            fig.colorbar(scatter, ax=ax[1], label='Grup Klaster Wilayah (Zip Code Prefix)')
        else:
            ax[1].text(0.5, 0.5, "Kolom koordinat belum masuk. Selesaikan Langkah 1 di Colab dahulu.", ha='center', va='center')
            
        plt.tight_layout()
        st.pyplot(fig)
    else:
        st.warning("⚠️ Data transaksi Q1 2018 tidak ditemukan pada rentang filter saat ini.")


with tab3:
    st.subheader("Karakteristik Loyalitas Pelanggan (Analisis Lanjutan)")
    
    df_q1_rfm = filtered_df[(filtered_df['order_purchase_timestamp'] >= '2018-01-01') & 
                            (filtered_df['order_purchase_timestamp'] <= '2018-03-31 23:59:59')]
    
    if not df_q1_rfm.empty:
        rfm_freq = df_q1_rfm.groupby('customer_unique_id')['order_id'].nunique().reset_index()
        rfm_freq.columns = ['customer_unique_id', 'frequency']
        
        def segment_customer(freq):
            if freq > 2: return "Top Loyal Customer"
            elif freq == 2: return "Repeat Customer"
            else: return "One-Time Buyer"
            
        rfm_freq['customer_segment'] = rfm_freq['frequency'].apply(segment_customer)
        segment_counts = rfm_freq['customer_segment'].value_counts().reset_index()
        segment_counts.columns = ['Segmen_Pelanggan', 'Jumlah_Pelanggan']
        
        segment_counts['Segmen_Pelanggan'] = pd.Categorical(
            segment_counts['Segmen_Pelanggan'], 
            categories=["One-Time Buyer", "Repeat Customer", "Top Loyal Customer"], 
            ordered=True
        )
        segment_counts = segment_counts.sort_values('Segmen_Pelanggan')
        
        fig, ax = plt.subplots(figsize=(12, 5))
        sns.barplot(x='Jumlah_Pelanggan', y='Segmen_Pelanggan', data=segment_counts, palette=["#003f5c", "#bc5090", "#ffa600"], ax=ax)
        ax.set_xscale('log') 
        
        total_pop = segment_counts['Jumlah_Pelanggan'].sum()
        for p in ax.patches:
            width = p.get_width()
            if width > 0:
                calc_pct = (width / total_pop) * 100
                ax.text(width + (width * 0.1), p.get_y() + p.get_height() / 2, f'{calc_pct:.2f}%', 
                        ha='left', va='center', fontsize=11, fontweight='bold')
                    
        ax.set_title("Distribusi Klaster Karakteristik Loyalitas Pelanggan (Skala Log)", fontsize=14, fontweight="bold", pad=15)
        ax.set_xlabel("Jumlah Konsumen Unik (Log Scale)", fontsize=12)
        ax.set_ylabel("Segmen Loyalitas Bisnis", fontsize=12)
        ax.tick_params(axis='both', labelsize=11)
        
        plt.tight_layout()
        st.pyplot(fig)
    else:
        st.warning("⚠️ Data tidak ditemukan pada rentang filter saat ini.")

st.markdown("---")
st.caption("Copyright © 2026 | Muhammad Daffa Marchdiansyah - Proyek Final Analisis Data E-Commerce")
import pandas as pd
import psycopg2
import matplotlib.pyplot as plt
import seaborn as sns

# veritabanı baglanti bilgileri

db_config = {
    "dbname": "your_db_name",
    "user": "your_username",
    "password": "your_password",
    "host": "localhost"
}

def run_abc_analysis():
    try:
        # veritabani baglantisi
        conn = psycopg2.connect(**db_config)

        # urun bazli ciro sorgusu
        query = """
            select 
                p.name_tr as urun_adi, 
                sum(oi.quantity * oi.unit_price) as toplam_ciro
            from order_items oi
            join products p on oi.product_id = p.id
            group by p.name_tr
            order by toplam_ciro desc
        """

        # veriyi dataframe'e aktarma
        df = pd.read_sql_query(query, conn)

        # abc analizi hesaplamalari
        toplam_gelir = df['toplam_ciro'].sum()
        df['yuzde_pay'] = (df['toplam_ciro'] / toplam_gelir) * 100
        df['kumulatif_yuzde'] = df['yuzde_pay'].cumsum()

        # segmentasyon siniflandirmasi
        def abc_segment (x):
            if x <= 80: return 'a (kritik)'
            elif x <= 95: return 'b (orta)'
            else: return 'c (dusuk)'

        df['segment'] = df['kumulatif_yuzde'].apply(abc_segment)

        # sonuclari terminale yazdirma
        print("abc analizi sonuclari listeleniyor...")
        print(df[['urun_adi', 'toplam_ciro', 'kumulatif_yuzde', 'segment']])

        # görselleştirme ayarları
        sns.set_theme(style="whitegrid")
        fig, ax1 = plt.subplots(figsize=(12, 6))

        # ciro bar grafigi
        ax1.set_title('abc analizi: urun cirolari ve kumulatif toplam', fontsize=14)
        sns.barplot(x='urun_adi', y='toplam_ciro', data=df, ax=ax1, hue='urun_adi', palette='viridis', legend=False)
        ax1.set_ylabel('toplam ciro', fontsize=10)
        ax1.set_xlabel('urunler', fontsize=10)
        plt.xticks(rotation=45, ha='right')

        # kumulatif yuzde cizgi grafigi
        ax2 = ax1.twinx()
        sns.lineplot(x='urun_adi', y='kumulatif_yuzde', data=df, marker='o', color='red', ax=ax2, linewidth=2)
        ax2.set_ylabel('kumulatif yuzde (%)', fontsize=10)
        ax2.set_ylim(0, 110)

        # pareto sinir cizgisi (%80)
        ax2.axhline(80, color='orange', linestyle='--')

        plt.tight_layout()
        plt.show()

        conn.close()

    except Exception as e:
        print(f"hata olustu: {e}")

if __name__ == "__main__":
    run_abc_analysis()
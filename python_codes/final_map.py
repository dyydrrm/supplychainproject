import psycopg2
import folium
from folium.plugins import HeatMap

# baglanti bilgileri
db_config = {
    "dbname": "supplychain_db",
    "user": "postgres",
    "password": "your_password",
    "host": "localhost"
}


def harita_yap():
    try:
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()

        # cografi gelir analizi sorgusu
        cur.execute("""
                    select a.city, st_y(a.geom::geometry), st_x(a.geom::geometry), sum(o.total_amount)
                    from orders o
                             join addresses a on o.shipping_address_id = a.id
                    where a.geom is not null
                    group by a.city, a.geom;
                    """)

        data = cur.fetchall()
        m = folium.Map(location=[45, 35], zoom_start=4, tiles='cartodb dark_matter')
        gelir_verisi = []

        for city, lat, lon, gelir in data:
            gelir_verisi.append([lat, lon, float(gelir)])

            # sehir isaretleyici
            folium.CircleMarker(
                location=[lat, lon],
                radius=5,
                popup=f"{city}: ${gelir:,.2f}",
                color='cyan',
                fill=True
            ).add_to(m)

        # isi haritasi katmani
        HeatMap(gelir_verisi).add_to(m)

        m.save("stratejik_harita.html")
        print("islem tamam: harita olusturuldu.")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"hata: {e}")


if __name__ == "__main__":
    harita_yap()
import psycopg2
import folium
from folium.plugins import HeatMap

# veritabani baglanti bilgileri
# not: guvenlik nedeniyle gercek sifreler kaldirilmistir.
db_config = {
    "dbname": "your_db_name",
    "user": "your_username",
    "password": "your_password",
    "host": "localhost"
}

def generate_supply_chain_map():
    try:
        # veritabani baglantisi
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()

        # sehir bazli koordinat ve yogunluk verilerinin cekilmesi
        # st_y: enlem (lat), st_x: boylam (lon)
        query = """
            select city, st_y(geom::geometry), st_x(geom::geometry), count(*)
            from addresses
            where geom is not null
            group by city, geom;
        """
        cur.execute(query)
        data = cur.fetchall()

        # harita objesinin olusturulmasi (dunya merkezli baslangic)
        m = folium.Map(location=[45, 35], zoom_start=4, tiles='CartoDB positron')

        # verilerin haritaya islenmesi
        heat_data = []
        for city, lat, lon, count in data:
            # sehirler icin isaretleyici (marker) eklenmesi
            folium.CircleMarker(
                location=[lat, lon],
                radius=5,
                popup=f"{city}: {count} adres",
                color='crimson',
                fill=True
            ).add_to(m)

            # isi haritasi veri listesinin doldurulmasi
            heat_data.append([lat, lon, count])

        # isi haritasi (heatmap) katmaninin eklenmesi
        HeatMap(heat_data).add_to(m)

        # haritanin html olarak kaydedilmesi
        output_file = "supply_chain_heatmap.html"
        m.save(output_file)
        print(f"harita basariyla olusturuldu: {output_file}")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"hata: {e}")

if __name__ == "__main__":
    generate_supply_chain_map()
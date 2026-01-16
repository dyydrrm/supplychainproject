import psycopg2

# baglanti bilgileri
db_config = {
    "dbname": "supplychain_db",
    "user": "postgres",
    "password": "your_password",
    "host": "localhost"
}

def kar_analizi_yap():
    try:
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()

        # gelir - kargo maliyeti = net kar hesabi
        # istanbul merkez koordinatlari: 28.97, 41.00
        cur.execute("""
            select 
                a.country, 
                sum(o.total_amount) as gelir,
                sum((st_distance(a.geom, st_setsrid(st_makepoint(28.97, 41.00), 4326)::geography) / 1000) * 0.5) as kargo,
                sum(o.total_amount) - sum((st_distance(a.geom, st_setsrid(st_makepoint(28.97, 41.00), 4326)::geography) / 1000) * 0.5) as net_kar
            from orders o
            join addresses a on o.shipping_address_id = a.id
            where a.geom is not null
            group by a.country
            order by net_kar desc;
        """)

        print("ülke bazlı net kâr raporu:")
        for country, gelir, kargo, kar in cur.fetchall():
            gelir = gelir or 0
            print(f"{country:12} | gelir: {gelir:9.2f}$ | kargo: {kargo:9.2f}$ | net kâr: {kar:9.2f}$")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"hata: {e}")

if __name__ == "__main__":
    kar_analizi_yap()
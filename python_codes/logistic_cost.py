import psycopg2

# baglanti bilgileri
db_config = {
    "dbname": "supplychain_db",
    "user": "postgres",
    "password": "your_password",
    "host": "localhost"
}

def lojistik_raporu_sun():
    try:
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()

        # istanbul merkezli mesafe ve maliyet analizi
        # 28.97, 41.00 -> istanbul koordinatlari
        cur.execute("""
            select 
                country, 
                avg(st_distance(geom, st_setsrid(st_makepoint(28.97, 41.00), 4326)::geography) / 1000) as mesafe,
                sum((st_distance(geom, st_setsrid(st_makepoint(28.97, 41.00), 4326)::geography) / 1000) * 0.5) as maliyet
            from addresses 
            where geom is not null
            group by country
            order by maliyet desc;
        """)

        print("ülke bazlı lojistik maliyetleri:")
        for country, dist, cost in cur.fetchall():
            print(f"{country:10} | {dist:7.2f} km | {cost:9.2f} $")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"hata: {e}")

if __name__ == "__main__":
    lojistik_raporu_sun()

import psycopg2

# baglanti bilgileri
db_config = {
    "dbname": "supplychain_db",
    "user": "postgres",
    "password": "your_password",
    "host": "localhost"
}


def fatura_raporu_sun():
    try:
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()

        # urun bedeli + kargo maliyeti = toplam tahsilat
        # istanbul merkez: 28.97, 41.00
        cur.execute("""
                    select o.id as no, 
                a.city, 
                o.total_amount as urun, 
                (st_distance(a.geom, st_setsrid(st_makepoint(28.97, 41.00), 4326)::geography) / 1000) * 0.5 as kargo,
                o.total_amount + ((st_distance(a.geom, st_setsrid(st_makepoint(28.97, 41.00), 4326)::geography) / 1000) * 0.5) as toplam
                    from orders o
                        join addresses a
                    on o.shipping_address_id = a.id
                    where a.geom is not null
                    order by toplam desc limit 20;
                    """)

        print("sipariş bazlı fatura dökümü (ilk 20):")
        print(f"{'no':<5} | {'şehir':<15} | {'ürün':<10} | {'kargo':<10} | {'toplam'}")

        for no, city, urun, kargo, toplam in cur.fetchall():
            print(f"{no:<5} | {city:<15} | {urun:10.2f}$ | {kargo:10.2f}$ | {toplam:10.2f}$")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"hata: {e}")


if __name__ == "__main__":
    fatura_raporu_sun()
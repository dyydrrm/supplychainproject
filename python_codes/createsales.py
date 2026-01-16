import psycopg2
from faker import Faker
import random
from datetime import datetime, timedelta

# veritabani baglanti bilgileri
db_config = {
    "dbname": "your_db_name",
    "user": "your_username",
    "password": "your_password",
    "host": "localhost",
    "port": "5432"
}

fake_tr = Faker('tr_TR')
fake_en = Faker('en_US')
fake_ru = Faker('ru_RU')


def get_connection():
    return psycopg2.connect(**db_config)


def seed_sales():
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        print("musteri verileri olusturuluyor...")

        countries = [
            ('Turkey', 'TR', fake_tr),
            ('USA', 'EN', fake_en),
            ('Russia', 'RU', fake_ru)
        ]

        customer_ids = []

        # 200 musteri olusturma
        for i in range(200):
            country_name, lang_code, f = random.choice(countries)
            fname = f.first_name()
            lname = f.last_name()

            # musteriler tablosuna ekleme
            cur.execute("""
                        insert into customers (first_name, last_name, preferred_lang)
                        values (%s, %s, %s) returning id
                        """, (fname, lname, lang_code))
            c_id = cur.fetchone()[0]
            customer_ids.append(c_id)

            # kontaklar tablosuna ekleme - polimorfik yapi
            cur.execute("""
                        insert into contacts (owner_id, owner_type, contact_type, contact_value, email, phone, address,
                                              country, is_primary)
                        values (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            c_id,
                            'Customer',
                            'Email',
                            f.email(),
                            f.email(),
                            f.phone_number(),
                            f.address().replace('\n', ' '),
                            country_name,
                            True
                        ))

            # adresler tablosuna ekleme
            cur.execute("""
                        insert into addresses (owner_id, owner_type, title, full_address, city, state, country,
                                               postal_code)
                        values (%s, %s, %s, %s, %s, %s, %s, %s) returning id
                        """, (
                            c_id,
                            'Customer',
                            'Home',
                            f.address().replace('\n', ', '),
                            f.city(),
                            f.state() if country_name == 'USA' else f.city(),
                            country_name,
                            f.postcode()
                        ))

        # urun listesini kontrol etme
        cur.execute("select id, price from products")
        products = cur.fetchall()

        if not products:
            print("hata: urun bulunamadi. once urun verileri yuklenmeli.")
            return

        print("siparis verileri olusturuluyor...")

        # 1000 siparis olusturma
        for _ in range(1000):
            customer_id = random.choice(customer_ids)

            # musteri adresini sorgulama
            cur.execute("select id from addresses where owner_id = %s and owner_type = 'Customer' limit 1",
                        (customer_id,))
            address_result = cur.fetchone()

            if not address_result:
                continue

            shipping_address_id = address_result[0]

            days_ago = random.randint(0, 365)
            order_date = datetime.now() - timedelta(days=days_ago)

            cur.execute("""
                        insert into orders (customer_id, shipping_address_id, order_date, status, total_amount)
                        values (%s, %s, %s, %s, 0) returning id
                        """, (customer_id, shipping_address_id, order_date, 'Completed'))
            order_id = cur.fetchone()[0]

            order_total = 0
            items_count = random.randint(1, 3)
            sampled_products = random.sample(products, min(items_count, len(products)))

            for p_id, p_price in sampled_products:
                qty = random.randint(1, 2)
                line_total = p_price * qty
                order_total += line_total

                cur.execute("""
                            insert into order_items (order_id, product_id, quantity, unit_price)
                            values (%s, %s, %s, %s)
                            """, (order_id, p_id, qty, p_price))

                # stok guncelleme
                cur.execute("update inventory set quantity = quantity - %s where product_id = %s", (qty, p_id))

            cur.execute("update orders set total_amount = %s where id = %s", (order_total, order_id))

        conn.commit()
        print(f"satis verileri basariyla yuklendi: {len(customer_ids)} musteri ve 1000 siparis.")

    except Exception as e:
        print(f"hata: {e}")
        if conn: conn.rollback()
    finally:
        if conn:
            cur.close()
            conn.close()


if __name__ == "__main__":
    seed_sales()
import psycopg2
from faker import Faker
import random
import re

# veritabani baglanti bilgileri
# kendi veritabani bilgilerinizle guncelleyiniz.

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


def create_slug(text):
    text = text.lower()
    text = re.sub(r'\s+', '-', text)
    return re.sub(r'[^\w\-]', '', text).strip('-')


# sektor bazli fiyat ve agirlik mantigi
sector_logic = {
    'Electronics': {'price': (1000, 50000), 'weight': (0.2, 15.0)},
    'Fashion & Textile': {'price': (100, 3000), 'weight': (0.1, 2.0)},
    'Home & Furniture': {'price': (500, 20000), 'weight': (1.0, 80.0)},
    'Food & Market': {'price': (10, 500), 'weight': (0.1, 5.0)},
    'Cosmetics': {'price': (50, 2500), 'weight': (0.05, 1.0)}
}

# kategori hiyerarsisi
data_tree = {
    ('Elektronik', 'Electronics', 'Электроника'): [
        ('Akıllı Telefon', 'Smartphone', 'Смартфон'),
        ('Dizüstü Bilgisayar', 'Laptop', 'Ноутбук'),
        ('Kulaklık', 'Headphones', 'Наушники')
    ],
    ('Moda & Tekstil', 'Fashion & Textile', 'Мода и текстиль'): [
        ('Erkek Giyim', 'Men Clothing', 'Мужская одежда'),
        ('Kadın Giyim', 'Women Clothing', 'Женская одежда')
    ]
}


def seed_database():
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        # depolarin olusturulmasi
        warehouses_to_add = [
            ('WH-01', 'Istanbul Ana Depo', 'Istanbul Main', 'Стамбул Главный'),
            ('WH-02', 'Moskova Dagitim', 'Moscow Dist.', 'Москва Распр.'),
            ('WH-03', 'Londra Bolge', 'London Regional', 'Лонdon Регион.')
        ]

        warehouse_ids = []
        for code, tr, en, ru in warehouses_to_add:
            cur.execute("""
                        insert into warehouses (warehouse_code, name_tr, name_en, name_ru)
                        values (%s, %s, %s, %s) on conflict (warehouse_code) do
                        update set name_tr = excluded.name_tr
                            returning id
                        """, (code, tr, en, ru))
            warehouse_ids.append(cur.fetchone()[0])

        # kategoriler ve urunler
        for main_cat, sub_cats in data_tree.items():
            m_tr, m_en, m_ru = main_cat
            cur.execute("""
                        insert into categories (name_tr, name_en, name_ru, slug)
                        values (%s, %s, %s, %s) returning id
                        """, (m_tr, m_en, m_ru, create_slug(m_en)))
            parent_id = cur.fetchone()[0]

            for s_tr, s_en, s_ru in sub_cats:
                cur.execute("""
                            insert into categories (name_tr, name_en, name_ru, slug, parent_id)
                            values (%s, %s, %s, %s, %s) returning id
                            """, (s_tr, s_en, s_ru, create_slug(s_en), parent_id))
                category_id = cur.fetchone()[0]

                # urun ve stok verileri
                for i in range(random.randint(15, 30)):
                    logic = sector_logic.get(m_en, {'price': (100, 1000), 'weight': (1, 10)})
                    brand = fake_en.company().split()[0]
                    p_name_en = f"{brand} {s_en} {random.randint(100, 999)}"

                    cur.execute("""
                                insert into products (sku, name_tr, name_en, name_ru, description_tr, description_en,
                                                      description_ru, category_id, price, weight_kg)
                                values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) returning id
                                """, (f"{s_en[:3].upper()}-{random.randint(1000, 9999)}", f"{brand} {s_tr}", p_name_en,
                                      f"{brand} {s_ru}",
                                      fake_tr.sentence(), fake_en.sentence(), fake_ru.sentence(), category_id,
                                      round(random.uniform(*logic['price']), 2),
                                      round(random.uniform(*logic['weight']), 2)))

                    product_id = cur.fetchone()[0]

                    # stok kayitlari
                    chosen_warehouse = random.choice(warehouse_ids)
                    cur.execute("""
                                insert into inventory (product_id, warehouse_id, quantity, min_stock_level)
                                values (%s, %s, %s, %s)
                                """, (product_id, chosen_warehouse, random.randint(10, 500), 20))

        conn.commit()
        print("veritabani basariyla dolduruldu.")

    except Exception as e:
        print(f"hata: {e}")
        if conn: conn.rollback()
    finally:
        if conn:
            cur.close()
            conn.close()


if __name__ == "__main__":
    seed_database()
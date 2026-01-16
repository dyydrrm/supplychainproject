import psycopg2
from geopy.geocoders import Nominatim
import time

# baglanti bilgileri
db_config = {
    "dbname": "supplychain_db",
    "user": "postgres",
    "password": "your_password",
    "host": "localhost"
}


def koordinatlari_bul():
    try:
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        geolocator = Nominatim(user_agent="supply_chain_app")

        # koordinati olmayan adresleri cekiyoruz
        cur.execute("select id, city, country from addresses where geom is null")
        adresler = cur.fetchall()

        for addr_id, city, country in adresler:
            try:
                # servis kurali: kisa bir mola
                time.sleep(1.2)

                tam_adres = f"{city}, {country}"
                konum = geolocator.geocode(tam_adres)

                if konum:
                    # koordinati postgis formatinda kaydediyoruz
                    cur.execute("""
                                update addresses
                                set geom = st_setsrid(st_makepoint(%s, %s), 4326)
                                where id = %s
                                """, (konum.longitude, konum.latitude, addr_id))
                    conn.commit()
                    print(f"ok: {tam_adres}")
                else:
                    print(f"bulunamadi: {tam_adres}")

            except Exception:
                time.sleep(2)
                continue

        cur.close()
        conn.close()
        print("islem tamamlandi.")

    except Exception as e:
        print(f"baglanti hatasi: {e}")


if __name__ == "__main__":
    koordinatlari_bul()
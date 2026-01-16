create extension if not exists postgis;

create table categories (
    id serial primary key,
    parent_id integer references categories(id),
    name_tr varchar(100) not null,
    name_en varchar(100) not null,
    name_ru varchar(100) not null,
    slug varchar(255) unique not null
);

create table products (
    id serial primary key,
    sku varchar(50) unique not null,
    name_tr varchar(100) not null,
    name_en varchar(100) not null,
    name_ru varchar(100) not null,
    category_id integer references categories(id),
    price decimal(10, 2),
    weight_kg decimal(10, 2),
    description_tr text,
    description_en text,
    description_ru text
);

create table warehouses (
    id serial primary key,
    warehouse_code varchar(100) unique not null,
    name_tr varchar(100),
    name_en varchar(100),
    name_ru varchar(100)
);

create table inventory (
    id serial primary key,
    product_id integer references products(id),
    warehouse_id integer references warehouses(id),
    quantity integer not null,
    min_stock_level integer default 10
);

create table customers (
    id serial primary key,
    first_name varchar(100),
    last_name varchar(100),
    preferred_lang varchar(3),
    created_at timestamp default current_timestamp
);

create table addresses (
    id serial primary key,
    owner_id integer not null, --customer veya warehouse id
    owner_type varchar(50) not null,
    title varchar(50),
    city varchar(50),
    country varchar(100),
    full_address text,
    state varchar(50),
    postal_code varchar(20),
    geom geometry(Point, 4326)
);

create table orders (
    id serial primary key,
    customer_id integer references customers(id),
    shipping_address_id integer references addresses(id),
    order_date timestamp default current_timestamp,
    status varchar(50),
    total_amount decimal(15, 2)
);

create table order_items (
    id serial primary key,
    order_id integer references orders(id),
    product_id integer references products(id),
    quantity integer not null,
    unit_price decimal(10, 2)
);

create table contacts (
    id serial primary key,
    owner_id integer not null,
    owner_type varchar(50) not null,
    email varchar(255),
    phone varchar(50),
    is_primary boolean default false
);

--  Global Şehir Dağıtımı Simülasyon Verisi
update addresses set geom = null;
update addresses set city = 'Moscow', country = 'Russia' where id % 10 = 0;
update addresses set city = 'Istanbul', country = 'Turkey' where id % 10 = 5;
update addresses set city = 'London', country = 'UK' where id % 10 = 7;
update addresses set city = 'Berlin', country = 'Germany' where id % 10 = 8;
update addresses set city = 'Paris', country = 'France' where id % 10 = 9;

-- ANALİTİK SORGULAR 

-- Lojistik ve Ciro Analizi (Ülke Bazlı)
select 
    a.country, 
    count(o.id) as siparis_sayisi, 
    round(sum(o.total_amount), 2) as toplam_ciro,
    round(avg(st_distance(a.geom, st_setsrid(st_makepoint(28.97, 41.00), 4326)::geography)/1000), 2) as ort_mesafe_km
from orders o 
join addresses a on o.shipping_address_id = a.id
where a.geom is not null 
group by a.country 
order by toplam_ciro desc;

--  Ürün Bazlı Kârlılık ve Stok Durumu
select 
    p.name_tr, 
    sum(oi.quantity) as toplam_satis,
    sum(oi.quantity * oi.unit_price) as toplam_gelir,
    (select sum(quantity) from inventory where product_id = p.id) as mevcut_stok
from products p
join order_items oi on p.id = oi.product_id
group by p.id, p.name_tr
order by toplam_gelir desc;

-- En Az Stokta Kalan Ürünler (Alarm)
select p.name_tr, w.name_tr as depo, i.quantity, i.min_stock_level
from inventory i
join products p on i.product_id = p.id
join warehouses w on i.warehouse_id = w.id
where i.quantity <= i.min_stock_level;

--  Müşteri Harcama ve Dil Tercihi Analizi
select preferred_lang, count(*) as kisi, avg(o.total_amount) as ort_siparis
from customers c
join orders o on c.id = o.customer_id
group by preferred_lang;

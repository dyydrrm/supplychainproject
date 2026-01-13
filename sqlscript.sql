create table categories (
    id serial primary key,
    parent_id integer null,
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
    description_tr text not null,
    description_en text not null,
    description_ru text not null,
    category_id integer not null,
    constraint fk_product_category foreign key (category_id) references categories (id)
);

create table warehouses (
    id serial primary key,
    warehouse_code varchar(100) unique not null,
    name_tr varchar(100) not null,
    name_en varchar(100) not null,
    name_ru varchar(100) not null
);

create table inventory (
    id serial primary key,
    quantity integer not null,
    min_stock_level integer not null,
    warehouse_id integer not null,
    product_id integer not null,
    constraint fk_inventory_warehouse foreign key (warehouse_id) references warehouses (id),
    constraint fk_inventory_product foreign key (product_id) references products (id)
);

create table customers (
    id serial primary key,
    first_name varchar(100) not null,
    last_name varchar(100) not null,
    preferred_lang varchar(3) not null,
    created_at timestamp default current_timestamp
);

create table addresses (
    id serial primary key,
    owner_id integer not null, -- polimorfik yapı: python ile yönetilecek
    owner_type varchar(50) not null,
    title varchar(50) not null,
    full_address text not null,
    city varchar(50) not null,
    state varchar(50) not null,
    country varchar(100) not null,
    postal_code varchar(20) not null,
    latitude decimal(9, 6),
    longitude decimal(9, 6)
);

create table orders (
    id serial primary key,
    customer_id integer not null,
    shipping_address_id integer not null,
    order_date timestamp default current_timestamp,
    status varchar(60) not null,
    total_amount decimal(15, 2) not null,
    constraint fk_order_customer foreign key (customer_id) references customers (id),
    constraint fk_order_address foreign key (shipping_address_id) references addresses (id)
);

create table order_items (
    id serial primary key,
    order_id integer not null,
    product_id integer not null,
    quantity integer not null,
    unit_price decimal(10, 2) not null,
    constraint fk_items_order foreign key (order_id) references orders (id),
    constraint fk_items_product foreign key (product_id) references products (id)
);

create table contacts (
    id serial primary key,
    owner_id integer not null, -- polimorfik yapı: python ile yönetilecek
    owner_type varchar(100) not null,
    contact_type varchar(100) not null,
    contact_value varchar(100) not null,
    is_primary boolean default false
);

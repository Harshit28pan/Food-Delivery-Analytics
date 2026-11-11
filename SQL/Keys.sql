USE food_delivery;

-- make the ID columns VARCHAR (a key cannot be created on TEXT columns)
ALTER TABLE customers MODIFY Customer_ID VARCHAR(10) NOT NULL;
ALTER TABLE restaurants MODIFY Restaurant_ID VARCHAR(10) NOT NULL;
ALTER TABLE delivery_partners MODIFY Delivery_Partner_ID VARCHAR(10) NOT NULL;

ALTER TABLE orders
    MODIFY Order_Key BIGINT NOT NULL,
    MODIFY Customer_ID VARCHAR(10) NOT NULL,
    MODIFY Restaurant_ID VARCHAR(10) NOT NULL,
    MODIFY Delivery_Partner_ID VARCHAR(10) NOT NULL;

-- primary keys
ALTER TABLE customers ADD PRIMARY KEY (Customer_ID);
ALTER TABLE restaurants ADD PRIMARY KEY (Restaurant_ID);
ALTER TABLE delivery_partners ADD PRIMARY KEY (Delivery_Partner_ID);
ALTER TABLE orders ADD PRIMARY KEY (Order_Key);

-- foreign keys (orders points to the other three tables)
ALTER TABLE orders ADD CONSTRAINT fk_orders_customer
    FOREIGN KEY (Customer_ID) REFERENCES customers (Customer_ID);
ALTER TABLE orders ADD CONSTRAINT fk_orders_restaurant
    FOREIGN KEY (Restaurant_ID) REFERENCES restaurants (Restaurant_ID);
ALTER TABLE orders ADD CONSTRAINT fk_orders_partner
    FOREIGN KEY (Delivery_Partner_ID) REFERENCES delivery_partners (Delivery_Partner_ID);
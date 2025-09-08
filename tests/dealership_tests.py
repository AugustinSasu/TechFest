import pytest

#script care insreaza cate 3 valori pentru fiecare tabelă.

# ALTER SESSION SET CURRENT_SCHEMA=APP_OWNER;
#
# -------------------------------------------------------------------------------
# -- 1) DEALERSHIP (3)
# -------------------------------------------------------------------------------
# INSERT INTO dealership (name, city, region)
# VALUES ('Endava Auto București', 'București', 'Sud-Muntenia');
#
# INSERT INTO dealership (name, city, region)
# VALUES ('Endava Auto Cluj', 'Cluj-Napoca', 'Nord-Vest');
#
# INSERT INTO dealership (name, city, region)
# VALUES ('Endava Auto Iași', 'Iași', 'Nord-Est');
#
#
# -------------------------------------------------------------------------------
# -- 2) EMPLOYEE (3)  -> le legăm de dealership prin subselect pe nume
# -------------------------------------------------------------------------------
# INSERT INTO employee (db_username, full_name, role_code, dealership_id)
# VALUES (
#   'SALES_ANNA',
#   'Anna Ionescu',
#   'SALES',
#   (SELECT d.dealership_id FROM dealership d WHERE d.name = 'Endava Auto București')
# );
#
# INSERT INTO employee (db_username, full_name, role_code, dealership_id)
# VALUES (
#   'SALES_MIHNEA',
#   'Mihnea Pop',
#   'SALES',
#   (SELECT d.dealership_id FROM dealership d WHERE d.name = 'Endava Auto Cluj')
# );
#
# INSERT INTO employee (db_username, full_name, role_code, dealership_id)
# VALUES (
#   'MGR_BOB',
#   'Bob Marinescu',
#   'MANAGER',
#   (SELECT d.dealership_id FROM dealership d WHERE d.name = 'Endava Auto București')
# );
#
#
# -------------------------------------------------------------------------------
# -- 3) CUSTOMER (3)
# -------------------------------------------------------------------------------
# INSERT INTO customer (full_name, phone, email)
# VALUES ('Ioana Georgescu',  '+40 721 111 222', 'ioana.georgescu@example.com');
#
# INSERT INTO customer (full_name, phone, email)
# VALUES ('Radu Petrescu',    '+40 722 333 444', 'radu.petrescu@example.com');
#
# INSERT INTO customer (full_name, phone, email)
# VALUES ('Carmen Dobre',     '+40 723 555 666', 'carmen.dobre@example.com');
#
#
# -------------------------------------------------------------------------------
# -- 4) VEHICLE (3)  -> VIN unice, model, an, preț de bază
# -------------------------------------------------------------------------------
# INSERT INTO vehicle (vin, model, trim_level, model_year, base_price)
# VALUES ('WVWZZZ1JZXA000001', 'Golf',   'Highline', 2024, 22000);
#
# INSERT INTO vehicle (vin, model, trim_level, model_year, base_price)
# VALUES ('WVGZZZ5NZYA000002', 'Tiguan', 'R-Line',   2025, 36000);
#
# INSERT INTO vehicle (vin, model, trim_level, model_year, base_price)
# VALUES ('WV1ZZZ2HZBA000003', 'Passat', 'Elegance', 2023, 30000);
#
#
# -------------------------------------------------------------------------------
# -- 5) SERVICE_ITEM (3)
# -------------------------------------------------------------------------------
# INSERT INTO service_item (service_type, name, description, list_price)
# VALUES ('EXTRA_OPTION', 'Pachet Tech', 'Navigație, cockpit digital, senzori parcare', 1500);
#
# INSERT INTO service_item (service_type, name, description, list_price)
# VALUES ('CASCO', 'CASCO 12 luni', 'Asigurare completă pe 12 luni', 900);
#
# INSERT INTO service_item (service_type, name, description, list_price)
# VALUES ('EXTENDED_WARRANTY', 'Garanție extinsă 2 ani', 'Extindere garanție producător', 1200);
#
#
# -------------------------------------------------------------------------------
# -- 6) SALE_ORDER (3)  -> legăm prin subselect: dealership (după nume), client (după email),
# --                        salesperson/manager (după db_username). created_by = username app.
# -- Notă: total_amount îl lăsăm NULL inițial; se va calcula după inserarea liniilor.
# -------------------------------------------------------------------------------
# -- Comandă #1 (client Ioana, București, vânzător Anna, cu manager Bob)
# INSERT INTO sale_order (
#   dealership_id, customer_id, salesperson_id, manager_id,
#   order_date, status, total_amount, created_by
# )
# VALUES (
#   (SELECT dealership_id FROM dealership WHERE name = 'Endava Auto București'),
#   (SELECT customer_id   FROM customer   WHERE email = 'ioana.georgescu@example.com'),
#   (SELECT employee_id   FROM employee   WHERE db_username = 'SALES_ANNA'),
#   (SELECT employee_id   FROM employee   WHERE db_username = 'MGR_BOB'),
#   DATE '2025-09-01',
#   'OPEN',
#   NULL,
#   'SALES_ANNA'
# );
#
# -- Comandă #2 (client Radu, Cluj, vânzător Mihnea, fără manager)
# INSERT INTO sale_order (
#   dealership_id, customer_id, salesperson_id, manager_id,
#   order_date, status, total_amount, created_by
# )
# VALUES (
#   (SELECT dealership_id FROM dealership WHERE name = 'Endava Auto Cluj'),
#   (SELECT customer_id   FROM customer   WHERE email = 'radu.petrescu@example.com'),
#   (SELECT employee_id   FROM employee   WHERE db_username = 'SALES_MIHNEA'),
#   NULL,
#   DATE '2025-09-02',
#   'OPEN',
#   NULL,
#   'SALES_MIHNEA'
# );
#
# -- Comandă #3 (client Carmen, București, vânzător Anna, fără manager)
# INSERT INTO sale_order (
#   dealership_id, customer_id, salesperson_id, manager_id,
#   order_date, status, total_amount, created_by
# )
# VALUES (
#   (SELECT dealership_id FROM dealership WHERE name = 'Endava Auto București'),
#   (SELECT customer_id   FROM customer   WHERE email = 'carmen.dobre@example.com'),
#   (SELECT employee_id   FROM employee   WHERE db_username = 'SALES_ANNA'),
#   NULL,
#   DATE '2025-09-03',
#   'OPEN',
#   NULL,
#   'SALES_ANNA'
# );
#
#
# -------------------------------------------------------------------------------
# -- 7) SALE_ITEM (3)  -> câte un item per comandă (2 mașini + 1 serviciu).
# -- unit_price e preluat din vehicle.base_price / service_item.list_price.
# -------------------------------------------------------------------------------
# -- Item pt Comanda #1: CAR = Golf
# INSERT INTO sale_item (order_id, item_type, vehicle_id, service_id, qty, unit_price)
# VALUES (
#   (SELECT so.order_id
#      FROM sale_order so
#      JOIN customer c ON c.customer_id = so.customer_id
#     WHERE c.email = 'ioana.georgescu@example.com'
#       AND so.order_date = DATE '2025-09-01'),
#   'CAR',
#   (SELECT v.vehicle_id FROM vehicle v WHERE v.vin = 'WVWZZZ1JZXA000001'),
#   NULL,
#   1,
#   (SELECT v.base_price FROM vehicle v WHERE v.vin = 'WVWZZZ1JZXA000001')
# );
#
# -- Item pt Comanda #2: SERVICE = CASCO 12 luni
# INSERT INTO sale_item (order_id, item_type, vehicle_id, service_id, qty, unit_price)
# VALUES (
#   (SELECT so.order_id
#      FROM sale_order so
#      JOIN customer c ON c.customer_id = so.customer_id
#     WHERE c.email = 'radu.petrescu@example.com'
#       AND so.order_date = DATE '2025-09-02'),
#   'SERVICE',
#   NULL,
#   (SELECT s.service_id FROM service_item s WHERE s.name = 'CASCO 12 luni'),
#   1,
#   (SELECT s.list_price FROM service_item s WHERE s.name = 'CASCO 12 luni')
# );
#
# -- Item pt Comanda #3: CAR = Tiguan
# INSERT INTO sale_item (order_id, item_type, vehicle_id, service_id, qty, unit_price)
# VALUES (
#   (SELECT so.order_id
#      FROM sale_order so
#      JOIN customer c ON c.customer_id = so.customer_id
#     WHERE c.email = 'carmen.dobre@example.com'
#       AND so.order_date = DATE '2025-09-03'),
#   'CAR',
#   (SELECT v.vehicle_id FROM vehicle v WHERE v.vin = 'WVGZZZ5NZYA000002'),
#   NULL,
#   1,
#   (SELECT v.base_price FROM vehicle v WHERE v.vin = 'WVGZZZ5NZYA000002')
# );
#
# -------------------------------------------------------------------------------
# -- (Opțional) Dacă vrei să setezi total_amount după ce ai introdus liniile:
# -- Actualizăm total_amount ca SUM(line_total) pentru fiecare comandă.
# -------------------------------------------------------------------------------
# -- UPDATE sale_order so
# -- SET so.total_amount = (
# --   SELECT SUM(si.line_total)
# --   FROM sale_item si
# --   WHERE si.order_id = so.order_id
# -- );
# -- COMMIT;

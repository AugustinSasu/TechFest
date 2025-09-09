-- Dealerships
INSERT INTO dealership(name, city, region) VALUES ('VW South Motors', 'Bucharest', 'S');
INSERT INTO dealership(name, city, region) VALUES ('VW West Auto', 'Timisoara', 'W');

-- Vehicles
BEGIN
    FOR i IN 1..30 LOOP
        INSERT INTO vehicle(vin, model, trim_level, model_year, base_price)
        VALUES ('1VWZZZ1PZ1P' || TO_CHAR(100000 + i),
            CASE MOD(i,5) WHEN 0 THEN 'Golf' WHEN 1 THEN 'Tiguan' WHEN 2 THEN 'Touran' WHEN 3 THEN 'Polo' ELSE 'Passat' END,
            CASE MOD(i,3) WHEN 0 THEN 'Basic' WHEN 1 THEN 'Comfort' ELSE 'Sport' END,
            2020 + MOD(i, 5),
            20000 + (i * 500));
    END LOOP;
END;
/

-- Service Items
BEGIN
    FOR i IN 1..10 LOOP
        INSERT INTO service_item(service_type, name, description, list_price)
        VALUES (
            CASE MOD(i, 5)
                WHEN 0 THEN 'EXTRA_OPTION'
                WHEN 1 THEN 'EXTENDED_WARRANTY'
                WHEN 2 THEN 'CASCO'
                WHEN 3 THEN 'SERVICING'
                ELSE 'OTHER'
            END,
            'Service Option #' || i,
            'Description for service option #' || i,
            100 * i
        );
    END LOOP;
END;
/


-- Salespeople
INSERT INTO employee(db_username, full_name, role_code, dealership_id) VALUES
('SALES_JDAN', 'John Dancu', 'SALES', (SELECT dealership_id FROM dealership WHERE name = 'VW North City')),
('SALES_RPOP', 'Radu Popescu', 'SALES', (SELECT dealership_id FROM dealership WHERE name = 'VW East Town')),
('SALES_MVAS', 'Maria Vasilescu', 'SALES', (SELECT dealership_id FROM dealership WHERE name = 'VW South Motors')),
('SALES_ALAZ', 'Alexandru Lazăr', 'SALES', (SELECT dealership_id FROM dealership WHERE name = 'VW West Auto')),
('SALES_ILOR', 'Ioana Loredana', 'SALES', (SELECT dealership_id FROM dealership WHERE name = 'VW North City')),
('SALES_TSTO', 'Tudor Stoica', 'SALES', (SELECT dealership_id FROM dealership WHERE name = 'VW East Town')),
('SALES_GCAM', 'Gabriel Campeanu', 'SALES', (SELECT dealership_id FROM dealership WHERE name = 'VW South Motors')),
('SALES_CNAG', 'Cristina Nagy', 'SALES', (SELECT dealership_id FROM dealership WHERE name = 'VW West Auto')),
('SALES_DGEO', 'Daniel Georgescu', 'SALES', (SELECT dealership_id FROM dealership WHERE name = 'VW North City')),
('SALES_BMIR', 'Bianca Miron', 'SALES', (SELECT dealership_id FROM dealership WHERE name = 'VW East Town')),
('SALES_FLUP', 'Florin Lup', 'SALES', (SELECT dealership_id FROM dealership WHERE name = 'VW South Motors')),
('SALES_SVLA', 'Simona Vladescu', 'SALES', (SELECT dealership_id FROM dealership WHERE name = 'VW West Auto')),
('SALES_CPOP', 'Claudiu Popa', 'SALES', (SELECT dealership_id FROM dealership WHERE name = 'VW North City')),
('SALES_MNEA', 'Mihai Neagu', 'SALES', (SELECT dealership_id FROM dealership WHERE name = 'VW East Town')),
('SALES_ANIC', 'Andreea Niculescu', 'SALES', (SELECT dealership_id FROM dealership WHERE name = 'VW South Motors'));


-- Managers

INSERT INTO employee(db_username, full_name, role_code, dealership_id) VALUES
('MGR_ALUP', 'Alina Lupescu', 'MANAGER', (SELECT dealership_id FROM dealership WHERE name = 'VW North City')),
('MGR_NVAS', 'Nicolae Vasilescu', 'MANAGER', (SELECT dealership_id FROM dealership WHERE name = 'VW South Motors')),
('MGR_IOAN', 'Ioan Dragomir', 'MANAGER', (SELECT dealership_id FROM dealership WHERE name = 'VW West Auto')),
('MGR_RFIL', 'Roxana Filip', 'MANAGER', (SELECT dealership_id FROM dealership WHERE name = 'VW West Auto')),
('MGR_BNEG', 'Bogdan Negrea', 'MANAGER', (SELECT dealership_id FROM dealership WHERE name = 'VW South Motors'));


-- Customers
INSERT INTO customer(full_name, phone, email) VALUES
('Vlad Ionescu', '0712000001', 'vlad.ionescu@example.com'),
('Elena Pop', '0712000002', 'elena.pop@example.com'),
('George Marinescu', '0712000003', 'george.marinescu@example.com'),
('Ana Petraru', '0712000004', 'ana.petraru@example.com'),
('Cristian Stoian', '0712000005', 'cristian.stoian@example.com'),
('Raluca Dima', '0712000006', 'raluca.dima@example.com'),
('Stefan Balan', '0712000007', 'stefan.balan@example.com'),
('Ioana Munteanu', '0712000008', 'ioana.munteanu@example.com'),
('Florin Pavel', '0712000009', 'florin.pavel@example.com'),
('Andreea Ilie', '0712000010', 'andreea.ilie@example.com'),
('Marius Enache', '0712000011', 'marius.enache@example.com'),
('Alina Neagu', '0712000012', 'alina.neagu@example.com'),
('Daniel Popa', '0712000013', 'daniel.popa@example.com'),
('Monica Vlad', '0712000014', 'monica.vlad@example.com'),
('Gabriel Radu', '0712000015', 'gabriel.radu@example.com'),
('Carmen Iacob', '0712000016', 'carmen.iacob@example.com'),
('Adrian Serban', '0712000017', 'adrian.serban@example.com'),
('Liliana Apostol', '0712000018', 'liliana.apostol@example.com'),
('Radu Petrescu', '0712000019', 'radu.petrescu@example.com'),
('Nicoleta Zaharia', '0712000020', 'nicoleta.zaharia@example.com'),
('Robert Georgescu', '0712000021', 'robert.georgescu@example.com'),
('Ioana Costache', '0712000022', 'ioana.costache@example.com'),
('Emil Dumitrescu', '0712000023', 'emil.dumitrescu@example.com'),
('Adela Muresan', '0712000024', 'adela.muresan@example.com'),
('Tiberiu Grigore', '0712000025', 'tiberiu.grigore@example.com'),
('Oana Badea', '0712000026', 'oana.badea@example.com'),
('Ionut Calin', '0712000027', 'ionut.calin@example.com'),
('Camelia Andrei', '0712000028', 'camelia.andrei@example.com'),
('Liviu Oprea', '0712000029', 'liviu.oprea@example.com'),
('Sorina Nistor', '0712000030', 'sorina.nistor@example.com');

-- Sale Orders + Line Items
DECLARE
  v_order_id NUMBER;
BEGIN
  FOR i IN 1..30 LOOP
    INSERT INTO sale_order(dealership_id, customer_id, salesperson_id, manager_id, status, total_amount, created_by, order_date)
    VALUES (
      (SELECT dealership_id FROM (
         SELECT dealership_id FROM dealership ORDER BY DBMS_RANDOM.VALUE
       ) WHERE ROWNUM = 1),
      (SELECT customer_id FROM (
         SELECT customer_id FROM customer ORDER BY customer_id
       ) OFFSET i - 1 ROWS FETCH NEXT 1 ROWS ONLY),
      (SELECT employee_id FROM (
         SELECT employee_id FROM employee WHERE role_code = 'SALES' ORDER BY DBMS_RANDOM.VALUE
       ) WHERE ROWNUM = 1),
      (SELECT employee_id FROM (
         SELECT employee_id FROM employee WHERE role_code = 'MANAGER' ORDER BY DBMS_RANDOM.VALUE
       ) WHERE ROWNUM = 1),
      'APPROVED',
      20000 + i * 300,
      (SELECT db_username FROM (
         SELECT db_username FROM employee WHERE role_code = 'SALES' ORDER BY DBMS_RANDOM.VALUE
       ) WHERE ROWNUM = 1),
      TRUNC(SYSDATE - DBMS_RANDOM.VALUE(30, 730))
    ) RETURNING order_id INTO v_order_id;

    INSERT INTO car_sale_item(order_id, vehicle_id, unit_price)
    VALUES (
      v_order_id,
      (SELECT vehicle_id FROM (
         SELECT vehicle_id FROM vehicle ORDER BY vehicle_id
       ) OFFSET i - 1 ROWS FETCH NEXT 1 ROWS ONLY),
      20000 + i * 500
    );

    INSERT INTO service_sale_item(order_id, service_id, qty, unit_price)
    VALUES (
      v_order_id,
      (SELECT service_id FROM (
         SELECT service_id FROM service_item ORDER BY service_id
       ) OFFSET MOD(i, 10) ROWS FETCH NEXT 1 ROWS ONLY),
      1,
      100 * MOD(i, 10) + 1
    );
  END LOOP;
END;
/

SELECT 
  e.full_name, 
  e.db_username, 
  COUNT(o.order_id) AS total_sales
FROM employee e
LEFT JOIN sale_order o ON e.employee_id = o.salesperson_id
WHERE e.role_code = 'SALES'
GROUP BY e.full_name, e.db_username
ORDER BY total_sales DESC;


SELECT * FROM vehicle;
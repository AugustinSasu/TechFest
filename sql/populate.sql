-- ==============================================================--
-- Demo Data Populate Script
-- ==============================================================--

-- (1) Dealerships & Employees (already run, but safe to include)
INSERT INTO dealership(name, city, region)
VALUES ('VW North City', 'Cluj-Napoca', 'NW');

INSERT INTO dealership(name, city, region)
VALUES ('VW East Town', 'Iasi', 'NE');

INSERT INTO employee(db_username, full_name, role_code, dealership_id)
VALUES (
  'SALES_ANNA', 'Anna Pop', 'SALES',
  (SELECT dealership_id FROM dealership WHERE name='VW North City')
);

INSERT INTO employee(db_username, full_name, role_code, dealership_id)
VALUES (
  'MGR_BOB', 'Bob Ionescu', 'MANAGER',
  (SELECT dealership_id FROM dealership WHERE name='VW North City')
);

COMMIT;

-- ==============================================================--
-- (2) Customers
-- ==============================================================--
INSERT INTO customer(full_name, phone, email) VALUES
('Ion Gheorghe', '0712‑123‑456', 'ion.gheorghe@example.com');

INSERT INTO customer(full_name, phone, email) VALUES
('Maria Ciobanu', '0722‑654‑321', 'maria.ciobanu@example.com');

COMMIT;

-- ==============================================================--
-- (3) Vehicles
-- ==============================================================--
INSERT INTO vehicle(vin, model, trim_level, model_year, base_price) VALUES
('1VWZZZ1PZ1P000001', 'Golf',      'Comfort', 2023, 22000.00);

INSERT INTO vehicle(vin, model, trim_level, model_year, base_price) VALUES
('1VWZZZ1PZ1P000002', 'Tiguan',    'Sport',   2024, 28000.00);

INSERT INTO vehicle(vin, model, trim_level, model_year, base_price) VALUES
('1VWZZZ1PZ1P000003', 'Passat',    'Elegance', 2022, 25000.00);

COMMIT;

-- ==============================================================--
-- (4) Service Items
-- ==============================================================--
INSERT INTO service_item(service_type, name, description, list_price) VALUES
('EXTRA_OPTION', 'Sunroof', 'Electrically operated sunroof.', 1200.00);

INSERT INTO service_item(service_type, name, description, list_price) VALUES
('EXTENDED_WARRANTY', '2‑Year Warranty', 'Covers parts & labor for 2 years.', 1500.00);

INSERT INTO service_item(service_type, name, description, list_price) VALUES
('SERVICING', 'Oil Change', 'Full synthetic oil change service.', 150.00);

COMMIT;

-- ==============================================================--
-- (5) Sale Orders + Line Items
-- ==============================================================--
-- Create a sale order for Ion: buys a 2023 Golf with an extra option
INSERT INTO sale_order(dealership_id, customer_id, salesperson_id, manager_id, status, total_amount, created_by)
VALUES (
 (SELECT dealership_id FROM dealership WHERE name='VW North City'),
 (SELECT customer_id FROM customer WHERE full_name='Ion Gheorghe'),
 (SELECT employee_id FROM employee WHERE db_username='SALES_ANNA'),
 (SELECT employee_id FROM employee WHERE db_username='MGR_BOB'),
 'APPROVED',
 23200.00,
 'SALES_ANNA'
);

-- Get the order ID above
-- (Assumes only one new order; adjust as needed.)
DECLARE
  v_order_id NUMBER;
BEGIN
  SELECT order_id INTO v_order_id
  FROM sale_order
  WHERE customer_id = (SELECT customer_id FROM customer WHERE full_name='Ion Gheorghe')
    AND ROWNUM = 1
  ORDER BY order_date DESC;

  -- Add car_sale_item: Golf
  INSERT INTO car_sale_item(order_id, vehicle_id, unit_price)
  VALUES (
    v_order_id,
    (SELECT vehicle_id FROM vehicle WHERE model='Golf'),
    22000.00
  );

  -- Add service_sale_item: Sunroof as extra add‑on
  INSERT INTO service_sale_item(order_id, service_id, qty, unit_price)
  VALUES (
    v_order_id,
    (SELECT service_id FROM service_item WHERE name='Sunroof'),
    1,
    1200.00
  );

  COMMIT;
END;
/

-- ==============================================================--
-- (6) Populate `ai_raw_input` with sample raw texts
-- ==============================================================--
-- Example entries from the app
INSERT INTO ai_raw_input(dealership_id, src_text)
VALUES (
  (SELECT dealership_id FROM dealership WHERE name='VW North City'),
  'Customer wants to schedule a Golf test drive.'
);

INSERT INTO ai_raw_input(dealership_id, src_text)
VALUES (
  (SELECT dealership_id FROM dealership WHERE name='VW North City'),
  'Looking for VW Tiguan lease options.'
);

INSERT INTO ai_raw_input(dealership_id, src_text)
VALUES (
  (SELECT dealership_id FROM dealership WHERE name='VW East Town'),
  'Inquiry about extended warranty for Passat.'
);

COMMIT;

-- ==============================================================--
-- End of Populate Script
-- ==============================================================--

-- Dealerships
INSERT INTO dealership(name, city, region) VALUES ('VW North City', 'Cluj-Napoca', 'NW');
INSERT INTO dealership(name, city, region) VALUES ('VW East Town',  'Iasi',        'NE');

-- Employees (map to DB usernames; assign home dealership)
INSERT INTO employee(db_username, full_name, role_code, dealership_id)
VALUES ('SALES_ANNA', 'Anna Pop', 'SALES',   (SELECT dealership_id FROM dealership WHERE name='VW North City'));

INSERT INTO employee(db_username, full_name, role_code, dealership_id)
VALUES ('MGR_BOB', 'Bob Ionescu', 'MANAGER', (SELECT dealership_id FROM dealership WHERE name='VW North City'));

COMMIT;

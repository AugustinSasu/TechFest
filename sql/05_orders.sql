DECLARE
    v_order_id NUMBER;
BEGIN
    FOR m IN 0..35 LOOP
        FOR j IN 1..100 LOOP
            INSERT INTO sale_order(dealership_id, customer_id, salesperson_id, manager_id, status, total_amount, created_by, order_date)
            VALUES (
            (SELECT dealership_id FROM (SELECT dealership_id FROM dealership ORDER BY DBMS_RANDOM.VALUE) WHERE ROWNUM = 1),
            (SELECT customer_id FROM (SELECT customer_id FROM customer ORDER BY DBMS_RANDOM.VALUE) WHERE ROWNUM = 1),
            (SELECT employee_id FROM (SELECT employee_id FROM employee WHERE role_code = 'SALES' ORDER BY DBMS_RANDOM.VALUE) WHERE ROWNUM = 1),
            (SELECT employee_id FROM (SELECT employee_id FROM employee WHERE role_code = 'MANAGER' ORDER BY DBMS_RANDOM.VALUE) WHERE ROWNUM = 1),
            'APPROVED',
            20000 + j * 100 + m,
            (SELECT db_username FROM (SELECT db_username FROM employee WHERE role_code = 'SALES' ORDER BY DBMS_RANDOM.VALUE) WHERE ROWNUM = 1),
            TRUNC(ADD_MONTHS(SYSDATE, -m) + DBMS_RANDOM.VALUE(0, 27))
            ) RETURNING order_id INTO v_order_id;


            INSERT INTO car_sale_item(order_id, vehicle_id, unit_price)
            VALUES (
            v_order_id,
            (SELECT vehicle_id FROM (SELECT vehicle_id FROM vehicle ORDER BY DBMS_RANDOM.VALUE) WHERE ROWNUM = 1),
            22000 + j * 10 + m
            );


            INSERT INTO service_sale_item(order_id, service_id, qty, unit_price)
            VALUES (
            v_order_id,
            (SELECT service_id FROM (SELECT service_id FROM service_item ORDER BY DBMS_RANDOM.VALUE) WHERE ROWNUM = 1),
            1,
            500 + j + m
            );
        END LOOP;
    END LOOP;
END;
/

COMMIT;
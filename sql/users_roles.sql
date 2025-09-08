ALTER SESSION SET CONTAINER=FREEPDB1;

-- Schema owner
CREATE USER app_owner IDENTIFIED BY "app_owner" QUOTA UNLIMITED ON users;
GRANT CONNECT, RESOURCE TO app_owner;

-- App roles
CREATE ROLE sales_role;
CREATE ROLE manager_role;

-- Example users (one salesperson, one manager)
CREATE USER sales_anna IDENTIFIED BY "sales_anna";
CREATE USER mgr_bob    IDENTIFIED BY "mgr_bob";
GRANT CREATE SESSION TO sales_anna, mgr_bob;

GRANT sales_role   TO sales_anna;
GRANT manager_role TO mgr_bob;

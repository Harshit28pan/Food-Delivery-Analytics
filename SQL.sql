Use food_delivery;

-- Show all tables in the food_delivery database.
SHOW TABLES;

-- Check the structure of the customers table.
DESCRIBE customers;

-- Check the structure of the restaurants table.
DESCRIBE restaurants;

-- Check the structure of the delivery_partners table.
DESCRIBE delivery_partners;

-- Check the structure of the orders table.
DESCRIBE orders;

-- Count the number of records imported into each table.
SELECT 'customers' AS Table_Name, COUNT(*) AS Total_Rows FROM customers
UNION ALL
SELECT 'restaurants', COUNT(*) FROM restaurants
UNION ALL
SELECT 'delivery_partners', COUNT(*) FROM delivery_partners
UNION ALL
SELECT 'orders', COUNT(*) FROM orders;



-- DATA MODELLING: PRIMARY KEYS AND FOREIGN KEYS
  

-- Show the Primary Keys that already exist in this database.
SELECT TABLE_NAME, COLUMN_NAME
FROM information_schema.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA = 'food_delivery'
  AND CONSTRAINT_NAME = 'PRIMARY'
ORDER BY TABLE_NAME;

-- Show the Foreign Keys that already exist in this database.
SELECT TABLE_NAME, COLUMN_NAME, CONSTRAINT_NAME,
       REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
FROM information_schema.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA = 'food_delivery'
  AND REFERENCED_TABLE_NAME IS NOT NULL;

-- The intended Primary Keys are Customer_ID, Restaurant_ID, Delivery_Partner_ID and Order_Key.
-- Order_Key is used because Order_ID is repeated in the orders dataset.
-- The orders table has three Foreign Keys: Customer_ID, Restaurant_ID and Delivery_Partner_ID.

-- Check whether every order has a matching customer, restaurant and delivery partner.
-- All three Bad_Rows values should be zero.
SELECT 'Orders without customer' AS Check_Name, COUNT(*) AS Bad_Rows
FROM orders o
LEFT JOIN customers c ON o.Customer_ID = c.Customer_ID
WHERE c.Customer_ID IS NULL
UNION ALL
SELECT 'Orders without restaurant', COUNT(*)
FROM orders o
LEFT JOIN restaurants r ON o.Restaurant_ID = r.Restaurant_ID
WHERE r.Restaurant_ID IS NULL
UNION ALL
SELECT 'Orders without delivery partner', COUNT(*)
FROM orders o
LEFT JOIN delivery_partners d
    ON o.Delivery_Partner_ID = d.Delivery_Partner_ID
WHERE d.Delivery_Partner_ID IS NULL;

-- Demonstrate the relationship by joining orders with all three master tables.
SELECT o.Order_Key, o.Order_ID, c.Customer_ID, r.Restaurant_ID,
       d.Delivery_Partner_ID, o.Final_Amount, o.Order_Status
FROM orders o
JOIN customers c ON o.Customer_ID = c.Customer_ID
JOIN restaurants r ON o.Restaurant_ID = r.Restaurant_ID
JOIN delivery_partners d
    ON o.Delivery_Partner_ID = d.Delivery_Partner_ID
LIMIT 10;

-- CREATE SUPPORT TABLES
-- We created four support tables to maintain data backup , track new records , monitor order status changes , and store daily buisness KPIs for reporting. 

-- Create an empty backup table using the current orders columns and add Backup_Time.
CREATE TABLE IF NOT EXISTS orders_backup AS
SELECT orders.*, NOW() AS Backup_Time
FROM orders
WHERE 1 = 0;

-- Create a log table to record every newly inserted order.
CREATE TABLE IF NOT EXISTS order_audit_log (
    Log_ID INT AUTO_INCREMENT PRIMARY KEY,
    Order_Key INT,
    Action_Type VARCHAR(20),
    Details VARCHAR(150),
    Action_Time DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create a history table to record changes in an order's status.
CREATE TABLE IF NOT EXISTS order_status_history (
    History_ID INT AUTO_INCREMENT PRIMARY KEY,
    Order_Key INT,
    Old_Status VARCHAR(30),
    New_Status VARCHAR(30),
    Changed_At DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create a table to store daily order and revenue KPIs.
CREATE TABLE IF NOT EXISTS daily_kpi_summary (
    KPI_Date DATE PRIMARY KEY,
    Total_Orders INT,
    Delivered_Orders INT,
    Cancelled_Orders INT,
    Returned_Orders INT,
    Delivered_Revenue DECIMAL(14,2),
    Updated_At DATETIME DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP
);



-- STORED PROCEDURES
   



-- Create a procedure to show the number of orders and order value by region.

DELIMITER //
DROP PROCEDURE IF EXISTS sp_region_summary //
CREATE PROCEDURE sp_region_summary()
BEGIN
    SELECT Region,
           COUNT(*) AS Total_Orders,
           SUM(Final_Amount) AS Total_Order_Amount
    FROM orders
    GROUP BY Region
    ORDER BY Total_Order_Amount DESC;
END //

-- Create a procedure to show order summary for a year provided by the user.

DELIMITER //
DROP PROCEDURE IF EXISTS sp_orders_by_year //
CREATE PROCEDURE sp_orders_by_year(IN p_year INT)
BEGIN
    SELECT Region,
           COUNT(*) AS Total_Orders,
           SUM(Final_Amount) AS Total_Order_Amount
    FROM orders
    WHERE YEAR(Order_Date) = p_year
    GROUP BY Region
    ORDER BY Total_Order_Amount DESC;
END //
DELIMITER ;

-- Create a procedure to replace the previous backup with a fresh orders backup.
-- we created this stored procedure to automate the backup process ,it clears the previous backup and copies the latest record 
-- from the orders table into the backup table.

DELIMITER //
DROP PROCEDURE IF EXISTS sp_backup_orders //
CREATE PROCEDURE sp_backup_orders()
BEGIN
    -- Remove the previous backup records.
    TRUNCATE TABLE orders_backup;

    -- Copy all current orders and add the backup timestamp.
    INSERT INTO orders_backup
    SELECT orders.*, NOW()
    FROM orders;
END //
DELIMITER ;

-- Create a procedure to refresh the KPI summary for the previous calendar day.
-- We created the sp_refresh_daily_kpi stored procedure to calculate the previous day's total orders, delivered orders, 
-- cancelled orders, returned orders, and delivered revenue. 
-- It inserts the daily summary or updates the existing record if that date is already present.

DELIMITER //
DROP PROCEDURE IF EXISTS sp_refresh_daily_kpi //
CREATE PROCEDURE sp_refresh_daily_kpi()
BEGIN
    -- Insert the previous day's order counts and delivered revenue.
    INSERT INTO daily_kpi_summary
        (KPI_Date, Total_Orders, Delivered_Orders,
         Cancelled_Orders, Returned_Orders, Delivered_Revenue)
    SELECT
        CURDATE() - INTERVAL 1 DAY,
        COUNT(*),
        SUM(CASE WHEN Order_Status = 'Delivered' THEN 1 ELSE 0 END),
        SUM(CASE WHEN Order_Status = 'Cancelled' THEN 1 ELSE 0 END),
        SUM(CASE WHEN Order_Status = 'Returned' THEN 1 ELSE 0 END),
        COALESCE(SUM(
            CASE WHEN Order_Status = 'Delivered' THEN Final_Amount ELSE 0 END
        ), 0)
    FROM orders
    WHERE Order_Date = CURDATE() - INTERVAL 1 DAY
    ON DUPLICATE KEY UPDATE
        Total_Orders = VALUES(Total_Orders),
        Delivered_Orders = VALUES(Delivered_Orders),
        Cancelled_Orders = VALUES(Cancelled_Orders),
        Returned_Orders = VALUES(Returned_Orders),
        Delivered_Revenue = VALUES(Delivered_Revenue);
END //
DELIMITER ;

-- Create one procedure to run the daily backup and KPI refresh together.


DROP PROCEDURE IF EXISTS sp_daily_maintenance //
DELIMITER //
CREATE PROCEDURE sp_daily_maintenance()
BEGIN
    CALL sp_backup_orders();
    CALL sp_refresh_daily_kpi();
END //

DELIMITER ;

-- Run the regional summary procedure.
CALL sp_region_summary();

-- Run the yearly summary procedure for 2025.
CALL sp_orders_by_year(2025);

-- Run the backup procedure once now to create an initial backup.
CALL sp_backup_orders();

-- Check how many order records were copied into the backup table.
SELECT COUNT(*) AS Backup_Rows FROM orders_backup;

-- POPULATE THE HISTORICAL DAILY KPI SUMMARY
   
-- Populate the KPI table for all dates already present in the dataset.
-- We used this query to aggregate the orders table date-wise and populate the daily KPI summary table with total orders, 
-- order statuses, and delivered revenue. This makes daily business reporting easier.

INSERT INTO daily_kpi_summary
    (KPI_Date, Total_Orders, Delivered_Orders,
     Cancelled_Orders, Returned_Orders, Delivered_Revenue)
SELECT
    Order_Date,
    COUNT(*),
    SUM(CASE WHEN Order_Status = 'Delivered' THEN 1 ELSE 0 END),
    SUM(CASE WHEN Order_Status = 'Cancelled' THEN 1 ELSE 0 END),
    SUM(CASE WHEN Order_Status = 'Returned' THEN 1 ELSE 0 END),
    COALESCE(SUM(
        CASE WHEN Order_Status = 'Delivered' THEN Final_Amount ELSE 0 END
    ), 0)
FROM orders
GROUP BY Order_Date
ON DUPLICATE KEY UPDATE
    Total_Orders = VALUES(Total_Orders),
    Delivered_Orders = VALUES(Delivered_Orders),
    Cancelled_Orders = VALUES(Cancelled_Orders),
    Returned_Orders = VALUES(Returned_Orders),
    Delivered_Revenue = VALUES(Delivered_Revenue);

-- View the daily KPI summary table.
SELECT *
FROM daily_kpi_summary
ORDER BY KPI_Date;

-- TRIGGERS

-- Create a BEFORE INSERT trigger to validate a new order and calculate Final_Amount.

DELIMITER //
DROP TRIGGER IF EXISTS trg_orders_before_insert //
CREATE TRIGGER trg_orders_before_insert
BEFORE INSERT ON orders
FOR EACH ROW
BEGIN
    -- Check the rating only when a rating is provided.
    IF NEW.Order_Rating IS NOT NULL
       AND (NEW.Order_Rating < 1 OR NEW.Order_Rating > 5) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Order rating must be between 1 and 5';
    END IF;

    -- Prevent negative order, delivery fee and discount amounts.
    IF NEW.Order_Value < 0
       OR NEW.Delivery_Fee < 0
       OR NEW.Discount_Applied < 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Order amounts cannot be negative';
    END IF;

    -- Prevent a discount from being greater than the order value.
    IF NEW.Discount_Applied > NEW.Order_Value THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Discount cannot exceed order value';
    END IF;

    -- Calculate the final payable amount automatically.
    SET NEW.Final_Amount =
        NEW.Order_Value - NEW.Discount_Applied + NEW.Delivery_Fee;
END //

-- Create an AFTER INSERT trigger to record every newly added order in the audit log.
-- We created an AFTER INSERT trigger to automatically record every newly inserted order in the order_audit_log table. 
-- It stores the order key, action type, customer ID, and final amount.

DELIMITER //
DROP TRIGGER IF EXISTS trg_orders_after_insert //
CREATE TRIGGER trg_orders_after_insert
AFTER INSERT ON orders
FOR EACH ROW
BEGIN
    -- Save the new order key, action type and order details.
    INSERT INTO order_audit_log (Order_Key, Action_Type, Details)
    VALUES (
        NEW.Order_Key,
        'INSERT',
        CONCAT('New order for customer ', NEW.Customer_ID,
               ', amount ', NEW.Final_Amount)
    );
END //

-- Create an AFTER UPDATE trigger to record changes in order status.

DELIMITER //
DROP TRIGGER IF EXISTS trg_orders_after_update_status //
CREATE TRIGGER trg_orders_after_update_status
AFTER UPDATE ON orders
FOR EACH ROW
BEGIN
    -- Save the old and new status only when the status changes.
    IF (OLD.Order_Status != NEW.Order_Status) THEN
        INSERT INTO order_status_history
            (Order_Key, Old_Status, New_Status)
        VALUES
            (OLD.Order_Key, OLD.Order_Status, NEW.Order_Status);
    END IF;
END //

DELIMITER ;

-- TEST THE TRIGGERS
   

-- Start a transaction so the test order and its trigger logs can be rolled back.
START TRANSACTION;

-- Insert a temporary test order using valid customer, restaurant and partner IDs.
-- The BEFORE INSERT trigger should calculate Final_Amount as 500 - 50 + 40 = 490.

INSERT INTO orders
    (Order_Key, Order_ID, Order_Date, Customer_ID, Restaurant_ID, Region,
     Delivery_Partner_ID, Order_Value, Delivery_Fee, Discount_Applied,
     Final_Amount, Payment_Mode, Order_Status,
     Delivery_Time_Minutes, Order_Rating, Festival_Flag)
SELECT
    (SELECT MAX(Order_Key) + 1 FROM orders),
    'TEST_TRIGGER', '2025-12-31', Customer_ID, Restaurant_ID, Region,
    Delivery_Partner_ID, 500, 40, 50, 0, 'UPI', 'Delivered',
    30, 5, 1
FROM orders
LIMIT 1;

-- Check that the BEFORE INSERT trigger calculated the final amount as 490.
SELECT Order_Key, Order_ID, Final_Amount
FROM orders
WHERE Order_ID = 'TEST_TRIGGER';

-- Check that the AFTER INSERT trigger wrote a record to the audit log.
SELECT *
FROM order_audit_log
ORDER BY Log_ID DESC
LIMIT 1;

-- Update the temporary order status to test the AFTER UPDATE trigger.
UPDATE orders
SET Order_Status = 'Returned'
WHERE Order_Key = (
    SELECT Order_Key
    FROM (
        SELECT Order_Key
        FROM orders
        WHERE Order_ID = 'TEST_TRIGGER'
        LIMIT 1
    ) AS temp
);

-- Check that the old and new statuses were saved in the history table.
SELECT *
FROM order_status_history
ORDER BY History_ID DESC
LIMIT 1;

-- Undo the temporary order and the log/history rows created by the triggers.
ROLLBACK;

-- EVENT SCHEDULER

-- Check whether the MySQL Event Scheduler is enabled.
SHOW VARIABLES LIKE 'event_scheduler';

-- SET GLOBAL event_scheduler = ON;

-- Remove the previous event definition so this script can be run again.
DROP EVENT IF EXISTS ev_daily_maintenance;

-- Create an event that runs the backup and KPI refresh procedure once every day.
CREATE EVENT ev_daily_maintenance
ON SCHEDULE EVERY 1 DAY
STARTS CURRENT_TIMESTAMP + INTERVAL 1 DAY
DO
    CALL sp_daily_maintenance();

-- Confirm that the daily event has been created.
SHOW EVENTS FROM food_delivery;

-- ESSENTIAL DATABASE VALIDATION

-- Check that all orders have matching customer, restaurant and delivery partner records.
-- All three Bad_Rows results should be zero.
SELECT 'Customer mismatch' AS Check_Name, COUNT(*) AS Bad_Rows
FROM orders o
LEFT JOIN customers c ON o.Customer_ID = c.Customer_ID
WHERE c.Customer_ID IS NULL
UNION ALL
SELECT 'Restaurant mismatch', COUNT(*)
FROM orders o
LEFT JOIN restaurants r ON o.Restaurant_ID = r.Restaurant_ID
WHERE r.Restaurant_ID IS NULL
UNION ALL
SELECT 'Delivery partner mismatch', COUNT(*)
FROM orders o
LEFT JOIN delivery_partners d
    ON o.Delivery_Partner_ID = d.Delivery_Partner_ID
WHERE d.Delivery_Partner_ID IS NULL;

-- Check that the Order_Key primary key has no duplicate values.
SELECT COUNT(*) - COUNT(DISTINCT Order_Key) AS Duplicate_Order_Keys
FROM orders;

-- Check that the stored final amount follows the project calculation.
SELECT COUNT(*) AS Incorrect_Final_Amounts
FROM orders
WHERE Final_Amount <> Order_Value - Discount_Applied + Delivery_Fee;

-- Show the number of rows stored in the daily KPI summary table.
SELECT COUNT(*) AS KPI_Days
FROM daily_kpi_summary;



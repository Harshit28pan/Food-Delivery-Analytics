USE food_delivery;

-- refresh the backup so it has the latest orders
CALL sp_backup_orders();

-- aggregated table 1: region wise (Which regions have the highest demand?)

DROP TABLE IF EXISTS agg_region_summary;
CREATE TABLE agg_region_summary AS
SELECT Region,
       COUNT(*) AS Total_Orders,
       SUM(CASE WHEN Order_Status = 'Delivered' THEN 1 ELSE 0 END) AS Delivered_Orders,
       SUM(CASE WHEN Order_Status = 'Cancelled' THEN 1 ELSE 0 END) AS Cancelled_Orders,
       SUM(CASE WHEN Order_Status = 'Returned' THEN 1 ELSE 0 END) AS Returned_Orders,
       SUM(CASE WHEN Order_Status = 'Delivered' THEN Final_Amount ELSE 0 END) AS Delivered_Revenue,
       ROUND(AVG(Order_Value), 2) AS Avg_Order_Value,
       ROUND(AVG(Delivery_Time_Minutes), 2) AS Avg_Delivery_Time,
       ROUND(AVG(Order_Rating), 2) AS Avg_Rating
FROM orders
GROUP BY Region;

-- aggregated table 2: month wise by region (How does demand change in festive months?)

DROP TABLE IF EXISTS agg_monthly_summary;
CREATE TABLE agg_monthly_summary AS
SELECT YEAR(Order_Date) AS Order_Year,
       MONTH(Order_Date) AS Order_Month,
       Region,
       MAX(Festival_Flag) AS Festival_Flag,
       COUNT(*) AS Total_Orders,
       SUM(CASE WHEN Order_Status = 'Delivered' THEN Final_Amount ELSE 0 END) AS Delivered_Revenue,
       ROUND(AVG(Order_Value), 2) AS Avg_Order_Value
FROM orders
GROUP BY YEAR(Order_Date), MONTH(Order_Date), Region;

-- aggregated table 3: customer type wise (Which customer segment gives the most revenue?)

DROP TABLE IF EXISTS agg_customer_type_summary;
CREATE TABLE agg_customer_type_summary AS
SELECT c.Customer_Type,
       COUNT(DISTINCT o.Customer_ID) AS Active_Customers,
       COUNT(*) AS Total_Orders,
       SUM(CASE WHEN o.Order_Status = 'Delivered' THEN o.Final_Amount ELSE 0 END) AS Delivered_Revenue,
       ROUND(AVG(o.Order_Value), 2) AS Avg_Order_Value,
       ROUND(AVG(o.Order_Rating), 2) AS Avg_Rating
FROM orders o
JOIN customers c ON o.Customer_ID = c.Customer_ID
GROUP BY c.Customer_Type;

-- aggregated table 4: delivery partner wise (Which partners and vehicles are the fastest?)

DROP TABLE IF EXISTS agg_partner_summary;
CREATE TABLE agg_partner_summary AS
SELECT d.Delivery_Partner_ID, d.Vehicle_Type, d.Region,
       COUNT(o.Order_Key) AS Total_Orders,
       ROUND(AVG(o.Delivery_Time_Minutes), 2) AS Avg_Delivery_Time,
       ROUND(AVG(o.Order_Rating), 2) AS Avg_Rating
FROM delivery_partners d
LEFT JOIN orders o ON d.Delivery_Partner_ID = o.Delivery_Partner_ID
GROUP BY d.Delivery_Partner_ID, d.Vehicle_Type, d.Region;

-- check the new tables
SHOW TABLES;
SELECT COUNT(*) AS Backup_Rows FROM orders_backup;
SELECT * FROM agg_region_summary;
SELECT COUNT(*) AS Month_Region_Rows FROM agg_monthly_summary;
SELECT * FROM agg_customer_type_summary;
SELECT COUNT(*) AS Partner_Rows FROM agg_partner_summary;

SELECT * FROM agg_region_summary;
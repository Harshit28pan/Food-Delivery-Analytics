# Food Delivery Analytics Case Study

**Case Study Description:**  
Analyze Food Delivery Demand Across Regions to Inform Market Expansion & Logistics
This dataset supports insights into customer behavior, restaurant performance, delivery partner efficiency, and regional demand patterns to guide logistics optimization and service quality improvements.
---

## Dataset Overview

---

### 1. Customers (22,000 records)
**Purpose:** Captures customer demographics, loyalty type, spending behavior, and cuisine preferences.  
**Key Fields:**
- `Customer_ID` – Unique identifier for each customer
- `Gender` – Male/Female/Other
- `Age_Group` – Segmented age ranges (18–25, 26–35, etc.)
- `City` – Region classification (Urban, Semi‑Urban, Metropolitian)
- `Customer_Type` – New, Returning, Loyal
- `Total_Orders` – Number of orders placed
- `Average_Spend` – Average spend per order (₹)
- `Preferred_Cuisine` – Cuisine preference (Italian, North Indian, South Indian, Fast Food, etc.)

---

### 2. Delivery Partners (1,100 records)
**Purpose:** Tracks delivery partner performance, speed, reliability, and ratings.  
**Key Fields:**
- `Delivery_Partner_ID` – Unique identifier for each partner
- `Partner_Name` – Partner full name
- `Vehicle_Type` – Bike, Scooter, Car, Bicycle
- `Avg_Delivery_Speed_KMPH` – Average delivery speed
- `Successful_Deliveries` – Count of on‑time deliveries
- `Delayed_Deliveries` – Count of late deliveries
- `Avg_Customer_Rating` – Average rating from customers
- `Region` – Operational region
- `Delivery_Efficiency_Score` – Composite score of speed, rating, and reliability

---

### 3. Orders (99,834 records)
**Purpose:** Core transactional table linking customers, restaurants, and delivery partners.  
**Key Fields:**
- `Order_ID` – Unique order identifier
- `Order_Date` – Date of order (2023–2025)
- `Customer_ID` – Linked to Customers table
- `Restaurant_ID – Linked to Restaurants table
- `Region` – Order region
- `Delivery_Partner_ID` – Linked to Delivery Partners table
- `Order_Value` – Bill amount before discount/fees
- `Delivery_Fee` – Fee charged for delivery
- `Discount_Applied` – Discount applied to order
- `Final_Amount` – Net payable amount (Order_Value – Discount + Fee)
- `Payment_Mode` – UPI, Card, Wallet, Cash
- `Order_Status` – Delivered, Cancelled, Returned
- `Delivery_Time_Minutes` – Actual delivery duration
- `Order_Rating` – Customer rating (1–5 stars)
- `Festival_Flag` – Boolean flag for festive season orders  

---
### 4. Restaurants (550 records)
**Purpose:** Captures restaurant capacity, ratings, and cuisine diversity.  
**Key Fields:**
- `Restaurant_ID` – Unique identifier for each restaurant
- `City` – Region classification
- `Avg_Preparation_Time_Minutes` – Average cooking time
- `Avg_Rating` – Average customer rating
- `Order_Capacity_Per_Day` – Daily order capacity
- `Restaurant_Name` – Synthetic restaurant name
- `Cuisine_Type` – Cuisine offered (Fast Food, Italian, Indian, etc.)

---

##  Note
All datasets are synthetic but designed to resemble realistic food delivery demand, customer behavior, restaurant performance, and logistics patterns for educational and analytical purposes.


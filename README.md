# Food Delivery Demand Analysis

An end-to-end Data Analytics project focused on analyzing food delivery operations, customer behavior, restaurant performance, delivery efficiency, and revenue trends using Python, SQL, Excel, Power BI, and Streamlit.

## Project Overview

This project analyzes food delivery data to understand business performance and identify meaningful insights related to orders, customers, restaurants, and delivery partners.

The project follows a complete data analytics workflow, starting from data cleaning and database integration to exploratory data analysis, statistical analysis, regression, forecasting, and interactive dashboard development.

## Project Objectives

- Clean and preprocess raw food delivery datasets.
- Store and manage data using MySQL.
- Perform Exploratory Data Analysis (EDA).
- Analyze customer behavior and ordering patterns.
- Evaluate restaurant and delivery partner performance.
- Apply statistical techniques and hypothesis testing.
- Build regression models to predict daily revenue.
- Forecast revenue for 2026.
- Create interactive dashboards for business insights.

## Technologies Used

| Category | Tools & Technologies |
|---|---|
| Programming | Python |
| Data Manipulation | Pandas, NumPy |
| Data Visualization | Matplotlib, Seaborn |
| Statistical Analysis | SciPy |
| Machine Learning | Scikit-learn |
| Database | MySQL |
| Database Integration | SQLAlchemy |
| Business Intelligence | Power BI |
| Spreadsheet Analysis | Microsoft Excel |
| Web Dashboard | Streamlit |

## Dataset Description

The project uses four main datasets:

1. **Orders** – Order details, order value, delivery time, payment mode, discounts, and order status.
2. **Customers** – Customer demographics, age group, customer type, and purchasing behavior.
3. **Restaurants** – Restaurant information, cuisine type, ratings, and preparation time.
4. **Delivery Partners** – Delivery partner details, vehicle type, delivery speed, and performance metrics.

The datasets are cleaned and combined to perform further analysis.

## Project Workflow

### 1. Data Cleaning and Preprocessing
- Handled duplicate records and missing values.
- Standardized text values and IDs.
- Corrected data types and formatting.
- Performed data validation and consistency checks.
- Exported cleaned datasets into CSV files.

### 2. SQL and Database Integration
- Imported cleaned datasets into MySQL.
- Created database relationships using primary and foreign keys.
- Performed SQL queries and aggregations.
- Created backup and summary tables.
- Connected MySQL with Python for further analysis.

### 3. Exploratory Data Analysis (EDA)
Performed three types of analysis:

- **Univariate Analysis:** Studied individual variables using histograms, boxplots, and count plots.
- **Bivariate Analysis:** Analyzed relationships between two variables.
- **Multivariate Analysis:** Explored relationships among multiple business variables.

### 4. Statistical Analysis
Applied statistical techniques including:

- Simple Random Sampling
- Stratified Sampling
- Systematic Sampling
- Central Limit Theorem (CLT)
- Normality Testing
- One-Sample Z-Test
- Two-Sample Z-Test
- One-Sample T-Test
- Two-Sample T-Test
- Paired T-Test

### 5. Regression and Revenue Forecasting

Applied Linear Regression to analyze and predict daily revenue.

- Created daily revenue data using delivered orders.
- Built and evaluated regression models.
- Compared actual and predicted revenue.
- Evaluated model performance using R², MAE, and RMSE.
- Generated a 2026 revenue forecast.

**Target Variable:** Daily_Revenue

## Dashboards

### Excel Dashboard
An interactive Excel dashboard developed to explore food delivery performance and business metrics.

### Power BI Dashboard
An interactive business intelligence dashboard for analyzing sales, revenue, customer behavior, and delivery performance.

### Streamlit Dashboard
A Python-based interactive dashboard with five sections:

- **Overview:** Business KPIs, monthly orders, and order status analysis.
- **Delivery Partners:** Delivery partner performance and efficiency.
- **Restaurants:** Restaurant performance and operational insights.
- **2026 Forecast:** Revenue prediction and forecasting analysis.
- **Statistics:** Statistical tests and analytical results.

## Project Folder Structure

```text
Food-Delivery-Analytics/
│
├── dataset/
│   ├── Customers.xlsx
│   ├── Orders.xlsx
│   ├── Restaurants.xlsx
│   └── Delivery_Partners.xlsx
│
├── cleaned_dataset/
│
├── final_dataset/
│   └── food_delivery_final.xlsx
│
├── Documents/
│   ├── EDA_Observation.docx
│   └── er_diagram.png
│
├── SQL/
│   ├── Keys.sql
│   ├── Mysql.sql
│   └── Agg_tab.sql
│
├── eda_charts/
├── statistics_charts/
├── regression_charts/
│
├── FoodDelivery_Streamlit/
│   ├── app.py
│   ├── config.py
│   ├── data/
│   └── src/
│
├── Data_Cleaning.py
├── Mysql_to_Python.py
├── EDA.py
├── Statistics.py
├── Regression.py
├── main.py
│
├── Excel_dashboard.xlsx
├── powerbi.pbix
└── Project_Word_document_final.docx
```

## How to Run the Project

### Prerequisites

- Python 3.x
- MySQL Server and MySQL Workbench
- Microsoft Excel
- Power BI Desktop

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/Food-Delivery-Analytics.git
```

### 2. Navigate to the Project Folder

```bash
cd Food-Delivery-Analytics
```

### 3. Install Required Python Libraries

```bash
pip install pandas numpy matplotlib seaborn scipy scikit-learn openpyxl sqlalchemy pymysql streamlit
```

### 4. Configure MySQL

- Start your MySQL Server.
- Create the `food_delivery` database.
- Configure the database connection in the Python project if required.
- Run the SQL scripts available in the SQL folder.

### 5. Run the Main Python Project

```bash
python main.py
```

Follow the instructions displayed in the terminal to select the analysis steps.

### 6. Run the Streamlit Dashboard

```bash
cd FoodDelivery_Streamlit
```

```bash
streamlit run app.py
```

The interactive dashboard will open in your web browser.

## Key Learning Outcomes

- Practical experience with data cleaning and preprocessing.
- Working with relational databases and SQL queries.
- Performing EDA and statistical analysis.
- Understanding regression and revenue forecasting.
- Creating interactive dashboards using Excel, Power BI, and Streamlit.
- Combining multiple tools to develop an end-to-end data analytics solution.

## Author

**Harshit Pandey**

B.Tech – Computer Science and Engineering (AI)

**Project Domain:** Data Analytics

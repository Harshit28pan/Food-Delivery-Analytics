# 🍔 Food Delivery Analytics

### End-to-End Data Analytics Project | Python • SQL • Excel • Power BI • Streamlit

An end-to-end Data Analytics project focused on analyzing food delivery operations, customer behavior, restaurant performance, delivery efficiency, and revenue trends. This project combines data cleaning, SQL database management, exploratory data analysis, statistical analysis, regression, forecasting, and interactive dashboard development to generate meaningful business insights.

---

## 📌 Project Overview

The **Food Delivery Analytics** project aims to understand the overall performance of a food delivery business by analyzing multiple datasets related to orders, customers, restaurants, and delivery partners.

The project follows a complete data analytics workflow, starting from raw data cleaning and database integration to advanced statistical analysis, revenue prediction, and interactive dashboard development.

The objective is to transform raw data into actionable insights that can help businesses understand customer preferences, monitor operational efficiency, evaluate restaurant performance, and analyze revenue trends.

## 🎯 Project Objectives

- Clean and preprocess raw food delivery datasets.
- Integrate multiple datasets using Python and MySQL.
- Perform Exploratory Data Analysis (EDA).
- Analyze customer ordering patterns and purchasing behavior.
- Evaluate restaurant and delivery partner performance.
- Apply statistical techniques and hypothesis testing.
- Build regression models to predict daily revenue.
- Generate future revenue forecasts for 2026.
- Develop interactive dashboards using Excel, Power BI, and Streamlit.

## 🛠️ Technologies Used

| Category | Tools & Technologies |
|---|---|
| Programming Language | Python |
| Data Manipulation | Pandas, NumPy |
| Data Visualization | Matplotlib, Seaborn |
| Statistical Analysis | SciPy |
| Machine Learning | Scikit-learn |
| Database | MySQL |
| Database Connectivity | SQLAlchemy, PyMySQL |
| Business Intelligence | Power BI |
| Spreadsheet Analysis | Microsoft Excel |
| Dashboard Development | Streamlit |
| Documentation | MS Word |

## 📂 Dataset Description

The project uses four main datasets:

1. **Orders Dataset:** Contains order details, order value, delivery time, payment methods, discounts, and order status.
2. **Customers Dataset:** Contains customer information, demographics, age groups, customer types, and purchasing behavior.
3. **Restaurants Dataset:** Contains restaurant details, cuisine types, ratings, and preparation time.
4. **Delivery Partners Dataset:** Contains delivery partner information, vehicle types, delivery speed, and performance metrics.

These datasets are cleaned, validated, and combined to create a final dataset for comprehensive analysis.

## ⚙️ Project Workflow

### 1. Data Cleaning and Preprocessing (Python)

- Handled missing values and duplicate records.
- Standardized text values and identifiers.
- Corrected data types and formatting.
- Performed data validation and consistency checks.
- Exported cleaned datasets for further analysis.

### 2. SQL and Database Integration

- Imported cleaned datasets into MySQL.
- Created relational database structures using Primary Keys and Foreign Keys.
- Performed SQL queries, joins, and aggregations.
- Created backup and summary tables.
- Connected MySQL with Python for further analysis.

### 3. Exploratory Data Analysis (EDA)

Performed three major types of analysis:

- **Univariate Analysis:** Studied individual variables using histograms, boxplots, and count plots.
- **Bivariate Analysis:** Explored relationships between two variables.
- **Multivariate Analysis:** Analyzed relationships among multiple business variables.

### 4. Statistical Analysis

Applied statistical techniques to understand data distributions, sample behavior, and business-related hypotheses.

Techniques included:

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
- Hypothesis Testing

### 5. Regression and Revenue Forecasting

Applied Linear Regression to analyze and predict daily revenue.

Key activities:

- Aggregated delivered orders into daily revenue data.
- Selected relevant independent variables.
- Built and evaluated regression models.
- Compared actual and predicted revenue.
- Evaluated model performance using R², MAE, and RMSE.
- Generated revenue forecasts for 2026.

**Target Variable:** `Daily_Revenue`

## 📊 Dashboards

### 1. Excel Dashboard

An interactive Excel dashboard developed to explore food delivery performance and business metrics.

### 2. Power BI Dashboard

An interactive business intelligence dashboard designed to analyze:

- Sales and revenue performance
- Customer behavior
- Delivery performance
- Business trends and key performance indicators

### 3. Streamlit Dashboard

A Python-based interactive dashboard containing five major sections:

- **Overview:** Business KPIs, monthly orders, and order status analysis.
- **Delivery Partners:** Delivery partner performance and efficiency.
- **Restaurants:** Restaurant performance and operational insights.
- **2026 Forecast:** Revenue prediction and forecasting analysis.
- **Statistics:** Statistical tests and analytical results.

## 📁 Project Structure

```text
Food-Delivery-Analytics/
│
├── Documents/
│
├── FoodDelivery_Streamlit/
│   ├── app.py
│   ├── config.py
│   ├── data/
│   └── src/
│
├── SQL/
│
├── cleaned_dataset/
├── dataset/
├── final_dataset/
│
├── eda_charts/
├── regression_charts/
├── statistics_charts/
│
├── Data_Cleaning.py
├── EDA.py
├── Statistics.py
├── Regression.py
├── Mysql_to_Python.py
├── main.py
│
├── Excel_dashboard.xlsx
├── powerbi.pbix
├── SQL.sql
├── README.md
└── Project_Word_document_final.docx
```

## 🚀 How to Run the Project

### Prerequisites

Make sure the following tools are installed:

- Python 3.x
- MySQL Server and MySQL Workbench
- Microsoft Excel
- Power BI Desktop

### Step 1: Clone the Repository

```bash
git clone https://github.com/Harshit28pan/Food-Delivery-Analytics.git
```

### Step 2: Navigate to the Project Folder

```bash
cd Food-Delivery-Analytics
```

### Step 3: Install Required Libraries

```bash
pip install pandas numpy matplotlib seaborn scipy scikit-learn openpyxl sqlalchemy pymysql streamlit
```

### Step 4: Configure MySQL

- Start your MySQL Server.
- Create the required database.
- Configure database connection details in the project.
- Execute the SQL scripts provided in the repository.

### Step 5: Run the Python Project

```bash
python main.py
```

Follow the instructions displayed in the terminal to execute the required analysis.

### Step 6: Run the Streamlit Dashboard

```bash
cd FoodDelivery_Streamlit
```

```bash
streamlit run app.py
```

The interactive dashboard will open in your default web browser.

## 💡 Key Learning Outcomes

Through this project, I gained practical experience in:

- Data cleaning and preprocessing using Python.
- Database management and SQL operations.
- Exploratory Data Analysis and data visualization.
- Statistical analysis and hypothesis testing.
- Linear Regression and revenue forecasting.
- Dashboard development using Excel and Power BI.
- Building interactive analytical applications using Streamlit.
- Integrating multiple tools into an end-to-end Data Analytics workflow.

## 👨‍💻 Author

**Harshit Pandey**

B.Tech – Computer Science and Engineering (AI)

Project Domain: Data Analytics

GitHub: [Harshit28pan](https://github.com/Harshit28pan)

---

⭐ If you find this project interesting, feel free to explore the repository and share your feedback!

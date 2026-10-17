# Ganesh Nashta Center - Sales & Business Intelligence Dashboard

A Python-based desktop application developed to manage sales, billing, menu items, customers, inventory, and business analytics for Ganesh Nashta Center.

The project uses Tkinter for the graphical user interface and MySQL for database management. It also provides sales analysis, demand forecasting, food-waste tracking, inventory alerts, and reporting features.

---

## Project Overview

Small food businesses often manage sales, billing, inventory, and customer information manually. This can lead to calculation errors, time-consuming operations, and difficulties in tracking business performance.

The Ganesh Nashta Center Sales Dashboard provides a centralized application to simplify these operations, maintain sales records, and display useful business information through a graphical dashboard.

## Objectives

1. To add and manage products and customers easily.
2. To make bills quickly by selecting products and quantity.
3. To print bills and save the sales details.
4. To see total sales and sold products on the dashboard.

---

## Features

### 1. Login System
- Provides a login interface.
- Validates user credentials before opening the dashboard.

### 2. Menu Management
- Add new menu items.
- View existing menu items.
- Update item information.
- Delete menu items.
- Manage categories, selling prices, cost prices, and available quantities.

### 3. Customer Management
- Add customer details.
- View customer records.
- Update customer information.
- Delete customer records.

### 4. Sales and Billing
- Select customers and menu items.
- Enter item quantities.
- Calculate bill amounts automatically.
- Check available stock before recording a sale.
- Save sales transactions in MySQL.
- Update item quantities after a successful sale.

### 5. Bill Generation and Printing
- Generate bills containing transaction details.
- Save generated bills in the Bills folder.
- Open saved bills.
- Send bills to the default printer.

### 6. Sales Dashboard
- Display total sales.
- Display total profit.
- Show the number of orders.
- Show the total quantity of items sold.
- Visualize sales trends using charts.

### 7. Inventory Management
- Maintain ingredient quantities.
- Set minimum stock levels.
- Identify ingredients that require replenishment.

### 8. Food-Waste Tracking
- Record prepared quantities.
- Record sold quantities.
- Calculate wasted quantities.
- Store reasons for food waste.

### 9. Sales Analysis
- Identify best-selling menu items.
- Analyze item quantities, revenue, and profit.
- Review sales by payment method.
- Visualize sales trends.

### 10. Demand Forecasting
- Analyze historical sales data.
- Use Linear Regression to estimate future demand.
- Display a seven-day demand forecast.

### 11. Alerts and Reports
- Identify low-stock ingredients.
- Display sales and food-waste information.
- Generate sales summaries.
- Filter reports by date.
- Export report data to CSV.

---

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Application logic |
| Tkinter | Graphical user interface |
| MySQL | Database management |
| mysql-connector-python | Python-MySQL connectivity |
| Pandas | Data analysis and processing |
| NumPy | Numerical operations |
| Matplotlib | Charts and data visualization |
| Scikit-learn | Demand forecasting |
| GitHub | Source code hosting |

---

## Project Structure

```text
GaneshNashtaDashboard/
│
├── main.py
├── login.py
├── database.py
├── dashboard.py
├── menu.py
├── customers.py
├── sales.py
├── inventory.py
├── waste.py
├── analysis.py
├── forecast.py
├── alerts.py
├── reports.py
├── theme.py
├── README.md
├── requirements.txt
├── .gitignore
│
└── Bills/
# Grocery Sales Report Generator

## Description
I created this script as a project to apply the knowledge pandas, matplotlib, and seaborn I gained from the Udemy course “Python A-Z: Python for Data Science” by Kirill Eremenko. The script is designed to analyze and report sales data from Corvus Coffee Roasters, based on the sales reports provided by their grocery distributor, Whisha. The data is downloaded as a CSV file through the distributor’s portal. To run the program, use the provided sample file, “Sales and Credits by Store.csv.” This project utilizes Pandas, Seaborn, 
and Matplotlib for data analysis and visualization.

As a wholesale manager, I frequently need to calculate key metrics to track our grocery store sales performance and share the results with my team. This script streamlines that process by making report generation quick and repeatable, enabling us to easily analyze product performance and distribute reports across teams and to our supervisors.

### Key Features:
The script performs several tasks:

1. Cleans and prepares the data for analysis by removing unnecessary rows and columns, renaming columns, and converting sales data to integers.
2. Calculates various sales metrics, including total sales by customer group, month, and year, as well as customer growth rates.
3. Generates visualizations like bar charts, pie charts, and facet grids to represent sales data for different customer groups, products, and months.
4. Creates a PDF report summarizing key sales metrics and includes visualizations for insights.

## Project Structure
This project is structured as follows:

```bash
├── data/
│   └── Sales and Credits by Store.csv      # Example CSV data file for generating reports
├── GrocerySalesReport.py                 # Main script for generating the sales report
├── requirements.txt        # Required Python packages
├── report.pdf              # Generated sales report (example output)
├── visualizations.pdf      # Generated visualizations (example output)
└── README.md               # Project documentation
```

## Requirements
The following Python packages are required to run this project:

- `pandas` — for data manipulation and analysis
- `matplotlib` — for generating visualizations
- `seaborn` - for generating and stylizing visualizations
- `reportlab` — for PDF generation
- `PyPDF2` — for merging PDFs

You can install all dependencies by running:

```bash
pip install -r requirements.txt
```

The following CSV file is needed to run the project:

"Sales and Credits by Store.csv"

This file is only accessible via the distributor portal and has been adjusted with pseudo numbers.


## Usage
To run the script and generate the sales report:

```bash
python3 GrocerySalesReport.py
```

This will:


1. Read the data from data/Sales and Credits by Store.csv
2. Process the data
3. Output a sales_report.pdf with the analysis.





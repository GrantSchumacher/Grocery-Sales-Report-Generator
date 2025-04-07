# Grocery Sales Report Generator

## Description
This script generates a report with both numerical and visual insights into bagged whole bean coffee sales, helping with business decision-making for the local coffee roaster I work for.

I created this script to apply the knowledge I gained from the Udemy course "Python A-Z: Python for Data Science" by Kirill Eremenko, focusing on Pandas, Matplotlib, and Seaborn to a real world challenge. The script is designed to analyze sales data and report insights and visualizations based on the sales reports provided by the coffee roaster's grocery store distributor. The data is downloaded as a CSV file through the distributor’s portal and is not shared with the public - therefore, to run the program, use the provided sales data file, “Sales and Credits by Store.csv.”.

As a wholesale manager, I frequently need to calculate key metrics to track our grocery store sales performance and share the results with my team. This script streamlines that process by making report generation quick and repeatable, enabling us to easily analyze and visualize product performance and distribute reports across teams and to my supervisors.

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
├── GrocerySalesReport.py                   # Main script for generating the sales report
├── .gitignore                              # Ignore virtual environment 
├── requirements.txt                        # Required Python packages
├── report.pdf                              # Generated sales report (example output)
├── visualizations.pdf                      # Generated visualizations (example output)
└── README.md                               # Project documentation
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





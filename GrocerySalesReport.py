"""
Project: Grocery Sales Report Generator

Author: Grant Schumacher
Date: April 2025
Description:

I created this script as part of a project to apply the knowledge I gained from the Udemy course “Python A-Z: Python for Data Science” by Kirill Eremenko. The script is 
designed to analyze and report sales data from Corvus Coffee Roasters, based on the sales reports provided by their grocery distributor, Whisha. The data is downloaded 
as a CSV file through the distributor’s portal. To run the program, use the provided sample file, “Sales and Credits by Store.csv.” This project utilizes Pandas, Seaborn, 
and Matplotlib for data analysis and visualization.

As a wholesale manager, I frequently need to calculate key metrics to track our grocery store sales performance and share the results with my team. This script streamlines 
that process by making report generation quick and repeatable, enabling us to easily analyze product performance and distribute reports across teams and to our supervisors.

The script performs several tasks:

1. Cleans and prepares the data for analysis by removing unnecessary rows and columns, renaming columns, and converting sales data to integers.
2. Calculates various sales metrics, including total sales by customer group, month, and year, as well as customer growth rates.
3. Generates visualizations like bar charts, pie charts, and facet grids to represent sales data for different customer groups, products, and months.
4. Creates a PDF report summarizing key sales metrics and includes visualizations for insights.

The primary objective of this code is to: 
a) Put my studied knowledge of Pandas, Seaborn, and Matplotlib to the test in a read world application
b) Provide a comprehensive sales report that includes both numerical and visual insights for business decision-making.

Dependencies:
- pandas
- seaborn
- matplotlib
- reportlab
- PyPDF2
"""

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import re
from PyPDF2 import PdfMerger


file_name = "Data/Sales and Credits by Store.csv"

#Takes a file path for the Whisha Tableau Sales and Credits by Store Tableau CSV report and returns a cleaned data frame without total columns or rows
def load_data(file_path):
    data = pd.read_csv(file_path, encoding='utf-16', sep='\t', header=[0, 1])

    new_columns = []

    #Combine the multi level headers of year and month.
    for column in data.columns:

        #If there are two levels join them 
        if column[0] and column[1]:
            new_column = '_'.join(column)

        #Otherwise use the second level 
        else:
            new_column = col[1] 

        new_columns.append(new_column)
        
    data.columns = new_columns

    
    #Rename the first three columns
    data.rename(columns={
        data.columns[0]: 'Customer Group',
        data.columns[1]: 'Customer',
        data.columns[2]: 'Products'
    }, inplace=True)
    
    #Drop the Grand Total Column 
    data.drop('Grand Total_Total', axis = 1, inplace = True)
    
    #Drop the last row of the data. The last row in the given format is a row of totals
    data.drop(data.index[-1], inplace=True)

    #Convert all cells to the right of column 3 (all the sales numbers) to integers. Replace NAN with 0.
    #Selecting all rows and all columns to the right of column 3. Then applying a function to each, converting cell to numeric and filling nan with 0
    data.iloc[:, 3:] = data.iloc[:, 3:].apply(pd.to_numeric, errors='coerce').fillna(0).astype(int) 
    
    return data

#Returns the sales for a given year
def total_year_sales(data, year):
    df = data.copy()
    ytd = df.filter(like = str(year)).sum().sum()
    return ytd


#Returns growth percentage between two periods 
def growth(current, previous):
    growth = (current - previous)/current
    growth *= 100
    growth = round(growth, 2)
    return growth

#Returns the lifetime sales of customer group. If no customer group is specified returns data frame of total sales of each customer group as a Series
def lifetime_sales_by_customer_group(data, customer_group=None):

    df = data.copy()
    
    #Drop customer and products, we don't need them for this function

    df.drop('Customer', axis = 1, inplace = True)
    df.drop('Products', axis = 1, inplace = True)

    #Group by customer group and add together columns then rows 
    lifetime_sales = df.groupby('Customer Group').sum().sum(axis = 1)

    #Check if customer group has been specified
    if customer_group is None:
        return lifetime_sales

    else:
        #if customer group has been specified make sure the specified customer group exists
        if customer_group in lifetime_sales.index:
            #If it exists return the value of the lifetime sales of the customer group
            sales = lifetime_sales.at[customer_group]
            return sales
        else:
            #Otherwise raise an error
            raise ValueError(f"Customer group '{customer_group}' not found.")
    
    return sales


#Calculates the total sales for each month for a given year. Returns total as a series MONTH : TOTAL
def sales_by_month(data, year):
    df = data.copy()
    year_columns = df.filter(like = f"{year}_")
    month_totals = year_columns.sum(axis = 0)
    return month_totals


#Returns a data frame of the given number of top customers over the entire duration of the data set
def top_customers(data, number):
    df = data.copy()
    df['Total Units Sold'] = df.iloc[:,3:].sum(axis = 1) #Create a column called Total Units Sold and set it to the sum of all sales months
    grouped = df.groupby(['Customer Group', 'Customer'])['Total Units Sold'].sum().reset_index() 
     
    top_customers = (
        grouped.sort_values(['Customer Group', 'Total Units Sold'], ascending=[True, False]) #Sort by customer group and customer in descending order (highest performing to lowest performing)
        .groupby('Customer Group') #Group sorted data by customer group
        .head(number) #only get top number of customers
    )
    
    return top_customers


#Returns a data frame of the top products over the entire duration of the data set 
def top_products(data):
    df = data.copy()
    df['Total Units Sold'] = df.iloc[:, 3:].sum(axis = 1) #Create a column called Total Units Sold and set it to the sum of all sales months
    grouped = (
        df.groupby(['Products'])['Total Units Sold']
        .sum() #Sum the total units sold for each product after we grouped
        .reset_index() #Reset the index so that 'Products' is not the index
        .sort_values(by = 'Total Units Sold', ascending = False)
        .reset_index(drop = True) #Drop the current indices and make a new index
    )
    grouped['Products'] = grouped['Products'].str.replace("COV 12oz", "")
    grouped['Products'] = grouped['Products'].str.replace(r' \([A-Za-z]+\)', '', regex=True)  # Remove (WB)
    grouped['Products'] = grouped['Products'].str.split(' - ').str[0]  # Remove the SKU Number
    return grouped


#Returns a data frame of the top customer groups over the entire duration of the data set
def top_customer_groups(data):
    df = data.copy()
    df['Total Units Sold'] = df.iloc[:, 3:].sum(axis = 1) #Create a column called Total Units Sold and set it to the sum of all sales months
    grouped = (
        df.groupby(['Customer Group'])['Total Units Sold']
        .sum() #Sum the total units sold for each product after we grouped
        .reset_index() #Reset the index so that 'Products' is not the index
        .sort_values(by = 'Total Units Sold', ascending = False)
        .reset_index(drop = True) #Drop the current indices and make a new index
    )
    return grouped

#TOP CUSTOMERS BY MONTH
#Returns a data frame of the top number of customers for a given month
def top_customers_by_month(data, month, number):
    df = data.copy()
    result = (
        df.groupby(['Customer Group', 'Customer'])[month].sum().reset_index() #Find the total for the given month
        .rename(columns={month: month}) #Rename the column to include given month
        .sort_values(by = ['Customer Group', month], ascending = [True, False]) #Sort values ascending for customer group and descending for total sales
        .groupby('Customer Group') #Group them by customer group
        .head(number) #Only show the given number of top customers
        .reset_index(drop = True)
    )
    return result

#Returns the total units sold by all customers in all customer groups for a given month
def total_sales_by_month(data, month):
    df = data.copy()
    return df[month].sum()

#Returns the total sales for a given period. Period given as array of month strings. Can be single month.
def total_sales_by_period(data, period):
    df = data.copy()
    return df[period].sum().sum()




#Load the sales data
sales_data = load_data(file_name)



#Line Plot of total sales for a given year
def plot_sales_by_month(data, year):
    sales = []
    months = ['January', 'February', 'March', 'April', 'May', 'June',
              'July', 'August', 'September', 'October', 'November', 'December']

    #Find the total sales for each month in the given year
    sales = [total_sales_by_month(data, f"{year}_{month}") for month in months] 

    #Load months and sales into a data frame
    df = pd.DataFrame({
        'Month': months,
        'Sales': sales
    }) 

    #plot the data frame as a line plot
    sns.lineplot(data=df, x='Month', y='Sales') 
    
    plt.xticks(rotation=90)
    plt.title(f"Sales by Month for {year}", fontsize=13, fontweight='bold')
    plt.tight_layout()

#Pie Chart of customer group percentage of total sales
def plot_customer_pie_chart(data):
    df = data.copy()

    #Get all unqiue customer groups
    unique_customer_groups = df["Customer Group"].unique()  

    #Make a dictionary to store sales data
    sales_data = {}  

    #Iterate through unique customer groups
    for cg in unique_customer_groups:
        #Find the lifetime sales of each unique customer group
        sales_data[cg] = lifetime_sales_by_customer_group(df, cg) 

    #Filter out smaller accounts with less than "threshold" in sales. Iterate thrrough key value pairs in sales_data. If the value is 
    #greater than the threshold add it to filtered_data dictionary
    threshold = 1000 
    filtered_data = {}
    for k, v in sales_data.items(): 
        if v >= threshold: 
            filtered_data[k] = v 
    
    labels = list(filtered_data.keys()) #Labels for each section of the pie is the keys
    sizes = list(filtered_data.values()) #Sizes of pie is set to values
    plt.title("Customer Group Percentage of Total Sales", fontsize=13, fontweight='bold')
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=plt.cm.Paired.colors)
    plt.tight_layout()

#Bar Chart of total sales by year
def plot_yearly_growth(data, years):
    df = data.copy()
    sales = []
    
    #Iterate through given years, get the total year sales for the current year, and append to sales data
    for year in years: 
        yearly_sales = total_year_sales(df, str(year)) 
        sales.append(yearly_sales) 

    #Make bar plot
    sns.barplot(x = years, y = sales, palette="viridis") 

    plt.xlabel("Year", fontweight ="bold")
    plt.ylabel("Units Sold", fontweight ="bold")
    plt.tight_layout()

#Bar Chart of customer segmentation (total sales by customer group)
def plot_customer_group_sales(data, year):
    df = data.copy()
    
    #Filter columns by year
    year_columns = df.filter(like=f"{year}_") 
    
    #Add up total sales by row for filtered years
    df["Total Sales"] = year_columns.sum(axis=1) 

    #Group the data by customer group and sum the total sales for each group. 
    grouped_sales = df.groupby("Customer Group")["Total Sales"].sum().reset_index() 

    #Make bar plot with total sales
    sns.barplot(data = grouped_sales, x = "Customer Group", y = "Total Sales") 
    plt.xticks(rotation=90)
    plt.xlabel("Customer Group", fontweight="bold")
    plt.ylabel("Total Sales", fontweight="bold")
    plt.title(f"Customer Group Sales in {year}", fontsize=13, fontweight="bold")
    plt.tight_layout()


#Horizontal Bar Chart to show best selling products
def plot_top_products(data):
    sns.barplot(data = top_products(data), x = "Total Units Sold", y = "Products") 
    plt.xlabel("Units Sold", fontweight = "bold")
    plt.ylabel("SKU", fontweight = "bold")
    plt.title("Best Selling Products",fontsize = 13, fontweight="bold")
    plt.tight_layout()



#Sales by product and customer group
def plot_product_sales_by_customer_group(data, year):
    df = data.copy()

    #Filter the columns for the given year
    year_columns = df.filter(like=str(year)) 
    
    #Add rows for total units sold for the given year
    df['Total Units Sold'] = year_columns.sum(axis=1)

    #Group the data by customer group and products then add together the total units sold
    grouped = df.groupby(['Customer Group', 'Products'])['Total Units Sold'].sum().reset_index()

    #Get just the SKU Name instead of the UPC code and unit size
    grouped['Products'] = grouped['Products'].str.replace("COV 12oz", "")
    grouped['Products'] = grouped['Products'].str.replace(r' \([A-Za-z]+\)', '', regex=True)  # Remove (WB) whole bean indicator 
    grouped['Products'] = grouped['Products'].str.split(' - ').str[0]  # Remove the SKU Number

    #Pivot so that each product is a row, customer groups are columns, and values are total units sold
    grouped = grouped.pivot(index='Products', columns='Customer Group', values='Total Units Sold') 

    #Plot a stacked bar chart
    grouped.plot(kind='bar', stacked=True, figsize=(15, 8), colormap='Set1') 


    plt.title(f"Sales by SKU and Customer Group {year}", fontsize=14, fontweight='bold')
    plt.xlabel("Product", fontweight='bold')
    plt.ylabel("Total Units Sold", fontweight='bold')
    plt.legend(title="Customer Group", bbox_to_anchor=(.9, 1), loc='upper left')
    plt.tight_layout()


    

#Facet grid of customer product sales by month in customer group for given year
def plot_customer_group_facet_grid(data, year, customer_group):
    df = data.copy()
    
    #Filter sales for a given year
    year_columns = df.filter(like = str(year)) 

    #Filter data frame to only the year specified
    df = df[['Customer Group', 'Customer', 'Products'] + list(year_columns.columns)] 

    #Filter dataframe for specified customer group
    df = df[df['Customer Group'] == customer_group]


    #Transform from wide formate to long format
    #Keep 'Customer Group', 'Customer', and 'Products' as identifier columns.
    #Convert year-based columns into two new columns: 'Month' (former column names) and 'Units Sold' (values).
    #Melt was created with the help of Chat gpt
    sales_by_customer_by_product = df.melt(id_vars = ["Customer Group", "Customer", "Products"],
                                           value_vars=year_columns.columns,
                                           var_name="Month", 
                                           value_name="Units Sold")

    #Filter out any products that are less than 0 sold
    sales_by_customer_by_product = sales_by_customer_by_product[sales_by_customer_by_product["Units Sold"] > 0]

    #Order the months for the bar chart
    month_order = [f"{year}_January", f"{year}_February", f"{year}_March", f"{year}_April", f"{year}_May", f"{year}_June", f"{year}_July", f"{year}_August", f"{year}_September", f"{year}_October", f"{year}_November", f"{year}_December"]

    #Create Facet grid
    grid = sns.FacetGrid(sales_by_customer_by_product, col="Customer", hue="Products", col_wrap = 2, height = 4, aspect = 1.5)

    #Map bar plots to facet grid
    grid.map(sns.barplot, "Month", "Units Sold", order = month_order)

    grid.set_axis_labels("Month", "Units Sold")
    grid.set_titles("{col_name}", fontweight = 'bold')
    grid.set_xticklabels(rotation=45)
    grid.fig.subplots_adjust(top=.95)
    grid.fig.suptitle(f"Product Sales by store for {customer_group} in {year}", fontsize=16, fontweight='bold')
    grid.add_legend(title="Product")



# Function to generate a report in PDF format with both text and visualizations
def generate_report(data, year, output_filename="sales_report.pdf"):
  
    pdf = SimpleDocTemplate(output_filename, pagesize = letter)
    elements = []

    styles = getSampleStyleSheet()

    #Create the title
    elements.append(Paragraph(f"Sales Report for {year}", styles["Title"]))
    elements.append(Spacer(1,12))


    elements.append(Paragraph(f"Year Comparison", styles["Heading3"]))
    elements.append(Paragraph(f"In {year} there was a total of {str(total_year_sales(data, year))} units sold across all grocery groups.", styles["BodyText"]))

    #Try to give a report comparing current year to a previous year. 
    try:
        previous_year = year - 1
        
        current = total_year_sales(data, year)
        previous = total_year_sales(data, previous_year)
        calc_growth = growth(current, previous)

        elements.append(Paragraph(f"In {previous_year} was a total of {str(total_year_sales(data, previous_year))} units sold across all grocery groups.", styles["BodyText"]))
        elements.append(Paragraph(f"From {previous_year} to {year} the growth was {calc_growth}% ", styles["BodyText"]))

    #If there is no previous year then throw an error and replace the text with a statment that no previous year data was given
    except Exception as e:
        elements.append(Paragraph(f"No previous year's data was given - no comparison could be made", styles["BodyText"]))
        print(f"An error occurred: {e}")
    elements.append(Spacer(1,20))

    
    
    elements.append(Paragraph(f"Sales by Month", styles["Heading3"]))
    
    #Iterate through sales by month series and print month without year or underscore and then units sold
    for month, total in sales_by_month(data,year).items():
        elements.append(Paragraph(f"[{re.sub(r'[^a-zA-Z\s]', '', month)}] : {total} units", styles["BodyText"]))
    elements.append(Spacer(1,20))

    #Define quarters for current year (Q1, Q2, Q3, Q4)
    elements.append(Paragraph(f"Quarter over Quarter", styles["Heading3"]))
    Q1 = [str(year) + "_January", str(year) + "_February", str(year) + "_March"]
    Q2 = [str(year) + "_April", str(year) + "_May", str(year) + "_June"]
    Q3 = [str(year) + "_July", str(year) + "_August", str(year) + "_September"]
    Q4 = [str(year) + "_October", str(year) + "_November", str(year) + "_December"]

    # Try to print Q1 sales for the current year and the previous year, with growth percentage
    try:
        previous_year = year - 1

        # Append Q1 sales for current and previous year, along with growth percentage
        Q1_previous = [str(previous_year) + "_January", str(previous_year) + "_February", str(previous_year) + "_March"]
        elements.append(Paragraph(f"Q1 {year}: {total_sales_by_period(data, Q1)} units", styles["BodyText"]))
        elements.append(Paragraph(f"Q1 {previous_year}: {total_sales_by_period(data, Q1_previous)} units", styles["BodyText"]))
        elements.append(Paragraph(f"Growth: {growth(total_sales_by_period(data, Q1_previous), total_sales_by_period(data, Q1))}%", styles["BodyText"]))
        
    except Exception as e:
        # If no data is found for the previous year's Q1, display "No Previous Data" and "Growth: N/A"
        elements.append(Paragraph(f"Q1 {year-1}: No Previous Data", styles["BodyText"]))
        elements.append(Paragraph(f"Growth: N/A", styles["BodyText"]))
        print(f"an error occured {e}")
    elements.append(Spacer(1,12))

    # Repeat the process for Q2 through Q4
    try: 
        
        previous_year = year - 1
        Q2_previous = [str(previous_year) + "_April", str(previous_year) + "_May", str(previous_year) + "_June"]
        elements.append(Paragraph(f"Q2 {year}: {total_sales_by_period(data, Q2)} units", styles["BodyText"]))
        elements.append(Paragraph(f"Q2 {previous_year}: {total_sales_by_period(data, Q2_previous)} units", styles["BodyText"]))
        elements.append(Paragraph(f"Growth: {growth(total_sales_by_period(data, Q2_previous), total_sales_by_period(data, Q2))}%", styles["BodyText"]))
    except Exception as e:
        
        elements.append(Paragraph(f"Q2 {year-1}: No Previous Data", styles["BodyText"]))
        elements.append(Paragraph(f"Growth: N/A", styles["BodyText"]))
        print(f"an error occured {e}")
    elements.append(Spacer(1,12))

 
    try: 
        
        previous_year = year - 1
        Q3_previous = [str(previous_year) + "_July", str(previous_year) + "_August", str(previous_year) + "_September"]
        elements.append(Paragraph(f"Q3 {year}: {total_sales_by_period(data, Q3)} units", styles["BodyText"]))
        elements.append(Paragraph(f"Q3 {previous_year}: {total_sales_by_period(data, Q3_previous)} units", styles["BodyText"]))
        elements.append(Paragraph(f"Growth: {growth(total_sales_by_period(data, Q3_previous), total_sales_by_period(data, Q3))}%", styles["BodyText"]))
        
    except Exception as e:
        
        elements.append(Paragraph(f"Q3 {year-1}: No Previous Data", styles["BodyText"]))
        elements.append(Paragraph(f"Growth: N/A", styles["BodyText"]))
        print(f"an error occured {e}")
        
    elements.append(Spacer(1,12))
    
    try: 
        previous_year = year - 1
        Q4_previous = [str(previous_year) + "_October", str(previous_year) + "_November", str(previous_year) + "_December"]
        elements.append(Paragraph(f"Q4 {year}: {total_sales_by_period(data, Q4)} units", styles["BodyText"]))
        elements.append(Paragraph(f"Q4 {previous_year}: {total_sales_by_period(data, Q4_previous)} units", styles["BodyText"]))
        elements.append(Paragraph(f"Growth: {growth(total_sales_by_period(data, Q4_previous), total_sales_by_period(data, Q4))}%", styles["BodyText"]))
        
    except Exception as e:
        
        elements.append(Paragraph(f"Q4 {year-1}: No Previous Data", styles["BodyText"]))
        elements.append(Paragraph(f"Growth: N/A", styles["BodyText"]))
        print(f"an error occured {e}")
        
    elements.append(Spacer(1,12))

    
    elements.append(Paragraph(f"Visualizations", styles["Heading3"]))
    elements.append(Paragraph(f"See following pages for detailed visualizations.", styles["BodyText"]))
    
    pdf.build(elements)

    # Open a new PDF file "visualizations.pdf" to save the generated plots
    with PdfPages("visualizations.pdf") as visual_pdf:

        #Plot Sales by month 
        fig, ax = plt.subplots(figsize=(15,8))
        plot_sales_by_month(data, year)
        visual_pdf.savefig(fig)
        plt.close(fig)

        #Plot Customer Pie Chart
        fig, ax = plt.subplots(figsize=(12, 8))
        plot_customer_pie_chart(data)
        visual_pdf.savefig(fig)
        plt.close(fig)

        #Plot Customer Group Sales
        fig, ax = plt.subplots(figsize=(12,10))
        plot_customer_group_sales(data, year)
        visual_pdf.savefig(fig)
        plt.close(fig)

        #Plot Top Products
        fig, ax = plt.subplots(figsize=(15,8))
        plot_top_products(data)
        visual_pdf.savefig(fig)
        plt.close(fig)

        #Product Sales by Customer Group
        fig = plot_product_sales_by_customer_group(data, year)
        visual_pdf.savefig(fig) 
        plt.close(fig)

        #Facet Group Product Sales by Customer Group
        fig = plot_customer_group_facet_grid(data, year, "Whole Foods CO")
        visual_pdf.savefig(fig)  
        plt.close(fig)

        fig = plot_customer_group_facet_grid(data, year, "Safeway CO")
        visual_pdf.savefig(fig)  
        plt.close(fig)

        fig = plot_customer_group_facet_grid(data, year, "King Soopers")
        visual_pdf.savefig(fig)  
        plt.close(fig)

    merge_pdfs(["sales_report.pdf", "visualizations.pdf"], output_filename)

#Merges two given PDFs - this technique was chosen with the assistance of Chatgpt.
def merge_pdfs(pdf_list, output_filename):
    merger = PdfMerger()
    for pdf in pdf_list:
        merger.append(pdf)
    merger.write(output_filename)
    merger.close()


generate_report(sales_data, 2024)



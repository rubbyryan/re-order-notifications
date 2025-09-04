import psycopg2
import matplotlib.pyplot as plt
import pandas as pd

conn = psycopg2.connect(
    host="192.168.0.254",
    database="plaza",
    user="postgres",
    password="pg554dm1n@Melivo.com001"
)

cursor = conn.cursor()
query = """
SELECT d.productcode, p.description, ROUND(SUM(quantity))
FROM sales s
JOIN saledetails d ON s.saleid = d.saleid
JOIN products p ON p.productcode = d.productcode
GROUP BY d.productcode, p.description
ORDER BY SUM(quantity) DESC
LIMIT 10
"""
cursor.execute(query)

data = cursor.fetchall()
productcodes = []
descriptions = []
quantities = []
for row in data:
    productcodes.append(row[0])
    descriptions.append(row[1])
    quantities.append(row[2])

plt.bar(descriptions, quantities)
plt.xlabel('Product Description')
plt.ylabel('Quantity Sold')
plt.title('Top 10 Top Selling Products')
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig('top_selling_products.png')
plt.show()

cursor = conn.cursor()
query = """
SELECT d.productcode, p.description, ROUND(SUM(d.stdprice - d.stdavecostprice), 2)
FROM sales s
JOIN saledetails d ON s.saleid = d.saleid
JOIN products p ON p.productcode = d.productcode
GROUP BY d.productcode, p.description
ORDER BY SUM(d.stdprice - d.stdavecostprice) DESC
LIMIT 10
"""

cursor.execute(query)

# Fetch the data
data = cursor.fetchall()
productcodes = []
descriptions = []
profits = []
for row in data:
    productcodes.append(row[0])
    descriptions.append(row[1])
    profits.append(row[2])

# Plot the graph using matplotlib
plt.bar(descriptions, profits)
plt.xlabel('Product Description')
plt.ylabel('Profit')
plt.title('Top 10 Most Profitable Products')
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig('most_profitable_products.png')
plt.show()

#Create a cursor object and execute the SQL query
cursor = conn.cursor()
query = """
SELECT sales.saledate::date,
       ROUND(SUM(stdprice), 2) AS turnover,
       ROUND(SUM(stdprice / (1 + saledetails.stdvat / 100)), 2) AS totalsales,
       ROUND(SUM(quantity * stdavecostprice), 2) AS avecogs,
       ROUND(SUM(quantity * stdlatecostprice), 2) AS latestcogs,
       ROUND(SUM(quantity * stdhicostprice), 2) AS highestcogs,
       ROUND(SUM(stdprice / (1 + saledetails.stdvat / 100)) - SUM(quantity * stdavecostprice), 2) AS gp,
       ROUND(AVG(saledetails.stdunitprice), 2) AS avgsellingprice,
       ROUND(MIN(saledetails.stdunitprice), 2) AS minsellingprice,
       ROUND(MAX(saledetails.stdunitprice), 2) AS maxsellingprice,
       ROUND(CASE WHEN SUM(quantity * stdavecostprice) = 0 THEN NULL
                  ELSE (SUM(stdprice / (1 + saledetails.stdvat / 100)) - SUM(quantity * stdavecostprice)) / SUM(quantity * stdavecostprice) * 100 END, 2) AS markup,
       ROUND((SUM(stdprice / (1 + saledetails.stdvat / 100)) - SUM(quantity * stdavecostprice)) / SUM(stdprice / (1 + saledetails.stdvat / 100)) * 100, 2) AS margin,
       ROUND(SUM(quantity), 2) AS unitssold,
       COUNT(saledetails.saleid) AS salecount
FROM saledetails
JOIN products ON saledetails.productcode = products.productcode
JOIN sales ON sales.saleid = saledetails.saleid
WHERE quantity <> 0
  AND stdprice <> 0
  AND salestate = 'complete'
GROUP BY sales.saledate::date
HAVING SUM(stdprice) <> 0
ORDER BY saledate DESC
LIMIT 10
"""
cursor.execute(query)

# Fetch the data
data = cursor.fetchall()
columns = [desc[0] for desc in cursor.description]
df = pd.DataFrame(data, columns=columns)

# Display the data as a table
print(df)

# Save the data as an image
plt.figure(figsize=(10, 6))
plt.axis('off')
plt.table(cellText=df.values, colLabels=df.columns, cellLoc='center', loc='upper center')
plt.savefig('Daily_sales_data.png')
plt.close()

cursor= conn.cursor()
query = """  select to_char(sales.saledate, 'Month') as month,date_part('year',sales.saledate) as year,round(sum(stdprice),2) as turnover,round(sum(stdprice/(1+saledetails.stdvat/100)),2) as totalsales,round(sum(quantity*stdavecostprice),2) as avecogs,
            round(sum(quantity*stdlatecostprice),2) as latestcogs,round(sum(quantity*stdhicostprice),2) as highestcogs,
            round(sum(stdprice/(1+saledetails.stdvat/100))-sum(quantity*stdavecostprice),2)  as gp,round(avg(saledetails.stdunitprice),2) as avgsellingprice,
            round(min(saledetails.stdunitprice),2) as minsellingprice,round(max(saledetails.stdunitprice),2) as maxsellingprice, round(CASE WHEN sum(quantity*stdavecostprice)=0 THEN NULL ELSE (sum(stdprice/(1+saledetails.stdvat/100))-sum(quantity*stdavecostprice))/sum(quantity*stdavecostprice)*100 END,2) as markup,
            round((sum(stdprice/(1+saledetails.stdvat/100))-sum(quantity*stdavecostprice))/sum(stdprice/(1+saledetails.stdvat/100))*100,2) as margin,
            round(sum(quantity),2) as unitssold,count(saledetails.saleid) as salecount
            from saledetails
            join products on saledetails.productcode=products.productcode
            left outer join categories on categories.categoryid=products.categoryid
            join sales on sales.saleid=saledetails.saleid
            and quantity<>0 and stdprice<>0 and salestate='complete' group by to_char(sales.saledate, 'Month'),date_part('month',sales.saledate),date_part('year',sales.saledate)  having sum(stdprice)<>0 
            order by date_part('year',sales.saledate) desc,date_part('month',sales.saledate) desc
			limit 6"""

cursor.execute(query)

data = cursor.fetchall()
colunms = [desc[0] for desc in cursor.description]
df = pd.DataFrame(data, columns=columns)

print(df)

# Save the data as an image
plt.figure(figsize=(10, 6))
plt.axis('off')
plt.table(cellText=df.values, colLabels=df.columns, cellLoc='center', loc='upper center')
plt.savefig('Monthly_sales_data.png')
plt.close()










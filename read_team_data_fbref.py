import pandas as pd
import requests
from io import StringIO

url = "https://fbref.com/en/comps/9/Premier-League-Stats"
# Get the page content
response = requests.get(url)
# Wrap the response text in a StringIO object
html_string = StringIO(response.text)
tables = pd.read_html(html_string)

# Find the table with the caption 'Premier League'
pl_table = None
for table in tables:
    if "Premier League" in table.columns or "Squad" in table.columns:
        pl_table = table
        break

if pl_table is None:
    raise ValueError("Premier League table not found.")

# Set 'Squad' as the index/key
pl_table = pl_table.set_index(['Squad','Rk'])


print(pl_table.head())


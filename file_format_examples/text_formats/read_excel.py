import zipfile
import pandas as pd

with zipfile.ZipFile("data_store.xlsx", "r") as z:
    print(z.namelist())  # list all internal files
    with z.open("xl/worksheets/sheet1.xml") as f:
        print(f.read(500))  # first 500 bytes

df = pd.read_excel("data_store.xlsx")
print(df)
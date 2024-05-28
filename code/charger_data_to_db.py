from sqlalchemy import create_engine
from PIL import Image
import pandas as pd
import os

df1 = pd.read_excel(r"C:\Users\USER\Documents\GitHub\project001\modelinfo.xlsx")
df2 = pd.read_excel(r"C:\Users\USER\Documents\GitHub\project001\functions.xlsx")
df3 = pd.read_excel(r"C:\Users\USER\Documents\GitHub\project001\chargerInfo.xlsx")
db_connection_str = "mysql+pymysql://root@192.168.0.30:3306/cardb"
db_connection = create_engine(db_connection_str)
db_conn = db_connection.connect()

df1.to_sql(
    name="charger_model",
    con=db_connection,
    schema="cardb",
    if_exists="replace",
    index=False,
)

df2.to_sql(
    name="charger_Function",
    con=db_connection,
    schema="cardb",
    if_exists="replace",
    index=False,
)

df3.to_sql(
    name="charger_info",
    con=db_connection,
    schema="cardb",
    if_exists="replace",
    index=False,
)

from sqlalchemy import create_engine
import pandas as pd

db_connection_str = 'mysql+pymysql://root@192.168.0.30:3306/cardb'
db_connection = create_engine(db_connection_str)
db_conn = db_connection.connect()

df = pd.read_excel("./data/EV모델별 주행거리.xlsx")

df.to_sql(name = 'evcar_mileage',
             con = db_connection, 
             schema = 'cardb', 
             if_exists = 'replace',
             index = False)
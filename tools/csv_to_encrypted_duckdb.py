import duckdb
import os
from dotenv import load_dotenv

load_dotenv()

# Define your file paths and encryption key
csv_path = "data/WHR2024.csv"
db_path = "data/encrypted_data.duckdb"
encryption_key = str(os.getenv('PWD'))

# # Create an encrypted database
# con = duckdb.connect(db_path, config={"password": encryption_key})

# # 2. Import the CSV file into an encrypted table within the attached database
# con.execute(f"""
#     CREATE TABLE my_table AS 
#     SELECT * FROM read_csv_auto('{csv_path}');
# """)

# print("Successfully created encrypted DuckDB file and imported CSV data.")

# # Close the connection
# con.close()

# test data
con = duckdb.connect(db_path, read_only=True, config={"password": encryption_key})
df = con.execute('SELECT Year, "Country name", "Ladder score", "Explained by: Log GDP per capita" FROM my_table').fetchdf()
con.close()
print(df.dtypes)
print(df)

import pandas as pd
import asyncio
from dotenv import load_dotenv # comment out when deploying
import os
import duckdb
class DataLoader:
    def __init__(self):
        # This is the file path to the data
        self.path: str = 'data/WHR2024.csv'
        self.DUCKD_DIR: str = "data/encrypted_data.duckdb"
        # Ensure we load at least the columns we need for the app
        self.COLUMNS = [
            "Year",
            "Country name",
            "Ladder score",
            "Explained by: Log GDP per capita",
        ]
        self.happiness_data: pd.DataFrame | None = None
        self.country_list: dict[str, str] = []
        self.dict_years: dict = {}

    def _require_data(self):
        if self.happiness_data is None:
            raise ValueError("Data not loaded. Please call load_data() first.")

    async def load_data(self) -> pd.DataFrame:
        # CSV file
        # self.happiness_data = await asyncio.to_thread(
        #     pd.read_csv,
        #     self.path,
        #     usecols=self.COLUMNS,
        # )
        # DuckDB file
        self.happiness_data = await self.get_data_duckdb('SELECT Year, "Country name", "Ladder score", "Explained by: Log GDP per capita" FROM my_table')

        self.country_list = self.happiness_data["Country name"].unique().tolist()
        self.dict_years = {str(year): str(year) for year in sorted(self.happiness_data['Year'].unique())}
        return self.happiness_data

    # It runs duckdb calls on a thread (duckdb is synchronous and not awaitable).
    async def get_data_duckdb(self, query: str) -> pd.DataFrame:
        def _run_query():
            con = duckdb.connect(self.DUCKD_DIR, read_only=True, config={"password": str(os.getenv('PWD'))})
            try:
                df = con.execute(query).fetchdf()  # synchronous call returning pandas DataFrame
            finally:
                con.close()
            return df

        return await asyncio.to_thread(_run_query)

    async def get_top_happiest_countries(self, year: int, top: int) -> pd.DataFrame:
        self._require_data()
        data = self.happiness_data[self.happiness_data['Year'] == year]
        data = data.sort_values(by='Ladder score', ascending=False).head(top)
        return data
    
    async def get_data_by_year(self, year: int) -> pd.DataFrame:
        self._require_data()
        return self.happiness_data[self.happiness_data['Year'] == year]
        
    async def get_data_by_country(self, country: str) -> pd.DataFrame:
        self._require_data()
        return self.happiness_data[self.happiness_data["Country name"] == country].sort_values(by='Year', ascending=True)

    async def get_clean_data_for_scatter(self) -> pd.DataFrame:
        self._require_data()
        return self.happiness_data[["Ladder score", "Explained by: Log GDP per capita"]].dropna()

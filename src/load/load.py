import logging
import os

import pandas as pd
from sqlalchemy import create_engine

from dotenv import load_dotenv

load_dotenv()

DB_HOST = "localhost"
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def load_data() -> None:
    """
    Loads the CSV file into the database.
    """
    try:
        logging.info("Connecting to the database")
        engine = create_engine(
            f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )
        df = pd.read_csv("data/data.csv")
        logging.info("Uploading data to the database")
        df.to_sql(
            "electrical_vehicles_bronze", engine, if_exists="replace", index=False
        )
        logging.info("Data loaded successfully")
    except Exception as e:
        logging.error(f"Error: {e}")
        raise e


if __name__ == "__main__":
    load_data()

import logging
import os

import requests
from dotenv import load_dotenv


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

load_dotenv()
URL = os.getenv("URL")


def download_csv(url: str) -> None:
    """
    Downloads the CSV file from the given URL and saves it to a file.
    """

    root_path = os.getenv("AIRFLOW_HOME", os.getcwd())
    data_dir = os.path.join(root_path, "data")
    os.makedirs(data_dir, exist_ok=True)
    file_path = os.path.join(data_dir, "data.csv")
    try:
        response = requests.get(url)
        response.raise_for_status()

        with open(file_path, "w") as f:
            f.write(response.text)
        logging.info("CSV file downloaded successfully")

    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP error: {e}")
        raise e
    except Exception as e:
        logging.error(f"Error: {e}")
        raise e


if __name__ == "__main__":
    download_csv(URL)

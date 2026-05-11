import logging
import os

import requests
from dotenv import load_dotenv


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

load_dotenv()
URL = os.getenv("URL")

def download_csv(url: str) -> None:
    """
    Downloads the CSV file from the given URL and saves it to a file.
    """


    try:
        response = requests.get(url)
        response.raise_for_status()

        os.makedirs("data", exist_ok=True)
        with open("data/data.csv", "w") as f:
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
    
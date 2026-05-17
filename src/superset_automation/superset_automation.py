import requests
import logging
from dotenv import load_dotenv
import os
import json

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

load_dotenv()

SUPERSET_HOST = os.getenv("SUPERSET_HOST")
SUPERSET_PORT = os.getenv("SUPERSET_PORT")
SUPERSET_USER = os.getenv("SUPERSET_ADMIN_USERNAME")
SUPERSET_PASSWORD = os.getenv("SUPERSET_ADMIN_PASSWORD")
SUPERSET_URL = f"http://{SUPERSET_HOST}:{SUPERSET_PORT}"
DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_PORT = os.getenv("DB_PORT")
DB_HOST = os.getenv("DB_HOST")
DATASETS = {
    "vehicle_location": {"table_name": "vehicle_location"},
    "electrical_vehicles_per_year": {"table_name": "electrical_vehicles_per_year"},
}

GRAPH_PAYLOAD = {
    "vehicle_location": {
        "slice_name": "Vehicle Locations",
        "viz_type": "deck_scatter",
        "datasource_type": "table",
        "params": json.dumps(
            {
                "viz_type": "deck_scatter",
                "spatial": {
                    "type": "latlong",
                    "latCol": "latitude",
                    "lonCol": "longitude",
                },
                "color_picker": {"r": 0, "g": 0, "b": 255, "a": 1},
                "dimension": "is_cafv_eligibility",
                "color_scheme": "googleCategory20c",
                "point_radius": 20,
                "point_radius_fixed": {"type": "fix", "value": 20},
                "row_limit": 10000,
                "mapbox_style": "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                "autozoom": True,
            }
        ),
    }
}


def create_superset_session() -> requests.Session:
    """Creates a session, logs in, and sets auth + CSRF headers.

    Access token is to identify the user for the Superset API.
    CSRF token is to prove the user is logged in and authorized to make requests.
    """
    session = requests.Session()

    res = session.post(
        f"{SUPERSET_URL}/api/v1/security/login",
        json={
            "username": SUPERSET_USER,
            "password": SUPERSET_PASSWORD,
            "provider": "db",
        },
    )
    res.raise_for_status()
    access_token = res.json()["access_token"]
    logging.info("Access token obtained successfully")

    csrf_res = session.get(
        f"{SUPERSET_URL}/api/v1/security/csrf_token/",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    csrf_res.raise_for_status()
    csrf_token = csrf_res.json()["result"]
    logging.info("CSRF token obtained")

    session.headers.update(
        {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-CSRFToken": csrf_token,
            "Referer": SUPERSET_URL,
        }
    )

    return session


def create_database_connection(session) -> None:
    """
    This function creates a database connection in Superset.
    """

    payload = {
        "database_name": DB_NAME,
        "sqlalchemy_uri": f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
        "expose_in_sqllab": True,
        "allow_ctas": False,
        "allow_cvas": False,
    }

    response = session.post(f"{SUPERSET_URL}/api/v1/database/", json=payload)

    if response.status_code == 422:
        logging.info("Database connection already exists. Skipping creation.")
        return

    if not response.ok:
        logging.error(f"Error: {response.text}")
    response.raise_for_status()
    logging.info("Database connection created successfully")


def get_database_id(session) -> int:
    """Gets the database ID for the configured DB_NAME."""

    res = session.get(f"{SUPERSET_URL}/api/v1/database/")
    res.raise_for_status()
    for db in res.json().get("result", []):
        if db["database_name"] == DB_NAME:
            return db["id"]
    raise ValueError(f"Database '{DB_NAME}' not found in Superset")


def create_dataset(session, dataset, table_name):
    """This function creates a dataset in Superset."""

    database_id = get_database_id(session)

    payload = {
        "database": database_id,
        "table_name": table_name,
    }

    response = session.post(f"{SUPERSET_URL}/api/v1/dataset/", json=payload)

    if response.status_code == 422:
        logging.info(f"Dataset {dataset} already exists. Skipping creation.")
        return

    if not response.ok:
        logging.error(f"Error: {response.text}")
    response.raise_for_status()
    logging.info(f"Dataset {dataset} created successfully")


def get_dataset_id(session, table_name) -> int:
    """
    Gets dataset id for a table name
    """

    datasets_req = session.get(f"{SUPERSET_URL}/api/v1/dataset/")

    datasets_req.raise_for_status()

    for dataset in datasets_req.json().get("result", []):
        logging.info(f"{dataset}")
        if dataset["table_name"] == table_name:
            return dataset["id"]

    raise ValueError(f"Dataset {table_name} not found in Superset")


def create_chart(session, table_name) -> None:
    """This function creates a chart in Superset."""

    dataset_id = get_dataset_id(session, table_name)

    payload = GRAPH_PAYLOAD[table_name]

    payload["datasource_id"] = dataset_id

    response = session.post(f"{SUPERSET_URL}/api/v1/chart/", json=payload)
    if not response.ok:
        logging.error(f"Error: {response.text}")
        response.raise_for_status()

    logging.info("EV map chart created successfully")


if __name__ == "__main__":
    superset_session = create_superset_session()
    create_database_connection(superset_session)
    for dataset in DATASETS:
        create_dataset(superset_session, dataset, DATASETS[dataset]["table_name"])

    create_chart(superset_session, "vehicle_location")

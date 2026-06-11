import pandas as pd
import requests
import time

INPUT_FILE = "fuel-prices-for-be-assessment.csv"

OUTPUT_FILE = "fuel_stations_geocoded.csv"

df = pd.read_csv(INPUT_FILE)

latitudes = []
longitudes = []

for _, row in df.iterrows():

    location = (
        f"{row['Address']}, "
        f"{row['City']}, "
        f"{row['State']}, USA"
    )

    try:

        response = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={
                "q": location,
                "format": "json",
                "limit": 1
            },
            headers={
                "User-Agent": "fuel-app"
            }
        )

        data = response.json()

        if data:

            latitudes.append(
                float(data[0]["lat"])
            )

            longitudes.append(
                float(data[0]["lon"])
            )

        else:

            latitudes.append(None)
            longitudes.append(None)

    except Exception:

        latitudes.append(None)
        longitudes.append(None)

    # time.sleep(1)

df["Latitude"] = latitudes
df["Longitude"] = longitudes

df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("Done")

import os
import requests
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
from tqdm import tqdm

# ================================================
load_dotenv()
OPENWEATHER_KEY = os.getenv("OPENWEATHER_KEY")
AQICN_TOKEN = os.getenv("AQICN_TOKEN")

if not OPENWEATHER_KEY or not AQICN_TOKEN:
    raise ValueError("Missing API keys. Set OPENWEATHER_KEY and AQICN_TOKEN in your .env file")

OUT_DIR = "data/"
os.makedirs(OUT_DIR, exist_ok=True)

CITIES = {
    "Karachi": {"lat": 24.8607, "lon": 67.0011, "aqicn_station": "karachi"},
    "Lahore": {"lat": 31.5497, "lon": 74.3436, "aqicn_station": "lahore"},
    "Islamabad": {"lat": 33.6844, "lon": 73.0479, "aqicn_station": "islamabad"}
}
# ================================================

# ---------- 1️⃣ OpenAQ Historical / Hourly ----------
def fetch_openaq(city, days=30):
    """Fetch hourly OpenAQ data for given city and last N days."""
    end = datetime.utcnow()
    start = end - timedelta(days=days)
    params = {
        # CHANGE: Use country filter instead of the deprecated 'city' filter
        "country": "PK", 
        "limit": 10000,
        "date_from": start.isoformat(),
        "date_to": end.isoformat(),
        "parameter": ["pm25", "pm10", "no2", "o3", "so2"],
        "format": "json"
    }
    url = "https://api.openaq.org/v2/measurements"
    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    data = r.json().get("results", [])
    if not data:
        return pd.DataFrame()
    
    # NEW: Filter results to the specific city name after fetching all Pakistan data
    df = pd.DataFrame(data)
    df_city = df[df['city'].str.lower() == city.lower()].copy()

    if df_city.empty:
        print(f"⚠️ OpenAQ found no data for city: {city}")
        return pd.DataFrame()

    df_city = df_city.rename(columns={"value": "concentration"})
    df_city["timestamp"] = pd.to_datetime(df_city["date"].apply(lambda x: x["utc"]))
    
    # Pivot and finalize
    df_final = df_city.pivot_table(
        index="timestamp", 
        columns="parameter", 
        values="concentration", 
        aggfunc="mean"
    ).reset_index()
    
    df_final["source"] = "OpenAQ"
    df_final["city"] = city
    
    return df_final


# ---------- 2️⃣ OpenWeather ----------
def fetch_openweather(city, lat, lon):
    base = "https://api.openweathermap.org/data/2.5/air_pollution"
    def _get(url):
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.json().get("list", [])
    current = _get(f"{base}?lat={lat}&lon={lon}&appid={OPENWEATHER_KEY}")
    forecast = _get(f"{base}/forecast?lat={lat}&lon={lon}&appid={OPENWEATHER_KEY}")
    end = int(datetime.utcnow().timestamp())
    start = int((datetime.utcnow() - timedelta(days=5)).timestamp())
    history = _get(f"{base}/history?lat={lat}&lon={lon}&start={start}&end={end}&appid={OPENWEATHER_KEY}")
    rows = []
    for kind, records in zip(["current", "forecast", "history"], [current, forecast, history]):
        for rec in records:
            rows.append({
                "timestamp": datetime.utcfromtimestamp(rec["dt"]),
                "aqi": rec["main"]["aqi"],
                **rec["components"],
                "type": kind,
                "source": "OpenWeather",
                "city": city
            })
    return pd.DataFrame(rows)


# ---------- 3️⃣ AQICN ----------
def fetch_aqicn(city, station):
    url = f"https://api.waqi.info/feed/{station}/?token={AQICN_TOKEN}"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    data = r.json()
    if data["status"] != "ok":
        return pd.DataFrame()
    d = data["data"]
    records = []
    # Current
    iaqi = d.get("iaqi", {})
    comps = {k: v.get("v") for k, v in iaqi.items()}
    records.append({
        "timestamp": datetime.strptime(d["time"]["s"], "%Y-%m-%d %H:%M:%S"),
        "aqi": d.get("aqi"),
        **comps,
        "type": "current",
        "source": "AQICN",
        "city": city
    })
    # Forecast
    forecast = d.get("forecast", {}).get("daily", {})
    for pollutant, days in forecast.items():
        for entry in days:
            records.append({
                "timestamp": datetime.strptime(entry["day"], "%Y-%m-%d"),
                "pollutant": pollutant,
                "aqi": entry.get("avg"),
                "min": entry.get("min"),
                "max": entry.get("max"),
                "type": f"forecast_{pollutant}",
                "source": "AQICN",
                "city": city
            })
    return pd.DataFrame(records)


def build_dataset():
    all_dfs = []
    for city, info in tqdm(CITIES.items()):
        ow = fetch_openweather(city, info["lat"], info["lon"])
        aq = fetch_aqicn(city, info["aqicn_station"])
        
        # REMOVED: op = fetch_openaq(city, days=30)
        
        # Combine only the functional data sources
        combined = pd.concat([ow, aq], ignore_index=True) 
        combined.sort_values("timestamp", inplace=True)
        path = os.path.join(OUT_DIR, f"{city.lower()}_combined_aqi.csv")
        combined.to_csv(path, index=False)
        print(f"✅ Saved {len(combined)} records for {city} → {path}")
        all_dfs.append(combined)
    return pd.concat(all_dfs, ignore_index=True)

if __name__ == "__main__":
    df_all = build_dataset()
    print("All cities merged:", df_all.shape)
    df_all.to_csv(os.path.join(OUT_DIR, "pakistan_aqi_full.csv"), index=False)

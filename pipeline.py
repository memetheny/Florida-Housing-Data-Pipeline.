import sqlite3
from contextlib import closing
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

import pandas as pd

ROOT = Path(__file__).resolve().parent
ZILLOW_URL = (
    "https://files.zillowstatic.com/research/public_csvs/zhvi/"
    "Metro_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv"
)
FRED_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US"


def read_source(name, url):
    print(f"Downloading {name}...")
    try:
        with urlopen(url, timeout=45) as response:
            return pd.read_csv(response)
    except (URLError, TimeoutError) as error:
        message = f"Could not download {name}: {error}"
        if "CERTIFICATE_VERIFY_FAILED" in str(error):
            message += (
                "\nPython could not verify the site's SSL certificate. On macOS "
                "with python.org Python, run the 'Install Certificates.command' "
                "file in your Python application folder, then try again."
            )
        raise SystemExit(message) from error
    except (pd.errors.ParserError, pd.errors.EmptyDataError) as error:
        raise SystemExit(f"{name} returned data that is not a valid CSV: {error}") from error


def require_columns(name, raw, columns):
    # Fail with a clear message if a source renames or drops a column.
    missing = [column for column in columns if column not in raw.columns]
    if missing:
        raise SystemExit(f"{name} data is missing expected columns: {', '.join(missing)}")


def clean_home_values(raw):
    require_columns("Zillow", raw, ["RegionID", "RegionName", "RegionType", "StateName"])
    # Zillow puts each month in a separate column.
    month_columns = raw.columns[raw.columns.str.fullmatch(r"\d{4}-\d{2}-\d{2}")]
    florida = raw.loc[raw["StateName"].eq("FL") & raw["RegionType"].eq("msa")]
    values = florida.melt(
        id_vars=["RegionID", "RegionName"],
        value_vars=month_columns,
        var_name="date",
        value_name="zhvi",
    ).rename(columns={"RegionID": "metro_id", "RegionName": "metro"})
    values["month"] = pd.to_datetime(values.pop("date")).dt.strftime("%Y-%m")
    values = values.dropna(subset=["zhvi"])
    if values.empty or values.duplicated(["metro_id", "month"]).any():
        raise ValueError("Expected exactly one row per available Florida metro-month.")
    if values["zhvi"].le(0).any():
        raise ValueError("Home values must be positive.")
    return values


def clean_mortgage_rates(raw):
    require_columns("FRED", raw, ["observation_date", "MORTGAGE30US"])
    # Average the available weekly observations within each calendar month.
    raw["month"] = pd.to_datetime(raw["observation_date"]).dt.strftime("%Y-%m")
    raw["mortgage_rate_pct"] = pd.to_numeric(raw["MORTGAGE30US"], errors="coerce")
    return raw.groupby("month", as_index=False)["mortgage_rate_pct"].mean().dropna()


def main():
    home_values = clean_home_values(read_source("Zillow", ZILLOW_URL))
    rates = clean_mortgage_rates(read_source("FRED", FRED_URL))
    query = (ROOT / "analysis.sql").read_text(encoding="utf-8")

    with closing(sqlite3.connect(ROOT / "housing.db")) as database:
        home_values.to_sql("home_values", database, if_exists="replace", index=False)
        rates.to_sql("mortgage_rates", database, if_exists="replace", index=False)
        results = pd.read_sql_query(query, database)

    if results.empty:
        raise SystemExit("No matching records for the latest Zillow month.")
    print(f"Loaded {home_values['metro_id'].nunique()} Florida metros.")
    print(results.to_string(index=False))


if __name__ == "__main__":
    main()

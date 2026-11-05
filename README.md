# Florida Housing Data Pipeline

Which Florida metros had the fastest year-over-year home value growth in Zillow's latest available month? This project reshapes Zillow metro data with pandas, averages weekly national mortgage rates by month, and loads both tables into SQLite. The SQL query ranks the top five metros and displays the national mortgage rate for that month.

## Run locally

Use Python 3.10 or newer. From the project folder, run:

```bash
python -m pip install -r requirements.txt
python pipeline.py
```

On macOS, use `python3` if that is the command your system recognizes. On Windows, you can use `py` instead.

The script prints the results and creates `housing.db` locally. Each run refreshes the two tables. The query compares each metro with the same calendar month a year earlier. Metros missing either home value are excluded. The national mortgage rate provides context and is the same for every metro in the table.

## Sources

- [Zillow Research](https://www.zillow.com/research/data/) supplies the metro-level Zillow Home Value Index for all homes, smoothed and seasonally adjusted.
- [Freddie Mac via FRED](https://fred.stlouisfed.org/series/MORTGAGE30US) supplies the weekly U.S. 30-year fixed mortgage rate.

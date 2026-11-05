-- Rank Florida metros by year-over-year ZHVI growth in Zillow's latest month.
SELECT
    latest.metro,
    latest.month,
    ROUND(latest.zhvi) AS typical_home_value_usd,
    ROUND(100.0 * (latest.zhvi / prior.zhvi - 1), 2) AS yoy_growth_pct,
    ROUND(rates.mortgage_rate_pct, 2) AS national_mortgage_rate_pct
FROM home_values AS latest
JOIN home_values AS prior
    ON prior.metro_id = latest.metro_id
    AND prior.month = STRFTIME('%Y-%m', latest.month || '-01', '-12 months')
JOIN mortgage_rates AS rates
    ON rates.month = latest.month
WHERE latest.month = (SELECT MAX(month) FROM home_values)
ORDER BY (latest.zhvi / prior.zhvi - 1) DESC, latest.metro
LIMIT 5;

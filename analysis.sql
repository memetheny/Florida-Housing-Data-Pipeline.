-- Rank Florida metros by year-over-year ZHVI growth in Zillow's latest month.
SELECT
    current.metro,
    current.month,
    ROUND(current.zhvi) AS typical_home_value_usd,
    ROUND(100.0 * (current.zhvi / prior.zhvi - 1), 2) AS yoy_growth_pct,
    ROUND(rates.mortgage_rate_pct, 2) AS national_mortgage_rate_pct
FROM home_values AS current
JOIN home_values AS prior
    ON prior.metro_id = current.metro_id
    AND prior.month = STRFTIME('%Y-%m', current.month || '-01', '-12 months')
JOIN mortgage_rates AS rates
    ON rates.month = current.month
WHERE current.month = (SELECT MAX(month) FROM home_values)
ORDER BY (current.zhvi / prior.zhvi - 1) DESC, current.metro
LIMIT 5;

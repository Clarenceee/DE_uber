-- Docs: https://docs.mage.ai/guides/sql-blocks
SELECT d.pick_weekday, d.pick_hour, avg(f.fare_amount) as total_fare
FROM  fact_table f
JOIN datetime_dimension d
ON d.datetime_id = f.datetime_id
GROUP BY d.pick_weekday, d.pick_hour
ORDER BY total_fare DESC
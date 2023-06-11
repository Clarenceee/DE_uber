-- Docs: https://docs.mage.ai/guides/sql-blocks
SELECT p.payment_type_name, avg(f.fare_amount)
FROM {{df_1}} f
JOIN {{df_2}} p 
ON f.payment_method_id = p.payment_method_id
GROUP BY p.payment_type_name


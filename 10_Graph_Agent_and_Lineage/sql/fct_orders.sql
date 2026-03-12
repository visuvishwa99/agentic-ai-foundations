-- Create Fact Table for Orders
CREATE OR REPLACE TABLE fct_orders AS
SELECT 
    o.order_id,
    o.user_id,
    o.product_id,
    u.country_name,
    p.category,
    o.quantity * p.price AS total_amount,
    o.order_date
FROM raw_orders o
JOIN dim_users u ON o.user_id = u.user_id
JOIN dim_products p ON o.product_id = p.product_id;

-- Create Dimensions Table for Products
CREATE OR REPLACE TABLE dim_products AS
SELECT 
    p.product_id,
    p.product_name,
    p.category,
    p.price,
    s.supplier_name
FROM raw_products p
JOIN raw_suppliers s ON p.supplier_id = s.id;

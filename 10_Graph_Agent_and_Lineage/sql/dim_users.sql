-- Create Dimensions Table for Users
CREATE OR REPLACE TABLE dim_users AS
SELECT 
    u.user_id,
    u.username,
    u.email,
    c.country_name,
    u.created_at
FROM raw_users u
LEFT JOIN raw_countries c ON u.country_code = c.code;

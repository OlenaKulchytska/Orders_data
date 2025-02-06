WITH latest_orders AS (
    SELECT * FROM orders
    WHERE updated_at > (SELECT COALESCE(MAX(uploaded_at), '1970-01-01') FROM purchases)
),
latest_transactions AS (
    SELECT * FROM transactions
    WHERE updated_at > (SELECT COALESCE(MAX(uploaded_at), '1970-01-01') FROM purchases)
),
latest_verification AS (
    SELECT * FROM verification
    WHERE updated_at > (SELECT COALESCE(MAX(uploaded_at), '1970-01-01') FROM purchases)
)

SELECT 
    o.*, 
    t.*, 
    v.*, 
    CURRENT_TIMESTAMP AS uploaded_at
FROM latest_orders o
JOIN latest_transactions t ON o.id = t.order_id
JOIN latest_verification v ON t.id = v.transaction_id;

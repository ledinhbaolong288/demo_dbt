select
    cast(order_id as bigint) as order_id,
    cast(user_id as bigint) as user_id,
    cast(total_amount as numeric(18,2)) as total_amount,
    cast(created_at as timestamp) as created_at,
    cast(etl_time as timestamp) as etl_time
from raw.orders_raw
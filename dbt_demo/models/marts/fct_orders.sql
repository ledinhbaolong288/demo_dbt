select
    o.order_id,
    o.user_id,
    u.user_name,
    u.email,
    o.total_amount,
    o.created_at
from {{ ref('stg_orders') }} o
left join {{ ref('stg_users') }} u
    on o.user_id = u.user_id
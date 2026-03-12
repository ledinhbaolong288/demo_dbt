select
    cast(user_id as bigint) as user_id,
    trim(user_name) as user_name,
    lower(trim(email)) as email,
    cast(created_at as timestamp) as created_at,
    cast(updated_at as timestamp) as updated_at,
    cast(etl_time as timestamp) as etl_time
from raw.users_raw
from datetime import date
from .database import relation_sql

def _where(filters: dict, params: list) -> str:
    clauses = []
    if filters.get("start"):
        clauses.append("pickup_datetime >= ?"); params.append(filters["start"])
    if filters.get("end"):
        clauses.append("pickup_datetime < ?"); params.append(filters["end"])
    for column, key in (("pickup_location_id", "pickup_zone"), ("dropoff_location_id", "dropoff_zone"), ("payment_type", "payment_type")):
        if filters.get(key):
            clauses.append(f"{column} = ?"); params.append(filters[key])
    for column, low_key, high_key in (("fare_amount", "min_fare", "max_fare"), ("trip_distance", "min_distance", "max_distance")):
        if filters.get(low_key) is not None: clauses.append(f"{column} >= ?"); params.append(filters[low_key])
        if filters.get(high_key) is not None: clauses.append(f"{column} <= ?"); params.append(filters[high_key])
    return (" WHERE " + " AND ".join(clauses)) if clauses else ""

def query_frame(connection, filters: dict, group_sql: str = "", limit: int = 100000):
    params: list = []
    where = _where(filters, params)
    sql = f"SELECT * FROM {relation_sql()}{where} {group_sql} LIMIT {int(limit)}"
    return connection.execute(sql, params).fetchdf()

def kpis(connection, filters: dict) -> dict:
    params: list = []
    where = _where(filters, params)
    row = connection.execute(f"""SELECT count(*) total_trips, sum(total_amount) total_fare,
        avg(total_amount) average_fare, avg(trip_distance) average_distance,
        avg(trip_duration_minutes) average_duration,
        count(*) / NULLIF(count(DISTINCT CAST(pickup_datetime AS DATE)), 0) trips_per_day
        FROM {relation_sql()}{where}""", params).fetchone()
    return dict(zip(["total_trips", "total_fare", "average_fare", "average_distance", "average_duration", "trips_per_day"], row))

def aggregate(connection, filters: dict, expression: str, aliases: str):
    params: list = []
    where = _where(filters, params)
    return connection.execute(f"SELECT {expression} AS period, count(*) AS trips {aliases} FROM {relation_sql()}{where} GROUP BY 1 ORDER BY 1", params).fetchdf()

def grouped_metrics(connection, filters: dict, expression: str, metrics: str):
    params: list = []
    where = _where(filters, params)
    return connection.execute(
        f"SELECT {expression}, {metrics} FROM {relation_sql()}{where} "
        "GROUP BY 1, 2 ORDER BY 1, 2",
        params,
    ).fetchdf()

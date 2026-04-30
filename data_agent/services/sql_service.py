import duckdb
import pandas as pd
from fastapi import HTTPException


def execute_sql(df: pd.DataFrame, sql: str, limit: int = 500) -> pd.DataFrame:
    safe_limit = max(1, min(limit, 5000))
    conn = duckdb.connect(database=":memory:")
    conn.register("dataset", df)
    try:
        query = sql.strip().rstrip(";")
        wrapped = f"SELECT * FROM ({query}) AS q LIMIT {safe_limit}"
        return conn.execute(wrapped).df()
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Ошибка SQL: {str(exc)}") from exc
    finally:
        conn.close()

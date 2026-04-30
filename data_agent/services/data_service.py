from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import HTTPException

from config import STORAGE_DIR


def df_preview(df: pd.DataFrame, rows: int = 20) -> list[dict[str, Any]]:
    return df.head(rows).fillna("").to_dict(orient="records")


def profile_dataframe(df: pd.DataFrame) -> list[dict[str, Any]]:
    profile = []
    for col in df.columns:
        series = df[col]
        item: dict[str, Any] = {
            "column": str(col),
            "dtype": str(series.dtype),
            "null_count": int(series.isna().sum()),
            "unique_count": int(series.nunique(dropna=True)),
        }
        if pd.api.types.is_numeric_dtype(series):
            numeric = pd.to_numeric(series, errors="coerce")
            item["min"] = float(numeric.min()) if numeric.notna().any() else None
            item["max"] = float(numeric.max()) if numeric.notna().any() else None
            item["mean"] = float(numeric.mean()) if numeric.notna().any() else None
        profile.append(item)
    return profile


def filter_dataframe(
    df: pd.DataFrame,
    column: str,
    operator: str,
    value: str,
    limit: int = 100,
) -> dict[str, Any]:
    if column not in df.columns:
        raise HTTPException(status_code=400, detail=f"Колонка '{column}' не найдена.")

    operators = {"==", "!=", ">", ">=", "<", "<=", "contains"}
    if operator not in operators:
        raise HTTPException(status_code=400, detail="Некорректный оператор фильтра.")

    series = df[column]
    if operator == "contains":
        mask = series.astype(str).str.contains(value, case=False, na=False)
    else:
        cast_value: Any = float(value) if pd.api.types.is_numeric_dtype(series) else value
        if operator == "==":
            mask = series == cast_value
        elif operator == "!=":
            mask = series != cast_value
        elif operator == ">":
            mask = series > cast_value
        elif operator == ">=":
            mask = series >= cast_value
        elif operator == "<":
            mask = series < cast_value
        else:
            mask = series <= cast_value

    filtered = df[mask].head(max(1, min(limit, 1000)))
    return {
        "matched_rows": int(df[mask].shape[0]),
        "preview": filtered.fillna("").to_dict(orient="records"),
    }


def export_dataframe(df: pd.DataFrame, dataset_id: str, format_name: str) -> tuple[str, str, str]:
    fmt = format_name.lower()
    if fmt not in {"csv", "json", "parquet"}:
        raise HTTPException(status_code=400, detail="Формат экспорта: csv, json или parquet.")

    export_path = STORAGE_DIR / f"{dataset_id}_export.{fmt}"
    if fmt == "csv":
        df.to_csv(export_path, index=False)
        media = "text/csv"
    elif fmt == "json":
        df.to_json(export_path, orient="records", force_ascii=False, indent=2)
        media = "application/json"
    else:
        df.to_parquet(export_path, index=False)
        media = "application/octet-stream"

    return str(export_path), export_path.name, media

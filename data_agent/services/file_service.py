import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import HTTPException

from config import STORAGE_DIR, SUPPORTED_EXTENSIONS
from state import dataframes_cache, datasets_registry


def normalize_name(name: str | None) -> str:
    if not name:
        return "uploaded_file"
    return name.replace("\\", "_").replace("/", "_")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_dataframe_from_path(path: Path) -> pd.DataFrame:
    extension = path.suffix.lower()
    if extension == ".csv":
        return pd.read_csv(path)
    if extension in [".xlsx", ".xls"]:
        return pd.read_excel(path)
    if extension == ".json":
        return pd.read_json(path)
    if extension == ".parquet":
        return pd.read_parquet(path)
    raise HTTPException(
        status_code=400,
        detail="Неподдерживаемый формат. Используйте CSV, XLSX, JSON или Parquet.",
    )


def save_uploaded_file(raw: bytes, file_name: str) -> tuple[Path, str]:
    file_id = str(uuid.uuid4())
    safe_name = normalize_name(file_name)
    extension = Path(safe_name).suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Неподдерживаемый формат. Разрешены: {', '.join(sorted(SUPPORTED_EXTENSIONS))}",
        )
    target_path = STORAGE_DIR / f"{file_id}_{safe_name}"
    target_path.write_bytes(raw)
    return target_path, file_id


def dataset_info(dataset_id: str, df: pd.DataFrame, source_name: str, path: Path) -> dict[str, Any]:
    return {
        "id": dataset_id,
        "source_name": source_name,
        "path": str(path),
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "column_names": [str(c) for c in df.columns],
        "created_at": now_iso(),
    }


def register_dataset(dataset_id: str, df: pd.DataFrame, source_name: str, path: Path) -> dict[str, Any]:
    meta = dataset_info(dataset_id, df, source_name, path)
    datasets_registry[dataset_id] = meta
    dataframes_cache[dataset_id] = df
    return meta


def get_df(dataset_id: str) -> pd.DataFrame:
    if dataset_id in dataframes_cache:
        return dataframes_cache[dataset_id]
    meta = datasets_registry.get(dataset_id)
    if not meta:
        raise HTTPException(status_code=404, detail="Датасет не найден.")
    path = Path(meta["path"])
    df = load_dataframe_from_path(path)
    dataframes_cache[dataset_id] = df
    return df


def delete_dataset_files(dataset_id: str) -> None:
    meta = datasets_registry.pop(dataset_id, None)
    dataframes_cache.pop(dataset_id, None)
    if not meta:
        raise HTTPException(status_code=404, detail="Датасет не найден.")
    path = Path(meta["path"])
    if path.exists():
        path.unlink()

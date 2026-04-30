from typing import Any

import pandas as pd

from config import STORAGE_DIR

STORAGE_DIR.mkdir(parents=True, exist_ok=True)

# dataset_id -> metadata
datasets_registry: dict[str, dict[str, Any]] = {}

# dataset_id -> in-memory DataFrame cache
dataframes_cache: dict[str, pd.DataFrame] = {}

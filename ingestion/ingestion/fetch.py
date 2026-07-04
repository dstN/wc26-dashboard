import asyncio
import logging
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)


async def fetch_tables(url: str) -> Optional[list[pd.DataFrame]]:
    """Fast path: use pandas read_html (no JS rendering)."""
    loop = asyncio.get_event_loop()
    try:
        tables = await loop.run_in_executor(
            None, lambda: pd.read_html(url, flavor="lxml")
        )
        if tables:
            logger.debug("fetch_tables: %d tables from %s", len(tables), url)
            return tables
        return None
    except Exception as exc:
        logger.warning("fetch_tables failed for %s: %s", url, exc)
        return None

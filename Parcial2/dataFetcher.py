import os
from typing import List, Dict, Any
import httpx
from dotenv import load_dotenv

load_dotenv()

WB_API_URL = os.getenv(
    "WB_API_URL",
    "https://api.worldbank.org/v2/country/PAN/indicator/SH.IMM.MEAS?format=json&per_page=20000",
)


async def fetch_world_bank_data() -> List[Dict[str, Any]]:
    """
    Descarga y prepara los registros del Banco Mundial para Panamá (SH.IMM.MEAS).
    Devuelve una lista de dicts normalizados: {country, indicator, code, year, value}.
    """
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(WB_API_URL)
        r.raise_for_status()
        payload = r.json()

    # payload = [meta, data]
    if not isinstance(payload, list) or len(payload) < 2:
        return []

    _, data = payload
    out: List[Dict[str, Any]] = []

    for row in data:
        # row campos típicos: country, indicator, date (año), value
        try:
            country_name = row.get("country", {}).get("value", "Panama")
            indicator_name = row.get("indicator", {}).get("value", "SH.IMM.MEAS")
            year = int(row.get("date"))
            value = row.get("value")  # puede ser None
            out.append(
                {
                    "country": country_name,
                    "indicator": indicator_name,
                    "code": "SH.IMM.MEAS",
                    "year": year,
                    "value": float(value) if value is not None else None,
                }
            )
        except Exception:
            # Ignorar registros mal formados
            continue

    # Ordenar por año ascendente
    out.sort(key=lambda x: x["year"])
    return out

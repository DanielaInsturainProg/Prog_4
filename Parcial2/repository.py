from typing import List, Optional, Dict, Any
from .models import VaccineRecord, ProvinceRecord
import math
import hashlib

PANAMA_PROVINCES = [
    "Bocas del Toro", "Coclé", "Colón", "Chiriquí", "Darién",
    "Herrera", "Los Santos", "Panamá", "Panamá Oeste", "Veraguas",
    "Guna Yala", "Emberá", "Ngäbe-Buglé"
]


class VaccineRepository:
    """
    Repositorio en memoria. Se carga al iniciar la app con los datos del BM.
    """
    def __init__(self, records: List[Dict[str, Any]]):
        self._records = [VaccineRecord(**r) for r in records]
        # Índices simples por año
        self._by_year: Dict[int, VaccineRecord] = {r.year: r for r in self._records}

    def all(self) -> List[VaccineRecord]:
        return list(self._records)

    def by_year(self, year: int) -> Optional[VaccineRecord]:
        return self._by_year.get(year)

    def provinces_for_year(self, year: int) -> List[ProvinceRecord]:
        """
        Simula datos provinciales a partir del valor nacional de ese año.
        Si el valor nacional es None, devuelve provincias con None.
        La simulación reparte +/- hasta ~3 puntos porcentuales deterministas por provincia.
        """
        base = self.by_year(year)
        if not base:
            return []

        if base.value is None:
            return [ProvinceRecord(province=p, year=year, value=None) for p in PANAMA_PROVINCES]

        out: List[ProvinceRecord] = []
        for prov in PANAMA_PROVINCES:
            # offset determinista por provincia y año en [-3, +3]
            h = hashlib.sha256(f"{prov}-{year}".encode()).hexdigest()
            # tomar 2 bytes, mapear a [0,1], escalar a [-3, +3]
            v = int(h[:4], 16) / 0xFFFF
            offset = (v * 6.0) - 3.0
            val = max(0.0, min(100.0, base.value + offset))
            # redondeo a una cifra decimal
            out.append(ProvinceRecord(province=prov, year=year, value=round(val, 1)))
        return out

from fastapi import APIRouter, HTTPException
from typing import List
from .models import VaccineRecord, VaccineList, ProvinceRecord
from .repository import VaccineRepository

router = APIRouter()

# Este repositorio será inyectado desde main.py
repo: VaccineRepository | None = None


@router.get("/vacunas", response_model=VaccineList, tags=["vacunas"])
async def get_all():
    assert repo is not None
    return {"data": repo.all()}


@router.get("/vacunas/{year}", response_model=VaccineRecord, tags=["vacunas"])
async def get_by_year(year: int):
    assert repo is not None
    rec = repo.by_year(year)
    if not rec:
        raise HTTPException(status_code=404, detail="No hay registro para ese año")
    return rec


@router.get("/vacunas/provincia/{name}", response_model=List[ProvinceRecord], tags=["vacunas"])
async def get_province_years(name: str):
    """
    Devuelve todos los años simulados para una provincia dada.
    (Conveniencia adicional)
    """
    assert repo is not None
    name_norm = name.strip().lower()
    years = sorted({r.year for r in repo.all()})
    out: list[ProvinceRecord] = []
    for y in years:
        provs = repo.provinces_for_year(y)
        match = next((p for p in provs if p.province.lower() == name_norm), None)
        if match:
            out.append(match)
    if not out:
        raise HTTPException(status_code=404, detail="Provincia no encontrada o sin datos")
    return out


@router.get("/vacunas/{year}/provincias", response_model=list[ProvinceRecord], tags=["vacunas"])
async def get_all_provinces_for_year(year: int):
    """Devuelve datos simulados por provincia para un año dado."""
    assert repo is not None
    if not repo.by_year(year):
        raise HTTPException(status_code=404, detail="No hay registro para ese año")
    return repo.provinces_for_year(year)

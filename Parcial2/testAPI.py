import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.repository import VaccineRepository
from app import api as api_routes


@pytest.fixture(autouse=True)
def setup_repo(monkeypatch):
    # Datos mínimos falsos para pruebas (evita llamar a la API real)
    fake = [
        {"country": "Panama", "indicator": "Immunization, measles (% of children ages 12-23 months)",
         "code": "SH.IMM.MEAS", "year": 2000, "value": 85.0},
        {"country": "Panama", "indicator": "Immunization, measles (% of children ages 12-23 months)",
         "code": "SH.IMM.MEAS", "year": 2001, "value": 87.3},
        {"country": "Panama", "indicator": "Immunization, measles (% of children ages 12-23 months)",
         "code": "SH.IMM.MEAS", "year": 2002, "value": None},
    ]
    api_routes.repo = VaccineRepository(fake)
    yield
    api_routes.repo = None


def test_get_all():
    app = create_app()
    client = TestClient(app)
    r = client.get("/vacunas")
    assert r.status_code == 200
    data = r.json()["data"]
    assert isinstance(data, list)
    assert len(data) == 3
    assert data[0]["year"] == 2000


def test_get_by_year_found_and_not_found():
    app = create_app()
    client = TestClient(app)
    r = client.get("/vacunas/2001")
    assert r.status_code == 200
    assert r.json()["value"] == 87.3

    r2 = client.get("/vacunas/1999")
    assert r2.status_code == 404


def test_get_provinces_for_year():
    app = create_app()
    client = TestClient(app)
    r = client.get("/vacunas/2001/provincias")
    assert r.status_code == 200
    provs = r.json()
    assert len(provs) >= 10
    assert all(p["year"] == 2001 for p in provs)

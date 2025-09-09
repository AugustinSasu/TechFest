import pytest
from schemas.dealership import DealershipBase, DealershipCreate, DealershipUpdate, DealershipOut
from pydantic import ValidationError

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from main import app


def test_dealership_base_valid():
    obj = DealershipBase(name="Test Dealer", city="City", region="Region")
    assert obj.name == "Test Dealer"
    assert obj.city == "City"
    assert obj.region == "Region"

def test_dealership_base_missing_name():
    with pytest.raises(ValidationError):
        DealershipBase(city="City", region="Region")

def test_dealership_base_name_too_long():
    with pytest.raises(ValidationError):
        DealershipBase(name="x" * 101)

def test_dealership_create_inherits_base():
    obj = DealershipCreate(name="Dealer", city="A", region="B")
    assert isinstance(obj, DealershipBase)

def test_dealership_update_partial():
    obj = DealershipUpdate(city="New City")
    assert obj.city == "New City"
    assert obj.name is None

def test_dealership_update_name_too_long():
    with pytest.raises(ValidationError):
        DealershipUpdate(name="y" * 101)

def test_dealership_out_serialization():
    obj = DealershipOut(name="D", city="C", region="R", dealership_id=123)
    data = obj.model_dump()
    assert data["dealership_id"] == 123
    assert data["name"] == "D"
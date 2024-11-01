import pytest

from models.PackVeggie import PackVeggie
from models.UnitPriceVeggie import UnitPriceVeggie
from models.WeightedVeggie import WeightedVeggie
from models.Veggie import Veggie


def test_pack_veggie_creation():
    pack_veggie = PackVeggie(
        vegName="Mushrooms",
        numberOfPacks=10,
        pricePerPack=4.99
    )
    assert pack_veggie.vegName == "Mushrooms"
    assert pack_veggie.numberOfPacks == 10
    assert pack_veggie.pricePerPack == 4.99
    assert pack_veggie.__tablename__ == 'pack_veggies'
    assert str(pack_veggie).endswith("| Storage: 10 packs, Price: $4.99/pack")


def test_unit_price_veggie_creation():
    unit_veggie = UnitPriceVeggie(
        vegName="Corn",
        quantity=50,
        pricePerUnit=1.50
    )
    assert unit_veggie.vegName == "Corn"
    assert unit_veggie.quantity == 50
    assert unit_veggie.pricePerUnit == 1.50
    assert unit_veggie.__tablename__ == 'unit_price_veggies'
    assert str(unit_veggie).endswith("| Storage: 50 units, Price: $1.50/unit")


def test_weighted_veggie_creation():
    weighted_veggie = WeightedVeggie(
        vegName="Potatoes",
        weight=25.5,
        pricePerKilo=2.99
    )
    assert weighted_veggie.vegName == "Potatoes"
    assert weighted_veggie.weight == 25.5
    assert weighted_veggie.pricePerKilo == 2.99
    assert weighted_veggie.__tablename__ == 'weighted_veggies'
    assert str(weighted_veggie).endswith("| Storage: 25.50kg, Price: $2.99/kg")


def test_veggie_inheritance():
    pack_veggie = PackVeggie("Carrots", 5, 3.99)
    unit_veggie = UnitPriceVeggie("Lettuce", 30, 2.50)
    weighted_veggie = WeightedVeggie("Onions", 15.75, 1.99)

    # Test inheritance from Veggie class
    assert isinstance(pack_veggie, Veggie)
    assert isinstance(unit_veggie, Veggie)
    assert isinstance(weighted_veggie, Veggie)

    # Test vegName attribute from parent class
    assert hasattr(pack_veggie, 'vegName')
    assert hasattr(unit_veggie, 'vegName')
    assert hasattr(weighted_veggie, 'vegName')


def test_veggie_str_representation():
    test_veggies = [
        PackVeggie("Beans", 8, 5.99),
        UnitPriceVeggie("Garlic", 100, 0.99),
        WeightedVeggie("Tomatoes", 10.25, 3.99)
    ]

    for veggie in test_veggies:
        # Check that str contains the veggie name
        assert veggie.vegName in str(veggie)
        # Check that str contains the word "Price"
        assert "Price: $" in str(veggie)
import pytest

from models.PremadeBox import PremadeBox
from models.PackVeggie import PackVeggie


def test_premadebox_creation():
    box = PremadeBox(
        boxSize='M',
        numbOfBoxes=5
    )
    assert box.boxSize == 'M'
    assert box.numbOfBoxes == 5
    assert box.__tablename__ == 'premadeboxes'
    assert len(box.veggies) == 0


def test_box_prices():
    assert PremadeBox.getBoxPrice('S') == '$5.0'
    assert PremadeBox.getBoxPrice('M') == '$8.0'
    assert PremadeBox.getBoxPrice('L') == '$10.0'
    assert PremadeBox.getBoxPrice('X') == '$0.0'  # Invalid size


def test_max_veggies():
    assert PremadeBox.getMaxVeggies('S') == 3
    assert PremadeBox.getMaxVeggies('M') == 5
    assert PremadeBox.getMaxVeggies('L') == 8
    assert PremadeBox.getMaxVeggies('X') == 0  # Invalid size


def test_add_veggie():
    box = PremadeBox(boxSize='S', numbOfBoxes=1)
    veggie1 = PackVeggie("Carrots", 5, 3.99)
    veggie2 = PackVeggie("Mushrooms", 3, 4.99)
    veggie3 = PackVeggie("Beans", 4, 2.99)
    veggie4 = PackVeggie("Peas", 2, 3.50)

    # Add veggies up to max (3 for small box)
    assert box.addVeggie(veggie1) == True
    assert box.addVeggie(veggie2) == True
    assert box.addVeggie(veggie3) == True
    # Try to add one more (should fail)
    assert box.addVeggie(veggie4) == False

    assert len(box.veggies) == 3


def test_remove_veggie():
    box = PremadeBox(boxSize='M', numbOfBoxes=1)
    veggie1 = PackVeggie("Carrots", 5, 3.99)
    veggie2 = PackVeggie("Mushrooms", 3, 4.99)

    # Add and then remove veggies
    box.addVeggie(veggie1)
    box.addVeggie(veggie2)

    assert box.removeVeggie(veggie1) == True
    assert len(box.veggies) == 1
    assert box.removeVeggie(veggie1) == False 
    assert box.removeVeggie(veggie2) == True
    assert len(box.veggies) == 0


def test_can_add_veggie():
    box = PremadeBox(boxSize='S', numbOfBoxes=1)

    # Initially can add veggies
    assert box.canAddVeggie() == True

    # Add max number of veggies
    for _ in range(3):  # Small box max is 3
        veggie = PackVeggie(f"Veggie{_}", 1, 1.99)
        box.addVeggie(veggie)

    # Should not be able to add more
    assert box.canAddVeggie() == False
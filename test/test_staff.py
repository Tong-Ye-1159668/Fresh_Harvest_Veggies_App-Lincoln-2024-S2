# test_staff.py
import pytest
from datetime import date

from models.Staff import Staff


def test_staff_creation():
    staff = Staff(
        firstName="John",
        lastName="Doe",
        username="johndoe",
        password="password123",
        dateJoined=date(2024, 1, 1),
        deptName="Sales"
    )
    assert staff.firstName == "John"
    assert staff.lastName == "Doe"
    assert staff.username == "johndoe"
    assert staff.password == "password123"
    assert staff.dateJoined == date(2024, 1, 1)
    assert staff.deptName == "Sales"


def test_staff_inheritance():
    staff = Staff(
        firstName="Jane",
        lastName="Smith",
        username="janesmith",
        password="password456",
        dateJoined=date(2024, 2, 1),
        deptName="IT"
    )
    assert isinstance(staff, Staff)
    assert staff.__tablename__ == 'staffs'
    # Staff specific attributes exist
    assert hasattr(staff, 'dateJoined')
    assert hasattr(staff, 'deptName')
    # Person (parent) attributes exist
    assert hasattr(staff, 'firstName')
    assert hasattr(staff, 'lastName')


def test_staff_department_assignment():
    staff = Staff(
        firstName="Bob",
        lastName="Wilson",
        username="bobwilson",
        password="password789",
        dateJoined=date(2024, 3, 1),
        deptName="HR"
    )
    assert staff.deptName == "HR"

    # Test department change
    staff.deptName = "Marketing"
    assert staff.deptName == "Marketing"


def test_staff_representation():
    staff = Staff(
        firstName="Alice",
        lastName="Brown",
        username="alicebrown",
        password="password321",
        dateJoined=date(2024, 4, 1),
        deptName="Finance"
    )
    # Test basic attribute access
    assert f"{staff.firstName} {staff.lastName}" == "Alice Brown"
    assert staff.dateJoined.year == 2024
    assert staff.dateJoined.month == 4
    assert staff.dateJoined.day == 1
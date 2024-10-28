from models.Customer import Customer
from models.CorporateCustomer import CorporateCustomer
from models.Staff import Staff
from models.WeightedVeggie import WeightedVeggie
from models.PackVeggie import PackVeggie
from models.UnitPriceVeggie import UnitPriceVeggie
from datetime import datetime


def getCustomerList():
    """Read the customerData.txt file and return a list of Customer objects."""
    customerList = []
    with open("data/customerData.txt", "r") as customerFile:
        for line in customerFile:
            if line.strip():
                firstName, lastName, username, password, address = line.strip().split(',', 4)
                customer = Customer(
                    firstName=firstName.strip(),
                    lastName=lastName.strip(),
                    username=username.strip(),
                    password=password.strip(),
                    custAddress=address.strip()
                )
                customerList.append(customer)
    return customerList


def getCorporateCustomerList():
    """Read the corporateCustomerData.txt file and return a list of CorporateCustomer objects."""
    corporateList = []
    with open("data/corporateCustomerData.txt", "r") as corpFile:
        for line in corpFile:
            if line.strip():
                firstName, lastName, username, password, address = line.strip().split(',', 4)
                customer = CorporateCustomer(
                    firstName=firstName.strip(),
                    lastName=lastName.strip(),
                    username=username.strip(),
                    password=password.strip(),
                    custAddress=address.strip()
                )
                corporateList.append(customer)
    return corporateList


def getStaffList():
    """Read the staffData.txt file and return a list of Staff objects."""
    staffList = []
    with open("data/staffData.txt", "r") as staffFile:
        for line in staffFile:
            if line.strip():
                firstName, lastName, username, password, date_joined, dept = line.strip().split(',')
                staff = Staff(
                    firstName=firstName.strip(),
                    lastName=lastName.strip(),
                    username=username.strip(),
                    password=password.strip(),
                    dateJoined=datetime.strptime(date_joined.strip(), '%Y-%m-%d'),
                    deptName=dept.strip()
                )
                staffList.append(staff)
    return staffList


def getPackVeggieList():
    """Read the packVeggieData.txt file and return a list of PackVeggie objects."""
    packList = []
    with open("data/packVeggieData.txt", "r") as packFile:
        for line in packFile:
            if line.strip():
                name, num_packs, price = line.strip().split(',')
                veggie = PackVeggie(
                    vegName=name.strip(),
                    numberOfPacks=int(num_packs),
                    pricePerPack=float(price)
                )
                packList.append(veggie)
    return packList


def getUnitPriceVeggieList():
    """Read the unitPriceVeggieData.txt file and return a list of UnitPriceVeggie objects."""
    unitList = []
    with open("data/unitPriceVeggieData.txt", "r") as unitFile:
        for line in unitFile:
            if line.strip():
                name, quantity, price = line.strip().split(',')
                veggie = UnitPriceVeggie(
                    vegName=name.strip(),
                    quantity=int(quantity),
                    pricePerUnit=float(price)
                )
                unitList.append(veggie)
    return unitList


def getWeightedVeggieList():
    """Read the weightedVeggieData.txt file and return a list of WeightedVeggie objects."""
    weightedList = []
    with open("data/weightedVeggieData.txt", "r") as weightedFile:
        for line in weightedFile:
            if line.strip():
                name, weight, price = line.strip().split(',')
                veggie = WeightedVeggie(
                    vegName=name.strip(),
                    weight=float(weight) / 1000,  # Convert grams to kilos
                    pricePerKilo=float(price)
                )
                weightedList.append(veggie)
    return weightedList


def importAllData(session):
    """Import all data into the database."""
    try:
        # Add customers
        for customer in getCustomerList():
            session.add(customer)

        # Add corporate customers
        for corp_customer in getCorporateCustomerList():
            session.add(corp_customer)

        # Add staff
        for staff in getStaffList():
            session.add(staff)

        # Add pack veggies
        for pack_veggie in getPackVeggieList():
            session.add(pack_veggie)

        # Add unit price veggies
        for unit_veggie in getUnitPriceVeggieList():
            session.add(unit_veggie)

        # Add weighted veggies
        for weighted_veggie in getWeightedVeggieList():
            session.add(weighted_veggie)

        session.commit()
        print("All data imported successfully")

    except Exception as e:
        print(f"Error importing data: {str(e)}")
        session.rollback()
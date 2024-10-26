from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.CorporateCustomer import CorporateCustomer
from models.base import Base
from models.Customer import Customer


# Database configuration
engine = create_engine('mysql+mysqldb://root:Crazy2447YT!@localhost:3306/testdb', echo=True)
Base.metadata.create_all(engine)  # Creates tables

# Create session
Session = sessionmaker(bind=engine)
session = Session()

# Example: Add a customer
customer1 = Customer(firstName='Joe', lastName='Bloggs', username='jbloggs', password='1223', custAddress='auckland')
customer2 = CorporateCustomer(firstName='Joe', lastName='Bloggs', username='jbloggs1', password='1223', custAddress='auckland', maxCredit=1000, minBalance=100)
session.add(customer1)
session.add(customer2)
session.commit()

# Query all persons
persons = session.query(Customer).all()
for person in persons:
    print(person)

# Close session
session.close()

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.base import Base



# Database configuration
engine = create_engine('mysql+mysqldb://root:Crazy2447YT!@localhost:3306/testdb', echo=True)
Base.metadata.create_all(engine)  # Creates tables

# Create session
Session = sessionmaker(bind=engine)
session = Session()


# Close session
session.close()

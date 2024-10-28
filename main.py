from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import *
from views.login_window import LoginWindow
from importData import importAllData


def main():
    # Create database engine
    engine = create_engine('mysql+mysqldb://root:Crazy2447YT!@localhost:3306/testdb', echo=True)

    # Create tables
    Base.metadata.create_all(engine)

    # Import data
    with Session(engine) as session:
        importAllData(session)

    # Start application
    app = LoginWindow(engine)
    app.mainloop()


if __name__ == "__main__":
    main()
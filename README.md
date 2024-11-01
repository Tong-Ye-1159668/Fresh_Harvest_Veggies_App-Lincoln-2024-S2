# Fresh Harvest Veggies
## Tong Ye 1159668

### System Requirements

1. Python 3.x
2. SQLAlchemy
3. MySQL Server
4. MySQL Connector/Python (`mysql-connector-python`)
5. pytest (for testing)

### Setup Instructions

1. Install required packages:
   ```bash
   pip install sqlalchemy mysql-connector-python pytest
   ```

2. Set up local MySQL database:
   - Create a database named `fhvdb`
   - Configure MySQL credentials in `main.py`
   - engine = create_engine('mysql+mysqldb://root:YourPassword@localhost:3306/fhvdb')

3. Run the application:
   ```bash
   python main.py
   ```

### Testing

The project uses pytest for unit testing and integration testing. To run tests:

Test files are organized in the `tests/` directory.


#### Private Customer Accounts
| Username  | Password  |
|-----------|-----------|
| username1 | userpass  |
| username2 | userpass  |
| username3 | userpass  |
| username4 | userpass  |
| username5 | userpass  |
| username6 | userpass  |
| username7 | userpass  |
| username8 | userpass  |

#### Corporate Customer Accounts
| Username   | Password  |
|------------|-----------|
| cusername1 | userpass  |
| cusername2 | userpass  |
| cusername3 | userpass  |

#### Staff Accounts
| Username   | Password   |
|------------|------------|
| staffuser1 | staffpass  |
| staffuser2 | staffpass  |
| staffuser3 | staffpass  |

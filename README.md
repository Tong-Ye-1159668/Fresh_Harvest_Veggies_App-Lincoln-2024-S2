# Fresh Harvest Veggies Order System

#### Submitted on 01 November 2024

A comprehensive vegetable ordering and management system for Fresh Harvest Veggies as part of the COMP 642: Advanced Programming course during Semester 2 of my Master of Applied Computing studies at Lincoln University. This application demonstrates advanced Object-Oriented Programming principles while providing a practical solution for managing vegetable orders, premade boxes, and customer accounts.

## Interface

Login Window

![image](https://github.com/user-attachments/assets/d3c17c74-1e85-46ac-8314-2f7319814d29)

Customer Order Placement Window

![image](https://github.com/user-attachments/assets/e1779602-deaf-4b31-9680-85b363a6699d)

Customer Current Orders Window

![image](https://github.com/user-attachments/assets/43fbce5c-0f73-467d-b3c6-41ee47c26378)

Staff Manage Order Window

![image](https://github.com/user-attachments/assets/42ee32f4-6361-4813-b40c-e000b0017012)

Staff Manage Customer Window

![image](https://github.com/user-attachments/assets/2644763e-d9ee-495c-adc3-7ed05712e0f9)

Staff View Report Window

![image](https://github.com/user-attachments/assets/62040c44-2f26-4379-927f-724e625b6777)


## Features

### Customer Portal
- **Account Management**:
  - Secure login/logout functionality
  - View personal account information
- **Shopping Experience**:
  - Browse available vegetables
  - View premade box options
  - Place orders with multiple payment methods:
    - Credit card
    - Debit card
    - Account charging
- **Order Management**:
  - Track current orders
  - View order history
  - Cancel unfulfilled orders

### Staff Dashboard
- **Inventory Overview**:
  - Complete vegetable catalog
  - Premade box management
- **Order Processing**:
  - Monitor current orders
  - Update order status
  - Access order history
- **Customer Management**:
  - Customer database access
  - Generate customer reports
- **Business Analytics**:
  - Weekly sales reports
  - Monthly sales summaries
  - Annual performance metrics
  - Popular items tracking

## Technical Details

### Core Technologies
- **Backend:** Python 3.x
- **Database:** MySQL with SQLAlchemy ORM
- **GUI Framework:** Tkinter
- **Testing:** pytest

### Design Pattern
- Model-View-Controller (MVC) architecture
- Object-Oriented Programming principles
- Robust error handling and prevention
- Secure data management

## Purpose
This project emphasizes my ability to:
- Design and implement a comprehensive business application using Object-Oriented Programming principles
- Create intuitive user interfaces using Tkinter that serve different user roles (customers and staff)
- Develop robust database interactions using SQLAlchemy ORM
- Write maintainable, well-documented, and thoroughly tested code
- Handle complex business logic including order processing and payment systems
- Apply software design patterns (MVC) effectively in a real-world application

The inclusion of a custom-designed logo adds a professional touch, reflecting my attention to detail and creativity in software development.

---------------------

## Set Up the Environment

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

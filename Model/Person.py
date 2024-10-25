from abc import ABC, abstractmethod

from IPython.utils.coloransi import value
from sqlalchemy import Column, Integer, String

class Person(Base, ABC):
    __tablename__ = 'persons'

    __firstName = Column(String(50))
    __lastName = Column(String(50))
    __username = Column(String(50), unique = True)
    __password = Column(String(50))

    def __init__(self, firstName, lastName, username, password):
        self.__firstName = firstName
        self.__lastName = lastName
        self.__username = username
        self.__password = password

    # Abstract method to enforce implementation in subclass
    def getUserRole(self):
        pass

    # Getter and setter for firstname
    @property
    def firstName(self):
        return self.__firstName

    @firstName.setter
    def firstName(self, value):
        # Check if value is a string
        if not isinstance(value, str):
            raise ValueError("First name must be a string")

        # Strip whitespace and check if it's not empty
        value = value.strip()
        if not value:
            raise ValueError("First name cannot be empty")

        # Check if the length is between 1 and 50 characters
        if len(value) > 50:
            raise ValueError("First name must be between 1 and 50 characters")

        self.__firstName = value

    # Getter and setter for lastname
    @property
    def lastName(self):
        return self.__lastName

    @lastName.setter
    def lastName(self, value):
        # Check if value is a string
        if not isinstance(value, str):
            raise ValueError("Last name must be a string")

        # Strip whitespace and check if it's not empty
        value = value.strip()
        if not value:
            raise ValueError("Last name cannot be empty")

        # Check if the length is between 1 and 50 characters
        if len(value) > 50:
            raise ValueError("Last name must be between 1 and 50 characters")

        self.__lastName = value

    # Getter and setter for username
    @property
    def username(self):
        return self.__username

    @username.setter
    def username(self, value):
        # Check if value is a string
        if not isinstance(value, str):
            raise ValueError("Username must be a string")

        # Strip whitespace and check if it's not empty
        value = value.strip()
        if not value:
            raise ValueError("Username cannot be empty")

        # Check if the length is between 1 and 50 characters
        if len(value) > 50:
            raise ValueError("Username must be between 1 and 50 characters")

        self.__username = value

    # Getter and setter for password
    @property
    def password(self):
        return self.__password

    @password.setter
    def password(self, value):
        # Check if value is a string
        if not isinstance(value, str):
            raise ValueError("Password must be a string")

        # Strip whitespace and check if it's not empty
        value = value.strip()
        if not value:
            raise ValueError("Password cannot be empty")

        # Check if the length is between 6 and 50 characters
        if len(value) < 6 or len(value) > 50:
            raise ValueError("Password must be between 6 and 50 characters")

        self.__password = value


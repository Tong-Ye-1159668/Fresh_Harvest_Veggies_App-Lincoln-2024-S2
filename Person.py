from abc import ABC, abstractmethod

from IPython.utils.coloransi import value


class Person(ABC):
    def __init__(self, firstName, lastName):
        self.__firstName = firstName
        self.__lastName = lastName

    # Getter and setter for firstName
    @property
    def firstName(self):
        return self.__firstName

    @firstName.setter
    def firstName(self, value):
        self.__firstName = value


    # Getter and setter for lastName
    @property
    def lastName(self):
        return self.__lastName

    @lastName.setter
    def lastName(self, value):
        self.__lastName = value

class Customer(Person):
    def __init__(self, firstName, lastName, cID, cAddress, cBalance, maxOwing):
        super().__init__(firstName, lastName)
        self.__custID = cID
        self.__custAddress = cAddress
        self.__custBalance = cBalance
        self.__maxOwing = maxOwing

    # Getter and setter for custID
    @property
    def custID(self):
        return self.__custID

    @custID.setter
    def custID(self, value):
        self.__custID = value

    # Getter and setter for custAddress
    @property
    def custAddress(self):
        return self.__custAddress

    @custAddress.setter
    def custAddress(self, value):
        self.__custAddress = value

    # Getter and setter for custBalance
    @property
    def custBalance(self):
        return self.__custBalance

    @custBalance.setter
    def custBalance(self):
        self.__custBalance = value

    # Getter and setter for maxOwing
    @property
    def maxOwing(self):
        return self.__maxOwing

    @maxOwing.setter
    def maxOwing(self, value):
        self.__maxOwing = value

    def getCustomerName(self):
        return self.firstName + ' ' + self.lastName

class CorporateCustomer(Customer):
    def __init__(self, discountRate, maxCredit, minBalance,
                 firstName, lastName, cID, cAddress, cBalance, maxOwing):
        self.__discountRate = discountRate
        self.__maxCredit = maxCredit
        self.__minBalance = minBalance
        Customer.__init__(self, firstName, lastName, cID, cAddress, cBalance, maxOwing)


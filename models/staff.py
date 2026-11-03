from abc import abstractmethod
from models.person import Person


P = 2420089   #Reg number of Marlvin


class Staff(Person):

    @abstractmethod
    def fee(self):
        pass
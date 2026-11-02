from abc import abstractmethod
from models.person import Person


P = 2420089


class Staff(Person):

    @abstractmethod
    def fee(self):
        pass

    def buffer_hours(self):
        return 0
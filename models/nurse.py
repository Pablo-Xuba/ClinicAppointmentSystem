from models.staff import P, Staff


class Nurse(Staff):

    REG_NUMBER = P

    def role(self):
        return "Nurse"

    def fee(self):
        return 10 + (self.REG_NUMBER % 3)

    def buffer_hours(self):
        return 1
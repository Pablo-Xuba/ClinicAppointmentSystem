from models.staff import P, Staff


class Doctor(Staff):

    REG_NUMBER = P

    def role(self):
        return "Doctor"

    def fee(self):
        return 40 + 5 * (self.REG_NUMBER % 5)
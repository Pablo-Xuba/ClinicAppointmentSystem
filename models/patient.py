from models.person import Person


class Patient(Person):

    def __init__(self, name, person_id, emergency=False):
        super().__init__(name, person_id)

        self._emergency = emergency

    def role(self):
        return "Patient"

    @property
    def emergency(self):
        return self._emergency

    def flag_emergency(self):
        self._emergency = True

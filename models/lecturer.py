from models.person import Person


class Lecturer(Person):
    def __init__(self, name, person_id, module_name):
        self._module_name = module_name
        super().__init__(name, person_id)

    @property
    def module_name(self):
        return self._module_name

    def role(self):
        return "Lecturer"
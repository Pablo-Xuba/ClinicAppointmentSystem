from models.doctor import Doctor
from models.lecturer import Lecturer


class MedicalLecturer(Doctor, Lecturer):
    def __init__(self, name, person_id, module_name):
        super().__init__(name, person_id, module_name)

    def role(self):
        return "Doctor and Lecturer"
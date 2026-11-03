from models.doctor import Doctor
from models.lecturer import Lecturer


class MedicalLecturer(Doctor, Lecturer):
    def __init__(self, name, person_id, module_name):
        # Python's MRO passes this call through Doctor, Staff and Lecturer.
        super().__init__(name, person_id, module_name)

    def role(self):
        return "Doctor and Lecturer"
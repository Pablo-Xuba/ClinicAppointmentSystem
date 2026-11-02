from models.appointment import Appointment
from models.patient import Patient
from models.staff import Staff
from policies.cancellation_policy import CancellationPolicy
from services.appointment_log import AppointmentLog
from services.clock import Clock


# Invariants:
# 1. Patient and staff person IDs are unique across the clinic.
# 2. A patient and a staff member each have at most one active appointment
#    at any hour.
# 3. Emergency bookings may bump pending appointments, never confirmed ones.
# 4. Public clinic actions are logged, including failures.
class Clinic:
    def __init__(
        self,
        clock=None,
        appointment_log=None,
        cancellation_policy=None,
    ):
        self._clock = Clock() if clock is None else clock
        self._log = AppointmentLog() if appointment_log is None else appointment_log
        self._cancellation_policy = (
            CancellationPolicy()
            if cancellation_policy is None
            else cancellation_policy
        )
        self._patients = []
        self._staff = []
        self._appointments = []
        self._next_appointment_id = 1

    @property
    def patients(self):
        return tuple(self._patients)

    @property
    def staff_members(self):
        return tuple(self._staff)

    @property
    def appointments(self):
        return tuple(self._appointments)

    @property
    def current_hour(self):
        return self._clock.now()

    @property
    def log_entries(self):
        return self._log.entries

    def add_patient(self, patient: Patient):
        with self._log.action("add patient") as log:
            if not isinstance(patient, Patient):
                raise ValueError("Only Patient objects can be registered as patients")
            self._ensure_unique_person_id(patient.person_id)
            self._patients.append(patient)
            log.write(f"ADDED patient #{patient.person_id}")
        return patient

    def add_staff(self, staff: Staff):
        with self._log.action("add staff member") as log:
            if not isinstance(staff, Staff):
                raise ValueError("Only Staff objects can be registered as staff")
            self._ensure_unique_person_id(staff.person_id)
            self._staff.append(staff)
            log.write(f"ADDED staff #{staff.person_id} ({staff.role()})")
        return staff

    def flag_patient_emergency(self, person_id: int):
        with self._log.action(f"flag patient #{person_id} as emergency") as log:
            patient = self._find_patient(person_id)
            patient.flag_emergency()
            log.write(f"FLAGGED patient #{person_id} as emergency")
        return patient

    def book_appointment(self, patient: Patient, staff: Staff, start_hour: int):
        with self._log.action("booking") as log:
            self._ensure_registered(patient, self._patients, "patient")
            self._ensure_registered(staff, self._staff, "staff member")

            if start_hour < self._clock.now():
                raise ValueError("Cannot book an appointment in the past")

            conflicts = self._conflicts(patient, staff, start_hour)
            if conflicts:
                if not patient.emergency:
                    raise ValueError(
                        "Patient or staff member already has an appointment at that hour"
                    )
                if any(
                    appointment.status == Appointment.CONFIRMED
                    for appointment in conflicts
                ):
                    raise ValueError(
                        "An emergency booking cannot bump a confirmed appointment"
                    )
                if self._clock.now() >= start_hour:
                    raise ValueError(
                        "An emergency booking cannot bump an appointment "
                        "that has already started"
                    )

                for appointment in conflicts:
                    appointment.cancel(self._clock.now(), reason="bumped")
                    log.write(
                        f"CANCELLED appointment #{appointment.appointment_id}, "
                        "reason=bumped"
                    )

            appointment = Appointment(
                patient,
                staff,
                start_hour,
                appointment_id=self._next_appointment_id,
                cancellation_policy=self._cancellation_policy,
            )
            self._appointments.append(appointment)
            self._next_appointment_id += 1
            log.write(
                f"BOOKED appointment #{appointment.appointment_id} "
                f"for hour {start_hour}"
            )
        return appointment

    def confirm_appointment(self, appointment_id: int):
        with self._log.action(f"confirm appointment #{appointment_id}") as log:
            appointment = self._find_appointment(appointment_id)
            appointment.confirm()
            log.write(f"CONFIRMED appointment #{appointment_id}")
        return appointment

    def cancel_appointment(self, appointment_id: int, reason="normal"):
        with self._log.action(f"cancel #{appointment_id}") as log:
            appointment = self._find_appointment(appointment_id)
            appointment.cancel(self._clock.now(), reason=reason)
            log.write(
                f"CANCELLED appointment #{appointment_id}, reason={reason}"
            )
        return appointment

    def advance_time(self, hours: int):
        with self._log.action(f"advance clock by {hours} hour(s)") as log:
            self._clock.advance(hours)
            log.write(f"CLOCK hour={self._clock.now()}")
        return self._clock.now()

    def _ensure_unique_person_id(self, person_id):
        if any(person.person_id == person_id for person in self._patients):
            raise ValueError(f"Person ID {person_id} is already in use")
        if any(person.person_id == person_id for person in self._staff):
            raise ValueError(f"Person ID {person_id} is already in use")

    @staticmethod
    def _ensure_registered(person, registered_people, description):
        if not any(person is registered for registered in registered_people):
            raise ValueError(f"The {description} is not registered with this clinic")

    def _conflicts(self, patient, staff, start_hour):
        return [
            appointment
            for appointment in self._appointments
            if appointment.start_hour == start_hour
            and appointment.status != Appointment.CANCELLED
            and (appointment.patient is patient or appointment.staff is staff)
        ]

    def _find_appointment(self, appointment_id):
        for appointment in self._appointments:
            if appointment.appointment_id == appointment_id:
                return appointment
        raise LookupError(f"Appointment #{appointment_id} was not found")

    def _find_patient(self, person_id):
        for patient in self._patients:
            if patient.person_id == person_id:
                return patient
        raise LookupError(f"Patient #{person_id} was not found")
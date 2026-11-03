from models.patient import Patient
from models.staff import Staff
from policies.cancellation_policy import CancellationPolicy


# Rules (invariants) this class always keeps true:
# - Every appointment has a real Patient and Staff member.
# - The start hour is a whole number from 0 to 168; each visit lasts one hour.
# - A cancelled appointment stays cancelled and cannot be cancelled twice.
# - An appointment cannot be cancelled after it starts.
# - A confirmed appointment needs at least two hours' notice to be cancelled.
class Appointment:

    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    DURATION_HOURS = 1

    def __init__(
        self,
        patient: Patient,
        staff: Staff,
        start_hour: int,
        appointment_id=None,
        cancellation_policy=None,
    ):
        try:
            whole_hour = int(start_hour)
        except (TypeError, ValueError, OverflowError) as error:
            raise ValueError(
                "Appointment hour must be between 0 and 168"
            ) from error
        if (
            isinstance(start_hour, bool)
            or not 0 <= whole_hour <= 168
            or start_hour != whole_hour
        ):
            raise ValueError("Appointment hour must be between 0 and 168")
        if not isinstance(patient, Patient) or not isinstance(staff, Staff):
            raise ValueError("An appointment requires a Patient and a Staff member")

        self._patient = patient
        self._staff = staff
        self._start_hour = whole_hour
        self._appointment_id = appointment_id
        self._status = Appointment.PENDING
        self._cancellation_reason = None
        self._cancellation_policy = (
            CancellationPolicy()
            if cancellation_policy is None
            else cancellation_policy
        )

    @property
    def appointment_id(self):
        return self._appointment_id

    @property
    def patient(self):
        return self._patient

    @property
    def staff(self):
        return self._staff

    @property
    def start_hour(self):
        return self._start_hour

    @property
    def duration_hours(self):
        return Appointment.DURATION_HOURS

    @property
    def status(self):
        return self._status

    @property
    def cancellation_reason(self):
        return self._cancellation_reason

    def confirm(self):
        # Use this method for status changes so cancelled appointments stay final.
        if self._status == Appointment.CANCELLED:
            raise ValueError("Cancelled appointments cannot be restored")
        if self._status == Appointment.CONFIRMED:
            raise ValueError("Appointment is already confirmed")

        self._status = Appointment.CONFIRMED

    def cancel(self, current_hour, reason="normal"):
        if self._status == Appointment.CANCELLED:
            raise ValueError("Appointment is already cancelled")

        # The policy checks the time limit before changing the appointment.
        self._cancellation_policy.validate(
            self._status, current_hour, self._start_hour
        )

        self._status = Appointment.CANCELLED
        self._cancellation_reason = reason
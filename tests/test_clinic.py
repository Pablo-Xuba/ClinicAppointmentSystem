import io
import unittest

from models.appointment import Appointment
from models.doctor import Doctor
from models.medical_lecturer import MedicalLecturer
from models.nurse import Nurse
from models.patient import Patient
from models.person import Person
from models.pharmacist import Pharmacist
from services.appointment_log import AppointmentLog
from services.booking_service import Clinic
from services.clock import Clock


class ClinicTests(unittest.TestCase):
    def setUp(self):
        self.output = io.StringIO()
        self.log = AppointmentLog(output=self.output)
        self.clock = Clock(current_hour=10)
        self.clinic = Clinic(clock=self.clock, appointment_log=self.log)
        self.patient = Patient("Jordan", 1)
        self.other_patient = Patient("Taylor", 2)
        self.emergency_patient = Patient("Casey", 3)
        self.emergency_patient.flag_emergency()
        self.doctor = Doctor("Dr Smith", 10)
        self.nurse = Nurse("Sarah", 11)
        self.pharmacist = Pharmacist("John", 12)

    def test_empty_or_non_string_names_are_rejected(self):
        for name in ("", "   ", None):
            with self.subTest(name=name), self.assertRaises(ValueError):
                Patient(name, 1)

    def test_non_positive_or_non_integer_ids_are_rejected(self):
        for person_id in (0, -1, 1.5, True):
            with self.subTest(person_id=person_id), self.assertRaises(ValueError):
                Patient("Jordan", person_id)

    def test_valid_patient_can_be_registered(self):
        self.assertIs(self.clinic.add_patient(self.patient), self.patient)
        self.assertEqual(self.clinic.patients, (self.patient,))

    def test_valid_staff_can_be_registered(self):
        self.assertIs(self.clinic.add_staff(self.doctor), self.doctor)
        self.assertEqual(self.clinic.staff_members, (self.doctor,))

    def test_staff_fees_match_assignment_formulas(self):
        self.assertEqual(self.doctor.fee(), 60)
        self.assertEqual(self.nurse.fee(), 11)
        self.assertEqual(self.pharmacist.fee(), 5)

    def test_new_appointment_is_pending(self):
        self.clinic.add_patient(self.patient)
        self.clinic.add_staff(self.doctor)
        appointment = self.clinic.book_appointment(self.patient, self.doctor, 12)
        self.assertEqual(appointment.status, Appointment.PENDING)
        self.assertEqual(appointment.start_hour, 12)
        self.assertEqual(appointment.duration_hours, 1)

    def test_appointment_rejects_invalid_patient_or_staff_objects(self):
        with self.assertRaisesRegex(ValueError, "requires a Patient and a Staff"):
            Appointment(object(), self.doctor, 12)
        with self.assertRaisesRegex(ValueError, "requires a Patient and a Staff"):
            Appointment(self.patient, object(), 12)

    def test_pending_appointment_can_be_confirmed(self):
        appointment = Appointment(self.patient, self.doctor, 12)
        appointment.confirm()
        self.assertEqual(appointment.status, Appointment.CONFIRMED)

    def test_cancelled_appointment_cannot_be_restored(self):
        appointment = Appointment(self.patient, self.doctor, 12)
        appointment.cancel(current_hour=10)
        with self.assertRaisesRegex(ValueError, "cannot be restored"):
            appointment.confirm()

    def test_confirmed_appointment_cannot_be_cancelled_with_less_than_two_hours(self):
        appointment = Appointment(self.patient, self.doctor, 12)
        appointment.confirm()
        with self.assertRaisesRegex(ValueError, "too late"):
            appointment.cancel(current_hour=11)

    def test_confirmed_appointment_can_be_cancelled_with_two_hours_notice(self):
        appointment = Appointment(self.patient, self.doctor, 12)
        appointment.confirm()
        appointment.cancel(current_hour=10)
        self.assertEqual(appointment.status, Appointment.CANCELLED)

    def test_appointment_cannot_be_cancelled_after_it_starts(self):
        appointment = Appointment(self.patient, self.doctor, 12)
        with self.assertRaisesRegex(ValueError, "has started"):
            appointment.cancel(current_hour=12)

    def test_patient_cannot_book_two_active_appointments_at_same_hour(self):
        self.clinic.add_patient(self.patient)
        self.clinic.add_staff(self.doctor)
        self.clinic.add_staff(self.nurse)
        self.clinic.book_appointment(self.patient, self.doctor, 12)
        with self.assertRaisesRegex(ValueError, "already has an appointment"):
            self.clinic.book_appointment(self.patient, self.nurse, 12)

    def test_staff_cannot_have_two_active_appointments_at_same_hour(self):
        self.clinic.add_patient(self.patient)
        self.clinic.add_patient(self.other_patient)
        self.clinic.add_staff(self.doctor)
        self.clinic.book_appointment(self.patient, self.doctor, 12)
        with self.assertRaisesRegex(ValueError, "already has an appointment"):
            self.clinic.book_appointment(self.other_patient, self.doctor, 12)

    def test_ids_are_unique_across_patients_and_staff(self):
        self.clinic.add_patient(self.patient)
        duplicate = Doctor("Duplicate", self.patient.person_id)
        with self.assertRaisesRegex(ValueError, "already in use"):
            self.clinic.add_staff(duplicate)

    def test_normal_patient_cannot_bump_an_existing_appointment(self):
        self.clinic.add_patient(self.patient)
        self.clinic.add_patient(self.other_patient)
        self.clinic.add_staff(self.doctor)
        first = self.clinic.book_appointment(self.patient, self.doctor, 12)
        with self.assertRaisesRegex(ValueError, "already has an appointment"):
            self.clinic.book_appointment(self.other_patient, self.doctor, 12)
        self.assertEqual(first.status, Appointment.PENDING)

    def test_emergency_booking_bumps_pending_appointment(self):
        self.clinic.add_patient(self.patient)
        self.clinic.add_patient(self.emergency_patient)
        self.clinic.add_staff(self.doctor)
        original = self.clinic.book_appointment(self.patient, self.doctor, 12)
        emergency = self.clinic.book_appointment(
            self.emergency_patient, self.doctor, 12
        )
        self.assertEqual(original.status, Appointment.CANCELLED)
        self.assertEqual(original.cancellation_reason, "bumped")
        self.assertEqual(emergency.status, Appointment.PENDING)

    def test_emergency_booking_bumps_all_pending_conflicts(self):
        self.clinic.add_patient(self.patient)
        self.clinic.add_patient(self.emergency_patient)
        self.clinic.add_staff(self.doctor)
        self.clinic.add_staff(self.nurse)
        staff_conflict = self.clinic.book_appointment(
            self.patient, self.doctor, 12
        )
        patient_conflict = self.clinic.book_appointment(
            self.emergency_patient, self.nurse, 12
        )

        emergency = self.clinic.book_appointment(
            self.emergency_patient, self.doctor, 12
        )

        for appointment in (staff_conflict, patient_conflict):
            self.assertEqual(appointment.status, Appointment.CANCELLED)
            self.assertEqual(appointment.cancellation_reason, "bumped")
        self.assertEqual(emergency.status, Appointment.PENDING)

    def test_emergency_booking_cannot_bump_confirmed_appointment(self):
        self.clinic.add_patient(self.patient)
        self.clinic.add_patient(self.other_patient)
        self.clinic.add_patient(self.emergency_patient)
        self.clinic.add_staff(self.doctor)
        confirmed = self.clinic.book_appointment(self.patient, self.doctor, 12)
        self.clinic.confirm_appointment(confirmed.appointment_id)
        with self.assertRaisesRegex(ValueError, "cannot bump a confirmed"):
            self.clinic.book_appointment(
                self.emergency_patient, self.doctor, 12
            )
        self.assertEqual(confirmed.status, Appointment.CONFIRMED)
        self.assertEqual(len(self.clinic.appointments), 1)

    def test_emergency_rejection_does_not_partially_bump_other_pending_appointments(self):
        self.clinic.add_patient(self.patient)
        self.clinic.add_patient(self.other_patient)
        self.clinic.add_patient(self.emergency_patient)
        self.clinic.add_staff(self.doctor)
        self.clinic.add_staff(self.nurse)
        pending_staff_conflict = self.clinic.book_appointment(
            self.patient, self.doctor, 12
        )
        confirmed_patient_conflict = self.clinic.book_appointment(
            self.emergency_patient, self.nurse, 12
        )
        self.clinic.confirm_appointment(confirmed_patient_conflict.appointment_id)

        with self.assertRaisesRegex(ValueError, "cannot bump a confirmed"):
            self.clinic.book_appointment(
                self.emergency_patient, self.doctor, 12
            )

        self.assertEqual(pending_staff_conflict.status, Appointment.PENDING)
        self.assertEqual(confirmed_patient_conflict.status, Appointment.CONFIRMED)

    def test_log_closes_and_records_failure_after_failed_operation(self):
        self.clinic.add_patient(self.patient)
        self.clinic.add_staff(self.doctor)
        appointment = self.clinic.book_appointment(self.patient, self.doctor, 11)
        self.clinic.confirm_appointment(appointment.appointment_id)
        with self.assertRaises(ValueError):
            self.clinic.cancel_appointment(appointment.appointment_id)

        entries = self.clinic.log_entries
        self.assertEqual(entries.count("[log] opened"), entries.count("[log] closed"))
        self.assertTrue(any(entry.startswith("FAILED cancel #1:") for entry in entries))

    def test_medical_lecturer_calls_person_constructor_once(self):
        before = Person.constructor_count()
        medical_lecturer = MedicalLecturer("Dr Morgan", 30, "Anatomy")
        after = Person.constructor_count()
        self.assertEqual(after - before, 1)
        self.assertEqual(medical_lecturer.role(), "Doctor and Lecturer")
        self.assertEqual(medical_lecturer.fee(), self.doctor.fee())

    def test_clock_is_controlled_by_its_test_input_not_system_time(self):
        clock = Clock(current_hour=7)
        self.assertEqual(clock.now(), 7)
        clock.advance(2)
        self.assertEqual(clock.now(), 9)

    def test_clock_rejects_out_of_range_fractional_and_boolean_hours(self):
        for invalid_hour in (-1, 169, 1.5, True, "not an hour"):
            with self.subTest(hour=invalid_hour), self.assertRaises(ValueError):
                Clock(current_hour=invalid_hour)

    def test_clinic_collection_properties_do_not_expose_internal_lists(self):
        self.clinic.add_patient(self.patient)
        self.assertIsInstance(self.clinic.patients, tuple)
        with self.assertRaises(AttributeError):
            self.clinic.patients.append(self.other_patient)


if __name__ == "__main__":
    unittest.main()

from models.appointment import Appointment
from models.doctor import Doctor
from models.medical_lecturer import MedicalLecturer
from models.nurse import Nurse
from models.patient import Patient
from models.person import Person
from models.pharmacist import Pharmacist
from services.booking_service import Clinic
from services.clock import Clock


def _find_person(people, person_id):
    for person in people:
        if person.person_id == person_id:
            return person
    raise LookupError(f"Person #{person_id} was not found")


def _read_integer(prompt, minimum=None, maximum=None):
    value = input(prompt).strip()
    try:
        number = int(value)
    except ValueError as error:
        raise ValueError("Please enter a whole number.") from error

    if minimum is not None and number < minimum:
        raise ValueError(f"Enter a number no smaller than {minimum}.")
    if maximum is not None and number > maximum:
        raise ValueError(f"Enter a number no larger than {maximum}.")
    return number


def _show_patients(clinic):
    print("\nRegistered Patients")
    print("ID   | NAME                 | TYPE")
    print("-" * 48)
    if not clinic.patients:
        print("No patients have been registered.")
        return
    for patient in clinic.patients:
        patient_type = "EMERGENCY" if patient.emergency else "Regular"
        print(f"{patient.person_id:<4} | {patient.name:<20} | {patient_type}")


def _show_staff(clinic):
    print("\nRegistered Staff")
    print("ID   | NAME                 | ROLE                 | FEE")
    print("-" * 66)
    if not clinic.staff_members:
        print("No staff members have been registered.")
        return
    for staff_member in clinic.staff_members:
        print(
            f"{staff_member.person_id:<4} | "
            f"{staff_member.name:<20} | "
            f"{staff_member.role():<20} | {staff_member.fee()}"
        )


def _show_staff_fees(clinic):
    print("\nStaff Fees")
    print("ROLE                 | FEE")
    print("-" * 30)
    if not clinic.staff_members:
        print("No staff members have been registered.")
        return

    # One polymorphic loop works for every Staff subclass.
    for staff_member in clinic.staff_members:
        print(f"{staff_member.role():<20} | {staff_member.fee()}")


def _show_appointments(clinic):
    print("\nAppointments")
    print(
        "ID | PATIENT              | STAFF                | FEE | "
        "HOUR | STATUS    | REASON"
    )
    print("-" * 98)
    if not clinic.appointments:
        print("No appointments have been booked.")
        return
    for appointment in clinic.appointments:
        patient_name = appointment.patient.name
        if appointment.patient.emergency:
            patient_name += " (EMERGENCY)"
        reason = appointment.cancellation_reason or "-"
        print(
            f"{appointment.appointment_id:<2} | "
            f"{patient_name:<20} | "
            f"{appointment.staff.name:<20} | "
            f"{appointment.staff.fee():<3} | "
            f"{appointment.start_hour:<4} | "
            f"{appointment.status:<9} | {reason}"
        )


def _register_patient(clinic):
    name = input("Patient name: ").strip()
    person_id = _read_integer("Patient ID (positive whole number): ", minimum=1)
    patient = Patient(name, person_id)
    clinic.add_patient(patient)
    print(f"Registered patient {patient.name} (ID {patient.person_id}).")


def _register_staff(clinic):
    print("Staff type: 1. Doctor  2. Nurse  3. Pharmacist")
    choice = _read_integer("Choose staff type: ", minimum=1, maximum=3)
    name = input("Staff member name: ").strip()
    person_id = _read_integer("Staff ID (positive whole number): ", minimum=1)
    staff_classes = {1: Doctor, 2: Nurse, 3: Pharmacist}
    staff_member = staff_classes[choice](name, person_id)
    clinic.add_staff(staff_member)
    print(
        f"Registered {staff_member.role().lower()} "
        f"{staff_member.name} (ID {staff_member.person_id})."
    )


def _book_appointment(clinic):
    patient_id = _read_integer("Patient ID: ", minimum=1)
    staff_id = _read_integer("Staff ID: ", minimum=1)
    start_hour = _read_integer("Appointment start hour (0-168): ", minimum=0, maximum=168)
    patient = _find_person(clinic.patients, patient_id)
    staff_member = _find_person(clinic.staff_members, staff_id)
    appointment = clinic.book_appointment(patient, staff_member, start_hour)
    print(
        f"Booked appointment #{appointment.appointment_id} as "
        f"{appointment.status}."
    )


def _confirm_appointment(clinic):
    appointment_id = _read_integer("Appointment ID to confirm: ", minimum=1)
    appointment = clinic.confirm_appointment(appointment_id)
    print(f"Appointment #{appointment.appointment_id} confirmed.")


def _cancel_appointment(clinic):
    appointment_id = _read_integer("Appointment ID to cancel: ", minimum=1)
    reason = input("Cancellation reason (leave blank for normal): ").strip()
    appointment = clinic.cancel_appointment(
        appointment_id, reason=reason or "normal"
    )
    print(f"Appointment #{appointment.appointment_id} cancelled.")


def _flag_patient_emergency(clinic):
    patient_id = _read_integer("Patient ID to flag as emergency: ", minimum=1)
    patient = clinic.flag_patient_emergency(patient_id)
    print(f"{patient.name} is now marked as an emergency patient.")


def demonstrate_emergency_booking():
    print("\nEmergency Booking Demonstration")
    clock = Clock(current_hour=10)
    clinic = Clinic(clock=clock)
    routine_patient = Patient("Jordan", 9001)
    emergency_patient = Patient("Casey", 9002)
    confirmed_patient = Patient("Taylor", 9003)
    emergency_patient.flag_emergency()
    confirmed_patient.flag_emergency()
    doctor = Doctor("Dr Demo", 9101)
    nurse = Nurse("Nurse Demo", 9102)

    for patient in (routine_patient, emergency_patient, confirmed_patient):
        clinic.add_patient(patient)
    for staff_member in (doctor, nurse):
        clinic.add_staff(staff_member)

    routine_appointment = clinic.book_appointment(
        routine_patient, doctor, 12
    )
    replacement = clinic.book_appointment(emergency_patient, doctor, 12)
    print(
        f"Emergency patient bumped appointment "
        f"#{routine_appointment.appointment_id}; reason is "
        f"'{routine_appointment.cancellation_reason}'."
    )
    print(
        f"New emergency appointment #{replacement.appointment_id} "
        f"starts as {replacement.status}."
    )

    confirmed = clinic.book_appointment(confirmed_patient, nurse, 14)
    clinic.confirm_appointment(confirmed.appointment_id)
    try:
        clinic.book_appointment(emergency_patient, nurse, 14)
    except ValueError as error:
        print("Expected confirmed-appointment rejection:", error)

    try:
        clinic.book_appointment(routine_patient, doctor, 12)
    except ValueError as error:
        print("Expected ordinary-patient conflict:", error)


def demonstrate_multiple_inheritance():
    print("\nMultiple Inheritance Demonstration")
    before = Person.constructor_count()
    medical_lecturer = MedicalLecturer(
        "Dr Morgan", 9201, "Clinical Anatomy"
    )
    after = Person.constructor_count()
    print("Role:", medical_lecturer.role())
    print("Module:", medical_lecturer.module_name)
    print("Doctor fee:", medical_lecturer.fee())
    print("Person constructor calls:", after - before)
    print(
        "MRO:",
        " -> ".join(parent.__name__ for parent in MedicalLecturer.__mro__),
    )


def demonstrate_clock():
    print("\nClock Demonstration")
    clock = Clock(current_hour=10)
    print("Starting hour:", clock.now())
    clock.advance(3)
    print("After advancing three hours:", clock.now())


def run_system_demonstrations():
    print("\nClinic Appointment System Demonstration")
    clock = Clock(current_hour=10)
    clinic = Clinic(clock=clock)
    patients = [
        Patient("Alex", 9301),
        Patient("Sam", 9302),
        Patient("Riley", 9303),
    ]
    patients[1].flag_emergency()
    patients[2].flag_emergency()
    staff_members = [
        Doctor("Dr Smith", 9401),
        Nurse("Sarah", 9402),
        Pharmacist("John", 9403),
        MedicalLecturer("Dr Lee", 9404, "Anatomy"),
    ]

    print("\nRegistering sample patients and staff:")
    for patient in patients:
        clinic.add_patient(patient)
        emergency_label = " (EMERGENCY)" if patient.emergency else ""
        print(f"Patient: {patient.name}{emergency_label}")
    for staff_member in staff_members:
        clinic.add_staff(staff_member)
        print(f"Staff: {staff_member.name} ({staff_member.role()})")

    print("\nStaff fees (one polymorphic loop):")
    for staff_member in clinic.staff_members:
        print(f"{staff_member.role()}: {staff_member.fee()}")

    print("\nBooking and confirming an appointment:")
    confirmed = clinic.book_appointment(patients[0], staff_members[1], 11)
    clinic.confirm_appointment(confirmed.appointment_id)
    print(f"Appointment #{confirmed.appointment_id}: {confirmed.status}")

    print("\nCancelling a pending appointment:")
    pending = clinic.book_appointment(patients[0], staff_members[2], 14)
    clinic.cancel_appointment(pending.appointment_id, "patient request")

    print("\nDeliberate failed cancellation:")
    try:
        clinic.cancel_appointment(confirmed.appointment_id)
    except ValueError as error:
        print("Expected failure:", error)

    print("\nEmergency booking bumps a pending appointment:")
    bumped = clinic.book_appointment(patients[0], staff_members[0], 16)
    emergency_booking = clinic.book_appointment(patients[1], staff_members[0], 16)
    print(
        f"Appointment #{bumped.appointment_id} is {bumped.status}; "
        f"reason: {bumped.cancellation_reason}."
    )
    print(
        f"New emergency appointment #{emergency_booking.appointment_id}: "
        f"{emergency_booking.status}."
    )

    print("\nEmergency booking is rejected against a confirmed appointment:")
    protected = clinic.book_appointment(patients[2], staff_members[2], 18)
    clinic.confirm_appointment(protected.appointment_id)
    try:
        clinic.book_appointment(patients[1], staff_members[2], 18)
    except ValueError as error:
        print("Expected failure:", error)

    demonstrate_multiple_inheritance()
    demonstrate_clock()
    print("\nFinal sample appointment list:")
    _show_appointments(clinic)
    print("\nDemonstration complete. See the [log] lines above for action history.")


def _print_menu(clinic):
    print("\n" + "=" * 58)
    print(f"CLINIC APPOINTMENT SYSTEM  |  Current Clinic Hour: {clinic.current_hour} / 168")
    print("=" * 58)
    print("1.  Register Patient")
    print("2.  Register Staff Member")
    print("3.  View Patients")
    print("4.  View Staff Members")
    print("5.  View Staff Fees")
    print("6.  Book Appointment")
    print("7.  Confirm Appointment")
    print("8.  Cancel Appointment")
    print("9.  View All Appointments")
    print("10. Flag Patient as Emergency")
    print("11. Demonstrate Emergency Booking")
    print("12. Demonstrate Multiple Inheritance")
    print("13. Demonstrate Clock")
    print("14. View Appointment Log")
    print("15. Run System Demonstrations")
    print("16. Exit")
    print("=" * 58)


def main():
    clinic = Clinic(clock=Clock(current_hour=10))
    actions = {
        1: lambda: _register_patient(clinic),
        2: lambda: _register_staff(clinic),
        3: lambda: _show_patients(clinic),
        4: lambda: _show_staff(clinic),
        5: lambda: _show_staff_fees(clinic),
        6: lambda: _book_appointment(clinic),
        7: lambda: _confirm_appointment(clinic),
        8: lambda: _cancel_appointment(clinic),
        9: lambda: _show_appointments(clinic),
        10: lambda: _flag_patient_emergency(clinic),
        11: demonstrate_emergency_booking,
        12: demonstrate_multiple_inheritance,
        13: demonstrate_clock,
        14: lambda: _show_log(clinic),
        15: run_system_demonstrations,
    }

    print("Welcome to the Clinic Appointment System.")
    while True:
        _print_menu(clinic)
        try:
            choice = _read_integer("Select an option: ", minimum=1, maximum=16)
            if choice == 16:
                print("Thank you. Goodbye.")
                return
            actions[choice]()
        except (ValueError, LookupError) as error:
            print(f"Could not complete that action: {error}")
        except EOFError:
            print("\nInput ended. Goodbye.")
            return


def _show_log(clinic):
    print("\nAppointment Log")
    if not clinic.log_entries:
        print("No clinic actions have been recorded.")
        return
    for entry in clinic.log_entries:
        print(entry)


if __name__ == "__main__":
    main()

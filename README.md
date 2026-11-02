# Clinic Appointment System

## Project description

A Python terminal application for registering clinic patients and staff,
booking and managing one-hour appointments, enforcing appointment rules, and
recording clinic actions in a readable log. It uses only the Python standard
library.

**Student registration number:** 2420089  
**Pair members:** Marlvin A. Munyanyi and Takudzwa Pablo Magawagawa  
**Language:** Python 3.14

The registration number gives `P mod 4 = 1`, so the assigned extension in
this submission is **emergency bookings**.

## Folder structure

```text
ClinicAppointmentSystem/
├── main.py
├── README.md
├── models/
│   ├── __init__.py
│   ├── person.py
│   ├── patient.py
│   ├── staff.py
│   ├── doctor.py
│   ├── nurse.py
│   ├── pharmacist.py
│   ├── appointment.py
│   ├── lecturer.py
│   └── medical_lecturer.py
├── policies/
│   ├── __init__.py
│   └── cancellation_policy.py
├── services/
│   ├── __init__.py
│   ├── clock.py
│   ├── appointment_log.py
│   └── booking_service.py
└── tests/
    └── test_clinic.py
```

## Run the application

Open a terminal in the project directory and run:

```powershell
python main.py
```

The menu starts with a clinic hour of 10. Choose a numbered action, follow its
prompts, and use option 16 to exit. Option 15 runs the predictable sample
demonstration without changing the clinic used by the menu.

## Run the tests

```powershell
python -m unittest discover -s tests -v
```

The test suite checks validation, fees, appointment transitions, conflicting
bookings, emergency bumping, logging, multiple inheritance, and the testable
clock.

## Important classes

- `Person` ([models/person.py](./models/person.py)) is an abstract base class
  for people in the clinic. It validates names and positive integer IDs and
  declares the abstract `role()` method. Its constructor counter helps
  demonstrate the multiple-inheritance requirement.
- `Patient` ([models/patient.py](./models/patient.py)) adds the emergency
  flag. The clinic can flag a registered patient through its logged
  `flag_patient_emergency()` operation.
- `Staff` ([models/staff.py](./models/staff.py)) is an abstract person with an
  abstract `fee()` method. `Doctor`, `Nurse`, and `Pharmacist` each provide
  their own fee and role.
- `Lecturer` ([models/lecturer.py](./models/lecturer.py)) adds a module name.
  `MedicalLecturer` ([models/medical_lecturer.py](./models/medical_lecturer.py))
  inherits from both `Doctor` and `Lecturer`.
- `Appointment` ([models/appointment.py](./models/appointment.py)) stores its
  patient, staff member, start hour, status, and cancellation reason. Its
  duration is one hour.
- `Clinic` ([services/booking_service.py](./services/booking_service.py))
  owns the registered people and appointments. It checks IDs and booking
  conflicts, coordinates emergency bookings, and logs its operations. Its
  collection properties return tuples rather than the internal lists.
- `CancellationPolicy`
  ([policies/cancellation_policy.py](./policies/cancellation_policy.py))
  applies the cancellation-time rules.
- `Clock` ([services/clock.py](./services/clock.py)) provides a controllable
  current clinic hour; the program never reads the computer's clock.
- `AppointmentLog` ([services/appointment_log.py](./services/appointment_log.py))
  is a context manager that records successful and failed operations.

## Object-oriented design

- **Encapsulation:** object fields are kept in underscore-prefixed attributes.
  Read-only properties provide the information callers need. Clinic
  collections and log entries are returned as tuples, which do not let callers
  add or remove items from the clinic's internal lists.
- **Abstraction:** `Person` and `Staff` are abstract classes. A concrete
  patient or staff member must implement its role, and each concrete staff
  class must provide its fee.
- **Inheritance:** patients and staff are people; doctors, nurses, and
  pharmacists are staff. A medical lecturer is both a doctor and a lecturer.
- **Polymorphism:** the fee display uses one loop over the clinic's staff
  collection and calls `role()` and `fee()` on each object. It does not need
  type checks or separate loops for each staff kind.

For `P = 2420089`, the expected fees are:

| Staff role | Fee calculation | Fee |
|---|---:|---:|
| Doctor | `40 + 5 * (P % 5)` | 60 |
| Nurse | `10 + (P % 3)` | 11 |
| Pharmacist | `5` | 5 |

## Time, appointments, and booking rules

The clinic hour is a whole number from 0 to 168. An appointment has a start
hour in that range and lasts exactly one hour. `Clock.now()` is the only
source of the current clinic hour. Advance it through `Clinic.advance_time()`;
no operating-system or computer date/time is consulted.

New appointments start as `PENDING`. The legal transitions are:

```text
PENDING   -> CONFIRMED
PENDING   -> CANCELLED
CONFIRMED -> CANCELLED
```

`CANCELLED` is terminal: a cancelled appointment cannot be confirmed or
restored. A pending appointment can be cancelled before it starts. A confirmed
appointment can be cancelled only with at least two hours' notice. No
appointment can be cancelled at or after its start hour. Illegal transitions
raise an exception with an explanatory message.

The clinic prevents a patient or staff member from having two non-cancelled
appointments at the same hour. Cancelled appointments no longer count as
conflicts. Person IDs are unique across the clinic's patient and staff lists.
Registration rejects empty names, non-integer or non-positive IDs, and
duplicate IDs.

## Emergency-booking twist

An emergency patient is clearly marked in patient and appointment displays.
When an emergency booking conflicts with one or more `PENDING` appointments,
the clinic first checks all conflicts. If none are confirmed and the slots
have not started, it cancels each conflicting pending appointment with the
exact reason `"bumped"` and creates a new `PENDING` emergency appointment.

If any conflicting appointment is `CONFIRMED`, the emergency booking is
rejected and no pending appointment is cancelled as a side effect. A normal
patient cannot bump any appointment. Successful bookings, bumps, and
rejections are all logged.

## Logging and context managers

Each clinic operation uses the `AppointmentLog` context manager. Entering an
operation prints and records `[log] opened`. It records the successful action,
or a `FAILED ...` entry if the operation raises an exception. Exiting always
attempts to print and record `[log] closed`, then the original operation error
is re-raised. The menu catches ordinary validation and lookup errors so the
user can continue.

If the output stream fails while writing a log entry, that entry is not added
to the in-memory history and the write error propagates. The context manager
still attempts the closing line. If writing or closing fails, no program can
guarantee that the failed output reached its destination; this implementation
does not claim that it did. A logging failure is surfaced to the caller rather
than silently hidden.

## Multiple inheritance and MRO

`MedicalLecturer` inherits from `Doctor` and `Lecturer`. Both inheritance
paths lead to the same `Person` base class. The classes use cooperative
`super()` calls: Python follows the method resolution order (MRO), a
consistent list of classes, and passes initialization along that list. This
means the shared `Person` constructor runs exactly once. Option 12 prints the
constructor count and MRO; the tests check the count as well.

`MedicalLecturer.fee()` uses the inherited doctor fee. A lecturer module does
not add a different clinical fee. In Java, a class cannot extend both
`Doctor` and `Lecturer`; `Lecturer` would instead be modeled as an interface,
and the medical lecturer would extend `Doctor` while implementing
`Lecturer`.

## Five-minute demonstration

From the menu, select option 15. It uses fixed sample people and clinic hours,
and demonstrates:

1. Registering patients and staff, including emergency patients.
2. Printing all staff roles and fees in one polymorphic loop.
3. Booking and confirming an appointment.
4. Cancelling an appointment.
5. A deliberate failed cancellation and its failure log.
6. An emergency booking that bumps a pending appointment.
7. Rejection of an emergency booking that conflicts with a confirmed
   appointment.
8. The `MedicalLecturer` role, fee, MRO, and one-time `Person` initialization.
9. Advancing a controlled clock and reviewing the appointment list.

Every clinic action prints its log open/close lines and a success or failure
entry. Options 11, 12, and 13 run the emergency, multiple-inheritance, and
clock demonstrations individually.

## Design decision log

### D1. Where does the two-hour rule live?

It lives in the separate `CancellationPolicy`, called by `Appointment`.
Putting it only in `Clinic` could let callers bypass the rule by cancelling
an appointment directly. Putting it in `Staff` would incorrectly make a
clinic-wide rule depend on the kind of staff member. Keeping it in
`Appointment` itself would be simpler, but would mix appointment state
transitions with a rule that could later be changed or replaced. A small
policy object keeps the rule in one place and lets both direct appointment
changes and clinic operations use the same check.

### D2. Why is the Clock testable?

The clinic receives a `Clock` and asks it for `now()`. A test can set a known
hour and advance it without waiting. This makes boundary checks, such as
cancelling with exactly two hours' notice, repeatable. If the code read the
computer clock directly, those tests would depend on when they happened to
run and could not reliably set the clinic's current hour.

### D3. What changed when Pharmacist was added?

The `Pharmacist` class supplies its role and fee. The shared staff display
loop calls `role()` and `fee()`, so neither the loop nor `Clinic` needed a
pharmacist-specific change. This is the benefit of polymorphism.

### D4. What should MedicalLecturer.fee() return?

It returns the doctor fee because a medical lecturer is also a doctor, and
the lecturer role has no separate clinical fee. Cooperative `super()` calls
and Python's MRO route initialization through the shared `Person` base once.
Without that cooperative method chain, calling both parent initializers
directly could initialize the same person twice or overwrite shared values.

### D5. What if writing to or closing the log fails?

The error should be visible, not reported as a successful log. This
implementation appends an entry to history only after writing it succeeds.
It propagates write and close errors and attempts the close line in a
`finally` block. If the output device itself is unavailable, the program
cannot guarantee delivery of either the failed entry or closing line; that
limitation is made explicit rather than hidden.

### D6. Why can an emergency booking bump PENDING but not CONFIRMED?

A pending appointment has not yet been confirmed, so the assigned emergency
exception may replace it. A confirmed appointment is a commitment to the
patient and staff member. The emergency operation checks every conflict
before cancelling any pending appointment; if a confirmed appointment is
among them, the request is rejected without changing the pending bookings.

## Limitations

The application keeps its records in memory. They are reset when the program
exits; persistent storage was not required and no database was added. The
assigned emergency twist is implemented; waiting lists and patient discounts
are alternative twists and are not included.

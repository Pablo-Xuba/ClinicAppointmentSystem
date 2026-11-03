from abc import ABC, abstractmethod


class Person(ABC):
    _constructor_calls = 0

    def __init__(self, name, person_id):
        # Validate shared person data so every subclass follows the same rules
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Name cannot be empty")

        if not isinstance(person_id, int) or isinstance(person_id, bool):
            raise ValueError("ID must be a positive integer")
        if person_id <= 0:
            raise ValueError("ID must be a positive integer")

        self._name = name
        self._id = person_id
        # Keep the counter on Person so subclasses share one count
        Person._constructor_calls += 1

    @property
    def name(self):
        return self._name

    @property
    def person_id(self):
        return self._id

    @classmethod
    def constructor_count(cls):
        return Person._constructor_calls

    @abstractmethod
    def role(self):
        raise NotImplementedError("Subclasses must provide a role")

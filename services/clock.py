class Clock:

    def __init__(self, current_hour=0):
        if isinstance(current_hour, bool):
            raise ValueError("Clock hour must be a whole number from 0 to 168")
        try:
            whole_hour = int(current_hour)
        except (TypeError, ValueError, OverflowError) as error:
            raise ValueError(
                "Clock hour must be a whole number from 0 to 168"
            ) from error
        if not 0 <= whole_hour <= 168 or current_hour != whole_hour:
            raise ValueError("Clock hour must be a whole number from 0 to 168")
        self._current_hour = whole_hour

    def now(self):
        return self._current_hour

    def advance(self, hours):
        if isinstance(hours, bool):
            raise ValueError("Advance must be a non-negative whole number of hours")
        try:
            whole_hours = int(hours)
        except (TypeError, ValueError, OverflowError) as error:
            raise ValueError(
                "Advance must be a non-negative whole number of hours"
            ) from error
        if hours != whole_hours or whole_hours < 0:
            raise ValueError("Advance must be a non-negative whole number of hours")
        if self._current_hour + whole_hours > 168:
            raise ValueError("Clock cannot advance past hour 168")

        self._current_hour += whole_hours
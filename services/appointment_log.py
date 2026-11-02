from contextlib import contextmanager


class AppointmentLog:
    def __init__(self, output=None):
        self._output = output
        self._entries = []
        self._is_open = False

    @property
    def entries(self):
        return tuple(self._entries)

    @contextmanager
    def action(self, description):
        if self._is_open:
            raise RuntimeError("Appointment log operations cannot be nested")

        self._is_open = True
        try:
            self._record("[log] opened")
            try:
                yield self
            except Exception as error:
                self._record(f"FAILED {description}: {error}")
                raise
        finally:
            self._is_open = False
            self._record("[log] closed")

    def write(self, entry):
        if not self._is_open:
            raise RuntimeError("Appointment log is not open")
        self._record(entry)

    def _record(self, entry):
        if self._output is None:
            print(entry)
        else:
            print(entry, file=self._output)
        self._entries.append(entry)
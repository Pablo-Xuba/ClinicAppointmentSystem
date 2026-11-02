class CancellationPolicy:
    def validate(self, status, current_hour, start_hour):
        if current_hour >= start_hour:
            raise ValueError("Cannot cancel an appointment that has started")

        if status == "CONFIRMED" and start_hour - current_hour < 2:
            raise ValueError("too late: confirmed appointments need 2 hours' notice")
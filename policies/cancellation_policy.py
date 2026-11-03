class CancellationPolicy:
    def validate(self, status, current_hour, start_hour):
        # Any appointment is too late to cancel once its start hour arrives
        if current_hour >= start_hour:
            raise ValueError("Cannot cancel an appointment that has started")

        # Confirmed bookings need more notice than pending bookings
        if status == "CONFIRMED" and start_hour - current_hour < 2:
            raise ValueError("too late: confirmed appointments need 2 hours notice")
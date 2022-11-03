@staticmethod
def get_booking_status_type(completion_state):
    if completion_state == 0:
        return "Customer Confirmed for Survey Appointment"
    if completion_state == 1:
        return "Customer Survey is Partially Complete"
    if completion_state == 2:
        return "Customer Survey Completed"
    if completion_state == 3:
        return "Customer Cancelled Survey Appointment"


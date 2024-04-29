from schedule_data import ScheduleData

class Classroom:
    """Classroom class"""
    def __init__(self, capacity: int, classes_allowed: list):
        self.capacity = capacity
        self.classes_allowed = classes_allowed
        self.slot_reached_students = {} # dictionary of days and intervals with the number of students reached
        self.reached_capacity = False # True if the classroom reached its capacity
    
    def initialize_slot_reached_students(self, schedule_data: ScheduleData):
        """Initializes the slot_reached_students dictionary"""
        for day in schedule_data.days:
            for interval in schedule_data.intervals:
                self.slot_reached_students[day] = {interval: 0}
    
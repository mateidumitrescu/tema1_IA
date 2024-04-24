class ScheduleData:
    """ScheduleData class"""
    def __init__(self, professors: dict, classrooms: dict, courses: dict, intervals: list, days: list):
        self.professors = professors
        self.classrooms = classrooms
        self.courses = courses
        self.intervals = intervals
        self.days = days
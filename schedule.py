import random
from schedule_data import ScheduleData

class Schedule:
    """Schedule class"""
    def __init__(self, schedule_data: ScheduleData):
        """Constructor for Schedule class"""
        
        # actual data of the schedule
        self.schedule_data = schedule_data
        # dictionary of courses and number of students left to assign
        self.students_left = schedule_data.courses
        # dictionary of violated constraints
        self.violated_constraints = {prof: [] for prof in schedule_data.professors}
        # dictionary of days and intervals
        self.days = {}
        # initializing the days of the week
        self.initialize_days()
        
    def add_violated_constraint(self, professor: str, day: str, interval: tuple):
        """Adds a violated constraint to the dictionary"""
        self.violated_constraints[professor].append((day, interval))
    
    def initialize_days(self):
        """Initializes the days of the schedule"""
        for day in self.schedule_data.days:
            for interval in self.schedule_data.intervals:
                i = {}
                i[interval] = {}
            self.days[day] = i
        
        # initializing the intervals of the schedule and classrooms
        for day in self.days:
            for interval in self.schedule_data.intervals:
                if interval not in self.days[day]:
                    self.days[day][interval] = {}
                for classroom in self.schedule_data.classrooms:
                    if classroom not in self.days[day][interval]:
                        self.days[day][interval][classroom] = None

    def create_initial_state(self):
        """Creates the initial state of the schedule randomly"""
        for course in self.students_left:
            # assigning students to courses
            print("Trying to assign students to course: ", course)
            while self.students_left[course] > 0:
                self.try_assign_course(course)
            print("Assigned all students to course: ", course)
        # after assigning all courses and students, schedule must contain None values for the rest of the slots
        
        
        # sorting the days and intervals
        for day in self.days:
            self.days[day] = dict(sorted(self.days[day].items()))
                
    
    def try_assign_course(self, course: str):
        """Assigns a course to a classroom and interval"""
        assigned = False
        max_attempts = 1000 # maximum number of attempts to assign a course
        attempt = 0
        while attempt < max_attempts and not assigned:
            day = random.choice(self.schedule_data.days)
            interval = random.choice(self.schedule_data.intervals)
            classroom = random.choice(list(self.schedule_data.classrooms.items()))
            
            # getting only the professors that can teach the course
            available_professors = [professor for professor in self.schedule_data.professors\
                    if course in self.schedule_data.professors[professor].courses\
                    and not self.schedule_data.professors[professor].already_assigned
                    and self.schedule_data.professors[professor].nr_teaching_intervals < 7]
            
            professor = random.choice(available_professors)
            
            # checking if the course can be assigned to the classroom
            if self.can_assign_course(course, day, interval, classroom):
                # assigning the course to the classroom and professor
                self.assign_course(course, day, interval, classroom, professor)
                assigned = True
                print("Assigned course: ", course, " to classroom: ", classroom[0], " on day: ", day, " at interval: ", interval, " with professor: ", professor)
            
            attempt += 1
        print("Attempted to assign course: ", course, " ", attempt, " times")
    
    def can_assign_course(self, course: str, day: str, interval: tuple, classroom: tuple):
        """Checks if a course and professor can be assigned to a classroom"""
        # checking if the classroom is allowed to have the course
        if course not in classroom[1].classes_allowed:
            return False
        # no need to check if the professor can teach the course, it is already done in the assign_course method
        
        # checking if the classroom is full already
        if day in classroom[1].slot_reached_students:
            if interval in classroom[1].slot_reached_students[day]:
                if classroom[1].slot_reached_students[day][interval] == classroom[1].capacity:
                    return False
        
        # checking if classroom is already assigned in this slot
        if self.days[day][interval][classroom[0]] is not None:
            print("Classroom already assigned in this slot: ", day, " ", interval, " ", classroom[0])
            return False
        
        # all hard constraints checked, returning True
        return True
        
    def assign_course(self, course: str, day: str, interval: tuple, classroom: tuple, professor: str):
        """Assigns a course to a classroom, day, interval and professor"""
        
        # assigin the course to the classroom
        if day in self.days and interval in self.days[day]:
            self.days[day][interval][classroom[0]] = (professor, course)
        elif day in self.days:
            self.days[day][interval] = {classroom[0]: (professor, course)}
        else:
            self.days[day] = {interval: {classroom[0]: (professor, course)}}
        
        # updating the professor data and increasing number of teaching intervals
        self.schedule_data.professors[professor].nr_teaching_intervals += 1
        
        # updating the number of students left to assign to the course and the number of students reached in the classroom
        if self.students_left[course] > self.schedule_data.classrooms[classroom[0]].capacity:
            self.students_left[course] -= self.schedule_data.classrooms[classroom[0]].capacity
            self.schedule_data.classrooms[classroom[0]].slot_reached_students[day][interval] = self.schedule_data.classrooms[classroom[0]].capacity
        else:
            self.schedule_data.classrooms[classroom[0]].slot_reached_students[day][interval] = self.students_left[course]
            self.students_left[course] = 0
        
    
    def successors(self):
        """Generates the successors of the current state"""
        
        pass

    def astar_heuristic():
        """Heuristic function for A* algorithm"""
        pass

import sys
from utils import read_yaml_file, pretty_print_timetable
import random

class Professor:
    """Professor class"""
    def __init__(self, preferences: list, courses: list):
        self.preferences = preferences
        self.courses = courses
        self.nr_teaching_intervals = 0 # used to check if a professor reached 7 intervals per week
        self.already_assigned = False # switching to True when a professor is assigned to 7 intervals

class ScheduleData:
    """ScheduleData class"""
    def __init__(self, professors: dict, classrooms: dict, courses: dict, intervals: list, days: list):
        self.professors = professors
        self.classrooms = classrooms
        self.courses = courses
        self.intervals = intervals
        self.days = days

class Classroom:
    """Classroom class"""
    def __init__(self, capacity: int, classes_allowed: list):
        self.capacity = capacity
        self.classes_allowed = classes_allowed
        self.slot_reached_students = {} # dictionary of days and intervals with the number of students reached
    
    def initialize_slot_reached_students(self, schedule_data: ScheduleData):
        """Initializes the slot_reached_students dictionary"""
        for day in schedule_data.days:
            for interval in schedule_data.intervals:
                self.slot_reached_students[day] = {interval: 0}
        
class Schedule:
    """Schedule class"""
    def __init__(self, schedule_data: ScheduleData):
        """Constructor for Schedule class"""
        
        # actual data of the schedule
        self.schedule_data = schedule_data
        # dictionary of courses and number of students left to assign
        self.students_left = schedule_data.courses
        # dictionary of days and intervals
        self.days = {}
        # initializing the days of the week
        self.initialize_days()
        
    
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

def cost(schedule: Schedule):
    """Calculates the cost of the current state based on soft constraints"""
    cost = 0
    
    return cost
        
def hill_climbing(initial_state: Schedule, max_iters = 1000):
    """Hill climbing algorithm used in random restart hill climbing algorithm"""
    iters = 0
    current_state = initial_state
    current_state_cost = float('inf')
    while iters < max_iters:
        successors = current_state.successors()
        best_state = current_state
        for successor in successors:
            if cost(successor) < cost(best_state):
                best_state = successor
        
        if best_state == current_state:
            iters += 1
            break
        current_state = best_state
        current_state_cost = cost(best_state)
        iters += 1
    
    return current_state, current_state_cost, iters # return the best state found, its cost and the number of iterations

def random_restart_hill_climbing(schedule_data: ScheduleData, max_restarts: int = 300, max_iterations: int = 1000):
    """Random restart hill climbing algorithm"""
    total_iters = 0
    best_state = None
    best_cost = float('inf')
    initial_state = Schedule(schedule_data)
    
    for _ in range(max_iterations):
        initial_state.create_initial_state() # creating a random initial state
        state, cost, iters = hill_climbing(initial_state, max_iterations) # running hill climbing algorithm
        total_iters += iters # storing the total number of iterations
        
        if cost < best_cost: # the best state found so far
            best_state = state
            best_cost = cost
            if cost == 0:
                break
    
    return best_state, best_cost, total_iters
    
    

def astar(schedule_data: ScheduleData):
    pass

def parse_input_file(input_file: str):
    """Parses the input file and returns a Schedule object"""
    data = read_yaml_file(input_file)
    
    intervals = [eval(interval) for interval in data['Intervale']]
    
    courses = {name: student_count for name, student_count in data['Materii'].items()}
    
    professors = {}
    for name, details in data['Profesori'].items():
        preferences = details['Constrangeri']
        prof_courses = details['Materii']
        professors[name] = Professor(preferences, prof_courses)
        
    
    
    classrooms = {}
    for classroom, details in data['Sali'].items():
        capacity = details['Capacitate']
        classes_allowed = details['Materii']
        classrooms[classroom] = Classroom(capacity, classes_allowed)
    
    days = data['Zile']
    schedule_data = ScheduleData(professors, classrooms, courses, intervals, days)
    
    for classroom in schedule_data.classrooms:
        schedule_data.classrooms[classroom].initialize_slot_reached_students(schedule_data)
    return schedule_data

if __name__ == '__main__':
    algo = sys.argv[1]
    input_file = sys.argv[2]

    # TODO parse input file
    schedule_data = parse_input_file(input_file)

    # check arguments
    if algo == 'astar':
        astar(schedule_data)
    elif algo == 'hc':
        schedule, cost, total_iters = random_restart_hill_climbing(schedule_data)
        pretty_print_timetable(schedule.days, input_file)
        print("Final cost: ", cost)
        print("Total iterations: ", total_iters)

    
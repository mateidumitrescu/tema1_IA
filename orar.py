import sys
from utils import read_yaml_file

class Professor:
    """Professor class"""
    def __init__(self, preferences: list, courses: list):
        self.preferences = preferences
        self.courses = courses

class Classroom:
    """Classroom class"""
    def __init__(self, capacity: int, classes_allowed: list):
        self.capacity = capacity
        self.classes_allowed = classes_allowed

class Course:
    """Course class"""
    def __init__(self, student_count: int):
        self.student_count = student_count
        
class Schedule:
    """Schedule class"""
    def __init__(self, professors: list, classrooms: list, courses: list, intervals: list, days: list):
        self.professors = professors
        self.classrooms = classrooms
        self.courses = courses
        self.intervals = intervals
        self.days = days
    
    def is_valid(self):
        """Checks if the schedule is valid"""
        
        pass
    
    def successors(self):
        """Generates the successors of the current state"""
        pass

    def astar_heuristic():
        """Heuristic function for A* algorithm"""
        pass

def hill_climbing_algorithm():
    pass

def astar_algorithm():
    pass

def parse_input_file(input_file: str):
    data = read_yaml_file(input_file)
    
    intervals = [interval for interval in data['Intervale']]
    print(intervals, end='\n\n')
    
    courses = {name: Course(student_count) for name, student_count in data['Materii'].items()}
    for c in courses:
        print(c, courses[c].student_count, end='\n\n')
    
    professors = {}
    for name, details in data['Profesori'].items():
        preferences = details['Constrangeri']
        prof_courses = details['Materii']
        professors[name] = Professor(preferences, prof_courses)
        print(name, professors[name].preferences, professors[name].courses)
    
    print()
    
    
    classrooms = {}
    for classroom, details in data['Sali'].items():
        capacity = details['Capacitate']
        classes_allowed = details['Materii']
        classrooms[classroom] = Classroom(capacity, classes_allowed)
        print(classroom, classrooms[classroom].capacity, classrooms[classroom].classes_allowed)
    
    days = data['Zile']
    print(days)
    
    

if __name__ == '__main__':
    algo = sys.argv[1]
    input_file = sys.argv[2]

    # TODO parse input file
    data = parse_input_file(input_file)

    # check arguments
    if algo == 'astar':
        astar_algorithm()
    elif algo == 'hc':
        hill_climbing_algorithm()

    
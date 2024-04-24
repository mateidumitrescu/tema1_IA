import sys
from utils import read_yaml_file, pretty_print_timetable
from schedule import Schedule
from schedule_data import ScheduleData
from professor import Professor
from classroom import Classroom        

def calculate_cost(schedule: Schedule):
    """Calculates the cost of the current state based on soft constraints"""
    cost = 0
    for day in schedule.days:
        for interval, classroom in schedule.days[day].items():
            interval = str(interval[0]) + "-" + str(interval[1]) # converting tuple to string
            for value in classroom.values():
                if value is not None:
                    professor = value[0]
                    # checking if the professor has any constraints
                    if day not in schedule.schedule_data.professors[professor].preferences:
                        print("Professor ", professor, " doesn't want to work on day ", day)
                        schedule.add_violated_constraint(professor, day, None)
                        cost += 1
                    if interval not in schedule.schedule_data.professors[professor].preferences:
                        print("Professor ", professor, " doesn't want to work in interval ", interval)
                        schedule.add_violated_constraint(professor, None, interval)
                        cost += 1
    print("Violated constraints: ", schedule.violated_constraints)               
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
            if calculate_cost(successor) < calculate_cost(best_state):
                best_state = successor
        
        if best_state == current_state:
            iters += 1
            break
        current_state = best_state
        current_state_cost = calculate_cost(best_state)
        iters += 1
    
    return current_state, current_state_cost, iters # return the best state found, its cost and the number of iterations

def random_restart_hill_climbing(
    input_file: str,
    schedule_data: ScheduleData,
    max_restarts: int = 300,
    max_iterations: int = 1000):

    """Random restart hill climbing algorithm"""
    total_iters = 0
    best_state = None
    best_cost = float('inf')
    initial_state = Schedule(schedule_data)
    
    for _ in range(max_iterations):
        initial_state.create_initial_state() # creating a random initial state
        print(pretty_print_timetable(initial_state.days, input_file))
        print("Initial cost: ", calculate_cost(initial_state))
        break
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
        professors[name].parse_preferences()
    
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
        schedule, cost, total_iters = random_restart_hill_climbing(input_file=input_file, schedule_data=schedule_data)
        # pretty_print_timetable(schedule.days, input_file)
        print("Final cost: ", cost)
        print("Total iterations: ", total_iters)

    
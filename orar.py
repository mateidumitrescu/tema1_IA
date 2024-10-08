import sys
from utils import read_yaml_file, pretty_print_timetable
from schedule import Schedule
from schedule_data import ScheduleData
from professor import Professor
from classroom import Classroom        
from hc import HillClimbing
from astar import AStar
from check_constraints import check_optional_constraints, check_mandatory_constraints
import os
import time
        

def parse_input_file(input_file: str):
    """Parses the input file and returns a Schedule object"""
    data = read_yaml_file(input_file)
    
    intervals = [eval(interval) for interval in data['Intervale']]
    
    courses = {name: student_count for name, student_count in data['Materii'].items()}
    
    professors = {}
    for name, details in data['Profesori'].items():
        preferences = details['Constrangeri']
        # keeping only preferences which dont contain !
        preferences = [pref for pref in preferences if pref[0] != '!' or 'Pauza' in pref]
        prof_courses = details['Materii']
        professors[name] = Professor(preferences, prof_courses)
        professors[name].parse_preferences()
        professors[name].preferences = [tuple(map(int, pref.split('-')))\
            if '-' in pref and not pref.startswith('!')\
                and 'Pauza' not in pref else pref for pref in professors[name].preferences]

        

    
    classrooms = {}
    for classroom, details in data['Sali'].items():
        capacity = details['Capacitate']
        classes_allowed = details['Materii']
        classrooms[classroom] = Classroom(capacity, classes_allowed)
    
    days = data['Zile']
    schedule_data = ScheduleData(professors, classrooms, courses, intervals, days, data)
    
    for classroom in schedule_data.classrooms:
        schedule_data.classrooms[classroom].initialize_slot_reached_students(schedule_data)
    return schedule_data

if __name__ == '__main__':
    algo = sys.argv[1]
    input_file = sys.argv[2]

    schedule_data = parse_input_file(input_file)
    
    if os.path.exists('output.txt'):
        os.remove('output.txt')
    

    # check arguments
    if algo == 'astar':
        initial_state = Schedule(schedule_data)
        initial_state.create_initial_state()
        start_time = time.time()
        result, best_cost = AStar.algorithm(initial_state, input_file)
        
        if len(result) > 0:
            best_cost = check_optional_constraints(result[-1].days, initial_state.specs)
            print(best_cost)
            with open('output.txt', 'w') as file:
                file.write(pretty_print_timetable(result[-1].days, input_file))
                file.write(f'\nCost: {best_cost}')
                file.write(f'\nExecution time: {time.time() - start_time}')
        else:
            with open('output.txt', 'w') as file:
                file.write("No solution found")
        
    elif algo == 'hc':
        start_time = time.time()
        HillClimbing.random_restart_hill_climbing(start_time, input_file=input_file, schedule_data=schedule_data)
        # pretty_print_timetable(schedule.days, input_file)
        

    
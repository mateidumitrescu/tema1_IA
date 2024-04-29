from schedule import Schedule
from schedule_data import ScheduleData
from check_constraints import check_optional_constraints, pretty_print_timetable
import sys

class HillClimbing:

    @staticmethod
    def calculate_cost(schedule: Schedule):
        """Calculates the cost of the current state based on soft constraints"""
        cost = 0
        for day in schedule.days:
            for interval, classroom in schedule.days[day].items():
                for value in classroom.values():
                    if value is not None:
                        professor = value[0]
                            # checking if the professor has any constraints
                        if day not in schedule.schedule_data.professors[professor].preferences:
                            #print("Professor ", professor, " doesn't want to work on day ", day)
                            schedule.add_violated_constraint(professor, day, None)
                            cost += 1
                        if interval not in schedule.schedule_data.professors[professor].preferences:
                            #print("Professor ", professor, " doesn't want to work in interval ", interval)
                            schedule.add_violated_constraint(professor, None, interval)
                            cost += 1
        #print("Violated constraints: ", schedule.violated_constraints)               
        return cost
    
    @staticmethod
    def hill_climbing(initial_state: Schedule, input_file: str, max_iters = 1000):
        """Hill climbing algorithm used in random restart hill climbing algorithm"""
        iters = 0
        current_state = initial_state
        current_state_cost = sys.maxsize
        while iters < max_iters:
            current_state_cost = HillClimbing.calculate_cost(current_state)
            successors = current_state.successors()
            best_state = current_state
            for successor in successors:
            
                successor_cost = HillClimbing.calculate_cost(successor)
                if successor_cost < current_state_cost:
                    best_state = successor


        
            if best_state == current_state:
                iters += 1
                break
        
            current_state = best_state
        
            iters += 1
    
        return current_state, current_state_cost, iters # return the best state found, its cost and the number of iterations
    
    
    @staticmethod
    def random_restart_hill_climbing(
    input_file: str,
    schedule_data: ScheduleData,
    max_restarts: int = 5000,
    max_iterations: int = 5000):

        """Random restart hill climbing algorithm"""
        total_iters = 0
        best_state = None
        best_cost = sys.maxsize
        initial_state = Schedule(schedule_data)
    
    
        for _ in range(max_restarts):

            initial_state.create_initial_state() # creating a random initial state
            
            state, cost, iters = HillClimbing.hill_climbing(initial_state, input_file, max_iterations) # running hill climbing algorithm
            total_iters += iters # storing the total number of iterations
        
            if cost <= best_cost: # the best state found so far
            
                best_state = state
                best_cost = cost
                print("CHANGED STATE!", "New cost: ", cost)
                print(pretty_print_timetable(best_state.days, input_file))
                print("Violated optional constraints: ", check_optional_constraints(best_state.days, schedule_data.specs))
                if cost == 0:
                    print("FOUND OPTIMAL SOLUTION!")
                    break
    
        print("Reached limit of iterations!")
        print("Final cost: ", best_cost)
        print("Total iterations: ", total_iters)
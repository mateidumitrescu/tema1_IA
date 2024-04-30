from heapq import heappush, heappop
from schedule import Schedule
from utils import pretty_print_timetable
from check_constraints import check_optional_constraints

class AStar:
    
    @staticmethod
    def algorithm(start: Schedule, input_file: str):
        frontier = []
        heappush(frontier, (start.heuristic(), start))
    
        discovered = {start.state_hash(): (None, 0, start.heuristic())}

        
        best_partial_solution = None
        best_partial_cost = float('inf')

        while frontier:
            current_cost, current = heappop(frontier)
            current_total_cost = current_cost + current.heuristic()
            print(pretty_print_timetable(current.days, input_file))

           
            if current_total_cost < best_partial_cost and current.is_valid():
                best_partial_solution = current
                best_partial_cost = current_total_cost

            if current.is_goal():
               
                best_partial_solution = current
                best_partial_cost = current_total_cost
                print("Goal found!")
                break  # Can stop if the goal state is found

            for neighbour in current.successors():
                print(check_optional_constraints(neighbour.days, neighbour.specs))
                neighbour_hash = neighbour.state_hash()
                new_cost = discovered[current.state_hash()][1] + current.transition_cost(neighbour)
                total_cost = new_cost + neighbour.heuristic()

                
                if neighbour.is_valid() and (neighbour_hash not in discovered or new_cost < discovered[neighbour_hash][1]):
                    discovered[neighbour_hash] = (current.state_hash(), new_cost, total_cost)
                    heappush(frontier, (total_cost, neighbour))

        path_to_best_partial = []
        if best_partial_solution:
            current = best_partial_solution
            while current:
                path_to_best_partial.append(current)
                parent_hash = discovered[current.state_hash()][0]
                current = parent_hash and current.get_state_by_hash(parent_hash)
            path_to_best_partial.reverse()  # Reverse path to start from initial state

        return path_to_best_partial, best_partial_cost  # Return the path and cost of the best partial solution
import random
from schedule_data import ScheduleData
import copy
from check_constraints import check_mandatory_constraints

class Schedule:
    """Schedule class"""
    def __init__(self, schedule_data: ScheduleData):
        """Constructor for Schedule class"""
        
        self.specs = schedule_data.specs # used for checking constraints
        
        # actual data of the schedule
        self.schedule_data = schedule_data
        # dictionary of courses and number of students left to assign
        self.students_left = None
        # dictionary of violated constraints
        self.violated_constraints = {prof: [] for prof in schedule_data.professors}
        # dictionary of days and intervals
        self.days = {}
        
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
    
    def initialize_all_data(self):
        """Initializes all the data of the schedule"""
        self.violated_constraints = {prof: [] for prof in self.schedule_data.professors}
        # initializing the days of the week
        self.initialize_days()
        self.students_left = {course: self.schedule_data.courses[course] for course in self.schedule_data.courses}
        for prof in self.schedule_data.professors:
            self.schedule_data.professors[prof].nr_teaching_intervals = 0
            self.schedule_data.professors[prof].already_assigned = False
        for classroom in self.schedule_data.classrooms:
            self.schedule_data.classrooms[classroom].initialize_slot_reached_students(self.schedule_data)

    def create_initial_state(self):
        """Creates the initial state of the schedule randomly"""
        
        self.initialize_all_data()
        
        
        for course in self.students_left:
            # assigning students to courses
            #print("Trying to assign students to course: ", course)
            attempts = 0
            assigned = False
            while self.students_left[course] > 0:
                # tryin
                assigned = self.try_assign_students(course)
                if not assigned:
                    self.try_assign_left_students(course)
                attempts += 1
                
            #print("Assigned all students to course: ", course)
            # after assigning all courses and students, schedule must contain None values for the rest of the slots
            
        
        # sorting the days and intervals
        for day in self.days:
            self.days[day] = dict(sorted(self.days[day].items()))
        
        if not self.is_valid():
            self.create_initial_state()
    
    def try_assign_left_students(self, course: str):
        """Assigns a course randomly to a classroom and interval"""
        available_professors = list(professor for professor in self.schedule_data.professors.keys()\
            if course in self.schedule_data.professors[professor].courses and\
            not self.schedule_data.professors[professor].already_assigned)
        
        if len(available_professors) == 0:
            self.create_initial_state()
            return
        
        random_professor = random.choice(available_professors)
        
        
        # first trying to assign the course to an empty slot
        for day in self.days:
                for interval in self.days[day]:
                    for classroom in self.days[day][interval]:
                        if self.days[day][interval][classroom] is None and course in self.schedule_data.classrooms[classroom].classes_allowed:
                            self.assign_course(course, day, interval, classroom, random_professor)
                            # print("Assigned randomly!!!!")
                            return True

        # if no empty slots are available, trying to assign the course to a slot not reaching the capacity
        for day in self.days:
            for interval in self.days[day]:
                for classroom in self.days[day][interval]:
                    if self.days[day][interval][classroom] is not None and\
                        self.schedule_data.classrooms[classroom].slot_reached_students[day][interval] < self.schedule_data.classrooms[classroom].capacity\
                        and course in self.schedule_data.classrooms[classroom].classes_allowed:
                        # assigning the rest of the students to the course not reaching the capacity
                        empty_spots = self.schedule_data.classrooms[classroom].capacity - self.schedule_data.classrooms[classroom].slot_reached_students[day][interval]
                        if empty_spots >= self.students_left[course]:
                            self.schedule_data.classrooms[classroom].slot_reached_students[day][interval] += self.students_left[course]
                            self.students_left[course] = 0
                            return True
                        else:
                            self.schedule_data.classrooms[classroom].slot_reached_students[day][interval] += empty_spots
                            self.students_left[course] -= empty_spots
                            return False
                        
                            
                        
    
    def try_assign_students(self, course: str):
        """Assigns a course to a classroom and interval"""
        assigned = False
        max_attempts = 1000 # maximum number of attempts to assign a course
        attempt = 0
        while attempt < max_attempts and not assigned:
            # getting only the professors that can teach the course
            available_professors = [professor for professor in self.schedule_data.professors
                    if course in self.schedule_data.professors[professor].courses
                    and not self.schedule_data.professors[professor].already_assigned]
            if len(available_professors) == 0:
                self.create_initial_state()
                return

            professor = random.choice(available_professors)
            day_preferences = [pref for pref in self.schedule_data.professors[professor].preferences if pref in self.schedule_data.days]
            interval_preferences = [pref for pref in self.schedule_data.professors[professor].preferences if pref in self.schedule_data.intervals]

            if len(day_preferences) == 0:
                days = random.choices(self.schedule_data.days)
            else:
                days = random.choices(day_preferences)
            if len(interval_preferences) == 0:
                intervals = random.choices(self.schedule_data.intervals)
            else:
                intervals = random.choices(interval_preferences)
            
            classrooms = [classroom for classroom in self.schedule_data.classrooms if course in self.schedule_data.classrooms[classroom].classes_allowed]
            
            classrooms = random.choices(classrooms)
            
            
            # checking if the course can be assigned to the classroom
            can_assign_course = False
            reason = None
            for day in days:
                for interval in intervals:
                    for classroom in classrooms:
                        can_assign_course, reason = self.can_assign_course(course, day, interval, classroom)
                        if can_assign_course and not self.already_teaching(professor, day, interval):
                            # assigning the course to the classroom and professor
                            self.assign_course(course, day, interval, classroom, professor)
                            assigned = True
                            #print("Assigned course: ", course, " to classroom: ", classroom, " on day: ", day, " at interval: ", interval, " with professor: ", professor)
                            break
                            
                    if assigned:
                        break
                if assigned:
                    break

            attempt += 1
        return assigned
    
    def already_teaching(self, professor: str, day: str, interval: tuple):
        """Checks if a professor is already teaching in a certain day and interval"""
        #print(professor, " is professor")
        for d in self.days:
            if d == day:
                for i in self.days[d]:
                    if str(i) == str(interval):
                        for data in self.days[d][i].values():
                            if data is not None and data[0] == professor:
                                return True
        return False
        
    def can_assign_course(self, course: str, day: str, interval: tuple, classroom: str):
        """Checks if a course and professor can be assigned to a classroom"""
        # checking if the classroom is full already
        if day in self.schedule_data.classrooms[classroom].slot_reached_students:
            if interval in self.schedule_data.classrooms[classroom].slot_reached_students[day]:
                if self.schedule_data.classrooms[classroom].slot_reached_students[day][interval] == self.schedule_data.classrooms[classroom].capacity:
                    return False, 'Classroom is full.'
                
        
        # checking if classroom is already assigned in this slot
        if self.days[day][interval][classroom] is not None:
            #print("Classroom already assigned in this slot: ", day, " ", interval, " ", classroom[0])
            return False, 'Classroom already assigned in this slot.'
        
        
        # all hard constraints checked, returning True
        return True, None
        
    def assign_course(self, course: str, day: str, interval: tuple, classroom: str, professor: str):
        """Assigns a course to a classroom, day, interval and professor"""
        
        # assigin the course to the classroom
        if day in self.days and interval in self.days[day]:
            self.days[day][interval][classroom] = (professor, course)
        elif day in self.days:
            self.days[day][interval] = {classroom: (professor, course)}
        else:
            self.days[day] = {interval: {classroom: (professor, course)}}
        
        # updating the professor data and increasing number of teaching intervals
        self.schedule_data.professors[professor].increment_nr_teaching_intervals()
        
        # updating the number of students left to assign to the course and the number of students reached in the classroom
        if self.students_left[course] > self.schedule_data.classrooms[classroom].capacity:
            self.students_left[course] -= self.schedule_data.classrooms[classroom].capacity
            self.schedule_data.classrooms[classroom].slot_reached_students[day][interval] = self.schedule_data.classrooms[classroom].capacity
        else:
            self.schedule_data.classrooms[classroom].slot_reached_students[day][interval] = self.students_left[course]
            self.students_left[course] = 0
    
    def is_valid(self):
        """Checks if the current schedule is valid based on hard constraints"""
        return check_mandatory_constraints(self.days, self.specs) == 0
        
    
    def find_new_prof_to_reassign(self, professor: str, course: str):
        """Finds a random new professor available"""
        new_professor = None
        available_professors = [prof for prof in self.schedule_data.professors\
            if course in self.schedule_data.professors[prof].courses\
            and not self.schedule_data.professors[prof].already_assigned]

        if len(available_professors) == 0:
            return False
        
        #print("AVAILABLE PROFESSORS: ", available_professors)

        new_professor = random.choice(available_professors)
        return new_professor
            
    
    def get_random_violated_slot(self, professor: str,
                                 day_constraints_violated: list,
                                 interval_constraints_violated: list):
        """Returns a random violated slot, classroom, and course for a professor based on the constraints."""
        violated_day = None
        violated_interval = None

        if len(day_constraints_violated) != 0:
            violated_day = random.choice(day_constraints_violated)
            for day in self.days:
                if day == violated_day:
                    for interval in self.days[day]:
                        for classroom, data in self.days[day][interval].items():
                            if data and data[0] == professor:
                                return day, interval, classroom, data[1]
        elif len(interval_constraints_violated) != 0:
            violated_interval = random.choice(interval_constraints_violated)
            for day in self.days:
                for interval in self.days[day]:
                    if interval == violated_interval:
                        for classroom, data in self.days[day][interval].items():
                            if data and data[0] == professor:
                                return day, interval, classroom, data[1]
        
        
            
    
    def generate_available_slots(self, day_constraints_violated: list,
                                  interval_constraints_violated: list):
        """Generates available day and interval for a professor based on the constraints."""
        slots = {}
        for day in self.days:
            for interval in self.days[day]:
                if day not in day_constraints_violated and interval not in interval_constraints_violated:
                    slots[(day, interval)] = True
        return slots
    
    def try_assign_left_students_non_empty_slots(self, course: str, left_students: int):
        """Tries to assign the rest of the students to a course and returns False if couldnt assign all students"""
        
        for day in self.days:
            for interval in self.days[day]:
                # getting a random professor that can teach the course
                available_professors = list(professor for professor in self.schedule_data.professors.keys()\
                if course in self.schedule_data.professors[professor].courses and\
                not self.schedule_data.professors[professor].already_assigned)

                if len(available_professors) == 0:
                    return False
                random_professor = random.choice(available_professors)
                
                for classroom in self.days[day][interval]:
                    
                    if self.days[day][interval][classroom] is None and\
                        course in self.schedule_data.classrooms[classroom].classes_allowed:
                        # assigning the rest of the students to the course not reaching the capacity
                        empty_spots = self.schedule_data.classrooms[classroom].capacity - self.schedule_data.classrooms[classroom].slot_reached_students[day][interval]
                        if empty_spots >= left_students:
                            self.days[day][interval][classroom] = (random_professor, course)
                            self.schedule_data.professors[random_professor].increment_nr_teaching_intervals()
                            self.schedule_data.classrooms[classroom].slot_reached_students[day][interval] += left_students
                            left_students = 0
                            return True
                        else:
                            self.days[day][interval][classroom] = (random_professor, course)
                            self.schedule_data.professors[random_professor].increment_nr_teaching_intervals()
                            self.schedule_data.classrooms[classroom].slot_reached_students[day][interval] += empty_spots
                            left_students -= empty_spots
                    if left_students == 0:
                        return True
        return False

    def try_to_assign_left_students(self, course: str, number_of_students: int):
        """Tries to assign the rest of the students to a course and returns False if couldnt assign all students"""
        for day in self.days:
            for interval in self.days[day]:
                for classroom in self.days[day][interval]:
                    if self.days[day][interval][classroom] is not None and course in self.schedule_data.classrooms[classroom].classes_allowed\
                        and self.schedule_data.classrooms[classroom].slot_reached_students[day][interval] < self.schedule_data.classrooms[classroom].capacity:
                        empty_spots = self.schedule_data.classrooms[classroom].capacity - self.schedule_data.classrooms[classroom].slot_reached_students[day][interval]
                        if empty_spots >= number_of_students:
                            self.schedule_data.classrooms[classroom].slot_reached_students[day][interval] += number_of_students
                            number_of_students = 0
                            return True
                        else:
                            self.schedule_data.classrooms[classroom].slot_reached_students[day][interval] += empty_spots
                            number_of_students -= empty_spots
        
        return False

        
    
    def try_to_assign_professor(self, professor: str, available_slots: dict, course: str, old_day: str, old_interval: tuple, old_classroom: str):
        """Tries to assign a professor to a new slot and returns left professor if no empty slots are available."""
        assigned = False
        for slot, available in available_slots.items():
            if available:
                for classroom in self.days[slot[0]][slot[1]]:
                    if self.days[slot[0]][slot[1]][classroom] is None and old_classroom == classroom:
                        # case when the classroom is the same
                        self.days[slot[0]][slot[1]][classroom] = (professor, course)
                        self.days[old_day][old_interval][old_classroom] = None
                        assigned = True
                        break
                    elif self.days[slot[0]][slot[1]][classroom] is None and old_classroom != classroom\
                        and classroom in self.schedule_data.classrooms[classroom].classes_allowed:
                        # case when the classroom is different
                        
                        # case when the classroom is not full and number of students from old classroom is less than the capacity
                        if self.schedule_data.classrooms[old_classroom].slot_reached_students[slot[0]][slot[1]] <= self.schedule_data.classrooms[classroom].capacity:
                            self.schedule_data.classrooms[classroom].slot_reached_students[slot[0]][slot[1]] = self.schedule_data.classrooms[old_classroom].slot_reached_students[old_day][old_interval]
                            self.schedule_data.classrooms[old_classroom].slot_reached_students[old_day][old_interval] = 0
                            self.days[slot[0]][slot[1]][classroom] = (professor, course)
                            self.days[old_day][old_interval][old_classroom] = None
                            assigned = True
                            break

                        # case when the classroom is not full and number of students from old classroom is greater than the capacity
                        elif self.schedule_data.classrooms[old_classroom].slot_reached_students[old_day][old_interval] > self.schedule_data.classrooms[classroom].capacity:
                            left_to_assign = self.schedule_data.classrooms[old_classroom].slot_reached_students[old_day][old_interval] - self.schedule_data.classrooms[classroom].capacity
                            self.schedule_data.classrooms[classroom].slot_reached_students[slot[0]][slot[1]] = self.schedule_data.classrooms[classroom].capacity
                            self.days[slot[0]][slot[1]][classroom] = (professor, course)
                            assigned, left_students = self.try_to_assign_left_students(course, left_to_assign)
                            if left_students:
                                assigned = self.try_assign_left_students_non_empty_slots(course) 
                            else:
                                assigned = True  
                if assigned:
                    break
            if assigned:
                break
        
        for slot, available in available_slots.items():
            if available:
                for classroom in self.days[slot[0]][slot[1]]:
                    if self.days[slot[0]][slot[1]][classroom] and self.days[slot[0]][slot[1]][classroom][1] == course:
                        old_professor = self.days[slot[0]][slot[1]][classroom][0]
                        self.days[old_day][old_interval][old_classroom] = None
                        self.days[slot[0]][slot[1]][classroom] = (professor, course)
                        self.schedule_data.professors[old_professor].decrement_nr_teaching_intervals()
                        assigned = True
            if assigned:
                break
        
        return assigned
        
    
    def resolve_violated_constraints(self, professor: str, violated_constraints: list):
        """Resolves the violated constraints for a professor"""
        day_constraints_violated = [vc[0] for vc in violated_constraints if vc[0] is not None]
        interval_constraints_violated = [vc[1] for vc in violated_constraints if vc[1] is not None]
        
        
        violated_day, violated_interval, old_classroom, course_to_reassign =\
            self.get_random_violated_slot(professor, day_constraints_violated, interval_constraints_violated)
        
        # generating a new day and interval for the professor which suit the preferences and a violated slot to replace
        available_slots = self.generate_available_slots(day_constraints_violated,\
            interval_constraints_violated)

        if len(available_slots) == 0:
            return False
        
        assigned = self.try_to_assign_professor(professor, available_slots, course_to_reassign, violated_day, violated_interval, old_classroom)
        return assigned
        
    
    def successors(self):
        """Generates the successors of the current state"""
        successors = []
        for professor in self.violated_constraints:
            # getting the violated constraints for each professor
            violated_constraints = self.violated_constraints[professor]
            if len(violated_constraints) == 0:
                continue
            new_schedule = copy.deepcopy(self)
            new_schedule.violated_constraints = {prof: [] for prof in new_schedule.schedule_data.professors}
            resolved = new_schedule.resolve_violated_constraints(professor, violated_constraints)
            if resolved and new_schedule.is_valid():
                successors.append(new_schedule)

        return successors
    
    def astar_heuristic():
        """Heuristic function for A* algorithm"""
        pass
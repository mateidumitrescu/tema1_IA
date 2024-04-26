class Professor:
    """Professor class"""
    def __init__(self, preferences: list, courses: list):
        self.preferences = preferences
        self.courses = courses
        self.nr_teaching_intervals = 0 # used to check if a professor reached 7 intervals per week
        self.already_assigned = False # switching to True when a professor is assigned to 7 intervals
    
    def parse_interval(self, interval: str):
        """Parses the interval string and returns a list of time slots covered by this interval."""
        start, end = map(int, interval.split('-'))
        return [f"{hour}-{hour+2}" for hour in range(start, end, 2)]


    def parse_preferences(self):
        """Parses the preferences to expand time intervals into specific slots. example: 8-14 -> 8-10, 10-12, 12-14"""
        refactored_preferences = []
        for pref in self.preferences:
            if '-' in pref and not pref.startswith('!'):
                # preffered intervals
                refactored_preferences.extend(self.parse_interval(pref))
            elif pref.startswith('!') and '-' in pref[1:]:
                # negated intervals
                negated_intervals = self.parse_interval(pref[1:])
                refactored_preferences.extend(f'!{interval}' for interval in negated_intervals)
            else:
                # day prefs
                refactored_preferences.append(pref)
        self.preferences = refactored_preferences
    
    def increment_nr_teaching_intervals(self):
        """Increments the number of teaching intervals"""
        self.nr_teaching_intervals += 1
        if self.nr_teaching_intervals == 7:
            self.already_assigned = True
    
    def decrement_nr_teaching_intervals(self):
        """Decrements the number of teaching intervals"""
        self.nr_teaching_intervals -= 1
        if self.nr_teaching_intervals < 7:
            self.already_assigned = False

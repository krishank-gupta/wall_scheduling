from pulp import *
from itertools import combinations
import csv
from datetime import time

# Define open hours, employee availability, staff needed for each shift
openhours = {
    #Day: start, open, employees needed
    "Sunday": [
        (time(14), time(16), 2), # 2 employees needed for this shift
        (time(16), time(18), 2),
        (time(18), time(20), 3), # 3 employees needed for this shift
    ],
    "Monday": [
        (time(16), time(18), 2),
        (time(18), time(20), 3),
        (time(20), time(22), 2)
    ],
    "Tuesday": [
        (time(16), time(18), 2),
        (time(18), time(20), 3),
        (time(20), time(22), 2)
    ],
    "Wednesday": [
        (time(16), time(18), 3),
        (time(18), time(20), 3),
        (time(20), time(22), 2)
    ],  
    "Thursday": [
        (time(14), time(16), 2),
        (time(16), time(18), 2),
        (time(18), time(20), 2)
    ],
    "Friday": [
        (time(12), time(14), 2),
        (time(14), time(16), 2),
        (time(16), time(18), 2)
    ],
    "Saturday": [
    ]
}

# Discourage algorithm to return results with the following pairs working together
# Names must match the csv file, edit responses if necessary
# CONFLICTS = {
#     ("PersonX", "PersonY"): 5,  # higher value = more discouraged
#     ("PersonA", "PersonY"): 5
# }

# Add conflicts in the format above
CONFLICTS = {

}

# Encourage algorithm to return resuts with the following pairs working together

# For gender queer and beginner hours, put people comfortable working together below 
# So that they are likely to be scheduled together and those hours can be 
# PREFERRED_PAIRS = {
#     ("PersonA", "PersonB"): 5,
#     ("PersonC", "PersonD"): 5
# }

# Add preferred pairs in the format above
PREFERRED_PAIRS = {
}

# Convert form response from csv file to actual week day
# If form question for availability changes, change this variable
DAY_COLUMNS = {
    "Availability: [Sunday]": "Sunday",
    "Availability: [Monday]": "Monday",
    "Availability: [Tuesday]": "Tuesday",
    "Availability: [Wednesday]": "Wednesday",
    "Availability: [Thursday]": "Thursday",
    "Availability: [Friday]": "Friday",
    "Availability: [Saturday]": "Saturday",
}

FAIRNESS_WEIGHT = 12  # try 1–10
EXACT_TWO_REWARD = 12   # stronger than deviation penalty

######################################################################################################
##################################### DO NOT EDIT BELOW THIS LINE ####################################
##################################### DO NOT EDIT BELOW THIS LINE ####################################
##################################### DO NOT EDIT BELOW THIS LINE ####################################
######################################################################################################

# Ensure lower case for CONFLICTS and PREFERRED_PAIRS
CONFLICTS = {tuple(map(str.lower, pair)): w for pair, w in CONFLICTS.items()}
PREFERRED_PAIRS = {tuple(map(str.lower, pair)): w for pair, w in PREFERRED_PAIRS.items()}

# Employee availability in pulled from csv file

# Change this line if you need to override availability variable.
# The format is commented below
employee_availability = {}

# employee_availability = {
#     "Jack": {
#         # Day: start, end (time is assumed to be in pm)
#         "Monday": [(time(12), time(2))]
#     },
#     "Jackson": {
#         "Monday": [(time(12), time(2))],
#         "Tuesday": [(time(12), time(2))]
#     }, 
#     "Jake": {
#         "Monday": [(time(12), time(2))],
#         "Tuesday": [(time(12), time(2))]
#     },
#     "Marina": {
#         "Monday": [(time(12), time(2))]
#     }
# }


def parse_time_range(time_range: str):
    """
    Docstring for parse_time_range
    
    :param time_range: takes in a range like 12 - 2 or 2 - 4 
    :type t: str
    :return: tuple with starttime and endtime as datetime objects
    :rtype: tuple
    """

    def parse_time(t: str) -> time:
        hour, minute = map(int, t.strip().split(":"))

        # Convert to 24-hour time (PM assumed)
        if hour != 12:
            hour += 12

        return time(hour=hour, minute=minute)

    start_str, end_str = time_range.split("-")

    start_time = parse_time(start_str)
    end_time = parse_time(end_str)

    return start_time, end_time


def parse_availability(cell):
    """
    Converts '12:00 - 2:00, 4:00 - 6:00'
    -> [(time(12), time(14)), (time(16), time(18))]
    """
    if not cell or not cell.strip():
        return []

    ranges = cell.split(",")
    return [parse_time_range(r.strip()) for r in ranges]


# read responses file
with open("responses.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        name = row["Name"].strip().lower()
        employee_availability[name] = {}

        for csv_col, day in DAY_COLUMNS.items():
            availability = parse_availability(row.get(csv_col, ""))
            if availability:
                employee_availability[name][day] = availability


# At this point, the employee availability should be fully parsed 
# And updated into the employee_availability dictionary

# Start a problem definition
lp = LpProblem("wall_scheduling", LpMaximize)

deviation = {}
exact_two = {}

for employee in employee_availability:
    deviation[employee] = LpVariable(
        f"deviation_{employee}",
        lowBound=0,
        cat="Continuous"
    )
    exact_two[employee] = LpVariable(
        f"exact_two_{employee}",
        cat="Binary"
    )


# variable[(employee, day, start, end)] = 1 if employee works that shift
variable = {}

for day, shifts in openhours.items():
    for start, end, _ in shifts:
        for employee, availability in employee_availability.items():
            if day in availability:
                for a_start, a_end in availability[day]:
                    if a_start <= start and a_end >= end:
                        variable[(employee, day, start, end)] = LpVariable(
                            f"{employee}_{day}_{start.strftime('%H%M')}_{end.strftime('%H%M')}",
                            cat="Binary"
                        )

# 1) Enough employees on staff
for day, shifts in openhours.items():
    for start, end, required in shifts:
        lp += (
            lpSum(
                variable[(e, day, start, end)]
                for e in employee_availability
                if (e, day, start, end) in variable
            )
            == required,
            f"coverage_{day}_{start.strftime('%H%M')}_{end.strftime('%H%M')}"
        )

# 2) Employee min 1 shift and max 3 shifts
for employee in employee_availability:
    employee_shifts = [
        var for (e, _, _, _), var in variable.items() if e == employee
    ]

    if employee_shifts:
        S = lpSum(employee_shifts)
        lp += (
            S >= 1,
            f"min_1_shift_{employee}"
        )
        lp += (
            lpSum(employee_shifts) <= 3,
            f"max_3_shifts_{employee}"
        )

        lp += deviation[employee] >= S - 2
        lp += deviation[employee] >= 2 - S

        lp += S >= 2 * exact_two[employee]
        lp += S <= 2 + (1 - exact_two[employee]) * 10

# 3) No consecutive shifts for an employee
for employee in employee_availability:
    shifts = [
        (day, start, end, variable[(employee, day, start, end)])
        for (e, day, start, end) in variable
        if e == employee
    ]

    for (d1, s1, e1, v1), (d2, s2, e2, v2) in combinations(shifts, 2):
        if d1 == d2 and (e1 == s2 or e2 == s1):
            lp += (
                v1 + v2 <= 1,
                f"no_consecutive_{employee}_{d1}_"
                f"{s1.strftime('%H%M')}_{e1.strftime('%H%M')}_"
                f"{s2.strftime('%H%M')}_{e2.strftime('%H%M')}"
            )

# 4) Penalize staff who shouldn't be placed together
penalties = []

for (e1, e2), weight in CONFLICTS.items():
    for (employee, day, start, end) in variable:
        if employee == e1 and (e2, day, start, end) in variable:
            p = LpVariable(
                f"penalty_{e1}_{e2}_{day}_{start.strftime('%H%M')}",
                lowBound=0,
                upBound=1,
                cat="Binary"
            )

            # Activate penalty if both are scheduled
            lp += (
                p >= variable[(e1, day, start, end)] + variable[(e2, day, start, end)] - 1
            )

            penalties.append((p, weight))

# 5) Encourage algorithms to pair these pairs
bonuses = []

for (e1, e2), weight in PREFERRED_PAIRS.items():
    for (employee, day, start, end) in variable:
        if employee == e1 and (e2, day, start, end) in variable:
            b = LpVariable(
                f"bonus_{e1}_{e2}_{day}_{start.strftime('%H%M')}",
                lowBound=0,
                upBound=1,
                cat="Binary"
            )

            # Bonus active only if both are assigned
            lp += (
                b <= variable[(e1, day, start, end)]
            )
            lp += (
                b <= variable[(e2, day, start, end)]
            )

            bonuses.append((b, weight))


lp += (
    lpSum(weight * b for b, weight in bonuses)
    - lpSum(weight * p for p, weight in penalties)
    - FAIRNESS_WEIGHT * lpSum(deviation.values())
    + EXACT_TWO_REWARD * lpSum(exact_two.values())
)

lp.solve(PULP_CBC_CMD(msg=False))

print(f"Status: {LpStatus[lp.status]}\n")

final_schedule_set = []

for key, var in variable.items():
    if var.varValue==1:
        final_schedule_set.append(var.name)
        
        
def who_is_working(shift):
    employees = []
    for instance in final_schedule_set:
        if shift in instance:
            employees.append(instance.split("_")[0])

    return employees


def when_are_they_working(employee):
    shifts = []
    for instance in final_schedule_set:
        if instance.split("_")[0] == employee:
            shifts.append(instance.split("_")[1:4])

    return shifts


def total_hours():
    return len(final_schedule_set)


# for instance in final_schedule_set:
    # print("final: ", instance)


for emp in employee_availability:
    shifts = when_are_they_working(emp)
    print(f"{emp.title()} is working {len(shifts)} shifts: {shifts}")

for time_slot in openhours:
    for start, end, _ in openhours[time_slot]:
        shift_str = f"{time_slot}_{start.strftime('%H%M')}_{end.strftime('%H%M')}"
        employees = who_is_working(shift_str)
        print(f"On {time_slot} from {start.strftime('%H:%M')} to {end.strftime('%H:%M')}, working: {employees}")
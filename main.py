from pulp import *
from itertools import combinations
from collections import defaultdict
import csv
from datetime import time

from config import (
    OPENHOURS,
    CONFLICTS,
    PREFERRED_PAIRS,
    DAY_COLUMNS,
    FAIRNESS_WEIGHT,
    EXACT_TWO_REWARD,
)

# ==============================================================================
# NORMALISE CONFIG
# Lowercase names in CONFLICTS and PREFERRED_PAIRS so matching is
# case-insensitive regardless of how names are typed in config.py.
# ==============================================================================

CONFLICTS = {tuple(map(str.lower, pair)): w for pair, w in CONFLICTS.items()}
PREFERRED_PAIRS = {tuple(map(str.lower, pair)): w for pair, w in PREFERRED_PAIRS.items()}

def parse_time(t: str) -> time:
    """
    Parse a time string like '10:00 AM' or '2:00 PM'.
    Falls back to assuming PM if no AM/PM indicator is present.
    """
    t = t.strip().upper()
    is_am = t.endswith("AM")
    is_pm = t.endswith("PM")

    # Strip AM/PM suffix if present
    if is_am or is_pm:
        t = t[:-2].strip()

    hour, minute = map(int, t.split(":"))

    if is_am:
        if hour == 12:
            hour = 0          # 12:00 AM = midnight
    else:
        # PM assumed if no suffix
        if hour != 12:
            hour += 12        # 2:00 PM -> 14:00, but 12:00 PM stays as 12

    return time(hour=hour, minute=minute)

def parse_time_range(time_range: str) -> tuple:
    """
    Parse a range string like '2:00 - 4:00' into a (start, end) time tuple.
    """
    start_str, end_str = time_range.split("-")
    return parse_time(start_str), parse_time(end_str)


def parse_availability(cell: str) -> list:
    """
    Convert a cell value like '12:00 - 2:00, 4:00 - 6:00'
    into [(time(12,0), time(14,0)), (time(16,0), time(18,0))].
    """
    if not cell or not cell.strip():
        return []
    return [parse_time_range(r.strip()) for r in cell.split(",")]


def load_availability(filepath: str) -> dict:
    """
    Read responses.csv and return a dict of:
        { lowercase_name: { day: [(start, end), ...] } }
    """
    availability = {}
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["Name"].strip().lower()
            availability[name] = {}
            for csv_col, day in DAY_COLUMNS.items():
                slots = parse_availability(row.get(csv_col, ""))
                if slots:
                    availability[name][day] = slots
    return availability


# ==============================================================================
# LP MODEL
# ==============================================================================

def build_and_solve(employee_availability: dict):
    lp = LpProblem("wall_scheduling", LpMaximize)

    # --- Fairness tracking variables ---
    deviation = {}
    exact_two = {}
    for employee in employee_availability:
        deviation[employee] = LpVariable(f"deviation_{employee}", lowBound=0, cat="Continuous")
        exact_two[employee] = LpVariable(f"exact_two_{employee}", cat="Binary")

    # --- Decision variables ---
    # variable[(employee, day, start, end)] = 1 if that employee works that shift
    variable = {}
    for day, shifts in OPENHOURS.items():
        for start, end, _ in shifts:
            for employee, avail in employee_availability.items():
                if day in avail:
                    for a_start, a_end in avail[day]:
                        if a_start <= start and a_end >= end:
                            var_name = (
                                f"{employee}_{day}_"
                                f"{start.strftime('%H%M')}_{end.strftime('%H%M')}"
                            )
                            variable[(employee, day, start, end)] = LpVariable(
                                var_name, cat="Binary"
                            )

    # --- Constraint 1: Required coverage per shift ---
    for day, shifts in OPENHOURS.items():
        for start, end, required in shifts:
            lp += (
                lpSum(
                    variable[(e, day, start, end)]
                    for e in employee_availability
                    if (e, day, start, end) in variable
                )
                == required,
                f"coverage_{day}_{start.strftime('%H%M')}_{end.strftime('%H%M')}",
            )

    # --- Constraint 2: Each employee works between 1 and 3 shifts ---
    for employee in employee_availability:
        employee_vars = [var for (e, _, _, _), var in variable.items() if e == employee]
        if not employee_vars:
            continue

        S = lpSum(employee_vars)
        lp += (S >= 1, f"min_1_shift_{employee}")
        lp += (S <= 3, f"max_3_shifts_{employee}")

        # Track deviation from 2 shifts for fairness penalty
        lp += deviation[employee] >= S - 2
        lp += deviation[employee] >= 2 - S

        # Reward exactly 2 shifts
        lp += S >= 2 * exact_two[employee]
        lp += S <= 2 + (1 - exact_two[employee]) * 10

    # --- Constraint 3: No consecutive shifts for any employee ---
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
                    f"{s2.strftime('%H%M')}_{e2.strftime('%H%M')}",
                )

    # --- Objective: penalties and bonuses ---
    penalties = []
    for (e1, e2), weight in CONFLICTS.items():
        for (employee, day, start, end) in variable:
            if employee == e1 and (e2, day, start, end) in variable:
                p = LpVariable(
                    f"penalty_{e1}_{e2}_{day}_{start.strftime('%H%M')}",
                    lowBound=0, upBound=1, cat="Binary",
                )
                lp += p >= variable[(e1, day, start, end)] + variable[(e2, day, start, end)] - 1
                penalties.append((p, weight))

    bonuses = []
    for (e1, e2), weight in PREFERRED_PAIRS.items():
        for (employee, day, start, end) in variable:
            if employee == e1 and (e2, day, start, end) in variable:
                b = LpVariable(
                    f"bonus_{e1}_{e2}_{day}_{start.strftime('%H%M')}",
                    lowBound=0, upBound=1, cat="Binary",
                )
                lp += b <= variable[(e1, day, start, end)]
                lp += b <= variable[(e2, day, start, end)]
                bonuses.append((b, weight))

    lp += (
        lpSum(weight * b for b, weight in bonuses)
        - lpSum(weight * p for p, weight in penalties)
        - FAIRNESS_WEIGHT * lpSum(deviation.values())
        + EXACT_TWO_REWARD * lpSum(exact_two.values())
    )

    lp.solve(PULP_CBC_CMD(msg=False))
    return lp, variable


# ==============================================================================
# RESULT LOOKUP
# Build two plain dicts from solved variables — no string parsing.
#   shifts_by_employee: { employee -> [(day, start, end), ...] }
#   employees_by_shift: { (day, start, end) -> [employee, ...] }
# ==============================================================================

def build_lookup(variable: dict) -> tuple[dict, dict]:
    shifts_by_employee = defaultdict(list)
    employees_by_shift = defaultdict(list)

    for (employee, day, start, end), var in variable.items():
        if var.varValue == 1:
            shifts_by_employee[employee].append((day, start, end))
            employees_by_shift[(day, start, end)].append(employee)

    return dict(shifts_by_employee), dict(employees_by_shift)

# ==============================================================================
# Infeasible Results Diagnostic
# Re-runs the model by changing constraints to identify why a solution can't be found.
# ==============================================================================

def diagnose_infeasible(employee_availability: dict):
    lp = LpProblem("wall_scheduling_diagnostic", LpMinimize)

    variable = {}
    for day, shifts in OPENHOURS.items():
        for start, end, _ in shifts:
            for employee, avail in employee_availability.items():
                if day in avail:
                    for a_start, a_end in avail[day]:
                        if a_start <= start and a_end >= end:
                            variable[(employee, day, start, end)] = LpVariable(
                                f"{employee}_{day}_{start.strftime('%H%M')}_{end.strftime('%H%M')}",
                                cat="Binary"
                            )

    # Shortfall variable for each shift — how many staff short are we?
    shortfall = {}
    for day, shifts in OPENHOURS.items():
        for start, end, required in shifts:
            s = LpVariable(
                f"shortfall_{day}_{start.strftime('%H%M')}_{end.strftime('%H%M')}",
                lowBound=0, cat="Integer"
            )
            shortfall[(day, start, end)] = s

            lp += (
                lpSum(
                    variable[(e, day, start, end)]
                    for e in employee_availability
                    if (e, day, start, end) in variable
                ) + s == required,
                f"coverage_{day}_{start.strftime('%H%M')}_{end.strftime('%H%M')}"
            )

    # Minimize total shortfall
    lp += lpSum(shortfall.values())
    lp.solve(PULP_CBC_CMD(msg=False))

    print("\n--- Infeasibility Diagnostic ---")
    total = 0
    for (day, start, end), s in shortfall.items():
        gap = int(round(s.varValue))
        if gap > 0:
            total += gap
            available = [
                e for e in employee_availability
                if (e, day, start, end) in variable
            ]
            print(
                f"  {day} {start.strftime('%H:%M')}–{end.strftime('%H:%M')}: "
                f"short by {gap} staff "
                f"(only {len(available)} available: {[e.title() for e in available]})"
            )
    if total == 0:
        print("  Coverage gaps are not the issue — check min/max shift constraints.")
    print(f"  Total staff shortfall: {total}\n")

# ==============================================================================
# ENTRY POINT
# ==============================================================================

if __name__ == "__main__":
    employee_availability = load_availability("responses.csv")

    lp, variable = build_and_solve(employee_availability)

    status = LpStatus[lp.status]
    print(f"Status: {status}\n")

    if status == "Infeasible":
        print(
            "No valid schedule could be found. Please check the diagnostic below to identify coverage gaps or conflicting constraints in the availability data."
        )

        diagnose_infeasible(employee_availability)
    else:
        shifts_by_employee, employees_by_shift = build_lookup(variable)

        # Per-employee summary
        for employee in employee_availability:
            shifts = shifts_by_employee.get(employee, [])
            readable = [
                f"{day} {start.strftime('%H:%M')}–{end.strftime('%H:%M')}"
                for day, start, end in shifts
            ]
            print(f"{employee.title()} is working {len(shifts)} shift(s): {readable}")

        print()

        # Per-shift summary
        for day, shift_list in OPENHOURS.items():
            for start, end, _ in shift_list:
                workers = employees_by_shift.get((day, start, end), [])
                names = [w.title() for w in workers]
                print(
                    f"{day} {start.strftime('%H:%M')}–{end.strftime('%H:%M')}: "
                    f"{', '.join(names) if names else 'UNCOVERED'}"
                )
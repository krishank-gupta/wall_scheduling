from datetime import time

# ==============================================================================
# SHIFT SCHEDULE
# Define open hours and how many employees are needed per shift.
# Format: (start_time, end_time, employees_needed)
# ==============================================================================

OPENHOURS = {
    "Sunday": [
        (time(10), time(12), 3),
        (time(14), time(16), 2),
        (time(16), time(18), 2),
        (time(18), time(20), 3),
    ],
    "Monday": [
        (time(16), time(18), 2),
        (time(18), time(20), 3),
        (time(20), time(22), 2),
    ],
    "Tuesday": [
        (time(16), time(18), 2),
        (time(18), time(20), 3),
        (time(20), time(22), 2),
    ],
    "Wednesday": [
        (time(16), time(18), 3),
        (time(18), time(20), 3),
        (time(20), time(22), 2),
    ],
    "Thursday": [
        (time(14), time(16), 2),
        (time(16), time(18), 2),
        (time(18), time(20), 2),
    ],
    "Friday": [
        (time(12), time(14), 2),
        (time(14), time(16), 2),
        (time(16), time(18), 2),
    ],
    "Saturday": [],
}

# ==============================================================================
# CONFLICTS
# Pairs of staff who should NOT be scheduled together.
# Higher weight = more strongly discouraged.
# Names must match the Name column in responses.csv (case-insensitive).
# ==============================================================================

CONFLICTS = {
    ("Julia", "Krish"): 5,
    ("Julia", "Krish"): 5
}

# ==============================================================================
# PREFERRED PAIRS
# Pairs of staff who SHOULD be scheduled together when possible.
# Useful for gender-queer hours, beginner hours, etc.
# Higher weight = more strongly encouraged.
# Names must match the Name column in responses.csv (case-insensitive).
# ==============================================================================

PREFERRED_PAIRS = {
    ("Julia", "Marina"): 5,
    ("Berit", "Maggie"): 5
}

# ==============================================================================
# CSV COLUMN MAPPING
# Maps the Google Form column headers to day names.
# If you rename the availability questions in your form, update the keys here.
# ==============================================================================

DAY_COLUMNS = {
    "Availability: [Sunday]": "Sunday",
    "Availability: [Monday]": "Monday",
    "Availability: [Tuesday]": "Tuesday",
    "Availability: [Wednesday]": "Wednesday",
    "Availability: [Thursday]": "Thursday",
    "Availability: [Friday]": "Friday",
    "Availability: [Saturday]": "Saturday",
}

# ==============================================================================
# SOLVER WEIGHTS
# FAIRNESS_WEIGHT: penalizes employees scheduled for more or fewer than 2 shifts.
#                 Increase to enforce fairness more strictly (try 1–20).
# EXACT_TWO_REWARD: rewards employees scheduled for exactly 2 shifts.
#                  Should be >= FAIRNESS_WEIGHT to be effective.
# ==============================================================================

FAIRNESS_WEIGHT = 12
EXACT_TWO_REWARD = 12
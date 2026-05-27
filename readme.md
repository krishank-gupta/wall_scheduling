# Climbing Wall Scheduling Program — Instructions

## Overview

This program takes staff availability from a Google Form and automatically generates an optimized weekly schedule using a linear programming algorithm.

## Features

The program takes staff availability as input in the form of a CSV file. The program has opening hours and the number of staff per shift configured in the code (this can be changed in the top section of the main.py file). The program can also configure staff who should and shouldn't be placed together in the same shift. This is useful for staff who can work together during beginner hours/gender queer hours/lead hours, or if there are staff who don't work well together. The program tries to give everybody 2 shifts which are non-consecutive based on their availability. 

The program defaults to a PM timing because all open shifts are in the evening time. If at some point there is going to be an AM opening shift, then the csv file result should include 'AM' for every AM time. For example: `10:00 AM - 12:00, 4:00 - 6:00` and then the config file can be updated to include the new shift as follows
`
    "Sunday": [
        (time(10), time(12), 2),
        (time(14), time(16), 2),
        (time(16), time(18), 2),
        (time(18), time(20), 3),
    ],
`
If there is no possible schedule based on availability, the program runs a diagnostic to identify which shifts can't have enough staff so that the manager can find additional staffing for those shifts or reduce number of staff required for those shifts.
---

## Step 1: Create the Google Form

Set up a Google Form to collect staff availability. Use [this form as a template](https://docs.google.com/forms/d/e/1FAIpQLScDm7RmICxDxqS0QrIsot4kdgMcUTFGyrRPfM1XToTgjM7aqw/viewform?usp=sharing&ouid=116637393748767995209).

Responses will be collected in a linked Google Sheet like [this one](https://docs.google.com/spreadsheets/d/1DLvVRkcAmcM9ygJNwkUg9-JlUUYqW3F3ZOnGmCwotSs/edit?usp=sharing).

> **Important:** The **Name** and **Availability** question labels in your form must exactly match what is in the code (case-sensitive). Do not rename these columns in the sheet.

---

## Step 2: Download the Code

Go to the [GitHub repository](https://github.com/krishank-gupta/wall_scheduling/tree/main) and download the code using the green **Code** button → **Download ZIP**. Then unzip the folder somewhere on your computer. Delete the responses.csv file because the next step will create a new one with the fresh data.

---

## Step 3: Export Responses as CSV

In your Google Sheet, go to **File → Download → Comma-separated values (.csv)** and save the downloaded file into the unzipped folder. 
Make sure the file is named `responses.csv`.

---

## Step 4: Install Python

If you don't already have Python installed, download it from [python.org/downloads](https://www.python.org/downloads/) and follow the installation instructions.

---

## Step 5: Open a Terminal

Open a terminal window (Terminal on Mac/Linux, Command Prompt or PowerShell on Windows).

Type `cd ` (with a space after it), then drag the unzipped folder into the terminal window and press **Enter**. This navigates the terminal into the project folder.

---

## Step 6: Install Dependencies

Type the following command on the terminal window and press **Enter**:

```
pip install -r requirements.txt
```

This will install the required `pulp` library. It may take a few seconds.

---

## Step 7: Configure Conflicts and Preferred Pairs

Open `config.py` in a text editor (such as TextEdit on Mac, Notepad on Windows, or VS Code).

Find the `CONFLICTS` and `PREFERRED_PAIRS` sections near the top of the file and edit them to reflect any staffing preferences:

- **CONFLICTS** — pairs of staff who should *not* be scheduled together
- **PREFERRED_PAIRS** — pairs of staff who *should* be scheduled together when possible (e.g. for beginner or gender-queer hours)

*These restrictions will only be respected if there is a potential solution while respecting them. 

Names must match exactly how they appear in the `responses.csv` file (the program handles capitalization automatically).

You can also edit the opening hours in this section and how many staff are needed in any opening shift.

---

## Step 8: Run the Program

In the terminal, run:

```
python3 main.py
```

Press **Enter**. The program will generate and print the schedule.

---

## Understanding the Output

The output has three parts:

1. **Status line** — either `Optimal` (a valid schedule was found) or `Infeasible` (there isn't enough staff availability to fill all shifts — you may need to adjust shift requirements or follow up with staff).

2. **Per-employee summary** — each staff member and how many shifts they are scheduled for, along with which shifts those are.

3. **Per-shift summary** — each shift listed with the names of staff assigned to it.

---

## After Running

Use the output to build a final schedule in a spreadsheet. Some manual adjustments may be necessary based on your program's specific needs.

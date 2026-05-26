# Climbing Wall Scheduling Program — Instructions

## Overview

This program takes staff availability from a Google Form and automatically generates an optimized weekly schedule using a linear programming algorithm.

---

## Step 1: Create the Google Form

Set up a Google Form to collect staff availability. Use [this form as a template](https://docs.google.com/forms/d/e/1FAIpQLScDm7RmICxDxqS0QrIsot4kdgMcUTFGyrRPfM1XToTgjM7aqw/viewform?usp=sharing&ouid=116637393748767995209).

Responses will be collected in a linked Google Sheet like [this one](https://docs.google.com/spreadsheets/d/1DLvVRkcAmcM9ygJNwkUg9-JlUUYqW3F3ZOnGmCwotSs/edit?usp=sharing).

> **Important:** The **Name** and **Availability** question labels in your form must exactly match what is in the code (case-sensitive). Do not rename these columns in the sheet.

---

## Step 2: Download the Code

Go to the [GitHub repository](https://github.com/krishank-gupta/wall_scheduling/tree/main) and download the code using the green **Code** button → **Download ZIP**. Then unzip the folder somewhere on your computer.

---

## Step 3: Export Responses as CSV

In your Google Sheet, go to **File → Download → Comma-separated values (.csv)** and save the file into the unzipped folder. Make sure the file is named `responses.csv`.

---

## Step 4: Install Python

If you don't already have Python installed, download it from [python.org/downloads](https://www.python.org/downloads/) and follow the installation instructions.

---

## Step 5: Open a Terminal

Open a terminal window (Terminal on Mac/Linux, Command Prompt or PowerShell on Windows).

Type `cd ` (with a space after it), then drag the unzipped folder into the terminal window and press **Enter**. This navigates the terminal into the project folder.

---

## Step 6: Install Dependencies

Run the following command and press **Enter**:

```
pip install -r requirements.txt
```

This will install the required `pulp` library. It may take a few seconds.

---

## Step 7: Configure Conflicts and Preferred Pairs

Open `main.py` in a text editor (such as TextEdit on Mac, Notepad on Windows, or VS Code).

Find the `CONFLICTS` and `PREFERRED_PAIRS` sections near the top of the file and edit them to reflect any staffing preferences:

- **CONFLICTS** — pairs of staff who should *not* be scheduled together
- **PREFERRED_PAIRS** — pairs of staff who *should* be scheduled together when possible (e.g. for beginner or gender-queer hours)

Names must match exactly how they appear in the `responses.csv` file (the program handles capitalization automatically).

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
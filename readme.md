# Scheduling System

## Instructions

The first step is to download the data required from the google sheets. Download it as a csv file. 
Put it in the same folder as main.py and name it responses.csv

1) #### Open Hours

Now, edit the open hours. Go to main.py and find the lines with openhours. The times entered must be in 24hr format. 

```
openhours = {
    #Day: start, open, employees needed
    "Sunday": [
        (time(12), time(14), 1)
        (time(14), time(16), 1)
        (time(16), time(18), 1)
        (time(18), time(20), 1)
        (time(20), time(22), 1)
    ],
}
```

Edit each day so that it reflects the times you want to be open. The scheduling system is dynamic and works accordingly. A totally closed day can be left as:

```
    "Saturday": [

    ],

```

All times are assumed to be in pm format

2) #### Pair constraints

The system handles requests to encourage specifc pairs who want to work together and discourage pairs who don't want to work together. These need to be added manually. 

Find lines in main.py with the following code

```
# Discourage algorithm to return results with the following pairs working together
conflicts = {
    ("Jack", "John"): 5   # higher value = more discouraged
}

# Encourage algorithm to return resuts with the following pairs working together
preferred_pairs = {
    ("Jane", "Jone"): 5,  # higher value = more encouraged
    ("Mia", "Moa"): 5
}
```

Change names accordingly. The names must match the name submitted via google sheets. 

## Features

### Encourage/Discourage
The user can choose pairs of people who don't want to work together or pairs of people who really want to work together. The algorithm only complies if possible.


## How does it work

The algorithm uses a linear program to optimize (maximize flow)
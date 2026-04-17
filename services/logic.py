import random

def get_best_option(station, destination):
    # Simulated data
    walking_time = random.randint(5, 15)
    waiting_time = random.randint(3, 20)

    if walking_time < waiting_time:
        decision = "Walk"
    else:
        decision = "Take Auto/Bus"

    return {
        "station": station,
        "destination": destination,
        "walking_time": walking_time,
        "waiting_time": waiting_time,
        "suggestion": decision
    }
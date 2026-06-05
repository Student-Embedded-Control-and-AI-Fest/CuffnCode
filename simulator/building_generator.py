import random

def generate_energy_data():

    return {
        "hvac": random.randint(300,700),
        "lighting": random.randint(100,350),
        "elevator": random.randint(200,600),
        "server": random.randint(400,900),
        "solar": random.randint(100,500)
    }
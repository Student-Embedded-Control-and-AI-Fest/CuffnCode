import random

def generate_traffic():
    return {
        "lane1": random.randint(0, 30),
        "lane2": random.randint(0, 30),
        "lane3": random.randint(0, 30),
        "lane4": random.randint(0, 30),
    }
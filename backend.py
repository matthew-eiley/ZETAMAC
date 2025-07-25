from enum import Enum
import random
from datetime import datetime, timedelta
import time

class Difficulty(Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3

class Operation(Enum):
    ADD = 1
    SUB = 2
    MULT = 3
    DIV = 4

def generate_q_a(game):
    mult_div_base = [1, 12]
    match game:
        case Difficulty.EASY:
            add_sub = [1, 25]
            mult_div_spec = [1, 10]
        case Difficulty.MEDIUM:
            add_sub = [1, 50]
            mult_div_spec = [1, 15]
        case Difficulty.HARD:
            add_sub = [1, 100]
            mult_div_spec = [1, 20]
    
    operation_code = random.randint(1, 4)
    operation = Operation(operation_code)
    match operation:
        case Operation.ADD:
            x = random.randint(add_sub[0], add_sub[1])
            y = random.randint(add_sub[0], add_sub[1])
            q = f"{x} + {y}"
            a = x + y
            return q, int(a)
        case Operation.SUB:
            x = random.randint(add_sub[0], add_sub[1])
            y = random.randint(add_sub[0], x)
            q = f"{x} - {y}"
            a = x - y
            return q, int(a)
        case Operation.MULT:
            x = random.randint(mult_div_spec[0], mult_div_spec[1])
            y = random.randint(mult_div_base[0], mult_div_base[1])
            q = f"{x} * {y}"
            a = x * y
            return q, int(a)
        case Operation.DIV:
            y = random.randint(mult_div_base[0], mult_div_base[1])
            x = y * random.randint(mult_div_spec[0], mult_div_spec[1])
            q = f"{x} / {y}"
            a = x / y
            return q, int(a)

def run_game():
    user = input("ENTER YOUR NAME: ")
    diff = input("ENTER A DIFFICULTY LEVEL (easy, medium, hard): ")
    match diff.upper():
        case "EASY":
            game = Difficulty(1)
        case "MEDIUM":
            game = Difficulty(2)
        case "HARD":
            game = Difficulty(3)
        case _:
            print("INVALID DIFFICULTY LEVEL")
            run_game()
    
    print("3...")
    time.sleep(1)
    print("2...")
    time.sleep(1)
    print("1...")
    time.sleep(1)
    
    start = datetime.today()
    length = timedelta(seconds=120)
    score = 0
    wrong = []
    
    while datetime.today() - start < length:
        q, a = generate_q_a(game)
        print(f"\n{q}")
        ans = int(input())
        if ans == a:
            if datetime.today() - start < length: # to make sure they didn't take too long to answer
                score += 1
        else:
            wrong.append({
                "q": q,
                "correct": a,
                "your": ans
            })
    
    with open(f"./{game.name}_db.csv", "a") as db:
        db.write(f"{user},{start},{score},{len(wrong)}\n")

    print(f"\nYOU SCORED: {score} POINTS!")
    if len(wrong) != 0:
        print(f"\nYOU MADE {len(wrong)} MISTAKES:")
        for mistake in wrong:
            print(f"\n\tQUESTION: {mistake['q']}")
            print(f"\tCORRECT ANSWER: {mistake['correct']}")
            print(f"\tYOUR ANSWER: {mistake['your']}")

run_game()
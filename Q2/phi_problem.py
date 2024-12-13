import threading
import time
import sys

PHILOS = 5
DELAY = 0.005 
FOOD = 50


chopstick = [threading.Lock() for _ in range(PHILOS)]
food_lock = threading.Lock()

sleep_seconds = 0
food = FOOD

def food_on_table():
    global food
    with food_lock:
        if food > 0:
            food -= 1
        return food

def grab_chopstick(phil, c, hand):
    chopstick[c].acquire()
    print(f"Philosopher {phil}: got {hand} chopstick {c}")

def down_chopsticks(c1, c2):
    chopstick[c1].release()
    chopstick[c2].release()

def philosopher(num):
    id = num
    left_chopstick = (id + 1) % PHILOS
    right_chopstick = id

    print(f"Philosopher {id} is done thinking and now ready to eat.")

    while True:
        f = food_on_table()
        if f <= 0:
            break

       
        if id == 1:
            time.sleep(sleep_seconds)

        grab_chopstick(id, right_chopstick, "right")
        grab_chopstick(id, left_chopstick, "left")

        print(f"Philosopher {id}: eating.")
        time.sleep(DELAY * (FOOD - f + 1))

        down_chopsticks(left_chopstick, right_chopstick)

    print(f"Philosopher {id} is done eating.")

if __name__ == "__main__":

    if len(sys.argv) == 2:
        sleep_seconds = float(sys.argv[1])

    philosophers_threads = []
    for i in range(PHILOS):
        t = threading.Thread(target=philosopher, args=(i,))
        philosophers_threads.append(t)
        t.start()

    for t in philosophers_threads:
        t.join()

    print("All philosophers have finished.")

#!/usr/bin/env python3

import time
import multiprocessing

def calc_square(numbers):
    for n in numbers:
        print(n,'square ' + str(n*n))
        time.sleep(0.3)

def calc_cube(numbers):
    for n in numbers:
        print(n,'cube ' + str(n*n*n))
        time.sleep(.1)

if __name__ == "__main__":
    arr = [2,3,8]
    p1 = multiprocessing.Process(target=calc_square, args=(arr,))
    p2 = multiprocessing.Process(target=calc_cube, args=(arr,))

    p1.start()
    p2.start()

    p1.join()
    p2.join()

    print("Done!")
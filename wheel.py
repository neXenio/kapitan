import multiprocessing
import time


def track_job(job, update_interval=3):
    while job._number_left > 0:
        print("Tasks remaining = {0}".format(job._number_left * job._chunksize))
        print("left", job._number_left)
        print("chunk", job._chunksize)
        time.sleep(update_interval)


def hi(x):  # This must be defined before `p` if we are to use in the interpreter
    time.sleep(x)
    return x


a = [x for x in range(50)]

p = multiprocessing.Pool(12)

res = p.map_async(hi, a)

track_job(res, 1)

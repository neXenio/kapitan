import logging
import multiprocessing as mp
import os
import random
import time

from kapitan_new.logger import monitoring, setup_process_logging

logger = logging.getLogger(__name__)


def compile(args):
    logger.info("compile")

    mp.set_start_method("spawn")
    manager = mp.Manager()

    num_processes = 12  # mp.cpu_count() -1
    logger.ok("ok")
    logger.status("status")

    print("\n" * (num_processes - 2))
    print(f"\033[{num_processes}A")

    shared_data = manager.list([True] * num_processes)
    color = not args.no_color

    with mp.Pool(os.cpu_count() - 1) as pool:
        r = pool.map_async(worker_function, [(i, shared_data, color) for i in range(num_processes)])
        # pool.map_async(worker_function, [(x,shared_running_list) for x in range(3)])

        monitoring_process = mp.Process(target=monitoring, args=(num_processes, shared_data))
        monitoring_process.start()
        r.wait()
        monitoring_process.join()

    print(f"\033[{num_processes}B")

    logger.error("done")


def worker_function(args):
    process_number, shared_data, color = args
    logger = setup_process_logging(process_number + 1, color)

    logger.info(f"Rendering")
    time.sleep(2)

    logger.info(f"Compiling")
    logger.debug("hey")
    time.sleep(2)
    logger.info(f"Done")
    logger.warning("warn")
    logger.ok("OK")

    # Set the shared data index to False when finished
    shared_data[process_number] = False
    return process_number

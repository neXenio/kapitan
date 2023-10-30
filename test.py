import logging
import multiprocessing
import random
import time


def configure_logging(process_name, line_number):
    logger = logging.getLogger(process_name)  # Use a custom logger for each process
    logger.setLevel(logging.INFO)

    # Create a custom handler for console output
    console_handler = ConsoleLoggingHandler(line_number)
    formatter = logging.Formatter(f"{process_name}: %(message)s")
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    return logger


def worker_function(process_name, shared_data, line_number):
    logger = configure_logging(process_name, line_number)

    logger.info(f"Rendering")
    time.sleep(random.random() * 5)
    logger.info(f"Compiling")
    time.sleep(random.random() * 5)
    logger.info(f"Done")

    # Set the shared data index to False when finished
    shared_data[line_number - 1] = False


class ConsoleLoggingHandler(logging.Handler):
    def __init__(self, line_number):
        super().__init__()
        self.line_number = line_number

    def emit(self, record):
        try:
            msg = self.format(record)
            print_in_line(self.line_number, f"\033[30C{msg}", overwrite_line=True)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            self.handleError(record)


def continuous_spin_timer_and_result(num_processes, shared_data):
    spin_chars = "⣾⣽⣻⢿⡿⣟⣯⣷"
    num_chars = len(spin_chars)
    indices = [0] * num_processes
    start_time = time.time()

    while any(shared_data):
        elapsed_time = time.time() - start_time
        timer = f"Time: {elapsed_time:.2f}s"

        for i in range(num_processes):
            if shared_data[i]:
                indices[i] = (indices[i] + 1) % num_chars
                msg = f"{timer} | Loading {spin_chars[indices[i]]} | "
                print_in_line(i + 1, msg, overwrite_line=False)

        time.sleep(0.1)


def print_in_line(line: int, msg: str, overwrite_line: bool = True):
    assert line > 0
    move_down = f"\033[{line-1}B" if not line == 1 else ""
    move_up = f"\033[{line}A"
    carry = "\033[K" if overwrite_line else ""
    print(f"{move_down}{msg}{carry}{move_up}")


if __name__ == "__main__":
    import sys

    num_processes = 4
    manager = multiprocessing.Manager()

    # Create a list of shared data values for each process
    shared_data_list = manager.list([True] * num_processes)

    print("\n" * (num_processes - 2))
    print(f"\033[{num_processes}A")

    with multiprocessing.Pool(processes=num_processes) as pool:
        for i in range(num_processes):
            pool.apply_async(worker_function, args=(f"target-{i + 1}", shared_data_list, i + 1))

        wheel_process = multiprocessing.Process(
            target=continuous_spin_timer_and_result, args=(num_processes, shared_data_list)
        )
        wheel_process.start()

        # Wait for all worker processes to complete
        pool.close()
        pool.join()

        # Signal the wheel process to exit
        wheel_process.join()

    # Add newlines to separate the log output from the command prompt
    print(f"\033[{num_processes}B")

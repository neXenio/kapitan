import sys
import time

count = 3

# def print_in_line(line: int, msg: str, overwrite_line: bool = True):
#     assert line > 0
#     move_down = f"\033[{line-1}B" if not line==1 else ""
#     move_up = f"\033[{line}A"
#     carry = "\033[K" if overwrite_line else ""
#     print(f"{move_down}{msg}{carry}{move_up}")

# print("Instances:", count)
# print("\n" * (count-2))
# print(f"\033[{count}A")
# for i in range(count):
#     time.sleep(1)
#     for j in range(count):
#         msg = "\033[K" + str(i+1) * (count-i)
#         print_in_line(j+1, str(i+1) * (count-i))


# print(f"\033[{count}B")
print(12)
sys.stdout.flush()
time.sleep(1)

print("\033[1A", end="")
sys.stdout.flush()

time.sleep(1)
print("\033[K", end="")
sys.stdout.flush()

time.sleep(1)
print("c", end="")
sys.stdout.flush()


time.sleep(1)
print(2)

import sys
import os

sys.path.append(f"{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}/src")
import compvalueutil


def main():
    test_args = [
        "tests/test001",
        "3",
        "tests/1.txt",
        "0",
        "1",
        "tests/2.txt",
        "0",
        "1",
        "tests/3.txt",
        "0",
        "1",
        "-hist_x_min_max",
        "0",
        "100",
    ]
    my_compvalueutil = compvalueutil.Compvalueutil()
    my_compvalueutil.run(test_args)


if __name__ == "__main__":
    main()

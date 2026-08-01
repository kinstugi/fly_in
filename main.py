from input_processor import InputProcessor
import sys


if __name__ == "__main__":
    args = sys.argv
    args.append('01_linear_path.txt')
    if len(args) != 2:
        print("run code, `python3 main.py <path_to_file>`")
        exit()
    processor = InputProcessor(args[1])

from utils import parse_arguments
from benchmark import run_benchmark


def main() -> None:
    args = parse_arguments()
    if args.benchmark:
        run_benchmark(args.benchmark)
    elif args.plot:
        print("plot")


if __name__ == "__main__":
    main()

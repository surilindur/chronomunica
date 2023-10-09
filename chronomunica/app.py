from utils import parse_arguments
from benchmark import Benchmark


if __name__ == "__main__":
    args = parse_arguments()
    if args.benchmark:
        benchmark = Benchmark(args.benchmark)
        benchmark.execute()
    elif args.plot:
        print("plot")

from utils import parse_arguments
from experiment import Experiment


if __name__ == "__main__":
    args = parse_arguments()
    if args.experiment:
        experiment = Experiment(args.experiment)
        experiment.execute()
    elif args.plot:
        print("plot")

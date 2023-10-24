from runner.utils import parse_arguments
from runner.runner import ExperimentRunner
from experiment.experiment import Experiment

if __name__ == "__main__":
    args = parse_arguments()
    if args.experiment:
        runner = ExperimentRunner(manifest=args.experiment)
        runner.execute()
    elif args.create:
        experiment = Experiment(path=args.create, create=True)
    # elif args.plot:
    #    plot_results(args.plot)

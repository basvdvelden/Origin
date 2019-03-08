from origin.origin import Origin
import settings
from datetime import datetime


def measure_time(func, args=False, num_runs=1000):
    """
    Returns runtime of func executed num_runs times in seconds.
    :param func: function to measure
    :param args: given function's arguments
    :param num_runs: default is 1000
    :type func: function
    :type args: iterable
    :type num_runs: int
    """
    before = datetime.now()
    for n in range(num_runs):
        if args:
            func(*args)
        else:
            func()
    after = datetime.now()
    delta = after - before
    return delta.total_seconds()


def dynamic_save(origin):
    origin.save_walk(settings.walked_nodes)
    origin.train()


def main(load=True, p_runtime=True, sync=True, n=999999999999):
    """
    Creates game tree root and trains for n rounds.
    :param load: loads database to tree if true
    :param p_runtime: prints runtime per round if True
    :param sync: set True for saving progress to database
    :param n: amount of training rounds
    :type load: bool
    :type p_runtime: bool
    :type sync: bool
    :type n: int
    """

    origin = Origin()
    if load:
        origin.load()

    if sync and p_runtime:
        origin.train()
        run_times = []
        for rnd in range(n):
            run_times.append(measure_time(dynamic_save, args=(origin, ), num_runs=1))
            print(rnd, sum(run_times) / len(run_times))

    elif sync:
        origin.train()
        for rnd in range(n):
            dynamic_save(origin)
    else:
        for rnd in range(n):
            origin.train()


if __name__ == '__main__':
    main()

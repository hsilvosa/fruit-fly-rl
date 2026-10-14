"""Profile the spectator viewer offscreen; prints the heaviest functions per call path."""
import argparse, cProfile, pstats, sys, time
from fly_rl.cli import main

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--top", type=int, default=25);parser.add_argument("--sort", default="cumulative")
    parser.add_argument('rest', nargs=argparse.REMAINDER)
    options = parser.parse_args()
    sys.argv = ['fly_rl'] + options.rest
    profiler = cProfile.Profile()
    start = time.perf_counter()
    profiler.enable()
    try:
        main()
    except SystemExit:
        pass
    profiler.disable()
    print(f'wall seconds: {time.perf_counter() - start:.1f}')
    pstats.Stats(profiler).sort_stats(options.sort).print_stats(options.top)

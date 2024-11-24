import argparse

ENGINE_PATH = "/usr/games/stockfish"
ENGINE_MAX_THREADS = 16
MAX_CT_DIFF = 40

def parse_cmd_arguments():
    global ENGINE_PATH, ENGINE_MAX_THREADS, MAX_CT_DIFF
    parser = argparse.ArgumentParser(prog='ChessTrainer',
                                     description='Learn and train your chess openings')
    parser.add_argument('--engine-path',
                        help='Path to your engine',
                        default=ENGINE_PATH)
    parser.add_argument('--engine-max-threads',
                        help='Maximum number of threads used by the engine',
                        type=int, default=ENGINE_MAX_THREADS)
    parser.add_argument('--max-ct-diff',
                        help='Maximum CT (CentiPoints) diff allowed',
                        type=int, default=MAX_CT_DIFF)

    config = parser.parse_args()
    ENGINE_PATH = config.engine_path
    ENGINE_MAX_THREADS = config.engine_max_threads
    MAX_CT_DIFF = config.max_ct_diff

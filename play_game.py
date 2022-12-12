import argparse

from create_game import load_game

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Start creating the game',
    )

    parser.add_argument('file_path', type=str, help='path to game file (new or continue')
    args = parser.parse_args()

    game = load_game(args.file_path)
    game.play()


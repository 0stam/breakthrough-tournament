import sys

from src.player_process.docker_process import DockerProcess
from src.game.game import Game


def main():
    first_process = DockerProcess("roman_skiba", "player1")
    second_process = DockerProcess("roman_skiba", "player2")

    try:
        game = Game(
            board_size_x=8,
            board_size_y=8,
            first_process=first_process,
            second_process=second_process,
            t_process_preparation=10.0,
            t_init=1.0,
            t_info_parsing=0.5,
            t_move=1.0
        )

        results = game.run()

        print(results)
    except Exception as e:
        print(f"Error during game execution: {e}", file=sys.stderr)
    finally:
        first_process.cleanup()
        second_process.cleanup()


if __name__ == "__main__":
    main()
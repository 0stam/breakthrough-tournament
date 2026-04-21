import sys

from src.game.game import Game


def main():
    game = Game(
        board_size_x=3,
        board_size_y=11,
        first_args=["sh", "-c", "cd /home/rs/pwr/breakthrough-ai && exec .venv/bin/python -m src.main"],
        second_args=["sh", "-c", "cd /home/rs/pwr/breakthrough-ai && exec .venv/bin/python -m src.main"],
        t_init=1.0,
        t_info_parsing=0.5,
        t_move=1
    )

    results = game.run()

    print(results)


if __name__ == "__main__":
    main()
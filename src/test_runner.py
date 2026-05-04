import sys

from src.game.game import Game


def main():
    game = Game(
        board_size_x=8,
        board_size_y=8,
        first_args=["sh", "-c", "cd /home/rs/pwr/breakthrough-ai && exec .venv/bin/python -O -m src.main --depth 4 --disable-free-lines "],
        second_args=["sh", "-c", "cd /home/rs/pwr/breakthrough-ai && exec .venv/bin/python -O -m src.main --depth 2 --disable-free-lines"],
        t_init=1.0,
        t_info_parsing=0.5,
        t_move=15
    )

    results = game.run()

    print(results)


if __name__ == "__main__":
    main()
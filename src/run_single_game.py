import sys

from src.player_process.docker_process import DockerProcess
# from src.player_process.player_process import PlayerProcess
from src.game.game import Game


def main():
    cpu_limit = "3"
    memory_limit = "8g"

    docker_image_name = "roman_skiba"

    first_process = DockerProcess(
        image_name=docker_image_name,
        memory_limit=memory_limit,
        cpu_limit=cpu_limit,
        container_name="player1"
    )
    second_process = DockerProcess(
        image_name=docker_image_name,
        memory_limit=memory_limit,
        cpu_limit=cpu_limit,
        container_name="player2"
    )

    # For debugging, local processes can be used. Remember to provide correct paths
    # first_process = PlayerProcess(["/path/to/interpreter/.venv/bin/python", "/path/to/script/with/algorithm.py"])
    # second_process = PlayerProcess(["/path/to/interpreter/.venv/bin/python", "/path/to/script/with/algorithm.py"])

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
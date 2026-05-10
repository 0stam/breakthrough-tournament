# Breakthrough AI tournament runner

For player instructions, see: `PLAYER_INSTRUCTIONS.md`

## Installation

Make sure you have Pipenv installed:

```bash
pip install pipenv
```

Then run:

```bash
pipenv install
```

## Running

Change Docker image name in `src/run_single_game.py`

Run:

```bash
pipenv run single_game
```

## Debugging

For debugging purposes local processes can be used. To achievie that, uncomment related lines in `src/run_single_game.py`
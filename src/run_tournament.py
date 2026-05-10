from src.tournament.tournament import Tournament

def main():
    tournament = Tournament(num_of_rounds=3)
    tournament.load_players()
    tournament.run_tournament()
    tournament.print_standings()

if __name__ == "__main__":
    main()

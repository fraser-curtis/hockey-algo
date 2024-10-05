import sqlite3 as lite
import random
import pprint
from timeit import default_timer as timer

class Player:
    def __init__(self, name, cost, position, points, dollarcost, roi):
        self.name = name
        self.cost = cost
        self.position = position
        self.points = points
        self.roi = roi

def get_all_players():
    con = lite.connect('test.db')
    players_by_position = {'F': [], 'D': [], 'C': []}

    with con:
        con.row_factory = lite.Row
        cur = con.cursor()
        # cur.execute("SELECT * FROM players WHERE roi > 0.000015556")
        cur.execute("SELECT * FROM players")
        data = cur.fetchall()
        
        # Sort and categorize players by position
        for r in data:
            p = Player(*r)
            players_by_position[p.position].append(p)
        
        # Sort players in each position by ROI, descending
        for pos in players_by_position:
            players_by_position[pos].sort(key=lambda x: (-x.roi, x.cost))

    return players_by_position

def get_random_team(players, budget=35000000, f=8, d=6, c=4, randomness_factor=0.2):
    """Randomly selects a team with some perturbation for diversity."""
    money_team = []
    budget_remaining = budget
    positions_needed = {'F': f, 'D': d, 'C': c}

    # Select players with some randomness for diversity
    for pos, num_needed in positions_needed.items():
        for _ in range(num_needed):
            # Introduce randomness: Choose a random player with a given probability
            if random.random() < randomness_factor:
                candidates = [p for p in players[pos] if p.cost <= budget_remaining and p not in money_team]
                if candidates:
                    player = random.choice(candidates)
                    money_team.append(player)
                    budget_remaining -= player.cost
            else:
                # Otherwise, pick the best available player as per greedy strategy
                for player in players[pos]:
                    if player.cost <= budget_remaining and player not in money_team:
                        money_team.append(player)
                        budget_remaining -= player.cost
                        break  # Move on to the next player for the same position

    if len(money_team) == (f + d + c):
        return money_team
    return None

def total_points(team):
    return sum(player.points for player in team)

def total_cost(team):
    return sum(player.cost for player in team)

def get_better_player(players, current_player):
    # Get better players that cost the same or less
    better_players = [p for p in players[current_player.position] if p.cost <= current_player.cost and p.points > current_player.points]
    return sorted(better_players, key=lambda x: x.points, reverse=True)

def get_better_team(team, players):
    improved_team = team[:]
    for idx, current_player in enumerate(improved_team):
        better_players = get_better_player(players, current_player)
        if better_players:
            for new_player in better_players:
                if new_player not in improved_team:
                    improved_team[idx] = new_player
                    break
    return improved_team

# Caching dictionary for already attempted team improvements
player_cache = {}

def iterative_improvement(team, players):
    team_key = tuple(sorted(player.name for player in team))  # Unique team key for caching
    if team_key in player_cache:
        return player_cache[team_key]

    new_team = get_better_team(team, players)
    if total_points(new_team) > total_points(team):
        player_cache[team_key] = new_team
        return new_team
    else:
        player_cache[team_key] = team
        return team

def print_team(team):
    total_points = sum(player.points for player in team)
    for player in team:
        pprint.pprint(f"{player.name} {player.position} {player.points} {player.cost}")
    pprint.pprint(f"Total Points: {total_points}")
    pprint.pprint(f"Total Cost: {total_cost(team)}")

# Main execution
if __name__ == "__main__":
    players_by_position = get_all_players()
    top_teams = []  # List to store top N teams
    max_teams_to_store = 5  # Adjust N to the number of top teams you want to store
    seen_teams = set()  # To track unique teams

    start = timer()

    for _ in range(50000):
        new_team = get_random_team(players_by_position, randomness_factor=0.2)  # Introduce randomness
        if new_team:
            improved_team = iterative_improvement(new_team, players_by_position)
            team_key = tuple(sorted(player.name for player in improved_team))  # Unique key for the team
            
            if team_key not in seen_teams:
                seen_teams.add(team_key)
                team_points = total_points(improved_team)

                # Add team to top_teams and keep it sorted by points
                top_teams.append((team_points, improved_team))
                top_teams = sorted(top_teams, key=lambda x: x[0], reverse=True)

                # Keep only the top N teams
                if len(top_teams) > max_teams_to_store:
                    top_teams.pop()

    end = timer()

    # Display the top N teams
    print(f"Top {max_teams_to_store} Teams:")
    for i, (points, team) in enumerate(top_teams, start=1):
        print(f"\nTeam {i}:")
        print_team(team)

    print(f"Total Time: {end - start:.2f} seconds")

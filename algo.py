import winsound
import sqlite3 as lite
import random
import pprint
from timeit import default_timer as timer


class player(object):
    def __init__(self, name, cost, position, points, dollarcost, roi):
        self.name = name
        self.cost = cost
        self.position = position
        self.points = points
        self.dollarcost = dollarcost
        self.roi = roi


def get_random_team(players, budget=35000000, f=8, d=6, c=4):
    money_team = []
    budget = budget
    positions = {'F': f, 'D': d, 'C': c}

    # while positions['F'] > 0 and positions['C'] > 0 and positions['D'] > 0:
    while len(money_team) < (f+d+c):  # and budget > 1000000:
        player = get_random_player(budget, players)

        if not player:
            return

        if player not in money_team and positions[player.position] > 0:
            money_team.append(player)
            budget = budget - player.cost
            positions[player.position] = positions[player.position] - 1

    return money_team


def get_random_player(budget, players):
    playerData = list(filter(lambda x: x.cost <= budget, players))

    length = len(playerData)
    if length < 1:
        return

    index = random.randint(0, length-1)

    try:
        return playerData[index]
    except:
        print(budget)
        print(index)
        print(len(playerData))
        return


def get_all_players():
    con = lite.connect('test.db')
    players = []

    with con:
        con.row_factory = lite.Row
        cur = con.cursor()
        # cur.execute("select * from players order by points desc limit 10")
        cur.execute("select * from players where roi > 0.000015556")

        data = cur.fetchall()

        for r in data:
            players.append(player(*r))

        return players


def print_team(team):
    totalPoints = 0
    for player in team:
        pprint.pprint(player.name + " " +
                      player.position + " " + str(player.points) + " " + str(player.cost))
        totalPoints += player.points

    pprint.pprint(totalPoints)


def total_points(team):
    totalPoints = 0
    for player in team:
        totalPoints += player.points

    return totalPoints


def total_cost(team):
    cost = 0
    for player in team:
        cost += player.cost

    return cost


def get_better_player(players, p):
    playerData = list(filter(
        lambda x: x.cost <= p.cost and x.position == p.position, players))

    # can't find any better ROI for this player
    if len(playerData) < 1:
        return

    playerData = sorted(playerData, key=lambda x: x.points, reverse=True)

    return playerData


def get_better_team(team):
    pCount = 0
    newTeam = team
    for p in newTeam:
        newPlayers = get_better_player(players, p)

        for newPlayer in newPlayers:
            if newPlayer not in newTeam and newPlayer.points > p.points:
                # pprint.pprint("new: " + newPlayer.name + " " +
                #               newPlayer.position + " " + str(newPlayer.points))
                # pprint.pprint("old: " + p.name + " " +
                #               p.position + " " + str(p.points))

                newTeam[pCount] = newPlayer
                break

        pCount += 1

    return newTeam


count = 0
masterTeam = []
totalPoints = 0

players = get_all_players()

start = timer()
while count < 10000:  # or totalPoints > 700:
    count += 1

    newTeam = get_random_team(players)

    if newTeam:
        newTeam = get_better_team(newTeam)
        tp = total_points(newTeam)

        if tp > totalPoints:
            totalPoints = tp
            masterTeam = newTeam
            print(total_points(masterTeam))
            print_team(masterTeam)


end = timer()

print_team(masterTeam)
print(total_cost(masterTeam))
print(end - start)

masterTeam = get_better_team(masterTeam)
masterTeam = sorted(masterTeam, key=lambda x: x.position, reverse=True)
print_team(masterTeam)
print(total_cost(masterTeam))


frequency = 2500  # Set Frequency To 2500 Hertz
duration = 700  # Set Duration To 1000 ms == 1 second
# winsound.Beep(frequency, duration)

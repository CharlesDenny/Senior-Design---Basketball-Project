import json
import os
import csv
import datetime
import sys
import code

import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from matplotlib.patches import Rectangle, Circle, Arc

def dist(a, b):
    return ((abs(a[0] - b[0]) ** 2 + abs(a[1] - b[1]) ** 2) ** (1 / 2))


class player:
    def __init__(self, p, teamid, home):
        self.position = p['position']  # str
        self.playerid = str(p['playerid'])  # str
        self.jersey = p['jersey']  # string
        self.lastname = p['lastname']  # str
        self.firstname = p['firstname']  # str
        self.teamid = teamid  # str
        self.home = home
        self.pos = None

    def name(self): return self.firstname + ' ' + self.lastname

    def __eq__(self, other):
        return self.playerid == other.playerid

    def __hash__(self):
        return hash(self.playerid)


    def get_X_Coord(self, game, current_quarter, start_t, end_t): # Returns only the X-Coord, ideal for plotting
        theList = []
        momentList = game.moments
        momentCount = 0
        for moment in momentList:
            quarter = momentList[momentCount].period
            gameClock = momentList[momentCount].gameclock
            if quarter == current_quarter:
                if start_t >= gameClock >= end_t:
                    playerList = momentList[momentCount].players
                    playerCount = 0
                    for player in playerList:
                        if playerList[playerCount]['playerid'] == self.playerid:
                            x = g1.moments[momentCount].players[playerCount]['pos'][0]
                            theList.append(x)
                        playerCount += 1
            momentCount += 1
        return theList

    def get_Y_Coord(self, game, current_quarter, start_t, end_t): # Returns only the Y-Coord, ideal for plotting
        theList = []
        momentList = game.moments
        momentCount = 0
        for moment in momentList:
            quarter = momentList[momentCount].period
            gameClock = momentList[momentCount].gameclock
            if quarter == current_quarter:
                if start_t >= gameClock >= end_t:
                    playerList = momentList[momentCount].players
                    playerCount = 0
                    for player in playerList:
                        if playerList[playerCount]['playerid'] == self.playerid:
                            y = g1.moments[momentCount].players[playerCount]['pos'][1]
                            theList.append(y)
                        playerCount += 1
            momentCount += 1
        return theList


    def get_coordinates(self, game, current_quarter, start_t, end_t):
        d = {}
        theList = []

        momentlist = g1.moments
        momentCount = 0
        for moment in momentlist:
            quarter = momentlist[momentCount].period  # Get Quarter
            gameClock = momentlist[momentCount].gameclock  # Get Game Clock
            if quarter == current_quarter:
                if start_t >= gameClock >= end_t:
                    playerlist = momentlist[momentCount].players  # Initialize Players List
                    playerCount = 0
                    for player in playerlist:
                        if playerlist[playerCount]['playerid'] == self.playerid:
                            x = g1.moments[momentCount].players[playerCount]['pos'][0]  # Record Coordinates
                            y = g1.moments[momentCount].players[playerCount]['pos'][1]
                            d = {"quarter": current_quarter, "gameclock": gameClock, "x": x, "y": y}
                            theList.append(d)
                        playerCount += 1
            momentCount += 1
        return theList


class team:
    def __init__(self, t, home):
        self.teamid = str(t['teamid'])
        self.teamname = t['name']
        self.teamname_abbrev = t['abbreviation']
        self.players = []
        self.home = home  # home: False if visitor

        for p in t['players']:
            self.players.append(player(p, self.teamid, home))


class event:
    def __init__(self, line):
        self.eventid = int(line['eventid'])
        self.period = int(line['period'])
        gc = datetime.datetime.strptime(line['clock'], '%M:%S.%f').time()
        self.gameclock = gc.minute * 60 + gc.second
        self.text = line['text']
        self.visitor = int(line['visitor'])
        self.home = int(line['home'])
        self.possession = None

        if line['poss'] == 'True':
            self.possession = True
        elif line['poss'] == 'False':
            self.possession = False


class game:
    def __init__(self, gameid, pbp=True, moments=False):
        self.gameid = gameid
        self.gamedate = None
        self.visitor = None
        self.home = None
        self.players = {}
        self.moments = []
        self.events = []

        if moments:
            with open("C:\\Users\\kff50\\Documents\\Senior Year\\CMPSC 484\\Basketball Project\\nba_sportvu\\" + str(gameid) + ".json") as f:
            #with open('0021500423.json') as f:
                jsonf = json.load(f)
                self.gamedate = datetime.datetime.strptime(jsonf['gamedate'], '%Y-%m-%d')
                self.visitor = team(jsonf['events'][0]['visitor'], False)
                self.home = team(jsonf['events'][0]['home'], True)

                for player in self.visitor.players:
                    self.players[player.playerid] = player
                for player in self.home.players:
                    self.players[player.playerid] = player

                for e in jsonf['events']:
                    for m in e['moments']:
                        self.moments.append(moment(self, m))
                # magic sort
                self.moments = sorted(list(set(self.moments)), reverse=True)

        if pbp:
            with open("C:\\Users\\kff50\\Documents\\Senior Year\\CMPSC 484\\Basketball Project\\pbp\\2015.12.23.BOS.at.CHO.0021500423.csv") as f:
            #with open('2015.12.23.BOS.at.CHO.0021500423.csv') as f:
                reader = csv.DictReader(f)
                for line in reader:
                    self.events.append(event(line))

    def __str__(self):
        return '{} on {}: {:3} {} at {} {:3}'.format(self.gameid, self.gamedate.date(), self.events[-1].visitor,
                                                     self.visitor.teamname_abbrev, self.home.teamname_abbrev,
                                                     self.events[-1].home)

    def win(self):
        '''
        Returns true if home team won the game
        '''
        return bool(self.events[-1].home - self.events[-1].visitor)

    def tipwinner(self, exceptions=False):
        '''
        Returns true if home team won the opening tip
        '''

        if self.events[0].possession != None:
            if exceptions:
                return self.events[0].possession
            return None
        else:
            if 'Jump ball' in self.events[1].text:

                return self.events[1].possession
            else:
                assert self.events[1].text == 'Violation by Team (jump ball)'
                if exceptions:
                    return self.events[2].possession
                return None

    def getevent(self, period, gameclock):
        '''
        Returns the event given a period and game clock
        '''
        prev_event = self.events[0]
        for event in self.events[1:]:
            if event.period == period and event.gameclock <= gameclock:
                return prev_event
            else:
                prev_event = event


class moment:
    def __init__(self, game_parent, m):
        self.game = game_parent
        self.period = m[0]  # int
        self.timestamp = m[1]
        self.time = datetime.datetime.fromtimestamp(m[1] / 1000)  # datetime
        self.gameclock = m[2]  # float
        self.shotclock = m[3]  # float
        self.players = []
        self.ball = None  # there may be 9, 10, or 11 points, meaning missing players/ball

        for point in m[5]:
            if point[1] == -1:
                self.ball = (point[2], point[3], point[4])
            else:
                self.players.append({'playerid': str(point[1]), 'pos': (point[2], point[3])})

                # for playerid, playerobj in self.game.players.items():
                # if playerid == str(point[1]):
                # playerobj.pos=(point[2], point[3])
                # self.players.append(playerobj)
                # break

        for i in range(len(self.players) - 10):
            self.players.append(None)

    def __eq__(self, other):
        return self.time == other.time

    def __lt__(self, other):
        return self.time > other.time

    def __hash__(self):
        return hash(self.timestamp)

    def getoffensiveteam(self):
        e = self.event()
        poss_bool = e.possession
        if poss_bool:
            return self.game.home
        elif not poss_bool:
            return self.game.visitor
        else:
            return None

    def getbhbd(self):
        if not self.ball: return None

        closest = {'o': {'player': None, 'dist': 1000}, 'd': {'player': None, 'dist': 1000}}
        ot = self.getoffensiveteam()
        if not ot: return closest

        for p in self.players:
            if not p: continue
            i = 'o' if self.game.players[p['playerid']].teamid == ot.teamid else 'd'
            temp = dist((self.ball[0], self.ball[1]), p['pos'])
            if temp < closest[i]['dist']:
                closest[i]['player'] = self.game.players[p['playerid']]
                closest[i]['dist'] = temp
        return closest['o']['player'], closest['d']['player']

    # def getballhandler(self):
    # if not self.ball: return None

    # closest=None
    # closest_dist= 1000
    # ot=self.getoffensiveteam()
    # if not ot: return None

    # for p in self.players:
    # if not p: continue
    # i = 'o' if p['teamid'] == ot.teamid else 'd'
    # temp = dist((self.ball[0], self.ball[1]), p['pos'])
    # if temp < closest[i]['dist']:
    # closest[i]['player'] = p
    # closest[i]['dist'] = temp
    # return closest['o']['player'], closest['d']['player']

    # def getballdefender(self):
    # ballhandler = self.getballhandler()
    # if not ballhandler: return None

    # closest=None
    # closest_dist= 1000
    # ot=self.getoffensiveteam()
    # if not ot: return None

    # for p in [q for q in self.players if self.game.players[q['playerid']].teamid != ot.teamid]:
    # if not p: continue
    # if p['teamid'] == ot.teamid: continue
    # temp = dist(ballhandler.pos, p['pos'])
    # if temp < closest_dist:
    # closest=p
    # closest_dist=temp
    # return closest

    def event(self):
        return self.game.getevent(self.period, self.gameclock)




def moment_details(game, index):
    m1 = game.moments[index]
    print("Game: " + str(m1.game))
    print("Period: " + str(m1.period))
    print("Time remaining: " + str(m1.time))
    print("Game Clock: " + str(m1.gameclock))
    print("Shot Clock: " + str(m1.shotclock))
    print("\n")
    print("Players Involved: ")
    print(m1.players)


def h_player_details(game, index):
    p1 = (game.home.players[index])
    print("Name: " + p1.name())
    print("Player ID: " + str(p1.playerid))
    print("Jersey: " + str(p1.jersey))
    print("Position: " + p1.position)
    print("\n")

def h_team_details(game):
    t1 = game.home
    print("Team Id: " + str(t1.teamid))
    print("Team Name: " + t1.teamname)
    print("Abbreviation: " + t1.teamname_abbrev)
    print("\n")
    print("Team Roster: ")
    for p1 in t1.players:
        print("Name: " + p1.name())
        print("Player ID: " + p1.playerid)
        print("Jersey: " + p1.jersey)
        print("Position: " + p1.position)
        print("\n")


def a_player_details(game, index):
    p1 = (game.visitor.players[index])
    print("Name: " + p1.name())
    print("Player ID: " + p1.playerid)
    print("Jersey: " + p1.jersey)
    print("Position: " + p1.position)
    print("\n")


def a_team_details(game):
    t1 = game.visitor
    print("Team Id: " + str(t1.teamid))
    print("Team Name: " + t1.teamname)
    print("Abbreviation: " + t1.teamname_abbrev)
    print("\n")
    print("Team Roster: ")
    for p1 in t1.players:
        print("Name: " + p1.name())
        print("Player ID: " + p1.playerid)
        print("Jersey: " + p1.jersey)
        print("Position: " + p1.position)
        print("\n")

def event_details(game, index):
    e1 = game.events[index]
    print("Event ID: " + str(e1.eventid))
    print("Period: " + str(e1.period))
    print("Time remaining: " + str(e1.gameclock))
    print("Text: " + str(e1.text))
    print("Posession: " + str(e1.possession))
    print("Visitor: " + str(e1.visitor))
    print("Home: " + str(e1.home))
    print("\n")


def player_details(p1):
    print("Name: " + p1.name())
    print("Player ID: " + p1.playerid)
    print("Jersey: " + p1.jersey)
    print("Position: " + p1.position)
    print("\n")


def get_All_Events(game):
    for e1 in game.events:
        print("Event ID: " + str(e1.eventid))
        print("Period: " + str(e1.period))
        print("Time remaining: " + str(e1.gameclock))
        print("Text: " + str(e1.text))
        print("Posession: " + str(e1.possession))
        print("Visitor: " + str(e1.visitor))
        print("Home: " + str(e1.home))
        print("\n")


def convert(seconds):
    t = seconds
    day = t // 86400
    hour = (t - (day * 86400)) // 3600
    minit = (t - ((day * 86400) + (hour * 3600))) // 60
    seconds = t - ((day * 86400) + (hour * 3600) + (minit * 60))

    print("Minutes: " + '%d' % minit)
    print("Seconds: " + '%d' % seconds)


def get_ballcoordinates(game, current_quarter, start_t, end_t):
    d = {}
    theList = []

    momentlist = g1.moments
    momentCount = 0

    for moment in momentlist:
        quarter = momentlist[momentCount].period  # Get Quarter
        gameClock = momentlist[momentCount].gameclock  # Get Game Clock
        if quarter == current_quarter:
            if start_t >= gameClock >= end_t:
                x = momentlist[momentCount].ball[0] # Get Ball Coordinates
                y = momentlist[momentCount].ball[1]
                z = momentlist[momentCount].ball[2]
                d = {"quarter": quarter, "gameclock": gameClock, "x": x, "y": y, "z": z}
                theList.append(d)
        momentCount += 1
    return theList


def get_All_Player_Coordinates(g1, player_index, home, visitor):
    if home == True and visitor == False:
        p1 = g1.home.players[player_index]
        print(p1.name() + "'s X and Y Coordinates throughout the entire game: ")
        print("1st Quarter Coordinates: " + str(p1.get_coordinates(g1, 1, 720, 0)))
        print("2nd Quarter Coordinates: " + str(p1.get_coordinates(g1, 2, 720, 0)))
        print("3rd Quarter Coordinates: " + str(p1.get_coordinates(g1, 3, 720, 0)))
        print("4th Quarter Coordinates: " + str(p1.get_coordinates(g1, 4, 720, 0)))
    elif visitor == True and home == False:
        p1 = g1.visitor.players[player_index]
        print(p1.name() + "'s X and Y Coordinates throughout the entire game: ")
        print("1st Quarter Coordinates: " + str(p1.get_coordinates(g1, 1, 720, 0)))
        print("2nd Quarter Coordinates: " + str(p1.get_coordinates(g1, 2, 720, 0)))
        print("3rd Quarter Coordinates: " + str(p1.get_coordinates(g1, 3, 720, 0)))
        print("4th Quarter Coordinates: " + str(p1.get_coordinates(g1, 4, 720, 0)))
    else:
        print("Invalid combination of home and visitor, please re-enter")


def get_All_X_Coordinates(g1, player_Index, home, visitor):
    if home == True and visitor == False:
        p1 = g1.home.players[player_Index]
        print(p1.name() + "'s X-Coordinates throughout the entire game: ")
        print("1st Quarter X Coordinates: " + str(p1.get_X_Coord(g1, 1, 720, 0)))
        print("2nd Quarter X Coordinates: " + str(p1.get_X_Coord(g1, 2, 720, 0)))
        print("3rd Quarter X Coordinates: " + str(p1.get_X_Coord(g1, 3, 720, 0)))
        print("4th Quarter X Coordinates: " + str(p1.get_X_Coord(g1, 4, 720, 0)))

    elif visitor == True and home == False:
        p1 = g1.visitor.players[player_Index]
        print(p1.name() + "'s X-Coordinates throughout the entire game: ")
        print("1st Quarter Coordinates: " + str(p1.get_X_Coord(g1, 1, 720, 0)))
        print("2nd Quarter Coordinates: " + str(p1.get_X_Coord(g1, 2, 720, 0)))
        print("3rd Quarter Coordinates: " + str(p1.get_X_Coord(g1, 3, 720, 0)))
        print("4th Quarter Coordinates: " + str(p1.get_X_Coord(g1, 4, 720, 0)))
    else:
        print("Invalid combination of home and visitor, please re-enter")


def get_All_Y_Coordinates(g1, player_Index, home, visitor):
    if home == True and visitor == False:
        p1 = g1.home.players[player_Index]
        print(p1.name() + "'s Y-Coordinates throughout the entire game: ")
        print("1st Quarter Y Coordinates: " + str(p1.get_Y_Coord(g1, 1, 720, 0)))
        print("2nd Quarter Y Coordinates: " + str(p1.get_Y_Coord(g1, 2, 720, 0)))
        print("3rd Quarter Y Coordinates: " + str(p1.get_Y_Coord(g1, 3, 720, 0)))
        print("4th Quarter Y Coordinates: " + str(p1.get_Y_Coord(g1, 4, 720, 0)))

    elif visitor == True and home == False:
        p1 = g1.visitor.players[player_Index]
        print(p1.name() + "'s Y-Coordinates throughout the entire game: ")
        print("1st Quarter Y Coordinates: " + str(p1.get_Y_Coord(g1, 1, 720, 0)))
        print("2nd Quarter Y Coordinates: " + str(p1.get_Y_Coord(g1, 2, 720, 0)))
        print("3rd Quarter Y Coordinates: " + str(p1.get_Y_Coord(g1, 3, 720, 0)))
        print("4th Quarter Y Coordinates: " + str(p1.get_Y_Coord(g1, 4, 720, 0)))
    else:
        print("Invalid combination of home and visitor, please re-enter")


def draw_court(ax=None, color='black', lw=2, outer_lines=False):
    # If an axes object isn't provided to plot onto, just get current one
    if ax is None:
        ax = plt.gca()

    # Create the various parts of an NBA basketball court

    # Create the basketball hoop
    # Diameter of a hoop is 18" so it has a radius of 9", which is a value
    # 7.5 in our coordinate system
    hoop = Circle((0, 0), radius=7.5, linewidth=lw, color=color, fill=False)

    # Create backboard
    backboard = Rectangle((-30, -7.5), 60, -1, linewidth=lw, color=color)

    # The paint
    # Create the outer box 0f the paint, width=16ft, height=19ft
    outer_box = Rectangle((-80, -47.5), 160, 190, linewidth=lw, color=color,
                          fill=False)
    # Create the inner box of the paint, widt=12ft, height=19ft
    inner_box = Rectangle((-60, -47.5), 120, 190, linewidth=lw, color=color,
                          fill=False)

    # Create free throw top arc
    top_free_throw = Arc((0, 142.5), 120, 120, theta1=0, theta2=180,
                         linewidth=lw, color=color, fill=False)
    # Create free throw bottom arc
    bottom_free_throw = Arc((0, 142.5), 120, 120, theta1=180, theta2=0,
                            linewidth=lw, color=color, linestyle='dashed')
    # Restricted Zone, it is an arc with 4ft radius from center of the hoop
    restricted = Arc((0, 0), 80, 80, theta1=0, theta2=180, linewidth=lw,
                     color=color)

    # Three point line
    # Create the side 3pt lines, they are 14ft long before they begin to arc
    corner_three_a = Rectangle((-220, -47.5), 0, 140, linewidth=lw,
                               color=color)
    corner_three_b = Rectangle((220, -47.5), 0, 140, linewidth=lw, color=color)
    # 3pt arc - center of arc will be the hoop, arc is 23'9" away from hoop
    # I just played around with the theta values until they lined up with the
    # threes
    three_arc = Arc((0, 0), 475, 475, theta1=22, theta2=158, linewidth=lw,
                    color=color)

    # Center Court
    center_outer_arc = Arc((0, 422.5), 120, 120, theta1=180, theta2=0,
                           linewidth=lw, color=color)
    center_inner_arc = Arc((0, 422.5), 40, 40, theta1=180, theta2=0,
                           linewidth=lw, color=color)

    # List of the court elements to be plotted onto the axes
    court_elements = [hoop, backboard, outer_box, inner_box, top_free_throw,
                      bottom_free_throw, restricted, corner_three_a,
                      corner_three_b, three_arc, center_outer_arc,
                      center_inner_arc]

    if outer_lines:
        # Draw the half court line, baseline and side out bound lines
        outer_lines = Rectangle((-250, -47.5), 500, 470, linewidth=lw,
                                color=color, fill=False)
        court_elements.append(outer_lines)

    # Add the court elements onto the axes
    for element in court_elements:
        ax.add_patch(element)

    return ax


'''
g1 = game("0021500423", True, True)
print("MOMENT INFORMATION:")
print(g1.moments[0].game)
print(g1.moments[0].period)
print(g1.moments[0].timestamp)
print(g1.moments[0].time)
print(g1.moments[0].gameclock)
print(g1.moments[0].shotclock)
print(g1.moments[0].players)
print(g1.moments[0].players[0]['playerid'])
print(g1.moments[0].players[0]['pos'])
print(g1.moments[0].players[0]['pos'][0])
print(g1.moments[0].players[0]['pos'][1])
print(g1.moments[0].ball)
print(g1.gameid)
print(g1.gamedate)
print(g1.visitor.teamname)
print(g1.home.teamname)
'''

def main(argv):
    if len(argv) != 1:
        print('usage: python game.py gameid')
        return
    g = game(argv[0])
    code.interact(local=locals())
    return


if __name__ == "__main__":
    main(sys.argv[1:])
    g1 = game("0021500423", True, True)
    print("Ball Coordinates:")
    print((get_ballcoordinates(g1, 1, 720, 500)), "\n")     # Ball Coordinates

    """
    p1 = g1.home.players[5]                         # Kemba Walker
    print(p1.firstname)
    print(p1.lastname)
    print(p1.playerid)
    print(p1.jersey)
    print(p1.position)
    print(p1.get_coordinates(g1, 1, 720, 500))

    if len(p1.get_coordinates(g1, 1, 720, 500)) == 0:
        print("An empty list occurs whenever a player is not on the court during the time specified in the get_coordinates function.")

    print("\n")
    

    print(get_All_X_Coordinates(g1, 5, True, False))     # Kemba Walker X-Coordinates throughout entire game
    print(get_All_Y_Coordinates(g1, 5, True, False))      # Kemba Walker Y-Coordinates throughout entire game
    """

    p1 = g1.home.players[5]
    quarter = 1
    start_t = 720
    end_t = 0
    p1_X = p1.get_X_Coord(g1, quarter, start_t, end_t)
    p1_Y = p1.get_Y_Coord(g1, quarter, start_t, end_t)
    print("X-Length: " + str(len(p1_X)))
    print("Y-Length: " + str(len(p1_Y)))


    X_Coord = np.array(p1_X)
    Y_Coord = np.array(p1_Y)
    sns.set_style("white")
    sns.set_color_codes()
    """
    plt.figure(figsize=(12, 11))
    plt.scatter(X_Coord, Y_Coord)
    """
    plt.figure(figsize=(12, 11))
    plt.scatter(X_Coord, Y_Coord)
    draw_court()
    plt.xlim(-250, 250)
    plt.ylim(422.5, -47.5)
    plt.xlabel(p1.name() + ": X-Coordinates")
    plt.ylabel(p1.name() + ": Y-Coordinates")
    plt.suptitle(p1.name() + "'s Coordinates between " + str(start_t) + " - " + str(end_t) + "(Seconds)" + " in the " + str(quarter) + " quarter.")
    plt.show()







    #if len(p1_coord) == 0:
        #print("An empty list occurs whenever a player is not on the court during the time specified in the get_coordinates function.")
import json
import os
import csv
import datetime
import sys
import code


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
            #with open("C:\\Users\\kff50\\Documents\\Senior Year\\CMPSC 484\\Basketball Project\\nba_sportvu\\" + str(gameid) + ".json") as f:
            with open('0021500423.json') as f:
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
            #with open("C:\\Users\\kff50\\Documents\\Senior Year\\CMPSC 484\\Basketball Project\\pbp\\2015.12.23.BOS.at.CHO.0021500423.csv") as f:
            with open('2015.12.23.BOS.at.CHO.0021500423.csv') as f:
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

    def getShots(self):
        keyword1 = "makes"      # Defines Keywords From Play-By-Play Text To Find Shots.
        keyword2 = "misses"
        keyword3 = "shot"

        d = {}          # Initialize The Dictionary and List To Store General Shot Information.
        theList = []

        gameEvents = self.events
        for event in gameEvents:
            momentInfo = event.text
            quarter = event.period
            gameClock = event.gameclock

            if (keyword1 in event.text or keyword2 in event.text) and keyword3 in event.text:           # Look For Keywords To Find Shots.
                shotquarter = event.period
                beginsearch = gameClock + 5         # Begin Searching For The Start Of The Shot Five Seconds Before.
                endsearch = gameClock
                if keyword1 in event.text:
                    outcome = "Made"
                if keyword2 in event.text:
                    outcome = "Missed"
                playerCount = 0
                for players in self.players:            # Loop Through List Of Players To Determine Who Took The Shot.
                    if playerCount > 12:            # Maximum of 13 Players Per Team.
                        break
                    firstLetter = self.home.players[playerCount].firstname[0]           # Compare First Initial And Last Name In PLay-By-Play.
                    firstInitial = firstLetter + "."
                    lastname = self.home.players[playerCount].lastname
                    name = firstInitial + " " + lastname
                    if name in event.text:
                        shooter = self.home.players[playerCount]
                        teamabb = self.home.teamname_abbrev

                    firstLetter = self.visitor.players[playerCount].firstname[0]        # Compare First Initial And Last Name In PLay-By-Play.
                    firstInitial = firstLetter + "."
                    lastname = self.visitor.players[playerCount].lastname
                    name = firstInitial + " " + lastname
                    if name in event.text:
                        shooter = self.visitor.players[playerCount]
                        teamabb = self.visitor.teamname_abbrev
                    playerCount += 1
                playername = shooter.firstname + " " + shooter.lastname
                playerid = shooter.playerid
                d = {"player": playername, "id": playerid, "team": teamabb, "quarter": shotquarter,         # Stores General Shot Information
                     "begin": beginsearch, "end": endsearch, "outcome": outcome}
                theList.append(d)           # Adds Each General Shot Information To The List.

        momentlist = self.moments
        momentCount = 0
        listCount = 0

        shotDict = {}           # Initialize Shot Information Dictionary.
        coordinate = {}         # Initialize Coordinates Dictionary.
        shotCoordinates = []    # Initialize List Of Coordinates For Each Shot.
        theListOfShots = []     # Initialize List Of Shots.

        for entry in theList:           # Loop Through Each Shot Found.
            for m in momentlist:            # Loop Through Each Moment.
                quarter = momentlist[momentCount].period            # Get Quarter
                gameClock = momentlist[momentCount].gameclock           # Get Game Clock
                playername = theList[listCount]["player"]           # Get Shot Information
                playerid = theList[listCount]["id"]
                shotquarter = theList[listCount]["quarter"]
                beginsearch = theList[listCount]["begin"]
                endsearch = theList[listCount]["end"]
                outcome = theList[listCount]["outcome"]
                teamabb = theList[listCount]["team"]
                if quarter == shotquarter:          # Look For Quarter Shot Occurred.
                    if beginsearch >= gameClock >= endsearch:           # Look For Time Shot Occurred.
                        if momentlist[momentCount].ball != None:            # Check To Make Sure The Ball Coordinates Are Not Missing.
                            if momentlist[momentCount].ball[2] >= 10:           # Check To See When Shot Begins (10 = Height Of Rim).
                                x = momentlist[momentCount].ball[0]         # Get Ball Coordinates
                                y = momentlist[momentCount].ball[1]
                                z = momentlist[momentCount].ball[2]
                                coordinate = {"gameclock": gameClock, "x": x, "y": y, "z": z}           # Store Ball Coordinates For That Moment.
                                shotCoordinates.append(coordinate)          # Store Ball Coordinates For That Moment In List.
                momentCount += 1
            shotDict = {"playername": playername, "playerid": playerid, "team": teamabb, "quarter": shotquarter,
                        "time": endsearch, "result": outcome, "coordinates": shotCoordinates}
            theListOfShots.append(shotDict)         # Store All Shot Information In The List.
            shotCoordinates = []            # Resets The Coordinates List For The Next Shot.
            shotDict = {}           # Resets The Shot Information Dictionary For The Next Shot.
            listCount += 1
            momentCount = 0
        return theListOfShots


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
    """
    Trying to display playerid and pos seperately here 
    """







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

    momentlist = game.moments
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
    print(g1.getShots())

    '''
    print("Ball Coordinates:")
    print((get_ballcoordinates(g1, 1, 720, 500)), "\n")     # Ball Coordinates

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

    p1 = g1.home.players[0]                         # Spencer Hawes
    print(p1.firstname)
    print(p1.lastname)
    print(p1.playerid)
    print(p1.jersey)
    print(p1.position)
    print(p1.get_coordinates(g1, 1, 720, 500))

    if len(p1.get_coordinates(g1, 1, 720, 500)) == 0:
        print("An empty list occurs whenever a player is not on the court during the time specified in the get_coordinates function.")
'''

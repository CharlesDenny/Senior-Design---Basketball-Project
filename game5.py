import json
import os
import csv
import datetime
import sys
import code
import mpld3 as mpl
from time import sleep

import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from mpl_toolkits.mplot3d import Axes3D


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


    def get_coordinates(self, game, current_quarter, start_t, end_t):       # Gets players coordinates for a specified game, quarter, start/end time
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
            with open('0021500420.json') as f:
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
            with open('2015.12.22.DET.at.MIA.0021500420.csv') as f:
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

    def get_list_of_shots(self):                                    # Gets textual info of each shot
        keyword1 = "makes"  # Defines Keywords From Play-By-Play Text To Find Shots.
        keyword2 = "misses"
        keyword3 = "shot"

        d = {}  # Initialize The Dictionary and List To Store General Shot Information.
        theList = []

        gameEvents = self.events
        for event in gameEvents:
            assistFlag = False
            blockFlag = False
            momentInfo = event.text
            quarter = event.period
            gameClock = event.gameclock

            if (keyword1 in event.text or keyword2 in event.text) and keyword3 in event.text:  # Look For Keywords To Find Shots.
                shotquarter = event.period
                if gameClock < 715:     # Accounts for any shots at the beginning of a quarter.
                    beginsearch = gameClock + 5  # Begin Searching For The Start Of The Shot Five Seconds Before.
                else:
                    beginsearch = gameClock
                if gameClock >= 1:      # Accounts for any shots at the end of a quarter.
                    endsearch = gameClock - 1
                else:
                    endsearch = gameClock
                if keyword1 in event.text:
                    outcome = "Made"
                if keyword2 in event.text:
                    outcome = "Missed"
                playerCount = 0
                for players in self.players:  # Loop Through List Of Players To Determine Who Took The Shot.
                    if playerCount >= len(self.home.players) or playerCount >= len(self.visitor.players):  # Maximum of 13 Players Per Team.
                        break
                    firstLetter = self.home.players[playerCount].firstname[0]  # Compare First Initial And Last Name In PLay-By-Play.
                    firstInitial = firstLetter + "."
                    lastname = self.home.players[playerCount].lastname
                    name = firstInitial + " " + lastname
                    if name in event.text:

                        if "ft" in event.text:
                            ftloc = event.text.find("ft")
                            if event.text[ftloc-3] == " ":
                                feet = int(event.text[ftloc-2])
                            else:
                                firstDigit = event.text[ftloc-3]
                                secondDigit = event.text[ftloc-2]
                                feet = int((firstDigit + secondDigit))

                        if "rim" in event.text:
                            feet = 0

                        nloc = event.text.find(name)
                        if "assist" in event.text:
                            aloc = event.text.find("assist")
                            assistFlag = True
                            if nloc < aloc:
                                shooter = self.home.players[playerCount]
                                teamabb = self.home.teamname_abbrev
                                shooterIndex = playerCount
                            else:
                                assister = self.home.players[playerCount]
                                assisterIndex = playerCount
                        elif "block" in event.text:
                            bloc = event.text.find("block")
                            blockFlag = True
                            if nloc < bloc:
                                shooter = self.home.players[playerCount]
                                teamabb = self.home.teamname_abbrev
                                shooterIndex = playerCount
                            else:
                                blocker = self.home.players[playerCount]
                                blockerIndex = playerCount
                        else:
                            shooter = self.home.players[playerCount]
                            teamabb = self.home.teamname_abbrev
                            shooterIndex = playerCount

                    firstLetter = self.visitor.players[playerCount].firstname[
                        0]  # Compare First Initial And Last Name In PLay-By-Play.
                    firstInitial = firstLetter + "."
                    lastname = self.visitor.players[playerCount].lastname
                    name = firstInitial + " " + lastname
                    if name in event.text:

                        if "ft" in event.text:
                            ftloc = event.text.find("ft")
                            if event.text[ftloc-3] == " ":
                                feet = int(event.text[ftloc-2])
                            else:
                                firstDigit = event.text[ftloc-3]
                                secondDigit = event.text[ftloc-2]
                                feet = int((firstDigit + secondDigit))

                        if "rim" in event.text:
                            feet = 0

                        nloc = event.text.find(name)
                        if "assist" in event.text:
                            aloc = event.text.find("assist")
                            assistFlag = True
                            if nloc < aloc:
                                shooter = self.visitor.players[playerCount]
                                teamabb = self.visitor.teamname_abbrev
                                shooterIndex = playerCount
                            else:
                                assister = self.visitor.players[playerCount]
                                assisterIndex = playerCount
                        elif "block" in event.text:
                            bloc = event.text.find("block")
                            blockFlag = True
                            if nloc < bloc:
                                shooter = self.visitor.players[playerCount]
                                teamabb = self.visitor.teamname_abbrev
                                shooterIndex = playerCount
                            else:
                                blocker = self.visitor.players[playerCount]
                                blockerIndex = playerCount
                        else:
                            shooter = self.visitor.players[playerCount]
                            teamabb = self.visitor.teamname_abbrev
                            shooterIndex = playerCount
                    playerCount += 1

                if assistFlag:
                    SPlayername = shooter.firstname + " " + shooter.lastname
                    SPlayerid = shooter.playerid
                    APlayername = assister.firstname + " " + assister.lastname
                    APlayerid = assister.playerid
                    d = {"player": SPlayername, "id": SPlayerid, "shooterindex": shooterIndex, "team": teamabb, "quarter": shotquarter, "begin": beginsearch, "end": endsearch, "outcome": outcome, "distance": feet, "assist": APlayername, "assistid": APlayerid, "assisterindex": assisterIndex}
                    theList.append(d)  # Adds Each General Shot Information To The List.
                elif blockFlag:
                    SPlayername = shooter.firstname + " " + shooter.lastname
                    SPlayerid = shooter.playerid
                    BPlayername = blocker.firstname + " " + blocker.lastname
                    BPlayerid = blocker.playerid
                    d = {"player": SPlayername, "id": SPlayerid, "shooterindex": shooterIndex, "team": teamabb, "quarter": shotquarter, "begin": beginsearch, "end": endsearch, "outcome": outcome, "distance": feet, "block": BPlayername, "blockid": BPlayerid, "blockerindex": blockerIndex}
                    theList.append(d)  # Adds Each General Shot Information To The List.
                else:
                    SPlayername = shooter.firstname + " " + shooter.lastname
                    SPlayerid = shooter.playerid
                    d = {"player": SPlayername, "id": SPlayerid, "shooterindex": shooterIndex, "team": teamabb, "quarter": shotquarter, "begin": beginsearch, "end": endsearch, "outcome": outcome, "distance": feet}
                    theList.append(d)  # Adds Each General Shot Information To The List.
        return theList


    def get_shot_X_coord(self, theList):                    # Gets x coordinate for each shot
        momentlist = self.moments
        momentCount = 0
        listCount = 0
        shotCounter = 1

        shotDict = {}  # Initialize Shot Information Dictionary.
        coordinate = {}  # Initialize Coordinates Dictionary.
        shotCoordinates = []  # Initialize List Of Coordinates For Each Shot.
        theListOfShots = []  # Initialize List Of Shots.
        for entry in theList:  # Loop Through Each Shot Found.
            isRimHeightDiscovered = False
            isShotDiscovered = False
            for m in momentlist:  # Loop Through Each Moment.
                quarter = momentlist[momentCount].period  # Get Quarter
                gameClock = momentlist[momentCount].gameclock  # Get Game Clock
                playername = theList[listCount]["player"]  # Get Shot Information
                playerid = theList[listCount]["id"]
                shotquarter = theList[listCount]["quarter"]
                beginsearch = theList[listCount]["begin"]
                endsearch = theList[listCount]["end"]
                outcome = theList[listCount]["outcome"]
                teamabb = theList[listCount]["team"]
                if quarter == shotquarter:  # Look For Quarter Shot Occurred.
                    if beginsearch >= gameClock >= endsearch:  # Look For Time Shot Occurred.
                        if momentlist[momentCount].ball != None:  # Check To Make Sure The Ball Coordinates Are Not Missing.
                            if momentlist[momentCount].ball[2] >= 10:  # Check To See When Shot Begins (10 = Height Of Rim).
                                if not isShotDiscovered:
                                    isShotDiscovered = True
                                if not isRimHeightDiscovered:
                                    isRimHeightDiscovered = True
                                    rimHeightDiscoveredMoment = momentCount
                                    counter = momentCount
                                    while True:
                                        if momentlist[counter].ball == None or momentlist[counter-1].ball == None:
                                            counter -= 1
                                            continue
                                        else:
                                            if momentlist[counter-1].ball[2] < momentlist[counter].ball[2]:
                                                counter -= 1
                                            if momentlist[counter-1].ball[2] >= momentlist[counter].ball[2]:
                                                break
                                    while counter < rimHeightDiscoveredMoment:
                                        if momentlist[counter].ball == None:
                                            counter += 1
                                            continue
                                        else:
                                            x = momentlist[counter].ball[0]  # Get Ball Coordinates
                                            coordinate = x  # Store Ball Coordinates For That Moment.
                                            shotCoordinates.append(coordinate)  # Store Ball Coordinates For That Moment In List.
                                            counter += 1
                                x = momentlist[momentCount].ball[0]  # Get Ball Coordinates
                                coordinate = x  # Store Ball Coordinates For That Moment.
                                shotCoordinates.append(coordinate)  # Store Ball Coordinates For That Moment In List.
                            if momentlist[momentCount].ball[2] < 10 and isShotDiscovered:
                                break
                momentCount += 1
            theListOfShots.append(shotCoordinates)  # Store All Shot Information In The List.
            shotCoordinates = []  # Resets The Coordinates List For The Next Shot.
            shotDict = {}  # Resets The Shot Information Dictionary For The Next Shot.
            listCount += 1
            momentCount = 0
            shotCounter += 1
        return theListOfShots


    def get_shot_Y_coord(self, theList):                    # Gets y coordinate for each shot
        momentlist = self.moments
        momentCount = 0
        listCount = 0

        shotDict = {}  # Initialize Shot Information Dictionary.
        coordinate = {}  # Initialize Coordinates Dictionary.
        shotCoordinates = []  # Initialize List Of Coordinates For Each Shot.
        theListOfShots = []  # Initialize List Of Shots.
        for entry in theList:  # Loop Through Each Shot Found.
            isRimHeightDiscovered = False
            isShotDiscovered = False
            for m in momentlist:  # Loop Through Each Moment.
                quarter = momentlist[momentCount].period  # Get Quarter
                gameClock = momentlist[momentCount].gameclock  # Get Game Clock
                playername = theList[listCount]["player"]  # Get Shot Information
                playerid = theList[listCount]["id"]
                shotquarter = theList[listCount]["quarter"]
                beginsearch = theList[listCount]["begin"]
                endsearch = theList[listCount]["end"]
                outcome = theList[listCount]["outcome"]
                teamabb = theList[listCount]["team"]
                if quarter == shotquarter:  # Look For Quarter Shot Occurred.
                    if beginsearch >= gameClock >= endsearch:  # Look For Time Shot Occurred.
                        if momentlist[momentCount].ball != None:  # Check To Make Sure The Ball Coordinates Are Not Missing.
                            if momentlist[momentCount].ball[2] >= 10:  # Check To See When Shot Begins (10 = Height Of Rim).
                                if not isShotDiscovered:
                                    isShotDiscovered = True
                                if not isRimHeightDiscovered:
                                    isRimHeightDiscovered = True
                                    rimHeightDiscoveredMoment = momentCount
                                    counter = momentCount
                                    while True:
                                        if momentlist[counter].ball == None or momentlist[counter-1].ball == None:
                                            counter -= 1
                                            continue
                                        else:
                                            if momentlist[counter-1].ball[2] < momentlist[counter].ball[2]:
                                                counter -= 1
                                            if momentlist[counter-1].ball[2] >= momentlist[counter].ball[2]:
                                                break
                                    while counter < rimHeightDiscoveredMoment:
                                        if momentlist[counter].ball == None:
                                            counter += 1
                                            continue
                                        else:
                                            y = momentlist[counter].ball[1]  # Get Ball Coordinates
                                            coordinate = y  # Store Ball Coordinates For That Moment.
                                            shotCoordinates.append(coordinate)  # Store Ball Coordinates For That Moment In List.
                                            counter += 1
                                y = momentlist[momentCount].ball[1]  # Get Ball Coordinates
                                coordinate = y  # Store Ball Coordinates For That Moment.
                                shotCoordinates.append(coordinate)  # Store Ball Coordinates For That Moment In List.
                            if momentlist[momentCount].ball[2] < 10 and isShotDiscovered:
                                break
                momentCount += 1
            theListOfShots.append(shotCoordinates)  # Store All Shot Information In The List.
            shotCoordinates = []  # Resets The Coordinates List For The Next Shot.
            shotDict = {}  # Resets The Shot Information Dictionary For The Next Shot.
            listCount += 1
            momentCount = 0
        return theListOfShots


    def get_shot_Z_coord(self, theList):                # Gets z coordinate for each shot
        momentlist = self.moments
        momentCount = 0
        listCount = 0

        shotDict = {}  # Initialize Shot Information Dictionary.
        coordinate = {}  # Initialize Coordinates Dictionary.
        shotCoordinates = []  # Initialize List Of Coordinates For Each Shot.
        theListOfShots = []  # Initialize List Of Shots.
        for entry in theList:  # Loop Through Each Shot Found.
            isRimHeightDiscovered = False
            isShotDiscovered = False
            for m in momentlist:  # Loop Through Each Moment.
                quarter = momentlist[momentCount].period  # Get Quarter
                gameClock = momentlist[momentCount].gameclock  # Get Game Clock
                playername = theList[listCount]["player"]  # Get Shot Information
                playerid = theList[listCount]["id"]
                shotquarter = theList[listCount]["quarter"]
                beginsearch = theList[listCount]["begin"]
                endsearch = theList[listCount]["end"]
                outcome = theList[listCount]["outcome"]
                teamabb = theList[listCount]["team"]
                if quarter == shotquarter:  # Look For Quarter Shot Occurred.
                    if beginsearch >= gameClock >= endsearch:  # Look For Time Shot Occurred.
                        if momentlist[momentCount].ball != None:  # Check To Make Sure The Ball Coordinates Are Not Missing.
                            if momentlist[momentCount].ball[2] >= 10:  # Check To See When Shot Begins (10 = Height Of Rim).
                                if not isShotDiscovered:
                                    isShotDiscovered = True
                                if not isRimHeightDiscovered:
                                    isRimHeightDiscovered = True
                                    rimHeightDiscoveredMoment = momentCount
                                    counter = momentCount
                                    while True:
                                        if momentlist[counter].ball == None or momentlist[counter-1].ball == None:
                                            counter -= 1
                                            continue
                                        else:
                                            if momentlist[counter-1].ball[2] < momentlist[counter].ball[2]:
                                                counter -= 1
                                            if momentlist[counter-1].ball[2] >= momentlist[counter].ball[2]:
                                                break
                                    while counter < rimHeightDiscoveredMoment:
                                        if momentlist[counter].ball == None:
                                            counter += 1
                                            continue
                                        else:
                                            z = momentlist[counter].ball[2]  # Get Ball Coordinates
                                            coordinate = z  # Store Ball Coordinates For That Moment.
                                            shotCoordinates.append(coordinate)  # Store Ball Coordinates For That Moment In List.
                                            counter += 1
                                z = momentlist[momentCount].ball[2]  # Get Ball Coordinates
                                coordinate = z  # Store Ball Coordinates For That Moment.
                                shotCoordinates.append(coordinate)  # Store Ball Coordinates For That Moment In List.
                            if momentlist[momentCount].ball[2] < 10 and isShotDiscovered:
                                break
                momentCount += 1
            theListOfShots.append(shotCoordinates)  # Store All Shot Information In The List.
            shotCoordinates = []  # Resets The Coordinates List For The Next Shot.
            shotDict = {}  # Resets The Shot Information Dictionary For The Next Shot.
            listCount += 1
            momentCount = 0
        return theListOfShots

    def get_shot_coord(self, theList):                      # Gets shot coordinates
        momentlist = self.moments
        momentCount = 0
        listCount = 0

        shotDict = {}  # Initialize Shot Information Dictionary.
        coordinate = {}  # Initialize Coordinates Dictionary.
        shotCoordinates = []  # Initialize List Of Coordinates For Each Shot.
        theListOfShots = []  # Initialize List Of Shots.

        for entry in theList:  # Loop Through Each Shot Found.
            for m in momentlist:  # Loop Through Each Moment.
                quarter = momentlist[momentCount].period  # Get Quarter
                gameClock = momentlist[momentCount].gameclock  # Get Game Clock
                playername = theList[listCount]["player"]  # Get Shot Information
                playerid = theList[listCount]["id"]
                shotquarter = theList[listCount]["quarter"]
                beginsearch = theList[listCount]["begin"]
                endsearch = theList[listCount]["end"]
                outcome = theList[listCount]["outcome"]
                teamabb = theList[listCount]["team"]
                if quarter == shotquarter:  # Look For Quarter Shot Occurred.
                    if beginsearch >= gameClock >= endsearch:  # Look For Time Shot Occurred.
                        if momentlist[
                            momentCount].ball != None:  # Check To Make Sure The Ball Coordinates Are Not Missing.
                            if momentlist[momentCount].ball[
                                2] >= 10:  # Check To See When Shot Begins (10 = Height Of Rim).
                                x = momentlist[momentCount].ball[0]  # Get Ball Coordinates
                                y = momentlist[momentCount].ball[1]
                                z = momentlist[momentCount].ball[2]
                                coordinate = {"gameclock": gameClock, "x": x, "y": y,
                                              "z": z}  # Store Ball Coordinates For That Moment.
                                shotCoordinates.append(
                                    coordinate)  # Store Ball Coordinates For That Moment In List.
                momentCount += 1
            theListOfShots.append(shotCoordinates)  # Store All Shot Information In The List.
            shotCoordinates = []  # Resets The Coordinates List For The Next Shot.
            shotDict = {}  # Resets The Shot Information Dictionary For The Next Shot.
            listCount += 1
            momentCount = 0
        return theListOfShots

    def getShots(self, theList):                # Gets info for each shot as well as the coordinates for each shot
        momentlist = self.moments
        momentCount = 0
        listCount = 0
        shotAlreadyFound = False

        shotDict = {}  # Initialize Shot Information Dictionary.
        coordinate = {}  # Initialize Coordinates Dictionary.
        shotCoordinates = []  # Initialize List Of Coordinates For Each Shot.
        theListOfShots = []  # Initialize List Of Shots.
        shotTimes = []  # Initialize a List of Shot Times

        while listCount < len(theList):  # Loop Through Each Shot Found.
            isRimHeightDiscovered = False
            isShotDiscovered = False

            playername = theList[listCount]["player"]  # Get Shot Information
            playerid = theList[listCount]["id"]
            shooterindex = theList[listCount]["shooterindex"]
            shotquarter = theList[listCount]["quarter"]
            if not shotAlreadyFound:
                beginsearch = theList[listCount]["begin"]
            endsearch = theList[listCount]["end"]
            outcome = theList[listCount]["outcome"]
            teamabb = theList[listCount]["team"]
            distance = theList[listCount]["distance"]
            if "assist" in theList[listCount]:
                assist = theList[listCount]["assist"]
                assistid = theList[listCount]["assistid"]
                assistindex = theList[listCount]["assisterindex"]
            else:
                assistid = 0
            if "block" in theList[listCount]:
                block = theList[listCount]["block"]
                blockid = theList[listCount]["blockid"]
                blockindex = theList[listCount]["blockerindex"]
            else:
                blockid = 0
            for m in momentlist:  # Loop Through Each Moment.
                quarter = momentlist[momentCount].period  # Get Quarter
                gameClock = momentlist[momentCount].gameclock  # Get Game Clock
                if quarter == shotquarter:  # Look For Quarter Shot Occurred.
                    if beginsearch >= gameClock >= endsearch:  # Look For Time Shot Occurred.
                        if momentlist[momentCount].ball and momentlist[momentCount+1].ball != None:  # Check To Make Sure The Ball Coordinates Are Not Missing.
                            if momentlist[momentCount].ball[2] >= 10:  # Check To See When Shot Begins (10 = Height Of Rim).
                                if not isShotDiscovered:
                                    isShotDiscovered = True
                                if not isRimHeightDiscovered:
                                    isRimHeightDiscovered = True
                                    rimHeightDiscoveredMoment = momentCount
                                    counter = momentCount
                                    while True:
                                        if momentlist[counter].ball == None or momentlist[counter-1].ball == None:
                                            counter -= 1
                                            continue
                                        else:
                                            if momentlist[counter-1].ball[2] < momentlist[counter].ball[2]:
                                                counter -= 1
                                            if momentlist[counter-1].ball[2] >= momentlist[counter].ball[2]:
                                                break

                                    while counter < rimHeightDiscoveredMoment:
                                        if momentlist[counter].ball == None:
                                            counter += 1
                                            continue
                                        else:
                                            gameClock = momentlist[counter].gameclock
                                            x = momentlist[counter].ball[0]  # Get Ball Coordinates
                                            y = momentlist[counter].ball[1]
                                            z = momentlist[counter].ball[2]
                                            coordinate = {"quarter": quarter, "gameclock": gameClock, "x": x, "y": y, "z": z}  # Store Ball Coordinates For That Moment.
                                            shotCoordinates.append(coordinate)  # Store Ball Coordinates For That Moment In List.
                                            counter += 1
                                x = momentlist[momentCount].ball[0]  # Get Ball Coordinates
                                y = momentlist[momentCount].ball[1]
                                z = momentlist[momentCount].ball[2]
                                coordinate = {"quarter": quarter, "gameclock": gameClock, "x": x, "y": y,"z": z}  # Store Ball Coordinates For That Moment.
                                shotCoordinates.append(coordinate)  # Store Ball Coordinates For That Moment In List.
                            if momentlist[momentCount+1].ball[2] < 10 and isShotDiscovered:
                                endCoordinate = {"quarter": quarter, "gameclock": gameClock, "x": x, "y": y,"z": z}
                                break
                    #if endsearch > gameClock:       # In case the shot is not found, it just needs to move on.
                        #if len(shotCoordinates) == 0:
                        #beginsearch = momentlist[momentCount].gameclock
                        #else:
                        #listCount += 1
                        #break
                momentCount += 1

            shotAlreadyFound = False

            timeCounter = 0
            if len(shotTimes) > 0:
                for times in shotTimes:
                    if shotTimes[timeCounter]["quarter"] == endCoordinate["quarter"]:
                        if shotTimes[timeCounter]["gameclock"] == endCoordinate["gameclock"]:
                            if shotTimes[timeCounter]["x"] == endCoordinate["x"]:
                                if shotTimes[timeCounter]["y"] == endCoordinate["y"]:
                                    if shotTimes[timeCounter]["z"] == endCoordinate["z"]:
                                        shotAlreadyFound = True
                                        break
                    timeCounter += 1

            if not shotAlreadyFound:
                shotTimes.append(endCoordinate)
            if shotAlreadyFound:
                beginsearch = endCoordinate["gameclock"] - 0.04
                shotCoordinates = []
                momentCount = 0

            if not shotAlreadyFound:
                if len(shotCoordinates) == 0:
                    time = convert(int(endsearch + 1))
                else:
                    time = convert(int(shotCoordinates[0]["gameclock"]))

                if outcome == "Missed" and len(shotCoordinates) > 0 and distance >= 12:
                    airBall = self.detectAirBall(shotCoordinates)
                else:
                    airBall = False

                if assistid != 0:
                    shotDict = {"playername": playername, "playerid": playerid, "team": teamabb, "quarter": shotquarter, "time": time, "result": outcome, "distance": distance, "assist": assist, "assistid": assistid, "coordinates": shotCoordinates}
                if blockid != 0:
                    shotDict = {"playername": playername, "playerid": playerid, "team": teamabb, "quarter": shotquarter, "time": time, "result": outcome, "distance": distance, "block": block, "blockid": blockid}
                if assistid == 0 and blockid == 0 and outcome == "Missed" and distance >= 12:
                    shotDict = {"playername": playername, "playerid": playerid, "team": teamabb, "quarter": shotquarter, "time": time, "result": outcome, "distance": distance, "airball": airBall, "coordinates": shotCoordinates}
                if assistid == 0 and blockid == 0 and outcome == "Missed" and distance < 12:
                    shotDict = {"playername": playername, "playerid": playerid, "team": teamabb, "quarter": shotquarter, "time": time, "result": outcome, "distance": distance, "coordinates": shotCoordinates}
                if assistid == 0 and blockid == 0 and outcome == "Made":
                    shotDict = {"playername": playername, "playerid": playerid, "team": teamabb, "quarter": shotquarter, "time": time, "result": outcome, "distance": distance, "coordinates": shotCoordinates}
                theListOfShots.append(shotDict)  # Store All Shot Information In The List.
                shotCoordinates = []  # Resets The Coordinates List For The Next Shot.
                shotDict = {}  # Resets The Shot Information Dictionary For The Next Shot.
                listCount += 1
                momentCount = 0
        return theListOfShots

    def detectAirBall(self, coordinates):
        isAirBall = False
        xIncreasing = False
        xDecreasing = False
        yIncreasing = False
        yDecreasing = False
        uncertainty = 0.02
        strike = 0
        strikeout = 3
        upIndex = 1
        length = len(coordinates)
        maxHeightIndex = 0
        while upIndex < length:      # Search For Maximum Height
            if coordinates[upIndex]["z"] + uncertainty < coordinates[upIndex - 1]["z"]:
                maxHeightIndex = upIndex

                if coordinates[upIndex]["x"] < coordinates[upIndex - 1]["x"]:
                    xDecreasing = True
                else:
                    xIncreasing = True

                if coordinates[upIndex]["y"] < coordinates[upIndex - 1]["y"]:
                    yDecreasing = True
                else:
                    yIncreasing = True
                break
            else:
                upIndex += 1

        downIndex = maxHeightIndex

        while downIndex < length:
            if coordinates[downIndex]["z"] - uncertainty > coordinates[downIndex - 1]["z"]:
                #strike += 1
                #if strike == strikeout:
                return isAirBall

            if xDecreasing:
                if coordinates[downIndex]["x"] - uncertainty > coordinates[downIndex - 1]["x"]:
                    #strike += 1
                    #if strike == strikeout:
                    return isAirBall
            if xIncreasing:
                if coordinates[downIndex]["x"] + uncertainty < coordinates[downIndex - 1]["x"]:
                    #strike += 1
                    #if strike == strikeout:
                    return isAirBall
            if yDecreasing:
                if coordinates[downIndex]["y"] - uncertainty > coordinates[downIndex - 1]["y"]:
                    #strike += 1
                    #if strike == strikeout:
                    return isAirBall
            if yIncreasing:
                if coordinates[downIndex]["y"] + uncertainty < coordinates[downIndex - 1]["y"]:
                    #strike += 1
                    #if strike == strikeout:
                    return isAirBall

            downIndex += 1

        isAirBall = True

        return isAirBall


    def getJumpBalls(self):
        '''
        Get jump ball players, player information, and ball coordinates
        Written by: Daryn Watt 11/2019
        '''
        keyword = "Jump ball"
        jumpBallList = []
        hometeamabb = self.home.teamname_abbrev
        visitorteamabb = self.visitor.teamname_abbrev

        for event in self.events:  # search all game events for jump balls
            momentInfo = event.text
            gameClock = event.gameclock

            if keyword in momentInfo:  # look for keyword to designate a jump ball
                quarter = event.period
                beginsearch = gameClock
                endsearch = gameClock - 3  # track ball coordinates for 3 seconds after jump ball time stamp

                # Split event into 2 parts: players that face off, and player that gets possession
                substringIndex = str(momentInfo).index('(')
                vsPlayerStr = str(momentInfo)[:substringIndex]
                possessionStr = str(momentInfo)[substringIndex:]

                for players in self.home.players:
                    name = players.firstname[0] + ". " + players.lastname

                    if name in vsPlayerStr:
                        homePlayer = players
                        homePlayerName = players.firstname + " " + players.lastname

                    if name in possessionStr:
                        possPlayer = players
                        possPlayerName = players.firstname + " " + players.lastname
                        possPlayerTeamAbb = self.home.teamname_abbrev
                # END HOME FOR LOOP

                for players in self.visitor.players:
                    name = players.firstname[0] + ". " + players.lastname

                    if name in vsPlayerStr:
                        visitorPlayer = players
                        visitorPlayerName = players.firstname + " " + players.lastname

                    if name in possessionStr:
                        possPlayer = players
                        possPlayerName = players.firstname + " " + players.lastname
                        possPlayerTeamAbb = self.visitor.teamname_abbrev
                # END VISITOR FOR LOOP

                jumpBallDict = {"homePlayer": homePlayerName, "homePlayerId": homePlayer.playerid,
                                "homeTeam": hometeamabb,
                                "visitorPlayer": visitorPlayerName, "visitorPlayerId": visitorPlayer.playerid,
                                "visitorTeam": visitorteamabb, "possessionPlayer": possPlayerName,
                                "possessionPlayerId": possPlayer.playerid, "possessionTeam": possPlayerTeamAbb,
                                "quarter": quarter, "begin": beginsearch, "end": endsearch}

                jumpBallList.append(jumpBallDict)  # Adds Each General jump ball Information To The List.
        # END GAME EVENTS FOR LOOP

        ballCoordinates = []  # Initialize List Of Coordinates For Each Shot.
        returnList = []  # Initialize List Of jump balls.
        maxZ = 0.0

        for entry in jumpBallList:  # For each jump ball that occurred
            homePlayerName = entry["homePlayer"]
            visitorPlayerName = entry["visitorPlayer"]
            possPlayerName = entry["possessionPlayer"]

            homePlayerId = entry["homePlayerId"]
            visitorPlayerId = entry["visitorPlayerId"]
            possPlayerId = entry["possessionPlayerId"]

            homePlayerTeam = entry["homeTeam"]
            visitorPlayerTeam = entry["visitorTeam"]
            possPlayerTeam = entry["possessionTeam"]

            beginsearch = entry["begin"]
            endsearch = entry["end"]
            shotquarter = entry["quarter"]

            for m in self.moments:
                currentQuarter = m.period
                gameClock = m.gameclock

                if currentQuarter == shotquarter:  # If jump ball occurred in loop's current quarter
                    if beginsearch >= gameClock >= endsearch:  # Look For Time Shot Occurred.
                        if m.ball is not None:  # Make Sure The Ball Coordinates Are Not Missing.
                            x = m.ball[0]  # Get Ball Coordinates
                            y = m.ball[1]
                            z = m.ball[2]

                            if z > maxZ:
                                maxZ = z

                            coordinate = {"gameclock": gameClock, "x": x, "y": y, "z": z}
                            ballCoordinates.append(coordinate)  # Store Ball Coordinates For That Moment In List.

            shotDict = {"homePlayer": homePlayerName, "homePlayerId": homePlayerId, "homeTeam": homePlayerTeam,
                        "visitorPlayer": visitorPlayerName, "visitorPlayerId": visitorPlayerId,
                        "visitorTeam": visitorPlayerTeam,
                        "possessionPlayer": possPlayerName, "possessionPlayerId": possPlayerId,
                        "possessionTeam": possPlayerTeam, "quarter": shotquarter, "time": beginsearch,
                        "maxHeight": maxZ, "coordinates": ballCoordinates}

            returnList.append(shotDict)  # Store All jump ball Information In The List.

            ballCoordinates = []  # Resets The Coordinates List For The Next jump ball.
            shotDict = {}  # Resets The Information Dictionary For The next jump ball.
            maxZ = 0
        # END JUMP BALL LIST LOOP
        return returnList
    # END JUMP BALLS


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


def get_all_moments(game):
    count = len(game.moments)
    i = 0
    while i <= (count - 1):
        moment_details(game, i)


def moment_details(game, index):
    gameClock = convert(game.moments[index].gameclock)
    print("MOMENT INFORMATION:")
    print("Game ID: " + str(game.gameid))
    print("Game Date: " + str(game.gamedate))
    print("Home Team: " + str(game.home.teamname))
    print("Visitor Team : " + str(game.visitor.teamname))
    print("Current Period: " + str(game.moments[index].period))
    print("Timestamp: " + str(game.moments[index].timestamp))
    print("Time: " + str(game.moments[index].time))
    print("Game Clock: " + gameClock)
    print("Shot Clock: " + str(game.moments[index].shotclock))
    print("Players Involved: ")
    count = len(game.moments[index].players)
    i = 0
    while i <= (count - 1):
        print("Player ID: " + "\n" + str(game.moments[index].players[i]['playerid']))
        print("Player X Coordinate: ")
        print(game.moments[index].players[i]['pos'][0])
        print("Player Y Coordinate: ")
        print(game.moments[index].players[i]['pos'][1])
        i += 1

    print("Ball Coordinate: " + "\n" + str(game.moments[index].ball))



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
    gameClock = convert(e1.gameclock)
    print("Event ID: " + str(e1.eventid))
    print("Period: " + str(e1.period))
    print("Time remaining: " + gameClock)
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
        gameClock = convert(e1.gameclock)
        print("Event ID: " + str(e1.eventid))
        print("Period: " + str(e1.period))
        print("Time remaining: " + gameClock)
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

    minit = str(minit)
    seconds = str(seconds).zfill(2)

    time = minit + ":" + seconds
    return time


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
                gameClock = convert(gameClock)
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


def display_shot_XY(g1, shotIndex):                # Displays shot at given index in a specified game
    s1 = g1.get_list_of_shots()
    s2 = g1.get_shot_X_coord(s1)  # Gets X Coordinate for each shot
    s3 = g1.get_shot_Y_coord(s1)  # Gets Y Coordinate for each shot
    x_coord = np.array(s2)
    y_coord = np.array(s3)


    x = x_coord[shotIndex]
    y = y_coord[shotIndex]

    fig = plt.figure(figsize=(12, 11))
    plt.scatter(x, y)
    draw_court()

    plt.xlim(-250, 250)
    plt.ylim(422.5, -47.5)
    plt.xlabel("X-Coordinates")
    plt.ylabel("Y-Coordinates")


    plt.show()


def display_shot(g1, shotIndex):                # Displays shot at given index in a specified game
    s1 = g1.get_list_of_shots()
    s2 = g1.get_shot_X_coord(s1)  # Gets X Coordinate for each shot
    # print(s2)
    s3 = g1.get_shot_Y_coord(s1)  # Gets Y Coordinate for each shot
    # print(s3)
    s4 = g1.get_shot_Z_coord(s1)  # Gets Z Coordinate for each shot
    # print(s4)
    # print(g1.getShots(s1))            # Gets every shot as well as the coordinates for each for shot

    x_coord = np.array(s2)
    y_coord = np.array(s3)
    z_coord = np.array(s4)

    x = x_coord[shotIndex]
    y = y_coord[shotIndex]
    z = z_coord[shotIndex]


    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(x, y, z, c='r', marker='o')
    ax.set_xlabel('X Coordinates')
    ax.set_ylabel('Y Coordinates')
    ax.set_zlabel('Z Coordinates')



    # plt.title(g1.moments[0].)
    plt.show()
    plt.clf()
    plt.close()


def display_players_movement(p1, quarter, start_t, end_t):      # Displays players coordinates during the specified start and end time in the quarter
    p1_X = p1.get_X_Coord(g1, quarter, start_t, end_t)          # Get player X coordinates
    p1_Y = p1.get_Y_Coord(g1, quarter, start_t, end_t)          # Get player Y coordinates
    X_Coord = np.array(p1_X)                                    # Use numpy to sort X into a managable array
    Y_Coord = np.array(p1_Y)                                    # User numpy to sort Y into a managable array

    # Create base of plot
    sns.set_style("white")
    sns.set_color_codes()
    plt.figure(figsize=(12, 11))
    plt.scatter(X_Coord, Y_Coord)
    draw_court()

    plt.xlim(-250, 250)
    plt.ylim(422.5, -47.5)
    plt.xlabel(p1.name() + ": X-Coordinates")
    plt.ylabel(p1.name() + ": Y-Coordinates")
    start = convert(start_t)
    end = convert(end_t)
    if quarter == 1:
        plt.suptitle(p1.name() + "'s Coordinates between " + start + " - " + end + " (Seconds)" + " in the " + str(quarter) + "st quarter.")
    elif quarter == 2:
        plt.suptitle(p1.name() + "'s Coordinates between " + start + " - " + end + "(Seconds)" + " in the " + str(quarter) + "nd quarter.")
    elif quarter == 3:
        plt.suptitle(p1.name() + "'s Coordinates between " + start + " - " + end + "(Seconds)" + " in the " + str(quarter) + "rd quarter.")
    elif quarter == 4:
        plt.suptitle(p1.name() + "'s Coordinates between " + start + " - " + end + "(Seconds)" + " in the " + str(quarter) + "th quarter.")
    plt.show()
    plt.clf()



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



def main(argv):
    if len(argv) != 1:
        print('usage: python game.py gameid')
        return
    g = game(argv[0])
    code.interact(local=locals())
    return


if __name__ == "__main__":
    main(sys.argv[1:])
    g1 = game("0021500420", True, True)
    """
    m1 = g1.moments
    p1 = g1.home.players[5]                                     # Creates a Kemba Walker player object (g1, player index: 5)
    start_t = 720
    end_t = 700

    print(g1.get_list_of_shots())                               # Gets info of shot such as played, id, team, name, quarter, start/end time, outcome
    print(g1.get_shot_coord())                                  # Gets shot coordinates
    print(g1.getShots())                                        # Shot info + shot coordinates
    print(g1.get_shot_X_coord(g1, g1.get_list_of_shots()))      # Prints x coordinates for each shot in a game
    print(g1.get_shot_Y_coord(g1, g1.get_list_of_shots()))      # Prints y coordinates for each shot in a game
    print(g1.get_shot_Z_coord(g1, g1.get_list_of_shots()))      # Prints z coordinates for each shot in a game
    event_details(g1, 461)                                      # Prints details for event # 461 (3-point attempt, miss)
    print(get_All_Events(g1))                                   # Prints all events for g1
    moment_details(g1, 500)                                     # Prints the 500th moment in g1
    print(get_all_moments(g1))                                  # Prints all moments for g1
    """

    #momentlist = g1.moments
    #print(momentlist[1].players)

    '''
    eventlist = g1.events
    eventCount = 0
    for event in eventlist:
        print(eventlist[eventCount].eventid, eventlist[eventCount].period, eventlist[eventCount].gameclock)
        eventCount += 1
    '''

    shotlist = g1.get_list_of_shots()

    shots = g1.getShots(shotlist)
    for shot in shots:
        print(shot)

    print("\n")
    print("List of Airballs:")
    print("\n")

    i = 0
    for shot in shots:
        if "airball" in shots[i].keys():
            if shots[i]["airball"] == True:
                print(shot)
        i += 1
    #print(g1.getJumpBalls())                                    # Displays all jumpballs in g1
    #display_shot(g1, 0)                                         # Displays shot # 0 in g1    (X Y Z Coordinates)
    #display_shot_XY(g1, 0)                                      # Displays shot # 0 in g1    (X Y Coordinates)

    count = 0
    while(count < len(shots)):
        display_shot(g1, count)
        count += 1
    """
    display_players_movement(p1, 1, start_t, end_t)             # Displays Kemba Walkers entire X and Y movement in Quarter # 1
    print("Ball Coordinates: ")
    print(get_ballcoordinates(g1, 1, start_t, end_t))           # Gets ball coordinates for g1 throughout the entire 1st quarter

    p1 = g1.home.players[5]                         # Kemba Walker
    print(p1.firstname)
    print(p1.lastname)
    print(p1.playerid)
    print(p1.jersey)
    print(p1.position)

    coord1 = p1.get_coordinates(g1, 1, 720, 500)
    print(coord1)

    if len(coord1) == 0:
        print("An empty list occurs whenever a player is not on the court during the time specified in the get_coordinates function.")

    print("\n")
    """
import json
with open('0021500423.json') as jsonFile:                               # Load JSON File
    gameData = json.load(jsonFile)

class Player:
    def __init__(self, lastname, firstname, playerid, jersey, position, teamname, teamid, teamabb):
        self.lastname = lastname
        self.firstname = firstname
        self.playerid = playerid
        self.jersey = jersey
        self.position = position
        self.teamname = teamname
        self.teamid = teamid
        self.teamabb = teamabb
    def getLastName(self):
        return self.lastname
    def getFirstName(self):
        return self.firstname
    def getPlayerID(self):
        return self.playerid
    def getLastName(self):
        return self.lastname
    def getJersey(self):
        return self.jersey
    def getPosition(self):
        return self.position
    def getTeamName(self):
        return self.teamname
    def getTeamID(self):
        return self.teamid
    def getTeamAbb(self):
        return self.teamabb
    def getCoordinates(self, currentquarter, starttime, finishtime):
        d = {}
        thelist = []

        gameEvents = gameData["events"]
        eventCount = 0
        for event in gameEvents:
            moments = gameEvents[eventCount]["moments"]
            momentCount = 0
            for moment in moments:
                momentInfo = moments[momentCount][5]  # Initialize Moment Coordinates Array
                quarter = moments[momentCount][0]  # Get Quarter
                gameClock = moments[momentCount][2]  # Get Game Clock
                infoCount = 0
                if quarter == currentquarter:  # Look For Quarter
                    if starttime >= gameClock >= finishtime:
                        for info in momentInfo:
                            if momentInfo[infoCount][1] == self.playerid:  # Look For Players' ID
                                x = momentInfo[infoCount][2]  # Record Coordinates
                                y = momentInfo[infoCount][3]
                                d = {"quarter": quarter, "gameclock": gameClock, "x": x, "y": y}
                                thelist.append(d)
                            infoCount += 1
                momentCount += 1
            eventCount += 1
        return thelist

p1 = Player("Jared", "Sullinger", 203096, "7", "C-F", "Boston Celtics", 1610612738, "BOS")

print(p1.playerid)

test = p1.getCoordinates(1, 720, 710)

coordinateCount = 0
for coordinate in test:
    quarter = test[coordinateCount]["quarter"]
    gameclock = test[coordinateCount]["gameclock"]
    x = test[coordinateCount]["x"]
    y = test[coordinateCount]["y"]
    print("Quarter: ", quarter, "          Time: ", gameclock, "          X: ", x, "          Y: ", y)
    coordinateCount += 1




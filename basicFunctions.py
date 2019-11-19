import json
with open('0021500101.json') as jsonFile1:
    game1Data = json.load(jsonFile1)

with open('0021500102.json') as jsonFile2:
    game2Data = json.load(jsonFile2)


gameID = game1Data["gameid"]
gameDate = game1Data["gamedate"]
game1Events = game1Data["events"]             #509 total game events
game2Events = game2Data["events"]
homeTeam = game1Events[0]["home"]["name"]
homeTeamID = game1Events[0]["home"]["teamid"]
visitorTeam = game1Events[0]["visitor"]["name"]
visitorTeamID = game1Events[0]["visitor"]["teamid"]


def getGameID(gameData):
    return gameData["gameid"]


def getGameDate(gameData):
    return gameData["gamedate"]


def getAllGameEvents(gameData):
    return gameData["events"]


#returns the event matching the ID, or -1 if event not found
def getEventById(gameEvents, eventID):
    for event in gameEvents:
        if str(event["eventId"]) == str(eventID):
            return event
    return -1



#returns the moments of the event with the specified ID. If the event could not be found, -1 returned
def getEventMoments(gameEvents, eventID):
    for event in gameEvents:
        if str(event["eventId"]) == str(eventID):
            return event["moments"]
    return -1


#return the home players for a specified event. If the event number is not valid, -1 is returned
def getEventHomePlayers(gameEvents, eventNum):
    if getEventById(gameEvents, eventNum) != -1:
        return gameEvents[eventNum - 1]["home"]["name"]
    else:
        return -1


#returns the visitor players for a specified event. If the event number is not valid, -1 is returned
def getEventVisitorPlayers(gameEvents, eventNum):
    if getEventById(gameEvents, eventNum) != -1:
        return gameEvents[eventNum - 1]["visitor"]["name"]
    else:
        return -1



def getBallData(gameEvents):
    allBallData = []
    eventCount = 0

    for event in gameEvents:
        for moment in gameEvents[eventCount]["moments"]:
            allBallData.append(moment[5][0])
    return allBallData




#BEGIN PYTEST TEST FUNCTIONS

def test_getGameID():
    assert getGameID(game1Data) == "0021500101"
    assert getGameID(game2Data) == "0021500102"

def test_getGameDate():
    assert getGameDate(game1Data) == "2015-11-09"
    assert getGameDate(game2Data) == "2015-11-09"

def test_getAllGameEvents():
    assert getAllGameEvents(game1Data) == game1Events
    assert getAllGameEvents(game2Data) == game2Events

def test_getEventById():
    assert getEventById(game1Events, 600) == -1
    assert getEventById(game1Events, 1) == game1Events[0]

def test_getEventMoments():
    assert getEventMoments(game1Events, 1) == game1Events[0]["moments"]
    assert getEventMoments(game1Events, 5) == game1Events[4]["moments"]
    assert getEventMoments(game2Events, 1) == game2Events[0]["moments"]
    assert getEventMoments(game2Events, 600) == -1

def test_getBallData():
    assert len(getBallData(game1Events)) > 0
    assert len(getBallData(game2Events)) > 0
    assert getBallData(game1Events)[0] == [-1,-1,36.76206,20.81453,7.41527]

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
def getEventById(gameEvents, eventIDParam):
    for event in gameEvents:
        print(str(event["eventId"]))
        if str(event["eventId"]) == str(eventIDParam):
            return event
    return -1





def getEventHomePlayers(gameEvents, eventNum):
    return gameEvents[eventNum]["home"]["name"]





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






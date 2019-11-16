import json
with open('0021500101.json') as jsonFile1:
    game1Data = json.load(jsonFile1)

with open('0021500102.json') as jsonFile2:
    game2Data = json.load(jsonFile2)


gameID = game1Data["gameid"]
gameDate = game1Data["gamedate"]
gameEvents = game1Data["events"]             #509 total game events
homeTeam = gameEvents[0]["home"]["name"]
homeTeamID = gameEvents[0]["home"]["teamid"]
visitorTeam = gameEvents[0]["visitor"]["name"]
visitorTeamID = gameEvents[0]["visitor"]["teamid"]


def getGameID(gameData):
    return gameData["gameid"]


def getGameDate(gameData):
    return gameData["gamedate"]


def getGameEvents(gameData):
    return gameData["events"]


def getEventHomePlayers(gameEvents, eventNum):
    return gameEvents[eventNum]["home"]["name"]


def getPlayerLocations(playerID):
    playerlocation = []
    eventCount = 0

    for event in gameEvents:
        for moment in gameEvents[eventCount]["moments"]:
            # Get the data of each player from the moment
            for playerDataLine in moment[5]:
                if playerDataLine[1] == playerID:
                    playerlocation.append(playerDataLine)
        eventCount += 1
    return playerlocation





#BEGIN PYTEST TEST FUNCTIONS

def test_getGameID():
    assert getGameID(game1Data) == "0021500101"
    assert getGameID(game2Data) == "0021500102"

def test_getGameDate():
    assert getGameDate(game1Data) == "2015-11-09"
    assert getGameDate(game2Data) == "2015-11-09"










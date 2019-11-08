import json
with open('0021500101.json') as jsonFile:
    gameData = json.load(jsonFile)

gameID =  gameData["gameid"]
gameDate = gameData["gamedate"]
gameEvents = gameData["events"]             #509 total game events
homeTeam= gameEvents[0]["home"]["name"]
homeTeamID = gameEvents[0]["home"]["teamid"]
visitorTeam = gameEvents[0]["visitor"]["name"]
visitorTeamID = gameEvents[0]["visitor"]["teamid"]

print("Game ID: " + gameID)
print("Game Date: " + gameDate)
print("Home: " + homeTeam + " ID: " + str(homeTeamID))
print("Visitor: " + visitorTeam + " ID: " + str(visitorTeamID))

print("\nEvent 1")
print("Home Players are: ")
for player in gameEvents[0]["home"]["players"]:
    print(player["lastname"])

print("Visitor Players are: ")
for player in gameEvents[0]["visitor"]["players"]:
    print(player["lastname"])


numMoments = 0
for moment in gameEvents[4]["moments"]:
    numMoments += 1

print("Event has " + str(numMoments) + " moments")



#for event in gameEvents:            #print each game event
 #   print(event)





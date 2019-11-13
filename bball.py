import json
with open('0021500101.json') as jsonFile:
    gameData = json.load(jsonFile)

gameID =  gameData["gameid"]
gameDate = gameData["gamedate"]
gameEvents = gameData["events"]             #509 total game events
homeTeam = gameEvents[0]["home"]["name"]
homeTeamID = gameEvents[0]["home"]["teamid"]
visitorTeam = gameEvents[0]["visitor"]["name"]
visitorTeamID = gameEvents[0]["visitor"]["teamid"]

allBallData = []

print("Game ID: " + gameID)
print("Game Date: " + gameDate)
print("Home: " + homeTeam + " ID: " + str(homeTeamID))
print("Visitor: " + visitorTeam + " ID: " + str(visitorTeamID))

eventCount = 0

for event in gameEvents:
    print("Event ID: " + str(event["eventId"]))

    #get the players for the event
    print("Home Players: ")
    for player in gameEvents[eventCount]["home"]["players"]:
        print("\t" + str(player["lastname"]))

    print("Visitor Players: ")
    for player in gameEvents[eventCount]["visitor"]["players"]:
        print("\t" + str(player["lastname"]))

    #Get Moments for each event
    print("Moments: ")
    for moment in gameEvents[eventCount]["moments"]:
        # quarter     moment ID (?)   time remaining in quarter     time remaining on shot clock      ????
        print("\t\tQuarter: " + str(moment[0]) + "\t\t" + str(moment[1])
              + "\t\t" + str(moment[2]) + "\t\t" + str(moment[3]) + "\t\t" + str(moment[4]))

        print("\t\t\t Ball Data: " + str(moment[5][0]))
        allBallData.append(moment[5][0])

        #Get the data of each player from the moment
        for playerDataLine in moment[5]:
            print("\t \t\t\t" + str(playerDataLine))

    print("\n")
    eventCount += 1
#End outermost for loop




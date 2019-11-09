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


    print("Moments: ")
    for moment in gameEvents[eventCount]["moments"]:
        print("\t\tQuarter: " + str(moment[0]) + "\t\t" + str(moment[2]) + "\t\t" + str(moment[3]))


    print("\n")
    eventCount += 1




#for moment in gameEvents[0]["moments"]:
 #   for info in moment:
  #      print(info)
#    print("Quarter:" + str(moment[0]))
#    print("")






#for event in gameEvents:            #print each game event
 #   print(event)





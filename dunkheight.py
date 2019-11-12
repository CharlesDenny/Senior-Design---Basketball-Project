# WHAT THIS CODE DOES:
# The purpose of this code is to determine the ball's maximum height during a dunk attempt.
# As an example, this code analyzes a point in the fourth quarter, where Al Horford scores on a dunk.
# This exact moment can be viewed at this Youtube Link:  https://www.youtube.com/watch?v=RhR0oO8O6ww at the 1:20 mark in the highlight reel video.
# This code analyzes 4 seconds of game time from 7:44.0 through 7:40.0 left on the game clock as Horford receives the pass and dunks the ball.

import json
with open('0021500101.json') as jsonFile:                               # Load JSON File
    gameData = json.load(jsonFile)

gameEvents = gameData["events"]                                         # Initialize Events Array

#biggestDifference_X = 0
#biggestDifference_Y = 0
eventCount = 0

for event in gameEvents:                                                # For Each Event
    print("Event ID: " + str(event["eventId"]))                         # Print The Event ID
    moments = gameEvents[eventCount]["moments"]                         # Initialize Moments Array
    momentCount = 0
    for moment in moments:                                              # For Each Moment
        momentInfo = moments[momentCount][5]                            # Initialize Moment Coordinates Array
        quarter = moments[momentCount][0]                               # Get Quarter
        gameClock = moments[momentCount][2]                             # Get Game Clock
        infoCount = 0
        if quarter == 4:                                                # Look For Fourth Quarter
            if 464 >= gameClock >= 460:                                 # Look For Time Of Play(7:44.0 - 7:40.0)
                for info in momentInfo:                                 # For Each Moment Coordinates
                    if momentInfo[infoCount][1] == -1:                  # Look For Ball ID (-1)
                        ball_X = momentInfo[infoCount][2]               # Record Ball Coordinates
                        ball_Y = momentInfo[infoCount][3]
                        ball_Z = momentInfo[infoCount][4]
                    if momentInfo[infoCount][1] == 201143:              # Look For Horford's ID (201143)
                        horford_X = momentInfo[infoCount][2]            # Record Horford's Coordinates
                        horford_Y = momentInfo[infoCount][3]
                    infoCount += 1
                difference_X = horford_X - ball_X                       # Calculate Difference Between Horford & Ball
                difference_Y = horford_Y - ball_Y
                #if abs(difference_X) > biggestDifference_X:             # Keep Track Of Largest Difference
                    #biggestDifference_X = difference_X
                #if abs(difference_Y) > biggestDifference_Y:
                    #biggestDifference_Y = difference_Y
                print("Horford's Distance From Ball:   X: ", abs(difference_X), "          Y: ", abs(difference_Y))
                print("Game Clock: ", gameClock, "          Ball X: ", ball_X, "          Ball Y: ", ball_Y, "          Ball Z: ", ball_Z)
        momentCount += 1
    eventCount += 1

#print("Biggest X Difference: ", abs(biggestDifference_X))
#print("Biggest Y Difference: ", abs(biggestDifference_Y))

# RESULTS
# This is the point in which the ball reachest its highest point during the dunk.
# The height of the hoop in the NBA is 10 feet.  As you can see the ball's height reaches just above that.
# Horford's Distance From Ball:   X:  0.4301300000000001           Y:  0.7932499999999969
# Game Clock:  460.64           Ball X:  6.23214           Ball Y:  23.09079           Ball Z:  10.50394
# WHAT THIS CODE DOES:
# This code calculates the difference between the coordinates of the ball and the player who actually has the ball.
# The purpose of this is to determine the uncertainty/error between both coordinates
# The coordinates of the ball and player will never be exactly the same, since the player is typically dribbling a little bit in front of or to the side of their body.
# As an example, this code analyzes a point in the fourth quarter, where Paul Millsap is driving towards the basket to score.
# This exact moment can be viewed at this Youtube Link:  https://www.youtube.com/watch?v=RhR0oO8O6ww at the 1:37 mark in the highlight reel video.
# This code analyzes 2 seconds of game time from 3:30.0 through 3:28.0 left on the game clock while Millsap has the ball before scoring.

import json
with open('0021500101.json') as jsonFile:                               # Load JSON File
    gameData = json.load(jsonFile)

gameEvents = gameData["events"]                                         # Initialize Events Array

biggestDifference_X = 0
biggestDifference_Y = 0
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
            if 210 >= gameClock >= 208:                                 # Look For Time Millsap Has Ball (3:30.0 - 3:28.0)
                for info in momentInfo:                                 # For Each Moment Coordinates
                    if momentInfo[infoCount][1] == -1:                  # Look For Ball ID (-1)
                        ball_X = momentInfo[infoCount][2]               # Record Ball Coordinates
                        ball_Y = momentInfo[infoCount][3]
                    if momentInfo[infoCount][1] == 200794:              # Look For Millsap's ID (200794)
                        millsap_X = momentInfo[infoCount][2]            # Record Millsap's Coordinates
                        millsap_Y = momentInfo[infoCount][3]
                    infoCount += 1
                difference_X = millsap_X - ball_X                       # Calculate Difference Between Millsap & Ball
                difference_Y = millsap_Y - ball_Y
                if abs(difference_X) > biggestDifference_X:             # Keep Track Of Largest Difference
                    biggestDifference_X = difference_X
                if abs(difference_Y) > biggestDifference_Y:
                    biggestDifference_Y = difference_Y
                print("X: ", abs(difference_X), "          Y: ", abs(difference_Y))
        momentCount += 1
    eventCount += 1

print("Biggest X Difference: ", abs(biggestDifference_X))
print("Biggest Y Difference: ", abs(biggestDifference_Y))

# RESULTS:
# Biggest X Difference:  0.9638799999999996
# Biggest Y Difference:  3.985819999999997
# The Y value is higher than usual because if you notice in the video, Millsap has to reach out to catch the pass, then he pulls it to his body.
# Once Millsap pulls it to his body, the Y never exceeds more than 2.5 for the remaining time he has the ball.
# Based on these results, we may want to consider using a difference of 2.5 as a safe starting point.


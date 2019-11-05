import inline as inline
import matplotlib as matplotlib
import numpy as np
import requests
import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns

from IPython.display import IFrame
from matplotlib.patches import Circle, Rectangle, Arc
from scipy.spatial.distance import euclidean

sns.set_color_codes()
sns.set_style("white")

IFrame('http://stats.nba.com/movement/#!/?GameID=0041400235&GameEventID;=308', width=700, height=400)

# Data we want to connect from NBA API. EventID is number for specific play, GameID is number for this playoff game
url = "http://stats.nba.com/stats/locations_getmoments/?eventid=308&gameid;=0041400235"

response = requests.get(url)    # Get the webpage
response.json().keys()          # Take a look at the keys from the dic representing the JSON data

home = response.json()["home"]          # A dict containing home players data
visitor = response.json()["visitor"]    # A dict containing away players data
moments = response.json()["moments"]    # A list containing each moment

# Calls the home function, gets abbreviation, team name,
# every player's: fname, jersey, lname, playerID, and position, as well as team id
home
visitor                         # Calls the away team function

len(moments)                    # Check the length of moments
moments[0]
# Moments data
# Quarter of event, timestamp of each event (unix-time in milliseconds)
# Time left in game clock, time left in shot clock, 5th item always none
# 6th item is 11 lists
# 1st list: ball info: team & playerID that identify list as ball,x & y values of ball on court, height of ball (feet)
# Next 10 lists = each player [team & playerID that identify list as specific player, x & y, empty value for z coord]

# Column labels for data frame
headers = ["team_id", "player_id", "x_loc", "y_loc", "radius", "moment", "game_clock", "shot_clock"]

# Create separate list containing moments data for each player
player_moments = []         # Initialize new list
for moment in moments:      # For each player/ball in the list found within each moment
    for player in moment[5]:    # Add info to each player/ball
        # index of each moment, game and shot clock values for each moment
        player.extend((moments.idex(moment), moment[2], moment[3]))
        player_moments.append(player)   # Add player to list

# Inspect our list
player_moments[0:11]
df = pd.DataFrame(player_moments, columns=headers)  # Pass new list of moments, column labels to create data frame
df.head(11)     # Display first 11 rows

# Create a list of all players
players = home["players"]
players.extend(visitor["players"])      # Add visitor players to list

# Create a dictionary with playerID as key and list containing player name and number as value
id_dict = {}
for player in players:
    id_dict[player['playerid']] = [player["firstname"] + " " + player["lastname"], player["jersey"]]

id_dict         # Displays every playerID in the game as well as players name and jersey

# Include an ID for the ball
id_dict.update({-1: ['ball', np.nan]})

# Add player name and jersey columns to data frame
df["player_name"] = df.player_id.map(lambda x: id_dict[x][0])
df["player_jersey"] = df.player_id.map(lambda x: id_dict[x][1])

df.head(11)     # Display first 11 rows

harden = df[df.player_name == "James Harden"]       # Get harden's movements
court = plt.imread("fullcourt.png")                 # Read in the court png file

plt.figure(figsize=(15, 11.5))
# Plot movements as scatter plot
# Use a color map to show change in game clock
plt.scatter(harden.x_loc, harden.y_loc, c=harden.game_clock, cmap=plt.cm.Blues, s=1000, zorder=1)
# Darker colors represent moments earlier in the game
cbar = plt.colorbar(orientation="horizontal")
cbar.ax.invert_xaxis()

# Plot the court
plt.imshow(court, zorder=0, extent=[0,94,50,0])
# zorder=0 sets the court lines underneath Harden's movements
# extent sets the x and y axis values to plot the image within
# Original plot = (0,0), pass extent (0, 94) for x axis (50, 0) for y axis

plt.xlim(0, 101)    # Extend x values beyond court because harden goes out of bounds

plt.show()      # Display plot

# Function to draw basketball court lines


def draw_court(ax=None, color="gray", lw=1, zorder=0):
    if ax is None:
        ax = plt.gca()

    # Creates the out of bounds lines on the court
    outer = Rectangle((0, -50), width=94, height=50, color=color, zorder=zorder, fill=False, lw=lw)

    # Left and right basketball hoops
    l_hoop = Circle((5.35, -25), radius=.75, lw=lw, fill=False, color=color, zorder=zorder)
    r_hoop = Circle((88.65, -25), radius=.75, lw=lw, fill=False, color=color, zorder=zorder)

    # Left and right backboards
    l_backboard = Rectangle((4, -28), 0, 6, lw=lw, color=color, zorder=zorder)
    r_backboard = Rectangle((90, -28), 0, 6, lw=lw, color=color, zorder=zorder)

    # Left and right paint areas
    l_outer_box = Rectangle((0, -33), 19, 16, lw=lw, fill=False, color=color, zorder=zorder)
    l_inner_box = Rectangle((0, -31), 19, 12, lw=lw, fill=False, color=color, zorder=zorder)
    r_outer_box = Rectangle((75, -33), 19, 16, lw=lw, fill=False, color=color, zorder=zorder)
    r_inner_box = Rectangle((75, -31), 19, 12, lw=lw, fill=False, color=color, zorder=zorder)

    # Left and right free throw circles
    l_free_throw = Circle((19, -25), radius=6, lw=lw, fill=False, color=color, zorder=zorder)
    r_free_throw = Circle((75, -25), radius=6, lw=lw, fill=False, color=color, zorder=zorder)

    # Left and right corner 3-PT lines
    # a represents the top lines
    # b represents the bottom lines
    l_corner_a = Rectangle((0, -3), 14, 0, lw=lw, color=color, zorder=zorder)
    l_corner_b = Rectangle((0, -47), 14, 0, lw=lw, color=color, zorder=zorder)
    r_corner_a = Rectangle((80, -3), 14, 0, lw=lw, color=color, zorder=zorder)
    r_corner_b = Rectangle((80, -47), 14, 0, lw=lw, color=color, zorder=zorder)

    # Left and right 3-PT line arcs
    l_arc = Arc((5, -25), 47.5, 47.5, theta1=292, theta2=68, lw=lw, color=color, zorder=zorder)
    r_arc = Arc((89, -25), 47.5, 47.5, theta1=112, theta2=248, lw=lw, color=color, zorder=zorder)

    # Half court
    # ax.axvLine(470)
    half_court = Rectangle((47, -50), 0, 50, lw=lw, color=color, zorder=zorder)
    hc_big_circle = Circle((47, -25), radius=6, lw=lw, fill=False, color=color, zorder=zorder)
    hc_sm_circle = Circle((47, -25), radius=2, lw=lw, fill=False, color=color, zorder=zorder)

    court_elements = [l_hoop, l_backboard, l_outer_box, outer,
                      l_inner_box, l_free_throw, l_corner_a,
                      l_corner_b, l_arc, r_hoop, r_backboard,
                      r_outer_box, r_inner_box, r_free_throw,
                      r_corner_a, r_corner_b, r_arc, half_court,
                      hc_big_circle, hc_sm_circle]

    # Add the court elements onto the axes
    for element in court_elements:
        ax.add_patch(element)

    return ax

plt.figure(figsize=(15, 11.5))
# Plot the movements as scatter plot
# Use a colormap to show change in game clock
plt.scatter(harden.x_loc, -harden.y_loc, c=harden.game_clock, cmap=plt.cm.Blues, s=1000, zorder=1)
# Darker colors represent moments earlier on in the game
cbar = plt.colorbar(orientation="horizontal")
# Invert the colorbar to have higher numbers on the left
cbar.ax.invert_xaxis()

draw_court()

plt.xlim(0, 101)
plt.ylim(-50, 0)
plt.show()


def travel_dist(player_locations):
    # Get the differences for each column
    diff = np.diff(player_locations, axis=0)
    # Square differences and add them, get square root of that sum
    dist = np.sqrt((diff ** 2).sum(axis=1))
    # Return sum of all distances
    return dist.sum()


# Harden's travel distance
dist = travel_dist(harden[["x_Loc", "y_Loc"]])
dist

player_travel_dist = df.groupby('player_name')[['x_Loc', 'y_Loc']].apply(travel_dist)
player_travel_dist      # Get distance traveled by every player and the ball

# Get num of seconds for the play
seconds = df.game_clock.max() - df.game_clock.min()
# Feet per second
harden_fps = dist / seconds
# Convert to miles per hour
harden_mph = 0.681818 * harden_fps
harden_mph          # Get James Hardens speed

# Getting average speed of each player
player_speeds = (player_travel_dist/seconds) * 0.681818
player_speeds       # Every players name and average speed is displayed

# Calculating distance between players
harden_loc = df[df.player_name=="James Harden"][["x_Loc", "y_Loc"]]
harden_loc.head()   # Get james harden's location

# Calculating locations for each player and the ball
group = df[df.player_name != "James Harden"].groupby("player_name")[["x_Loc", "y_Loc"]]


# Function to find the distance between players at each moment
def player_dist(player_a, player_b):
    return [euclidean(player_a.iloc[i], player_b.iloc[i])
            for i in range(len(player_a))]
# Each players location are passed as player_a, harden is b


harden_dist = group.apply(player_dist, player_b=(harden_loc))
harden_dist     # Displays distance from every player and harden at different events

IFrame('http://stats.nba.com/movement/#!/?GameID=0041400235&GameEventID;=308', width=700, height=400)

# Boolean mask used to grab the data within the proper time period
time_mask = (df.game_clock <= 706) & (df.game_clock >= 702) & \
            (df.shot_clock <= 10.1) & (df.shot_clock >= 6.2)
time_df = df[time_mask]

# Check out distance between harden and ball
ball = time_df[time_df.player_name == "ball"]
harden2 = time_df[time_df.player_name=="James Harden"]
harden_ball_dist = player_dist(ball[["x_loc", "y_loc"]],
                               harden2[["x_loc", "y_loc"]])

plt.figure(figsize=(12, 9))

x = time_df.shot_clock.unique()
y = harden_ball_dist
plt.plot(x, y)
plt.xlim(8, 7)

plt.xlabel("Shot clock")
plt.ylabel("Distance between Harden and the Ball (feet)")
plt.vlines(7.7, 0, 30, color='gray', lw=0.7)

plt.show()

# Boolean mask to get the players we want
player_mask = (time_df.player_name == "Trevor Ariza") | \
              (time_df.player_name == "DeAndre Jordan") | \
              (time_df.player_name == "Dwight Howard") | \
              (time_df.player_name == "Matt Barnes") | \
              (time_df.player_name == "Chris Paul") | \
              (time_df.player_name == "James Harden")

# Group by players and get their locations
group2 = time_df[player_mask].groupby('player_name')[["x_loc", "y_loc"]]

# Get the differences in distances that we want
harden_jordan = player_dist(group2.get_group("James Harden"), group2.get_group("DeAndre Jordan"))
howard_barnes = player_dist(group2.get_group("Dwight Howard"), group2.get_group("Matt Barnes"))
ariza_barnes = player_dist(group2.get_group("Trevor Ariza"), group2.get_group("Matt Barnes"))
ariza_paul = player_dist(group2.get_group("Trevor Ariza"), group2.get_group("Chris Paul"))

# Create some lists that will help create our plot
# Distance data
distances = [ariza_barnes, ariza_paul, harden_jordan, howard_barnes]
# Labels for each line that we will plopt
labels = ["Ariza - Barnes", "Ariza - Paul", "Harden - Jordan", "Howard - Barnes"]
# Colors for each line
colors = sns.color_palette('colorblind', 4)
plt.figure(figsize=(12, 9))

# Use enumerate to index the labels and colors and match
# them with the proper distance data
for i, dist in enumerate(distances):
    plt.plot(time_df.shot_clock.unique(), dist, color=colors[i])
    y_pos = dist[-1]
    plt.text(6.15, y_pos, labels[i], fontsize=14, color=colors[i])

# Plot a line to indicate when Harden passes the ball
plt.vlines(7.7, 0, 30, color='gray', lw=0.7)
plt.annotate("Harden passes the ball", (7.7, 27),
             xytext=(8.725, 26.8), fontsize=12,
             arrowprops=dict(facecolor='lightgray', shrink=0.10))

# Create horizontal grid lines
plt.grid(axis='y', color='gray', linestyle='--', lw=0.5, alpha=0.5)
plt.xlim(10.1, 6.2)
plt.title("The Distance (in feet) Between Players \nFrom the Beginning"
          " of Harden's Drive up until Ariza Releases his Shot", size=16)
plt.xlabel("Time Left on Shot Clock (seconds)", size=14)

# Get rid of unneeded chart lines
sns.despine(left=True, bottom=True)
plt.show()
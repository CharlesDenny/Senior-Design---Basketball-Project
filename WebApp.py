# app.py
import base64
import os
import sys
from game_w_coord import *
from flask import Flask, url_for, render_template      # import flask
import matplotlib.pyplot as plt


__import__("game_w_coord")

app = Flask(__name__)             # create an app instance


@app.route('/')
def home():
    return "Welcome to Team 22's Demo"


@app.route('/shot')
def shot():
    gameid = '0021500423'
    g1 = game(gameid, True, True)
    list = g1.get_list_of_shots()

    print("Test")

    x = g1.get_shot_X_coord(list)
    y = g1.get_shot_Y_coord(list)
    z = g1.get_shot_Z_coord(list)


    x_coord = np.array(x)
    y_coord = np.array(y)
    z_coord = np.array(z)

    x1 = x_coord[0]
    y1 = y_coord[0]
    z1 = z_coord[0]

    print(x1)
    print(y1)

    print("Getting there")
    img = io.BytesIO()

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(x1, y1, z1, c='r', marker='o')
    plt.savefig(img, format='png')
    plt.xlabel("X-Coordinates")
    plt.ylabel("Y-Coordinates")
    print("Almost there")
    img.seek(0)
    print("So close")
    graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    print("Victory")
    return '<img src="data:image/png;base64,{}">'.format(graph_url)


@app.route('/jumpball')
def jump():

    gameid = '0021500423'
    g1 = game(gameid, True, True)
    list = g1.getJumpBallList()

    print("Test")

    x = g1.getJumpBallX(list)
    y = g1.getJumpBallY(list)


    x_coord = np.array(x)
    y_coord = np.array(y)


    x1 = x_coord[0]
    y1 = y_coord[0]

    print(x1)
    print(y1)

    """
    x = [1.1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11,
         10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
    y = [20, 1.99, 18, 1.2345677, 14, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12,
         13, 14, 15, 16, 17, 18, 19, 20]
    """

    print("Getting there")
    img = io.BytesIO()
    plt.plot(x1, y1)
    plt.savefig(img, format='png')
    plt.xlabel("X-Coordinates")
    plt.ylabel("Y-Coordinates")
    plt.title("Jumpball for " + str(g1.gameid) + str(g1.gamedate) + g1.visitor.teamname_abbrev + " at " + g1.home.teamname_abbrev + ", index = 0")
    print("Almost there")
    img.seek(0)
    print("So close")
    graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    print("Victory")
    return '<img src="data:image/png;base64,{}">'.format(graph_url)


if __name__ == "__main__":        # on running python app.py
    app.run(debug=True)                     # run the flask app
'use strict';

const fs = require('fs');

let rawdata = fs.readFileSync('0021500420.json');
let student = JSON.parse(rawdata);
let game1data = JSON.stringify(student)
let finalGamedata = JSON.parse(game1data)

function getGameID(student)
{
    return student["gameid"]
}

function getGameDate(student)
{
    return student["gamedate"]
}

function getVisitor(finalGamedata)
{
    var data = finalGamedata["events"][0]["visitor"]
    var data2 = data["players"]
    console.log("Name: " + data["name"])
    console.log("ID: " + data["teamid"])
    console.log("Abbreviation: " + data["abbreviation"])
   for (var player in data2)
   {
       console.log("Player Name: " + data2[player]["firstname"] + " " + data2[player]["lastname"])
       console.log("Player ID: " + data2[player]["playerid"])
       console.log("Number: " + data2[player]["jersey"])
       console.log("Position: " + data2[player]["position"])
       console.log()
   }
}

function getHome(finalGamedata)
{
    var data = finalGamedata["events"][0]["home"]
    var data2 = data["players"]
    console.log("Name: " + data["name"])
    console.log("ID: " + data["teamid"])
    console.log("Abbreviation: " + data["abbreviation"])
    for (var player in data2)
    {
        console.log("Player Name: " + data2[player]["firstname"] + " " + data2[player]["lastname"])
        console.log("Player ID: " + data2[player]["playerid"])
        console.log("Number: " + data2[player]["jersey"])
        console.log("Position: " + data2[player]["position"])
        console.log("")
    }
}

function getEvent(finalGameData, eventIndex)
{
    console.log(finalGameData["events"][eventIndex]["moments"])
}

function getMoment(finalGameData, eventIndex, momentIndex)
{
    return finalGameData["events"][eventIndex]["moments"][momentIndex]
}

function getMomentDetails(finalGameData, eventIndex, momentIndex)
{
    var data = finalGameData["events"][eventIndex]["moments"][momentIndex]
    console.log("Quarter: " + data[0][0])
    console.log("Time remaining: " + data[0][2])
}


var gameID = getGameID(student)
var gameDate = getGameDate(student)

var visitors = getVisitor(finalGamedata)
var home = getHome(finalGamedata)
var event1 = getEvent(finalGamedata, 1)
var moment1 = getMoment(finalGamedata, 0, 0)
var details = getMomentDetails(finalGamedata, 0, 0)

/*console.log(visitors)
console.log(home)
console.log(event1)
 */

console.log(details)




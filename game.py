import json
import os
import csv
import datetime
import sys
import code

def dist(a, b):
    return ((abs(a[0] - b[0])**2 + abs(a[1] - b[1])**2)**(1/2))
    
class player:
    def __init__(self, p, teamid, home):

        self.position   = p['position'] #str
        self.playerid   = str(p['playerid']) #str
        self.jersey     = p['jersey'] #string
        self.lastname   = p['lastname'] #str
        self.firstname  = p['firstname'] #str
        self.teamid     = teamid #str
        self.home       = home
        self.pos        = None
    
    def name(self): return self.firstname + ' ' + self.lastname
    
    def __eq__(self, other):
        return self.playerid == other.playerid

    def __hash__(self):
        return hash(self.playerid)
    
class team:
    def __init__(self, t, home):
        self.teamid            = str(t['teamid'])
        self.teamname          = t['name']
        self.teamname_abbrev   = t['abbreviation']
        self.players           = []
        self.home              = home #home: False if visitor
        
        for p in t['players']:
            self.players.append(player(p, self.teamid, home))
        
class event:
    def __init__(self, line):
        self.eventid    = int(line['eventid'])
        self.period     = int(line['period'])
        gc = datetime.datetime.strptime(line['clock'], '%M:%S.%f').time()
        self.gameclock  = gc.minute * 60 + gc.second
        self.text       = line['text']
        self.visitor    = int(line['visitor'])
        self.home       = int(line['home'])
        self.possession = None
        
        if line['poss']=='True': self.possession=True
        elif line['poss']=='False': self.possession=False

class game:
    def __init__(self, gameid, pbp=True, moments=False):
        self.gameid   = gameid
        self.gamedate = None
        self.visitor  = None
        self.home     = None
        self.players  = {}
        self.moments  = []
        self.events   = []
        
        if moments:
            with open('./data/sportvu/json/' + gameid + '.json', 'r') as f:
                jsonf = json.load(f)
                self.gamedate = datetime.datetime.strptime(jsonf['gamedate'], '%Y-%m-%d')
                self.visitor  = team(jsonf['events'][0]['visitor'], False)
                self.home     = team(jsonf['events'][0]['home'], True)

                for player in self.visitor.players:
                    self.players[player.playerid] = player
                for player in self.home.players:
                    self.players[player.playerid] = player
                
                
                for e in jsonf['events']:
                    for m in e['moments']:
                        self.moments.append(moment(self, m))
                #magic sort
                self.moments=sorted(list(set(self.moments)),reverse=True)
        
        if pbp:
            pbppath = './data/pbp/' +[f for f in os.listdir('./data/pbp') if gameid in f][0]
            with open(pbppath, 'r') as f:
                reader = csv.DictReader(f)
                for line in reader:
                    self.events.append(event(line))
                
    def __str__(self):
        return '{} on {}: {:3} {} at {} {:3}'.format(self.gameid, self.gamedate.date(), self.events[-1].visitor, self.visitor.teamname_abbrev,  self.home.teamname_abbrev,  self.events[-1].home)
                
    def win(self):
        '''
        Returns true if home team won the game
        '''
        return bool(self.events[-1].home - self.events[-1].visitor)

    def tipwinner(self, exceptions=False):
        '''
        Returns true if home team won the opening tip
        '''
        
        if self.events[0].possession != None:
            if exceptions:
                return self.events[0].possession
            return None
        else:
            if 'Jump ball' in self.events[1].text:

                return self.events[1].possession
            else:
                assert self.events[1].text == 'Violation by Team (jump ball)'
                if exceptions:
                    return self.events[2].possession
                return None

    def getevent(self, period, gameclock):
        '''
        Returns the event given a period and game clock
        '''
        prev_event = self.events[0]
        for event in self.events[1:]:
            if event.period == period and event.gameclock <= gameclock:
                return prev_event
            else: prev_event = event
                
class moment:
    def __init__(self, game_parent, m):
        self.game      = game_parent
        self.period    = m[0] #int
        self.timestamp = m[1]
        self.time      = datetime.datetime.fromtimestamp(m[1]/1000) #datetime
        self.gameclock = m[2] #float
        self.shotclock = m[3] #float
        self.players   = []
        self.ball      = None #there may be 9, 10, or 11 points, meaning missing players/ball
        
        for point in m[5]:
            if point[1] == -1:
                self.ball=(point[2], point[3], point[4])
            else:
                self.players.append({'playerid': str(point[1]) , 'pos': (point[2], point[3])})

                # for playerid, playerobj in self.game.players.items():
                    # if playerid == str(point[1]):
                        # playerobj.pos=(point[2], point[3])
                        # self.players.append(playerobj)
                        # break

        for i in range(len(self.players) - 10):
            self.players.append(None)

    def __eq__(self, other):
        return self.time == other.time

    def __lt__(self, other):
        return self.time > other.time

    def __hash__(self):
            return hash(self.timestamp)

    def getoffensiveteam(self):
        e = self.event()
        poss_bool = e.possession
        if poss_bool: return self.game.home
        elif not poss_bool: return self.game.visitor
        else: return None
        
    def getbhbd(self):
        if not self.ball: return None
        
        closest={'o': {'player': None, 'dist': 1000}, 'd': {'player': None, 'dist': 1000}}
        ot=self.getoffensiveteam()
        if not ot: return closest
        
        for p in self.players:
            if not p: continue
            i = 'o' if self.game.players[p['playerid']].teamid == ot.teamid else 'd'
            temp = dist((self.ball[0], self.ball[1]), p['pos'])
            if temp < closest[i]['dist']:
                closest[i]['player'] = self.game.players[p['playerid']]
                closest[i]['dist'] = temp
        return closest['o']['player'], closest['d']['player']
                
    # def getballhandler(self):
        # if not self.ball: return None
        
        # closest=None
        # closest_dist= 1000
        # ot=self.getoffensiveteam()
        # if not ot: return None
        
        # for p in self.players:
            # if not p: continue
            # i = 'o' if p['teamid'] == ot.teamid else 'd'
            # temp = dist((self.ball[0], self.ball[1]), p['pos'])
            # if temp < closest[i]['dist']:
                # closest[i]['player'] = p
                # closest[i]['dist'] = temp
        # return closest['o']['player'], closest['d']['player']

    # def getballdefender(self):
        # ballhandler = self.getballhandler()
        # if not ballhandler: return None
        
        # closest=None
        # closest_dist= 1000
        # ot=self.getoffensiveteam()
        # if not ot: return None
        
        # for p in [q for q in self.players if self.game.players[q['playerid']].teamid != ot.teamid]:
            # if not p: continue
            # if p['teamid'] == ot.teamid: continue
            # temp = dist(ballhandler.pos, p['pos'])
            # if temp < closest_dist:
                # closest=p
                # closest_dist=temp
        # return closest
        
    def event(self):
        return self.game.getevent(self.period, self.gameclock)

def main(argv):
    if len(argv) != 1:
        print('usage: python game.py gameid')
        return
    g=game(argv[0])
    # print(g)
    code.interact(local=locals())
    return
    
if __name__ == "__main__":
    main(sys.argv[1:])
from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd

from basketball_reference_web_scraper import client
# from basketball_reference_web_scraper.data import Team
from basketball_reference_web_scraper.data import OutputType

# NBA season we are analyzing
year = 2019
# url page we will be scrapping
url = "https://www.basketball-reference.com/leagues/NBA_{}_per_game.html".format(year)
# html object from the given URL
html = urlopen(url)
soup = BeautifulSoup(html, features="html.parser")

# Use findALL() to get the column headers
soup.findAll('tr', limit=2)
# Use getText to extract the text we need into a list
headers = [th.getText() for th in soup.findAll('tr', limit=2)[0].findAll('th')]
# Exclude the first column, we dont need the rankings
headers = headers[1:]
headers

# avoid the first row header
rows = soup.findAll('tr')[1:]
player_stats = [[td.getText() for td in rows[i].findAll('td')]
                for i in range(len(rows))]
stats = pd.DataFrame(player_stats, columns=headers)
stats.head(10)


# Get play by play data for the 2018-10-16 game played at the Boston Celtics
"""
play_by_play = client.play_by_play(
    home_team=Team.BOSTON_CELTICS,
    year=2018,
    month=10,
    day=16,
)
"""


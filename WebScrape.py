from bs4 import BeautifulSoup
import pandas as pd
import requests




# NBA season we are analyzing
year = 2019
# url page we will be scrapping
url = requests.get('https://www.basketball-reference.com/leagues/NBA_2019_per_game.html')
url2 = requests.get('https://www.basketball-reference.com/leagues/NBA_2020_per_game.html')
# html object from the given URL
soup = BeautifulSoup(url.text, features="html.parser")
soup2 = BeautifulSoup(url2.text, features="html.parser")
headers = []


def header_calculation(c):
    headers_a = [th.getText() for th in c.findAll('tr', limit=2)[0].findAll('th')]
    # Exclude the first column, we dont need the rankings
    headers_a = headers_a[1:]
    return headers_a


# Get Column Headers
def column_headers(a):
    # Use findALL() to get the column headers
    a.findAll('tr', limit=2)
    headers_b = header_calculation(a)
    print(headers_b)


column_headers(soup)
column_headers(soup2)


# avoid the first row header
def get_data(b):
    rows = b.findAll('tr')[1:]
    player_stats = [[td.getText() for td in rows[i].findAll('td')]
                    for i in range(len(rows))]
    headers_c = header_calculation(b)
    stats = pd.DataFrame(player_stats, columns=headers_c)
    print(stats.head(10))


get_data(soup)
get_data(soup2)

"""
print('****** TEAM BOX SCORES *******')
team_box_scores = client.team_box_scores(day=1, month=1, year=2018)
for total in team_box_scores[:10]:
    print(total)
"""






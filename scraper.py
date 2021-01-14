import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

url = 'https://www.ncaagamesim.com/college-basketball-predictions.asp'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

table = soup.find('table')

# Get column names
headers = table.find_all('th')
cols = [x.text for x in headers]

# Get all rows in table body
table_rows = table.find_all('tr')

rows = []
# Grab the text of each td, and put into a rows list
for each in table_rows[1:]:
    odd_avail = True
    data = each.find_all('td')
    time = data[0].text.strip()

    # Get matchup and odds
    try:
        matchup, odds = data[1].text.strip().split('\xa0')
        odd_margin = float(odds.split('by')[-1].strip())
    except:
        matchup = data[1].text.strip()
        odd_margin = '-'
        odd_avail = False

    # Get favored team
    try:
        odd_team_win = data[1].find_all('img')[-1]['title']
    except:
        odd_team_win = '-'
        odd_avail = False

    # Get simulation winner
    try:
        sim_team_win = data[2].find('img')['title']
    except:
        sim_team_win = '-'
        odd_avail = False

    awayTeam = matchup.split('@')[0].strip()
    homeTeam = matchup.split('@')[1].strip()

    # Get simulation margin
    try:
        sim_margin = float(re.findall("\d+\.\d+", data[2].text)[-1])
    except:
        sim_margin = '-'
        odd_avail = False

    # If all variables available, determine odds, simulation margin points, and optimal bet
    if odd_avail == True:
        if odd_team_win == sim_team_win:
            diff = abs(sim_margin - odd_margin)
            if sim_margin > odd_margin:
                bet = odd_team_win
            else:
                if odd_team_win == homeTeam:
                    bet = awayTeam
                else:
                    bet = homeTeam
        else:
            diff = odd_margin + sim_margin
            bet = sim_team_win
    else:
        diff = -1
        bet = '-'

    # Create table
    row = {cols[0]: time, 'Matchup': matchup, 'Odds Winner': odd_team_win, 'Odds': odd_margin,
           'Simulation Winner': sim_team_win, 'Simulation Margin': sim_margin, 'Bet Margin': diff, 'Bet' : bet}
    rows.append(row)

df = pd.DataFrame(rows)
df = df.sort_values(by = ['Bet Margin'], ascending = False)
print (df.to_string())
# df.to_csv('odds.csv', index=False)

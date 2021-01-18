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

range1Wins = range1Loss = range2Wins = range2Loss = range3Wins = range3Loss \
    = range4Wins = range4Loss = range5Wins = range5Loss = range6Wins = range6Loss \
    = range7Wins = range7Loss = 0

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

    # Beat the spread?
    try:
        beatSpread = data[4].find_all('img')[-1]['title']
    except:
        beatSpread = '-'

    if beatSpread == 'Beat the Spread':
        if 0 <= diff <= 2.9:
            range1Wins += 1
        if 3 <= diff <= 5.9:
            range2Wins += 1
        if 6 <= diff <= 8.9:
            range3Wins += 1
        if 9 <= diff <= 11.9:
            range4Wins += 1
        if 12 <= diff <= 14.9:
            range5Wins += 1
        if 15 <= diff <= 17.9:
            range6Wins += 1
        if diff >= 18:
            range7Wins += 1
    else:
        if 0 <= diff <= 2.9:
            range1Loss += 1
        if 3 <= diff <= 5.9:
            range2Loss += 1
        if 6 <= diff <= 8.9:
            range3Loss += 1
        if 9 <= diff <= 11.9:
            range4Loss += 1
        if 12 <= diff <= 14.9:
            range5Loss += 1
        if 15 <= diff <= 17.9:
            range6Loss += 1
        if diff >= 18:
            range7Loss += 1

    # Create table
    row = {cols[0]: time, 'Matchup': matchup, 'Odds Winner': odd_team_win, 'Odds': odd_margin,
           'Simulation Winner': sim_team_win, 'Simulation Margin': sim_margin, 'Bet Margin': diff, 'Bet' : bet}
    rows.append(row)

# Print Matchups and Predictions
df = pd.DataFrame(rows)
df = df.sort_values(by=['Bet Margin'], ascending=False)
print(df.to_string())

# Print Bet Margin Records
print('\n--{ Beat the Spread: }--\n')
rows = []
row = {'Bet Margin Range': '0 - 2.9', 'Record': str(range1Wins) + ' - ' + str(range1Loss)}
rows.append(row)
row = {'Bet Margin Range': '3 - 5.9', 'Record': str(range2Wins) + ' - ' + str(range2Loss)}
rows.append(row)
row = {'Bet Margin Range': '6 - 8.9', 'Record': str(range3Wins) + ' - ' + str(range3Loss)}
rows.append(row)
row = {'Bet Margin Range': '9 - 11.9', 'Record': str(range4Wins) + ' - ' + str(range4Loss)}
rows.append(row)
row = {'Bet Margin Range': '12 - 14.9', 'Record': str(range5Wins) + ' - ' + str(range5Loss)}
rows.append(row)
row = {'Bet Margin Range': '15 - 17.9', 'Record': str(range6Wins) + ' - ' + str(range6Loss)}
rows.append(row)
row = {'Bet Margin Range': '18+', 'Record': str(range7Wins) + ' - ' + str(range7Loss)}
rows.append(row)
df = pd.DataFrame(rows)
print(df.to_string())

# Export to spreadsheet file
# df.to_csv('odds.csv', index=False)

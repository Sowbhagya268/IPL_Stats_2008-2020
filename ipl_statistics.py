import streamlit as st
import pandas as pd
import numpy as np

st.title("Indian Premier League Stats")
st.sidebar.title('Indian Premier League')
st.sidebar.subheader('Choose stats')

category = st.sidebar.selectbox('Stats Type', ('Team Stats', 'Stadium Stats', 'Head to Head Matches Stats', 'Top Run Scorers', 'Top Wicket Takers', 'Top Man of the Match Award Holders',))

matches = pd.read_csv("IPL_matches.csv")
ball_data = pd.read_csv("IPL_deliveries.csv")
matches.rename(lambda x : str(x).lower(), axis = 1, inplace = True)
ball_data.rename(lambda x : str(x).lower(), axis = 1, inplace = True)

sea = []
for i in range(len(matches)) :
    sea.append(str(matches.iloc[i]['date'][:4]))
matches['season'] = sea

teams = list(matches['team1'].unique())
teams.sort()

matches['venue'].replace(['M.Chinnaswamy Stadium'], 'M Chinnaswamy Stadium', inplace = True)
matches['venue'].replace(['Punjab Cricket Association Stadium, Mohali'], 'Punjab Cricket Association IS Bindra Stadium, Mohali', inplace = True)
stadium = matches.drop_duplicates(subset=['venue'], keep='first')
stadium['city'].fillna('Abu Dhabi', inplace = True)
stads = []
for i in range(len(stadium)) :
    stads.append(stadium['venue'].iloc[i]+ " (" + stadium['city'].iloc[i] + ")")
stads.sort()

year = []
for i in range(2008,2021) :
    year.append(str(i))
year.append('Overall')



if category == 'Team Stats' :

    st.header('Team Stats')
    team = st.selectbox('Select Team', teams)
    season = st.selectbox('Select Season', year)

    d1 = matches.loc[matches['team1'] == team]
    d2 = matches.loc[matches['team2'] == team]
    data = pd.concat([d1,d2], ignore_index = True)

    if season != 'Overall' :
        data = data.loc[data['season']==season]

    if len(data) == 0 :
        st.write(team, 'team is not a particpant of IPL season', season)

    else :

        st.write('Matches Played :', len(data))
        win = data['winner'].value_counts()

        if team not in win :
            win[team] = 0
        st.write('Matches Won :', win[team])
        st.write('Matches Lost :', len(data)-win[team])
        st.write('Win Ratio :', round(win[team]/(len(data)),2))

        st.write(' ')
        st.subheader('Toss and Winning Probability')
        st.write(' ')
        toss = data.loc[data['toss_winner']== team]

        if len(toss) == 0 :
            st.write(Team, 'did not win any tosses in IPL', season)
        else :

            st.write('Tosses won :', len(toss))
            st.write(' ')

            for i in ['bat', 'field'] :

                toss_option =  toss.loc[toss['toss_decision'] == i]

                if i == 'bat' :
                    select = 'batting'
                else :
                    select = 'fielding'

                if len(toss_option) == 0 :
                    st.write(Team, "did not choose", select, "after winning toss in IPL", season, ".")

                else :
                    st.write('Matches chosen', select, ':', len(toss_option))
                    option_win = toss_option['winner'].value_counts()

                    if team not in option_win :
                        option_win[team] = 0

                    st.write('Matches won after choosing', select, ':', option_win[team])
                    st.write('Win Probability if', select,'is chosen :', round(option_win[team]/len(toss_option),2))
                    st.write(' ')



if category == 'Stadium Stats' :

    st.header('Stadium Stats')
    stad = st.selectbox('Select Stadium', stads)

    match = matches.loc[matches['venue'] == stad[:stad.index('(')-1]]
    st.write('Matches played :', len(match))

    toss_bat = match.loc[match['toss_decision'] == 'bat']
    bat_cancel = toss_bat['winner'].count()
    bat_win = toss_bat.loc[toss_bat['toss_winner'] == toss_bat['winner']]
    bat_lost = toss_bat.loc[toss_bat['toss_winner'] != toss_bat['winner']]

    toss_field = match.loc[match['toss_decision'] == 'field']
    field_cancel = toss_field['winner'].count()
    field_win = toss_field.loc[toss_field['toss_winner'] == toss_field['winner']]
    field_lost = toss_field.loc[toss_field['toss_winner'] != toss_field['winner']]
    field_win = field_win.loc[field_win['result'] != 'runs']

    bat = pd.concat([bat_win,field_lost], ignore_index = True)
    field = pd.concat([field_win,bat_lost], ignore_index = True)

    dlu = len(match)-len(bat)-len(field)

    cancelled = len(match)-bat_cancel-field_cancel
    if cancelled != 0 :
        st.write('Matches got cancelled/ suspended :', cancelled)
    st.write('Matches won by batting first :', len(bat)-(len(toss_field)-field_cancel)+dlu)
    if len(bat) != 0 :
        st.write('Highest win margin (runs) :', int(bat['result_margin'].max()))
    st.write('Matches won by fielding first :', len(field)-(len(toss_bat)-bat_cancel))
    if len(field) != 0 :
        st.write('Highest win margin (wickets) :', int(field['result_margin'].max()))



if category == 'Head to Head Matches Stats' :

    st.header('Head to Head Matches Stats')
    team1 = st.selectbox('Select Team1', teams)
    team2 = st.selectbox('Select Team2', teams)

    d1 = matches.loc[matches['team1'] == team1]
    d1 = d1.loc[d1['team2'] == team2]
    d2 = matches.loc[matches['team2'] == team1]
    d2 = d2.loc[d2['team1'] == team2]
    data = pd.concat([d1,d2], ignore_index = True)

    if team1 == team2 :
        st.write('Both teams should not be same')

    else :
        if len(data) == 0 :
            st.write(team1, 'and', team2, 'did not play any matches together')
        else :
            cancel = data['winner'].count()
            st.write('Matches Played :', len(data))
            if len(data)-cancel != 0 :
                st.write('Matches got cancelled/suspended :', len(data)-cancel)
            t1 = data.loc[data['winner'] == team1]
            st.write(team1, 'won :', len(t1))
            t2 = data.loc[data['winner'] == team2]
            st.write(team2, 'won :', len(t2))



if category == 'Top Run Scorers' :

    st.header('Top Run Scorers')
    chosen = st.slider('Select number of top run scorers',1,100)
    runs = ball_data.groupby('batsman')['batsman_runs'].sum()
    bound = ball_data.groupby('batsman')['batsman_runs'].value_counts()
    strike = ball_data.loc[ball_data['extras_type'] != 'wides']['batsman'].value_counts()

    runs = pd.DataFrame(runs)
    names = runs.index.tolist()

    runs['sixes'] = ""
    runs['fours'] = ""
    for i in range(len(runs)) :
        if 6 in bound[names[i]] :
            runs['sixes'].iloc[i] = bound[names[i]][6]
        else :
            runs['sixes'].iloc[i] = 0

        if 4 in bound[names[i]] :
            runs['fours'].iloc[i] = bound[names[i]][4]
        else :
            runs['fours'].iloc[i] = 0

    runs.sort_values(by='batsman_runs', ascending = False, inplace = True)
    runs = runs[:chosen]

    runs['strike_rate'] = ""
    for i in range(len(runs)):
        runs['strike_rate'].iloc[i] = round((runs['batsman_runs'].iloc[i])*100/(strike[runs.index[i]]),2)

    runs.sort_values(by=['batsman_runs', 'strike_rate'], ascending = False, inplace = True)

    l = []
    for i in range(1,chosen+1):
        l.append(i)

    runs['position'] = l
    runs.rename(columns={'batsman_runs':'runs'}, inplace = True)
    st.write(runs)



if category == 'Top Wicket Takers':

    st.header('Top Wicket Takers')
    ball_data['dismissal_kind'].fillna('not out', inplace = True)
    bowler = ball_data.loc[ball_data['dismissal_kind'] != 'not out']
    bowler = bowler.loc[bowler['dismissal_kind'] != 'run out']
    bowler = bowler.loc[bowler['dismissal_kind'] != 'retired hurt']

    chosen = st.slider('Select number of top wicket holders',1,50)
    top_bowler = bowler['bowler'].value_counts()[:chosen]
    top_bowler = pd.DataFrame(top_bowler)
    not_byes = ball_data.loc[ball_data['extras_type'] != 'byes']
    not_legbyes = not_byes.loc[not_byes['extras_type'] != 'legbyes']
    runs_given = not_legbyes.groupby('bowler')['total_runs'].sum()
    normal_balls = ball_data.loc[(ball_data['extras_type'] != 'noballs')]
    normal_balls = normal_balls.loc[normal_balls['extras_type'] != 'wides']
    over = normal_balls['bowler'].value_counts()
    #print("hahahahahhahahahhah/////////")
    print(over)

    top_bowler['runs_given'] = ""
    top_bowler['economy_rate'] = ""
    for i in range(len(top_bowler)) :
        print(over[top_bowler.index[i]])
        top_bowler['runs_given'].iloc[i] = runs_given[top_bowler.index[i]]
        top_bowler['economy_rate'].iloc[i] = round(top_bowler['runs_given'].iloc[i]*6/(over[top_bowler.index[i]]),2)

    l = []
    for i in range(1,chosen+1):
        l.append(i)

    top_bowler['position'] = l
    top_bowler.rename(columns={'bowler':'wickets'}, inplace = True)
    st.write(top_bowler)



if category == 'Top Man of the Match Award Holders' :

    st.header('Top Man of the Match Award Holders')
    season = st.selectbox('Select Season', year)

    if season == "Overall" :
        mmp = matches
        chosen = st.slider('Select number of top man of the match players',1,20)
        top = mmp['player_of_match'].value_counts()[:chosen]
        st.write(top)

    else :

        mmp = matches.loc[matches['season'] == season]
        chosen = st.slider('Select number of top man of the match players',1,10)
        top = mmp['player_of_match'].value_counts()[:chosen]
        l = list(top.index)
        top = pd.DataFrame(top)

        team_name = []
        for i in l :
            k = mmp['winner'].loc[mmp['player_of_match'] == i].unique()
            team_name.append(k[0])

        top['team'] = team_name
        top.rename(columns={'player_of_match':'no_of_matches'}, inplace = True)
        st.write(top)

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

sb = pd.read_csv("./spongebob_episodes.csv")


# Rows 9-88 are data cleaning, converting "Running time", "Episode ",
# Copyright year", "U.S. viewers (millions)" columns into numerics (float/int) 

#cleaning "Running time" column, data about the length of every 1/2 episode
def clean_time_data(time_string):
    if "TBA" == time_string: 
        return np.nan # handles lack of data
    if "(original" in time_string:  # handles additional details included in data
        drop, time_string = time_string.split("'",1)
        time_string, drop = time_string.split(" (",1)
    if "[" in time_string: # handles details: cut vs uncut time when both included in cell
        drop, time_string = time_string.split("'", 1)
        time_string, drop = time_string.split("'", 1)
    if "," in time_string: # handles default formatting (ex: # minutes, # seconds)
        minutes, seconds = time_string.split(",")
        minutes = int(minutes.strip().replace(" minutes", "")) 
        if "seconds" in time_string: # handles "1 second" exception
            seconds = int(seconds.strip().replace(" seconds", ""))/60
        else:
            seconds = int(seconds.strip().replace(" second", ""))/60
        time = minutes+seconds
    else: # handles no seconds (ex: # minutes)
        time = int(time_string.strip().replace(" minutes", ""))
    return time

#using clean_time_data to update our data
sb["Running time"] = np.array([clean_time_data(time) for time in sb['Running time']])


#cleaning "Episode №" column, data about which episode this is chronologically in the series
def clean_episode_number(num):
   # num = str(num)
    if "a" in num:
        num = num.replace("a","")
        return int(num) + 0/2          # every episode #a is now episode #.0
    if "b" in num:
        num = num.replace("b","")
        return int(num) + 2/5           # every episode #b is now episode #.4
    if "c" in num:
        num = num.replace("c","")
        return int(num) + 9/10          # every episode #c is now episode #.9
    if "-" in num:
        num1, num2 = num.split("-")
        return (int(num1)+int(num2))/2  # every episode #_1 - #_2 is now the average of those two numbers
    return int(num) + 0/2               # every episode # is now episode # (float)

#using clean_episode_number to update our data
sb["Episode №"] = np.array([clean_episode_number(episode) for episode in sb['Episode №']])


#cleaning "Copyright year" column, column about the year episode was copyrighted
def clean_copyright_year(year):
    if "(" in year:
        return int(1999) #handles one exception to typical numbering convention
    if "[" in year:
        year, drop = year.split("[") #handles note data in some years (ex: 2001[note1])
        return int(year)
    
    return int(year)

#using clean_copyright_year to update our data
sb['Copyright year'] = np.array([clean_copyright_year(year) for year in sb['Copyright year']])


#cleaning "U.S. viewers (millions)" column, column about how many millions of people watched the episode
def clean_us_viewers(viewers):
    if pd.isna(viewers): #ex: Missing value
        return np.nan
    if "TBD" in viewers: #ex: TBD
        return np.nan
    if "Nicktoons" in viewers: #ex: ['N/A (Nicktoons)', '2.96 (Nick)']
        drop, viewers = viewers.split(", '")
        viewers, drop = viewers.split(" ")    
    if "CBS" in viewers: #ex: ['3.63 (CBS)', '4.61 (Nick)']
        drop, viewers = viewers.split("'", 1)
        viewers, drop = viewers.split(" ", 1)
    if "," in viewers: #ex: ['#oi', ----]:
        drop, viewers = viewers.split("'",1)
        viewers, drop = viewers.split("'",1)
    return float(viewers)   

#using clean_us_viewers to update our data
sb['U.S. viewers (millions)'] = np.array([clean_us_viewers(viewers) for viewers in sb['U.S. viewers (millions)']])


# dropping columns we won't be using
sb = sb[['Animation', 'Episode №', 'Running time',
         'Season №','Supervising Producer(s)', 'U.S. viewers (millions)',
         'Writer(s)','characters']]


#all ensuing rows create plots that demonstrate the relationship between different variables and viewership


# creating plot of running time vs viewership
sb_rt_view = sb[['Running time', 'U.S. viewers (millions)']].dropna()
#sns.scatterplot(data=sb_ep_view, x = "Episode №", y = "U.S. viewers (millions)", alpha=0.5)#, lowess=True, scatter_kws={'s': 5})
sns.scatterplot(data=sb_rt_view, x = "Running time", y = "U.S. viewers (millions)", alpha=0.5)#,  lowess=True, scatter_kws={'s': 25, 'alpha':0.5}, line_kws={'color': 'red'})
plt.title('U.S. Viewers (Millions) Over Running Time')
plt.xlabel('Running Time')
plt.ylabel('U.S. Viewers (Millions)')
plt.savefig("running time scatterplot.png", bbox_inches='tight')
plt.show()


# creating plot of episodes vs viewership
sb_ep_view = sb[['Episode №', 'U.S. viewers (millions)']].dropna()
#sns.scatterplot(data=sb_ep_view, x = "Episode №", y = "U.S. viewers (millions)", alpha=0.5)#, lowess=True, scatter_kws={'s': 5})
sns.regplot(data=sb_ep_view, x = "Episode №", y = "U.S. viewers (millions)",  lowess=True, scatter_kws={'s': 25, 'alpha':0.5}, line_kws={'color': 'red'})
plt.title('U.S. Viewers (Millions) Over Episodes')
plt.xlabel('Episode Number')
plt.ylabel('U.S. Viewers (Millions)')
plt.savefig("viewers over episodes.png", bbox_inches='tight')
plt.show()


#creating plot of season vs viewership
sd_szn_view = sb[['Season №', 'U.S. viewers (millions)']].groupby('Season №').mean()
sns.barplot(data=sd_szn_view, x="Season №", y="U.S. viewers (millions)")
plt.title('U.S. Viewers (Millions) Over Seasons')
plt.xlabel('Season Number')
plt.ylabel('U.S. Viewers (Millions)')
plt.savefig("viewers over seasons.png", bbox_inches='tight')
plt.show()


#creating avg animator plot
sns.scatterplot(ani_means, x="Animator", y="Average U.S. viewers (millions)",
                size="Total Episodes Worked On", sizes=(100,1000),
                hue="Season Started", alpha=0.5,
                edgecolor="black")
plt.xticks(rotation=45, ha='right')
plt.legend(bbox_to_anchor=(1.05, 1), ncol=1, borderpad = 1.5)
plt.title("Average Viewership (millions) Based on Animator")
plt.savefig("avg viewer by animator.png", bbox_inches='tight')
plt.show()


#manipulating data to make animator jitterplot
sb_aniviewep = sb[["Animation", "U.S. viewers (millions)", "Episode №"]]
def ani_mean(names):
    results = []
    for name in names:
        filtered_episodes = sb_aniviewep[sb_aniviewep["Animation"].str.contains(name, na=False)].copy()
        filtered_episodes['Animator'] = name

        if name in ["Bob Jaques","Michelle Bryan","Alex Conaway","Jordy Judge"]:
            filtered_episodes['season'] = "Newer Animator, Started in Seasons 8-14"
        else:
            filtered_episodes['season'] = "Original Animator, Started in Seasons 1-7"
    
        results.append(filtered_episodes)

    all_episodes = pd.concat(results).reset_index(drop=True)
    return(all_episodes)

names = ["Tom Yasumi", "Alan Smart", "Andrew Overtoom", "Edgar Larrazábal", "Fred Miller","Sean Dempsey", "Larry Leichliter", "Leonard Robinson","Frank Weiss", "Bob Jaques","Michelle Bryan","Alex Conaway","Jordy Judge"]
#creating jitterplot
palette = ["#ADD8E6","#FFC0CB"]
sns.stripplot(ani_mean(names), x="Animator", y="U.S. viewers (millions)",
                hue="season", alpha=0.5,
                edgecolor="black", jitter=True)
plt.xticks(rotation=45, ha='right')
plt.legend(bbox_to_anchor=(1.05, 1), ncol=1, borderpad = 1.5)
plt.title("Viewership (millions) Based on Animator")
plt.savefig("jitter viewer by animator.png", bbox_inches='tight')
plt.show()


#manipulating data to make producer boxplot
sb_prodviewep = sb[["Supervising Producer(s)", "U.S. viewers (millions)", "Episode №"]]
def prod_mean(names):
    results = []
    for name in names:
        filtered_episodes = sb_prodviewep[sb_prodviewep["Supervising Producer(s)"].str.contains(name, na=False)].copy()
        filtered_episodes['Supervising Producer(s)'] = name

        if name == "Paul Tibbitt":
            filtered_episodes['season'] = "Original Producer, Seasons 1-7"
        else:
            filtered_episodes['season'] = "Newer Producer, Seasons 8-14"
    
        results.append(filtered_episodes)

    all_episodes = pd.concat(results).reset_index(drop=True)
    return(all_episodes)

names = ["Paul Tibbitt", "Marc Ceccarelli", "Vincent Waller", "Jennie Monica"]
#creating boxplot
sns.boxplot(data=prod_mean(names), y="U.S. viewers (millions)", x="Supervising Producer(s)", hue = "season")#palette=["pink","blue","blue","blue"])
plt.title("Viewership Based on Supervising Producer")
plt.savefig("producer boxplot.png")
plt.show()


#manipulating data to create writer plots
writers_list_print = ', '.join(sb["Writer(s)"].dropna().unique())
writers_list_result = "['Stephen Hillenburg', 'Derek Drymon', 'Tim Hill'], ['Stephen Hillenburg', 'Derek Drymon', 'Tim Hill (uncredited)'], ['Peter Burns', 'Doug Lawrence', 'Paul Tibbitt'], ['Ennio Torresan', 'Erik Wiese', 'Stephen Hillenburg', 'Derek Drymon', 'Tim Hill'], ['Paul Tibbitt', 'Peter Burns'], ['Steve Fonti', 'Chris Mitchell', 'Peter Burns', 'Tim Hill'], ['Ennio Torresan, Jr.', 'Erik Wiese', 'Doug Lawrence'], ['Sherm Cohen', 'Aaron Springer', 'Doug Lawrence'], ['Sherm Cohen', 'Aaron Springer', 'Peter Burns'], ['Paul Tibbitt', 'Mark O'Hare', 'Doug Lawrence'], ['Steve Fonti', 'Chris Mitchell', 'Peter Burns'], ['Chuck Klein', 'Jay Lender', 'Doug Lawrence'], ['Ennio Torresan, Jr.', 'Erik Wiese', 'Peter Burns'], ['Steve Fonti', 'Chris Mitchell', 'Doug Lawrence'], ['Paul Tibbitt', 'Mark O'Hare', 'Peter Burns'], ['Paul Tibbitt', 'Doug Lawrence'], ['Aaron Springer', 'Erik Wiese', 'Doug Lawrence'], ['Aaron Springer', 'Erik Wiese', 'Merriwether Williams'], ['Paul Tibbitt', 'Ennio Torresan, Jr.', 'Doug Lawrence'], ['Chuck Klein', 'Jay Lender', 'Merriwether Williams'], ['Sherm Cohen', 'Vincent Waller', 'Merriwether Williams'], ['Paul Tibbitt', 'Ennio Torresan', 'David Fain'], ['Sherm Cohen', 'Vincent Waller', 'David Fain'], ['Chuck Klein', 'Jay Lender', 'David Fain'], ['Walt Dohrn', 'Paul Tibbitt', 'Merriwether Williams'], ['Aaron Springer', 'C.H. Greenblatt', 'Merriwether Williams'], ['Walt Dohrn', 'Paul Tibbitt', 'Doug Lawrence'], ['Jay Lender', 'William Reiss', 'Merriwether Williams'], ['Jay Lender', 'William Reiss', 'Doug Lawrence'], ['Jay Lender', 'Bill Reiss', 'Doug Lawrence'], ['Paul Tibbitt', 'Walt Dohrn', 'Doug Lawrence'], ['Paul Tibbitt', 'Walt Dohrn', 'Merriwether Williams'], ['Aaron Springer', 'C.H. Greenblatt', 'Doug Lawrence'], ['Jay Lender', 'William Reiss', 'David B. Fain'], ['C.H. Greenblatt', 'Aaron Springer', 'Merriwether Williams'], ['Doug Lawrence', 'Jay Lender', 'Dan Povenmire'], ['Doug Lawrence', 'Jay Lender', 'William Reiss'], ['Aaron Springer', 'C.H. Greenblatt', 'Mark O'Hare'], ['Walt Dohrn', 'Paul Tibbitt', 'Mark O'Hare'], ['Jay Lender', 'Dan Povenmire', 'Merriwether Williams'], ['Jay Lender', 'Sam Henderson', 'Mark O'Hare'], ['Walt Dohrn', 'Mark O'Hare'], ['Kent Osborne', 'Paul Tibbitt'], ['Jay Lender', 'Sam Henderson', 'Merriwether Williams'], ['Paul Tibbitt', 'Kaz'], ['Paul Tibbitt', 'Kent Osborne', 'Merriwether Williams'], ['Paul Tibbitt', 'Kaz (TV airings and digital releases)', 'Kent Osborne (DVD releases)'], ['Jay Lender', 'Sam Henderson', 'Merriwether Williams (Early airings, DVD releases, and international non-US airings)', 'Kent Osborne (American TV airings\ufeff[citation needed], digital releases, and streaming services)'], ['Paul Tibbitt', 'Kent Osborne'], ['C.H. Greenblatt', 'Kaz'], ['Aaron Springer', 'C.H. Greenblatt', 'Kent Osborne'], ['Paul Tibbitt', 'Kaz', 'Kent Osborne', 'Merriwether Williams'], ['C.H. Greenblatt', 'Kaz', 'Merriwether Williams'], ['Paul Tibbitt', 'Kent Osborne'], ['Paul Tibbitt', 'Kent Osborne', 'Joe Liss (Recent American TV airings,\ufeff[citation needed] digital versions, and streaming releases)', 'Merriwether Williams (Original airing, early airings, DVD releases, and international non-US airings)'], ['Jay Lender', 'Sam Henderson', 'Dan Povenmire (uncredited: songwriter only)', 'Merriwether Williams'], ['Paul Tibbitt', 'Kent Osborne', 'C.H. Greenblatt', 'Merriwether Williams'], ['C.H. Greenblatt', 'Paul Tibbitt'], ['Mike Bell', 'Paul Tibbitt'], ['Mike Bell', 'Tim Hill'], ['Tim Hill', 'Mike Mitchell', 'Vincent Waller'], ['Aaron Springer', 'Paul Tibbitt'], ['Kyle McCulloch', 'Aaron Springer', 'Vincent Waller'], Mike Bell, ['Zeus Cervas', 'Erik C. Wiese', 'Tim Hill'], ['Luke Brookshier', 'Tom King', 'Steven Banks'], ['Zeus Cervas', 'Erik Wiese', 'Steven Banks (uncredited; songwriter only)', 'Tim Hill'], ['Luke Brookshier', 'Tom King', 'Tim Hill'], ['Casey Alexander', 'Chris Mitchell', 'Paul Tibbitt'], ['Casey Alexander', 'Chris Mitchell', 'Tim Hill'], ['Zeus Cervas', 'Erik Wiese', 'Steven Banks'], ['Zeus Cervas', 'Erik Wiese', 'Tim Hill'], ['Luke Brookshier', 'Tom King', 'Paul Tibbitt'], ['Casey Alexander', 'Chris Mitchell', 'Steven Banks'], ['Casey Alexander', 'Chris Mitchell', 'Dani Michaeli'], ['Luke Brookshier', 'Tom King', 'Dani Michaeli'], ['Zeus Cervas', 'Erik Wiese', 'Dani Michaeli'], ['Nate Cash', 'Tuck Tucker', 'Steven Banks'], ['Luke Brookshier (live-action writer only)', 'Tom King (live-action writer only)', 'Casey Alexander', 'Zeus Cervas', 'Mike Mitchell', 'Steven Banks', 'Tim Hill', 'Paul Tibbitt (live-action writer only)'], ['Luke Brookshier', 'Tom King', 'Steven Banks', 'Dani Michaeli'], ['Nate Cash', 'Steven Banks'], ['Casey Alexander', 'Zeus Cervas', 'Richard Pursel'], ['Casey Alexander', 'Zeus Cervas', 'Dani Michaeli (American TV airings, digital releases, and streaming services)', 'Richard Pursel (DVD releases and international non-US airings)'], ['Nate Cash', 'Tuck Tucker', 'Richard Pursel'], ['Luke Brookshier', 'Tom King', 'Eric Shaw'], ['Casey Alexander', 'Zeus Cervas', 'Eric Shaw'], ['Luke Brookshier', 'Richard Pursel'], ['Aaron Springer', 'Eric Shaw'], ['Casey Alexander', 'Zeus Cervas', 'Steven Banks'], ['Nate Cash', 'Dani Michaeli'], ['Tuck Tucker', 'Eric Shaw'], ['Casey Alexander', 'Zeus Cervas', 'Aaron Springer (live-action writer only)', 'Steven Banks (additional material for the live-action sequence)', 'Dani Michaeli', 'Vincent Waller (songwriter only)', 'Paul Tibbitt (songwriter and live-action writer only)'], ['Casey Alexander', 'Dani Michaeli', 'Steven Banks (additional story writing)'], ['Zeus Cervas', 'Dani Michaeli'], ['Greg Miller', 'Aaron Springer', 'Eric Shaw'], ['Nate Cash', 'Tuck Tucker', 'Eric Shaw'], ['Chris Reccardi', 'Aaron Springer', 'Dani Michaeli'], ['Luke Brookshier', 'Nate Cash', 'Dani Michaeli'], ['Luke Brookshier', 'Tom King', 'Steven Banks', 'Richard Pursel'], ['Chris Reccardi', 'Aaron Springer', 'Richard Pursel'], ['Luke Brookshier', 'Nate Cash', 'Eric Shaw'], ['Charlie Bean', 'Aaron Springer', 'Steven Banks'], ['Aaron Springer', 'Steven Banks'], ['Aaron Springer', 'Dani Michaeli'], ['Casey Alexander', 'Zeus Cervas', 'Derek Iversen'], ['Luke Brookshier', 'Nate Cash', 'Richard Pursel'], ['Luke Brookshier', 'Nate Cash', 'Steven Banks'], ['Nate Cash', 'Sean Charmatz', 'Steven Banks'], ['Chris Reccardi', 'Dani Michaeli'], ['Casey Alexander', 'Zeus Cervas', 'Dani Michaeli'], ['Aaron Springer', 'Richard Pursel'], ['Tom King', 'Dani Michaeli'], ['Aaron Springer', 'Paul Tibbitt', 'Steven Banks'], ['Aaron Springer', 'Derek Iversen'], ['Nate Cash', 'Sean Charmatz', 'Derek Iversen'], ['Casey Alexander', 'Zeus Cervas', 'Vincent Waller (originally)', 'Derek Iversen'], ['Luke Brookshier', 'Nate Cash', 'Derek Iversen'], ['Sean Charmatz', 'Dani Michaeli'], ['Luke Brookshier', 'Nate Cash', 'Steven Banks', 'Paul Tibbitt'], ['Casey Alexander', 'Zeus Cervas', 'Aaron Springer', 'Steven Banks', 'Paul Tibbitt'], ['Casey Alexander', 'Zeus Cervas', 'Doug Lawrence'], ['Zeus Cervas', 'Sean Charmatz', 'Derek Iversen'], ['Luke Brookshier', 'Nate Cash', 'Doug Lawrence'], ['Aaron Springer', 'Steven Banks', 'Derek Iversen'], ['Casey Alexander', 'Zeus Cervas', 'Steven Banks', 'Dani Michaeli'], ['Nate Cash', 'Sean Charmatz', 'Doug Lawrence'], ['Aaron Springer', 'Sean Charmatz', 'Richard Pursel'], ['Casey Alexander', 'Zeus Cervas', 'Sean Charmatz', 'Richard Pursel'], ['Casey Alexander', 'Zeus Cervas', 'Derek Iversen', 'Dani Michaeli', 'Richard Pursel'], ['Aaron Springer', 'Doug Lawrence'], ['Aaron Springer', 'Sean Charmatz', 'Derek Iversen'], ['Luke Brookshier', 'Nate Cash', 'Sean Charmatz', 'Dani Michaeli'], ['Sean Charmatz', 'Vincent Waller', 'Steven Banks'], ['Luke Brookshier', 'Marc Ceccarelli', 'Sean Charmatz', 'Steven Banks'], ['Luke Brookshier', 'Marc Ceccarelli', 'Derek Iversen'], ['Aaron Springer', 'Andrew Goodman', 'Dani Michaeli'], ['Casey Alexander', 'Zeus Cervas', 'Derek Iversen', 'Doug Lawrence (American TV airings)', 'Andrew Goodman'], ['Luke Brookshier', 'Marc Ceccarelli', 'Doug Lawrence'], ['Sean Charmatz', 'Vincent Waller', 'Paul Tibbitt'], ['Luke Brookshier', 'Marc Ceccarelli', 'Dani Michaeli'], ['Luke Brookshier', 'Marc Ceccarelli', 'Steven Banks'], ['Luke Brookshier', 'Marc Ceccarelli', 'Derek Iversen', 'Doug Lawrence'], ['Aaron Springer', 'Sean Charmatz', 'Dani Michaeli'], ['Marc Ceccarelli', 'Derek Iversen'], ['Casey Alexander', 'Zeus Cervas', 'Blake Lemons', 'Derek Iversen'], ['Casey Alexander', 'Zeus Cervas', 'Blake Lemons', 'Andrew Goodman'], ['Marc Ceccarelli', 'Luke Brookshier', 'Derek Iversen', 'Doug Lawrence'], ['Marc Ceccarelli', 'Luke Brookshier', 'Doug Lawrence'], ['Casey Alexander', 'Zeus Cervas', 'Blake Lemons', 'Doug Lawrence'], ['Jack Pendarvis', 'Derek Iversen (uncredited)'], Jack Pendarvis, ['Kyle McCulloch', 'Jack Pendarvis'], Kyle McCulloch, ['Kaz', 'Derek Iversen (uncredited)', 'Doug Lawrence (uncredited)'], Kaz, ['Josh Androsky', 'Daniel Dominguez'], Clare O'Kane, ['Solomon Georgio', 'Casey Alexander (2014 version, uncredited)', 'Zeus Cervas (2014 version, uncredited)'], ['Kaz', 'Kyle McCulloch'], Doug Lawrence, Andrew Goodman, ['Daniel Dominguez', 'Josh Androsky'], ['Kaz', 'Marc Ceccarelli (uncredited)'], ['Kaz', 'Stephen Hillenburg (story, uncredited)'], Ben Gruber, Richard Pursel, Dani Michaeli, ['Brian Morante', 'Doug Lawrence'], ['Chris Allison', 'Ryan Kramer', 'Kaz'], Luke Brookshier, ['Kaz', 'Dave Cunningham (story)'], Zeus Cervas, ['Andrew Goodman', 'John Trabbic'], ['Zeus Cervas', 'Kaz'], ['Luke Brookshier (uncredited)', 'Fred Osmond'], ['Kaz', 'Vincent Waller (additional writing)', 'Marc Ceccarelli (additional writing)', 'Doug Lawrence (additional writing)', 'Andrew Goodman (additional writing)', 'Luke Brookshier (additional writing)'], ['Kaz', 'Doug Lawrence'], ['Andrew Goodman', 'Benjamin Arcand (uncredited)'], ['John Trabbic (uncredited)', 'Doug Lawrence'], Danny Giovannini, ['Andrew Goodman', 'Adam Paloian (uncredited)'], ['Benjamin Arcand (uncredited)', 'Luke Brookshier']"
writers_list_print_2 = writers_list_result.replace("], [", ", ")
writers_list_result_hand_cleaned = ['Stephen Hillenburg', 'Derek Drymon', 'Tim Hill', 'Stephen Hillenburg', 'Derek Drymon', 'Tim Hill (uncredited)', 'Peter Burns', 'Doug Lawrence', 'Paul Tibbitt', 'Ennio Torresan', 'Erik Wiese', 'Stephen Hillenburg', 'Derek Drymon', 'Tim Hill', 'Paul Tibbitt', 'Peter Burns', 'Steve Fonti', 'Chris Mitchell', 'Peter Burns', 'Tim Hill', 'Ennio Torresan, Jr.', 'Erik Wiese', 'Doug Lawrence', 'Sherm Cohen', 'Aaron Springer', 'Doug Lawrence', 'Sherm Cohen', 'Aaron Springer', 'Peter Burns', 'Paul Tibbitt', "Mark O'Hare", 'Doug Lawrence', 'Steve Fonti', 'Chris Mitchell', 'Peter Burns', 'Chuck Klein', 'Jay Lender', 'Doug Lawrence', 'Ennio Torresan, Jr.', 'Erik Wiese', 'Peter Burns', 'Steve Fonti', 'Chris Mitchell', 'Doug Lawrence', 'Paul Tibbitt', 'Peter Burns', 'Paul Tibbitt', 'Doug Lawrence', 'Aaron Springer', 'Erik Wiese', 'Doug Lawrence', 'Aaron Springer', 'Erik Wiese', 'Merriwether Williams', 'Paul Tibbitt', 'Ennio Torresan, Jr.', 'Doug Lawrence', 'Chuck Klein', 'Jay Lender', 'Merriwether Williams', 'Sherm Cohen', 'Vincent Waller', 'Merriwether Williams', 'Paul Tibbitt', 'Ennio Torresan', 'David Fain', 'Sherm Cohen', 'Vincent Waller', 'David Fain', 'Chuck Klein', 'Jay Lender', 'David Fain', 'Walt Dohrn', 'Paul Tibbitt', 'Merriwether Williams', 'Aaron Springer', 'C.H. Greenblatt', 'Merriwether Williams', 'Walt Dohrn', 'Paul Tibbitt', 'Doug Lawrence', 'Jay Lender', 'William Reiss', 'Merriwether Williams', 'Jay Lender', 'William Reiss', 'Doug Lawrence', 'Jay Lender', 'Bill Reiss', 'Doug Lawrence', 'Paul Tibbitt', 'Walt Dohrn', 'Doug Lawrence', 'Paul Tibbitt', 'Walt Dohrn', 'Merriwether Williams', 'Aaron Springer', 'C.H. Greenblatt', 'Doug Lawrence', 'Jay Lender', 'William Reiss', 'David B. Fain', 'C.H. Greenblatt', 'Aaron Springer', 'Merriwether Williams', 'Doug Lawrence', 'Jay Lender', 'Dan Povenmire', 'Doug Lawrence', 'Jay Lender', 'William Reiss', 'Aaron Springer', 'C.H. Greenblatt', 'Walt Dohrn', 'Paul Tibbitt', 'Jay Lender', 'Dan Povenmire', 'Merriwether Williams', 'Jay Lender', 'Sam Henderson', 'Walt Dohrn', 'Kent Osborne', 'Paul Tibbitt', 'Jay Lender', 'Sam Henderson', 'Merriwether Williams', 'Paul Tibbitt', 'Kaz', 'Paul Tibbitt', 'Kent Osborne', 'Merriwether Williams', 'Paul Tibbitt', 'Kaz (TV airings and digital releases)', 'Kent Osborne (DVD releases)', 'Jay Lender', 'Sam Henderson', 'Merriwether Williams (Early airings, DVD releases, and international non-US airings)', 'Kent Osborne (American TV airings﻿[citation needed], digital releases, and streaming services)', 'Paul Tibbitt', 'Kent Osborne', 'C.H. Greenblatt', 'Kaz', 'Aaron Springer', 'C.H. Greenblatt', 'Kent Osborne', 'Paul Tibbitt', 'Kaz', 'Kent Osborne', 'Merriwether Williams', 'C.H. Greenblatt', 'Kaz', 'Merriwether Williams', 'Paul Tibbitt', 'Kent Osborne', 'Paul Tibbitt', 'Kent Osborne', 'Joe Liss (Recent American TV airings,﻿[citation needed] digital versions, and streaming releases)', 'Merriwether Williams (Original airing, early airings, DVD releases, and international non-US airings)', 'Jay Lender', 'Sam Henderson', 'Dan Povenmire (uncredited: songwriter only)', 'Merriwether Williams', 'Paul Tibbitt', 'Kent Osborne', 'C.H. Greenblatt', 'Merriwether Williams', 'C.H. Greenblatt', 'Paul Tibbitt', 'Mike Bell', 'Paul Tibbitt', 'Mike Bell', 'Tim Hill', 'Tim Hill', 'Mike Mitchell', 'Vincent Waller', 'Aaron Springer', 'Paul Tibbitt', 'Kyle McCulloch', 'Aaron Springer', 'Vincent Waller', 'Mike Bell', 'Zeus Cervas', 'Erik C. Wiese', 'Tim Hill', 'Luke Brookshier', 'Tom King', 'Steven Banks', 'Zeus Cervas', 'Erik Wiese', 'Steven Banks (uncredited; songwriter only)', 'Tim Hill', 'Luke Brookshier', 'Tom King', 'Tim Hill', 'Casey Alexander', 'Chris Mitchell', 'Paul Tibbitt', 'Casey Alexander', 'Chris Mitchell', 'Tim Hill', 'Zeus Cervas', 'Erik Wiese', 'Steven Banks', 'Zeus Cervas', 'Erik Wiese', 'Tim Hill', 'Luke Brookshier', 'Tom King', 'Paul Tibbitt', 'Casey Alexander', 'Chris Mitchell', 'Steven Banks', 'Casey Alexander', 'Chris Mitchell', 'Dani Michaeli', 'Luke Brookshier', 'Tom King', 'Dani Michaeli', 'Zeus Cervas', 'Erik Wiese', 'Dani Michaeli', 'Nate Cash', 'Tuck Tucker', 'Steven Banks', 'Luke Brookshier (live-action writer only)', 'Tom King (live-action writer only)', 'Casey Alexander', 'Zeus Cervas', 'Mike Mitchell', 'Steven Banks', 'Tim Hill', 'Paul Tibbitt (live-action writer only)', 'Luke Brookshier', 'Tom King', 'Steven Banks', 'Dani Michaeli', 'Nate Cash', 'Steven Banks', 'Casey Alexander', 'Zeus Cervas', 'Richard Pursel', 'Casey Alexander', 'Zeus Cervas', 'Dani Michaeli (American TV airings, digital releases, and streaming services)', 'Richard Pursel (DVD releases and international non-US airings)', 'Nate Cash', 'Tuck Tucker', 'Richard Pursel', 'Luke Brookshier', 'Tom King', 'Eric Shaw', 'Casey Alexander', 'Zeus Cervas', 'Eric Shaw', 'Luke Brookshier', 'Richard Pursel', 'Aaron Springer', 'Eric Shaw', 'Casey Alexander', 'Zeus Cervas', 'Steven Banks', 'Nate Cash', 'Dani Michaeli', 'Tuck Tucker', 'Eric Shaw', 'Casey Alexander', 'Zeus Cervas', 'Aaron Springer (live-action writer only)', 'Steven Banks (additional material for the live-action sequence)', 'Dani Michaeli', 'Vincent Waller (songwriter only)', 'Paul Tibbitt (songwriter and live-action writer only)', 'Casey Alexander', 'Dani Michaeli', 'Steven Banks (additional story writing)', 'Zeus Cervas', 'Dani Michaeli', 'Greg Miller', 'Aaron Springer', 'Eric Shaw', 'Nate Cash', 'Tuck Tucker', 'Eric Shaw', 'Chris Reccardi', 'Aaron Springer', 'Dani Michaeli', 'Luke Brookshier', 'Nate Cash', 'Dani Michaeli', 'Luke Brookshier', 'Tom King', 'Steven Banks', 'Richard Pursel', 'Chris Reccardi', 'Aaron Springer', 'Richard Pursel', 'Luke Brookshier', 'Nate Cash', 'Eric Shaw', 'Charlie Bean', 'Aaron Springer', 'Steven Banks', 'Aaron Springer', 'Steven Banks', 'Aaron Springer', 'Dani Michaeli', 'Casey Alexander', 'Zeus Cervas', 'Derek Iversen', 'Luke Brookshier', 'Nate Cash', 'Richard Pursel', 'Luke Brookshier', 'Nate Cash', 'Steven Banks', 'Nate Cash', 'Sean Charmatz', 'Steven Banks', 'Chris Reccardi', 'Dani Michaeli', 'Casey Alexander', 'Zeus Cervas', 'Dani Michaeli', 'Aaron Springer', 'Richard Pursel', 'Tom King', 'Dani Michaeli', 'Aaron Springer', 'Paul Tibbitt', 'Steven Banks', 'Aaron Springer', 'Derek Iversen', 'Nate Cash', 'Sean Charmatz', 'Derek Iversen', 'Casey Alexander', 'Zeus Cervas', 'Vincent Waller (originally)', 'Derek Iversen', 'Luke Brookshier', 'Nate Cash', 'Derek Iversen', 'Sean Charmatz', 'Dani Michaeli', 'Luke Brookshier', 'Nate Cash', 'Steven Banks', 'Paul Tibbitt', 'Casey Alexander', 'Zeus Cervas', 'Aaron Springer', 'Steven Banks', 'Paul Tibbitt', 'Casey Alexander', 'Zeus Cervas', 'Doug Lawrence', 'Zeus Cervas', 'Sean Charmatz', 'Derek Iversen', 'Luke Brookshier', 'Nate Cash', 'Doug Lawrence', 'Aaron Springer', 'Steven Banks', 'Derek Iversen', 'Casey Alexander', 'Zeus Cervas', 'Steven Banks', 'Dani Michaeli', 'Nate Cash', 'Sean Charmatz', 'Doug Lawrence', 'Aaron Springer', 'Sean Charmatz', 'Richard Pursel', 'Casey Alexander', 'Zeus Cervas', 'Sean Charmatz', 'Richard Pursel', 'Casey Alexander', 'Zeus Cervas', 'Derek Iversen', 'Dani Michaeli', 'Richard Pursel', 'Aaron Springer', 'Doug Lawrence', 'Aaron Springer', 'Sean Charmatz', 'Derek Iversen', 'Luke Brookshier', 'Nate Cash', 'Sean Charmatz', 'Dani Michaeli', 'Sean Charmatz', 'Vincent Waller', 'Steven Banks', 'Luke Brookshier', 'Marc Ceccarelli', 'Sean Charmatz', 'Steven Banks', 'Luke Brookshier', 'Marc Ceccarelli', 'Derek Iversen', 'Aaron Springer', 'Andrew Goodman', 'Dani Michaeli', 'Casey Alexander', 'Zeus Cervas', 'Derek Iversen', 'Doug Lawrence (American TV airings)', 'Andrew Goodman', 'Luke Brookshier', 'Marc Ceccarelli', 'Doug Lawrence', 'Sean Charmatz', 'Vincent Waller', 'Paul Tibbitt', 'Luke Brookshier', 'Marc Ceccarelli', 'Dani Michaeli', 'Luke Brookshier', 'Marc Ceccarelli', 'Steven Banks', 'Luke Brookshier', 'Marc Ceccarelli', 'Derek Iversen', 'Doug Lawrence', 'Aaron Springer', 'Sean Charmatz', 'Dani Michaeli', 'Marc Ceccarelli', 'Derek Iversen', 'Casey Alexander', 'Zeus Cervas', 'Blake Lemons', 'Derek Iversen', 'Casey Alexander', 'Zeus Cervas', 'Blake Lemons', 'Andrew Goodman', 'Marc Ceccarelli', 'Luke Brookshier', 'Derek Iversen', 'Doug Lawrence', 'Marc Ceccarelli', 'Luke Brookshier', 'Doug Lawrence', 'Casey Alexander', 'Zeus Cervas', 'Blake Lemons', 'Doug Lawrence', 'Jack Pendarvis', 'Derek Iversen (uncredited)', 'Jack Pendarvis', 'Kyle McCulloch', 'Jack Pendarvis', 'Kyle McCulloch', 'Kaz', 'Derek Iversen (uncredited)', 'Doug Lawrence (uncredited)', 'Kaz', 'Josh Androsky', 'Daniel Dominguez', "Clare O'Kane", 'Solomon Georgio', 'Casey Alexander (2014 version, uncredited)', 'Zeus Cervas (2014 version, uncredited)', 'Kaz', 'Kyle McCulloch', 'Doug Lawrence', 'Andrew Goodman', 'Daniel Dominguez', 'Josh Androsky', 'Kaz', 'Marc Ceccarelli (uncredited)', 'Kaz', 'Stephen Hillenburg (story, uncredited)', 'Ben Gruber', 'Richard Pursel', 'Dani Michaeli', 'Brian Morante', 'Doug Lawrence', 'Chris Allison', 'Ryan Kramer', 'Kaz', 'Luke Brookshier', 'Kaz', 'Dave Cunningham (story)', 'Zeus Cervas', 'Andrew Goodman', 'John Trabbic', 'Zeus Cervas', 'Kaz', 'Luke Brookshier (uncredited)', 'Fred Osmond', 'Kaz', 'Vincent Waller (additional writing)', 'Marc Ceccarelli (additional writing)', 'Doug Lawrence (additional writing)', 'Andrew Goodman (additional writing)', 'Luke Brookshier (additional writing)', 'Kaz', 'Doug Lawrence', 'Andrew Goodman', 'Benjamin Arcand (uncredited)', 'John Trabbic (uncredited)', 'Doug Lawrence', 'Danny Giovannini', 'Andrew Goodman', 'Adam Paloian (uncredited)', 'Benjamin Arcand (uncredited)', 'Luke Brookshier']
writers_list = writers_list_result_hand_cleaned

for i in range(len(writers_list)):
    if "(" in writers_list[i]:
        newname, drop = writers_list[i].split(" (", 1)
        writers_list[i] = newname

writers = list(set(writers_list))
sb_wriview = sb[["Writer(s)", "U.S. viewers (millions)", "Episode №"]]
## got list, names

def write_mean(names):
    results = []
    for name in names:
        episodes = sb_wriview[sb_wriview["Writer(s)"].str.contains(name, na=False)]
        episodes['Writer'] = name
        episodes['Total Worked On'] = len(episodes)
        episodes['Average Viewership'] = episodes["U.S. viewers (millions)"].mean()
        if name in ["Doug Lawrence", "Luke Brookshier", "Zeus Cervas", "Casey Alexander", "Aaron Springer"]:
            episodes['season'] = "Original Writer (Seasons 1+)"
        else:
            episodes['season'] = "Newer Writer, (Seasons 8+)"
        results.append(episodes)
    all_episodes = pd.concat(results).reset_index(drop=True)
    return all_episodes

tenwriters = ["Doug Lawrence", "Luke Brookshier", "Zeus Cervas", "Casey Alexander", "Aaron Springer","Kaz", "Kyle McCulloch", "Ben Gruber","Danny Giovannini", "Jack Pendarvis", "Mike Bell"]
writer_df = write_mean(writers)
writer_df_asc = writer_df.sort_values("Total Worked On", ascending = False)
#create average viewership plot
sns.scatterplot(writer_df_asc, x="Writer", y="Average Viewership",
                size="Total Worked On", sizes=(100,1000),
                hue="season", alpha=0.5)
plt.xticks(rotation=45, ha='right')
plt.legend(bbox_to_anchor=(1.05, 1), ncol=1, borderpad = 1.5)
plt.title("Average Viewership (millions) Based on Writer")
plt.ylabel("Average U.S. viewers (millions)")
plt.savefig("bubble plot avg writer.png", bbox_inches='tight')
plt.show()
#create jitterplot
palette = ["#ADD8E6","#FFC0CB"]
#sns.barplot(writer_df_asc, x = "Writer", y = "Average Viewership", hue = "season")
sns.stripplot(writer_df_asc, x="Writer", y="U.S. viewers (millions)",
                hue="season", alpha=0.5,
                edgecolor="black", jitter=True)
plt.xticks(rotation=45, ha='right')
plt.legend(bbox_to_anchor=(1.05, 1), ncol=1, borderpad = 1.5)
plt.title("Viewership (millions) Based on Writer")
plt.savefig("jitter viewer by writer.png", bbox_inches='tight')
plt.show()


#manipulating data to make characters density plot
sb_charview = sb[["characters", "U.S. viewers (millions)", "Season №"]]

def char_add(names):
    results = []
    for name in names:
        episodes = sb_charview[sb_charview["characters"].str.contains(name, na=False)]
        episodes['Character'] = name
        results.append(episodes)
    all_episodes = pd.concat(results).reset_index(drop=True)
    return all_episodes

names = ["SpongeBob SquarePants", "Patrick Star", "Squidward Tentacles", "Eugene H. Krabs", "Sheldon J. Plankton", "Sandy Cheeks", "Gary the Snail"]
#names = ["Squidward Tentacles", "SpongeBob SquarePants", "Sheldon J. Plankton", "Eugene H. Krabs", "Gary the Snail", "Sandy Cheeks", "Patrick Star"]
char_df = char_add(names)
#create density plot
sns.kdeplot(char_df, x='U.S. viewers (millions)', hue='Character', palette='viridis')#, fill=True)
plt.title("Density Plot of Viewership, Based on Character ")
plt.xlabel("Viewership (millions) Based on Character")
plt.savefig("character density plot.png")
plt.show()
#create weird blurry line plot that kind of looks cool?
sns.lineplot(char_df, x='Season №', y='U.S. viewers (millions)', hue='Character', palette='viridis')#, fill=True)
plt.title("Density Plot of Viewership vs ")
plt.xlabel("Viewership (millions) Based on Animator")
plt.show()

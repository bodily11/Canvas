import pandas as pd
import numpy as np
import datetime
import time
user = 0
course = 0
page_views = []
assignments = []
df = pd.read_csv('C:\Users\Bob\Desktop\Projects\course_88_581.csv',header=3)
c = pd.read_csv('C:\Users\Bob\Desktop\Projects\course_88_581.csv',header=0,nrows=1)

row_number = 0
for row in range(len(df.index)):
    if df.loc[row_number, "Start Time"] == '0000-00-00 00:00:00':
        df.loc[row_number, "Start Time"] = 0
        row_number += 1
    else:     
        df.loc[row_number, "Start Time"] = time.mktime(datetime.datetime.strptime(df.loc[row_number, 'Start Time'], "%Y-%m-%d %H:%M:%S").timetuple())
        row_number += 1

row_number = 0
for row in range(len(df.index)):
    if df.loc[row_number, "Stop Time"] == '0000-00-00 00:00:00' or df.loc[row_number, "Stop Time"] == '0000-00-00 00:00:00 ':
        df.loc[row_number, "Stop Time"] = 0
        row_number += 1
    else:

        df.loc[row_number, "Stop Time"] = time.mktime(datetime.datetime.strptime(df.loc[row_number, 'Stop Time'], "%Y-%m-%d %H:%M:%S").timetuple())
        row_number += 1

# if there isn't an active time, use subtraction between page views
df.loc[df["Active Time"] > -1, "Links"] = 999
df["Active Time"] = df["Active Time"].where(df["Active Time"] > 0, df['Stop Time'] - df['Start Time'])

# get page views out of the complete array
page_views = df[df.Message == "PAGE VIEW"]

# get assignments out of the complete array
assignments = df[df['Title'].str.contains("ASSIGNMENT:")]

# get quizzes out of the complete array
quizzes = df[df['Title'].str.contains("QUIZ:")]

# get discussion posts created and replied to out of complete array
posts = df[df['Title'].str.contains("CREATED:")]
replies = df[df['Title'].str.contains("REPLY TO:")]

# Categorize pages into Content, Procedural, and Social
page_views['Page Type'] = 'MISSING'
# procedural pages
page_views.loc[(page_views['Title'] == "courses")|
                (page_views['Title'] == "profile")|
                (page_views['Title'] == "context")|
                (page_views['Title'] == "gradebooks")|
                (page_views['Title'] == "calendars"),'Page Type'] = 'Procedural'
# content pages
page_views.loc[(page_views['Title'] == "assignments")|
                (page_views['Title'] == "users")|
                (page_views['Title'] == "submissions")|
                (page_views['Title'] == "files")|
                (page_views['Title'] == "wiki_pages")|
                (page_views['Title'] == "quizzes/quizzes"),'Page Type'] = "Content"
# social pages
page_views.loc[(page_views['Title'] == "conversations")|
                (page_views['Title'] == "discussion_topics_api")|
                (page_views['Title'] == "discussion_topics"),'Page Type'] = "Social"

# Get the total number of page views
page_view_counts = page_views['Start Time'].count()

# Categorize pages into Scan, Normal, and Time Out
page_views['Page Time'] = 'MISSING'
page_views.loc[(page_views["Active Time"] > 3600),'Page Time'] = "Time Out"
page_views.loc[(page_views["Active Time"] <= 3600)&(page_views["Active Time"] > 10),'Page Time'] = "Normal"
page_views.loc[(page_views["Active Time"] <= 10),'Page Time'] = "Scan"

# Calculate average time on page for content, procedural, and social pages
social_time = page_views[(page_views["Active Time"] <= 3600)&(page_views["Page Type"] == "Social")]
social_time_mean = social_time['Active Time'].mean()
procedural_time = page_views[(page_views["Active Time"] <= 3600)&(page_views["Page Type"] == "Procedural")]
procedural_time_mean = procedural_time['Active Time'].mean()
content_time = page_views[(page_views["Active Time"] <= 3600)&(page_views["Page Type"] == "Content")]
content_time_mean = content_time['Active Time'].mean()

# Substitute Time Out times with average times on page based on category
page_views.loc[(page_views['Active Time'] > 3600)&
                (page_views['Links'] != 999)&
                (page_views['Page Type'] == "Content"),"Active Time"] = content_time_mean
page_views.loc[(page_views['Active Time'] > 3600)&
                (page_views['Links'] != 999)&
                (page_views['Page Type'] == "Procedural"),"Active Time"] = procedural_time_mean
page_views.loc[(page_views['Active Time'] > 3600)&
                (page_views['Links'] != 999)&
                (page_views['Page Type'] == "Social"),"Active Time"] = social_time_mean

# Total time for each category
content_time_2 = page_views[(page_views["Page Type"] == "Content")]
content_time_total = content_time_2['Active Time'].sum()
procedural_time_2 = page_views[(page_views["Page Type"] == "Procedural")]
procedural_time_total = procedural_time_2['Active Time'].sum()
social_time_2 = page_views[(page_views["Page Type"] == "Social")]
social_time_total = social_time_2['Active Time'].sum()

# Number of scan, normal, and time out pages
page_time_count = page_views['Page Time'].value_counts()

# Number of content pages, procedural pages, and social pages
page_type_count = page_views['Page Type'].value_counts()

url_set = set(page_views['URL'])
feature_list = ["url", "Counts", "Time"]
d = pd.DataFrame(0, index = np.arange(len(url_set)), columns = feature_list)
row_count = 0
for url in url_set:
    tempvar = page_views.loc[(page_views['URL'] == url)]
    d.loc[row_count, 'url'] = url
    d.loc[row_count, 'Time'] = tempvar['Active Time'].sum()
    d.loc[row_count, 'Counts'] = tempvar['Active Time'].count()
    row_count += 1
    
# Content, Procedural, and Social combined with Scan, Normal, Time Out, and Repeat
page_type_list = ["Content","Procedural","Social"]
page_time_list = ["Scan","Normal","Time Out"]
count_time = ["Count","Time"]
type_time = ["ContentScanCount","ContentScanTime","ContentNormalCount","ContentNormalTime","ContentTime OutCount","ContentTime OutTime","ProceduralScanCount","ProceduralScanTime","ProceduralNormalCount","ProceduralNormalTime","ProceduralTime OutCount","ProceduralTime OutTime","SocialScanCount","SocialScanTime","SocialNormalCount","SocialNormalTime","SocialTime OutCount","SocialTime OutTime"]
e = pd.DataFrame(0, index = np.arange(1), columns = type_time)
row_count = 0
for ptype in page_type_list:
    for ptime in page_time_list:
        for category in count_time:
            tempvar = page_views.loc[(page_views['Page Type'] == ptype)&(page_views['Page Time'] == ptime)]
            if category == "Count":
                e.loc[row_count, ptype + ptime + category] = tempvar['Active Time'].count()
            elif category == "Time":
                e.loc[row_count, ptype + ptime + category] = tempvar['Active Time'].sum()
            

# Get amount of time the assignment was submitted before the due date (parse the cell based on numbers spaces, etc)
# Also grab the URL right before the assignment submission to get the Canvas ID for the assignment
assignments['Time_Before_Due_Date'] = assignments['On Time'].str.split(' ')
assignments['Time_Before_Due_Date'].fillna(0, inplace=True)
duedateindex = list(assignments.index)
row_count = 0
for row in assignments['Time_Before_Due_Date']:    
    if duedateindex[row_count] == 0:
        assignments.loc[duedateindex[row_count], 'testURL'] = df.loc[duedateindex[row_count], 'URL']         
    elif df.loc[duedateindex[row_count]-1, 'URL'] != df.loc[duedateindex[row_count]-1, 'URL']:
        assignments.loc[duedateindex[row_count], 'testURL'] = df.loc[duedateindex[row_count]-2, 'URL']
    else:
        assignments.loc[duedateindex[row_count], 'testURL'] = df.loc[duedateindex[row_count]-1, 'URL']
    if row == 0:
        row_count += 1
    else:
        if row[1] == "Day(s)":
            assignments.loc[duedateindex[row_count], 'Time_Before_Due_Date'] = float(row[0])*24*3600 + float(row[2])*3600 + float(row[4])*60 + float(row[6])
        elif row[1] == "hrs":
            assignments.loc[duedateindex[row_count], 'Time_Before_Due_Date'] = float(row[0])*3600 + float(row[2])*60 + float(row[4])
        row_count += 1

# Figure out how to read in series of .csv files (maybe all in one folder one at a time?) through a list of courseID's and userID's <- is probably going to be the best idea

# Fix list of URL's in the urls set. If there is a module page it should count as the assignment page

# Grab the URL above the assignment submission cell if it's there, if not, then do the one above that.

# Get previews for every URL, defined as looking at an assignment page more than 24 hours before the due date for longer than 5 seconds

#Figure out how to parse a URL by / into pieces, 5 should have assignments or quizzes, 6 should have assignment ID
page_views['newURL'] = page_views['URL'].str.split('/')

# Do we care about repeat pages?





# Meet with Curtis to decide what kind of data we want from the data    

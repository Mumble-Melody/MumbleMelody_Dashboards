import math
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from datetime import datetime
from datetime import date
from datetime import timedelta
import numpy as np
import matplotlib.pyplot as plt
import os
#from os.path import exists
from itertools import compress

from collections import OrderedDict

from selenium import webdriver
import chromedriver_binary  # Adds chromedriver binary to path

import seaborn as sns
from bokeh.plotting import figure, output_notebook, show, save, output_file
from bokeh.io import export_png
from bokeh.models import Range1d, ColumnDataSource
from bokeh.transform import dodge
from bokeh.resources import CDN
from bokeh.embed import file_html

# Initialize the app with a service account, granting admin privileges
FIREBASE_PRIVATE_KEY_ID = os.environ['FIREBASE_PRIVATE_KEY_ID']
FIREBASE_PRIVATE_KEY = os.environ['FIREBASE_PRIVATE_KEY']

import json
#
with open('mumble-melody-longitudinal-firebase-adminsdk-34x0r-52f98ad6f0.json', 'r+') as f:
    firebase_json = json.load(f)
    firebase_json['private_key_id'] = str(os.environ['FIREBASE_PRIVATE_KEY_ID'])
    firebase_json['private_key'] = "-----BEGIN PRIVATE KEY-----\n" + str(os.environ['FIREBASE_PRIVATE_KEY']) + "=\n-----END PRIVATE KEY-----\n"


cred = credentials.Certificate("mumble-melody-longitudinal-firebase-adminsdk-34x0r-52f98ad6f0-temp.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://mumble-melody-longitudinal-default-rtdb.firebaseio.com/'
})

#os.chdir('/Users/alishakodibagkar/MIT/Mumble_Melody_Firebase/MumbleMelody_Dashboards')
#os.system('/bin/rm images/Fig1.png')
#os.system('/bin/rm images/Fig2.png')
#os.system('/bin/rm images/Fig3.png')
#os.system('/bin/rm images/Fig4.png')
#os.system('/usr/bin/git -C a/Users/alishakodibagkar/MIT/Mumble_Melody_Firebase/MumbleMelody_Dashboards dd .')
#os.system('/usr/bin/git -C /Users/alishakodibagkar/MIT/Mumble_Melody_Firebase/MumbleMelody_Dashboards commit -m "remove old images"')
#os.system('pwd')

output_notebook()

#this gets all the data from firebase
ref = db.reference()
all_data = ref.get()

#set what today is
current_datetime = datetime.now()
today = current_datetime.date()
today_string = str(today)
today_save_filepath = 'images/'
#if exists(today_save_filepath) == False:
#    print(exists(today_save_filepath))
#    os.mkdir(today_save_filepath)
    
#set start date
startdate = date(2022, 7, 22)

#days since starting
delta = today - startdate
dayssincestart = delta.days


#1. Number of New Devices
#We want to find all subjects who downloaded the app since the start date
num_newdownloads = np.zeros(dayssincestart)
total_num_newdownloads = 0;
new_user_list = [];

#create a list of the previous 7 days (not including the current day)
dates = [];
for i in range(dayssincestart,0,-1):
    dates.append(str(today-timedelta(days=i)))

#iterate through each subject ID
for key_subID in all_data:
    
    #check if the subject is a Developer
    sub_developer = 0;
    for key_datetime in all_data[key_subID]:
        for key_time_of_use in all_data[key_subID][key_datetime]:
            if  "Developer Application" in all_data[key_subID][key_datetime][key_time_of_use]:
                sub_developer = 1;
    if sub_developer == 0:
    
        #now check if the current access is the initial access for each subject- in firebase the dates are in order which is good
        access_number = 1
        for key_datetime in all_data[key_subID]:
            if access_number == 1:

                #save # of first access downloads for the last 7 days
                key_datetime_object = datetime.strptime(key_datetime, '%Y-%m-%d %H:%M:%S +0000')
                key_date_object = key_datetime_object.date()
                if ((today - key_date_object).days < dayssincestart+1) and ((today - key_date_object).days > 0) :
                    daynumber = dayssincestart - (today - key_date_object).days;
                    num_newdownloads[daynumber] = num_newdownloads[daynumber] + 1;
                    total_num_newdownloads = total_num_newdownloads + 1;
                    new_user_list.append(key_subID)
            access_number = access_number + 1;
            
#now, check for Day 1 retention of new users
users_laterday = [];

#iterate through each subject ID
for key_subID in new_user_list:
    
    #check if the subject is a Developer - shouldnt be
    sub_developer = 0;
    for key_datetime in all_data[key_subID]:
        for key_time_of_use in all_data[key_subID][key_datetime]:
            if  "Developer Application" in all_data[key_subID][key_datetime][key_time_of_use]:
                sub_developer = 1;
                developer_app = developer_app + 1
    if sub_developer == 0:
        
        #now check if the new users had a use after the first day
        access_number = 1;
        daynumber = dayssincestart+1;
        for key_datetime in all_data[key_subID]:
            if access_number == 1:

                #save day number of first access
                key_datetime_object = datetime.strptime(key_datetime, '%Y-%m-%d %H:%M:%S +0000')
                key_date_object = key_datetime_object.date()
                if ((today - key_date_object).days < dayssincestart+1) and ((today - key_date_object).days > 0) :
                    daynumber =dayssincestart - (today - key_date_object).days;
   
            else:
                key_datetime_object = datetime.strptime(key_datetime, '%Y-%m-%d %H:%M:%S +0000')
                key_date_object = key_datetime_object.date()
                daynumber_tocompare = dayssincestart - (today - key_date_object).days;
                if daynumber_tocompare > daynumber:
                    users_laterday.append(key_subID)
                    
            access_number = access_number + 1;

users_laterday_total = len(np.unique(users_laterday))

#now, check whether users have used modes at all
users_ofmode_unaltered = [];
users_ofmode_whisper = [];
users_ofmode_reverb = [];
users_ofmode_harmonize = [];
users_ofmodes = [];


#iterate through each subject ID
for key_subID in new_user_list:
    
    #check if the subject is a Developer - shouldnt be
    sub_developer = 0;
    for key_datetime in all_data[key_subID]:
        for key_time_of_use in all_data[key_subID][key_datetime]:
            if  "Developer Application" in all_data[key_subID][key_datetime][key_time_of_use]:
                sub_developer = 1;
    if sub_developer == 0:
        
        #now check if the new users had a use after the first day
        access_number = 1;
        daynumber = dayssincestart+1;
        for key_datetime in all_data[key_subID]:
            for key_val in all_data[key_subID][key_datetime]:
                    if all_data[key_subID][key_datetime][key_val] == 'Unaltered':
                        users_ofmode_unaltered.append(key_subID)
                        users_ofmodes.append(key_subID)
                    if all_data[key_subID][key_datetime][key_val] == 'Whisper':
                        users_ofmode_whisper.append(key_subID)
                        users_ofmodes.append(key_subID)
                    if all_data[key_subID][key_datetime][key_val] == 'Reverb':
                        users_ofmode_reverb.append(key_subID)
                        users_ofmodes.append(key_subID)
                    if all_data[key_subID][key_datetime][key_val] == 'Harmonize':
                        users_ofmode_harmonize.append(key_subID)
                        users_ofmodes.append(key_subID)

users_ofmode_unaltered = np.unique(users_ofmode_unaltered)
users_ofmode_whisper = np.unique(users_ofmode_whisper)
users_ofmode_reverb = np.unique(users_ofmode_reverb)
users_ofmode_harmonize = np.unique(users_ofmode_harmonize)
users_ofmodes = np.unique(users_ofmodes)

p = figure(plot_width = 1000, plot_height = 400,x_range=dates,title=("Total Number of New Users: "+str(total_num_newdownloads)+ ", New Users with Uses After Day 1: "+str(users_laterday_total)) + ", New Users that Have Used Modes: "+str(len(users_ofmodes)))
p.title.align = 'center'
p.xaxis.axis_label = 'Date'
p.yaxis.axis_label = 'Number of New Users'
p.xaxis.major_label_orientation = math.pi/2
p.line(dates,num_newdownloads,line_width = 2, color = "blue")
#show(p)
export_png(p, filename=(today_save_filepath + 'Fig1.png'))

#2. Number of Unique Users Per Day

#We want to find number of unique users per day
unique_users = np.zeros(dayssincestart)
total_unique_users = 0;
user_list = [];
user_list_basedonday = [ [] for _ in range(dayssincestart)]

#create a list of the previous days (not including the current day)
dates = [];
for i in range(dayssincestart,0,-1):
    dates.append(str(today-timedelta(days=i)))

#iterate through each subject ID
for key_subID in all_data:
    
#check if the subject is a Developer
    sub_developer = 0;
    for key_datetime in all_data[key_subID]:
        for key_time_of_use in all_data[key_subID][key_datetime]:
            if  "Developer Application" in all_data[key_subID][key_datetime][key_time_of_use]:
                sub_developer = 1;
    if sub_developer == 0:
    
        for key_datetime in all_data[key_subID]:
            key_datetime_object = datetime.strptime(key_datetime, '%Y-%m-%d %H:%M:%S +0000')
            key_date_object = key_datetime_object.date()
            if ((today - key_date_object).days < dayssincestart+1) and ((today - key_date_object).days > 0) :
                daynumber = dayssincestart - (today - key_date_object).days;
                
                #look at unique users per day
                if key_subID not in user_list_basedonday[daynumber]:
                    unique_users[daynumber] = unique_users[daynumber] + 1;
                    user_list_basedonday[daynumber].append(key_subID)
                    
                #look at how many total unique users there were in the week
                if key_subID not in user_list:
                    total_unique_users = total_unique_users + 1;
                    user_list.append(key_subID)
                    
users_per_day_toplot = np.zeros(dayssincestart)
for i in range (0,len(user_list_basedonday)):
    users_per_day_toplot[i] = len(user_list_basedonday[i])
    
p = figure(plot_width = 1000, plot_height = 400,x_range=dates,title=("Total Number of Unique Users: "+str(total_unique_users)))
p.title.align = 'center'
p.xaxis.axis_label = 'Date'
p.yaxis.axis_label = 'Number of Unique Users'
p.xaxis.major_label_orientation = math.pi/2
p.line(dates, users_per_day_toplot,line_width = 2, color = "blue")
#show(p)
export_png(p, filename=(today_save_filepath + 'Fig2.png'))

#3. Duration per day for all users: mean/median/min/max

#We want to find mean/median/min/max duration for all users each day in the last week

total_durations_eachday_allusers = [ [] for _ in range(dayssincestart)]
total_durations_eachday_unaltered = [ [] for _ in range(dayssincestart)]
total_durations_eachday_whisper = [ [] for _ in range(dayssincestart)]
total_durations_eachday_reverb = [ [] for _ in range(dayssincestart)]
total_durations_eachday_harmonize = [ [] for _ in range(dayssincestart)]

#look through all users
for key_subID in all_data:
    
    #check if the subject is a Developer
    sub_developer = 0;
    for key_datetime in all_data[key_subID]:
        for key_time_of_use in all_data[key_subID][key_datetime]:
            if  "Developer Application" in all_data[key_subID][key_datetime][key_time_of_use]:
                sub_developer = 1;
    if sub_developer == 0:
                
        for key_datetime in all_data[key_subID]:
            
            #retrieve date
            key_datetime_object = datetime.strptime(key_datetime, '%Y-%m-%d %H:%M:%S +0000')
            key_date_object = key_datetime_object.date()
   
            # if the date is within the last 7 days
            if ((today - key_date_object).days < dayssincestart+1) and ((today - key_date_object).days > 0) :

#                 #add session durations for all the users in the last week
#                 for key_val in all_data[key_subID][key_datetime]:
#                     if key_val == 'total session':
#                         daynumber = 7 - (today - key_date_object).days;
#                         string_duration_toadd = all_data[key_subID][key_datetime][key_val]
#                         float_duration_toadd = float(string_duration_toadd)
#                         total_durations_eachday_allusers[daynumber].append(float_duration_toadd)
#                         total_durations_allusers.append(float_duration_toadd);
                
                #calculate durations: click mode --> Off/othermode/end of session
                daynumber = dayssincestart - (today - key_date_object).days;
                from datetime import datetime
                format = '%H:%M:%S'
                duration_start = False
                duration_beginning = "";
                duration_end = "";
                prev_key_val = "";
                
                #Unaltered
                for key_val in all_data[key_subID][key_datetime]:
                    if all_data[key_subID][key_datetime][key_val] == "Unaltered":
                        duration_start = True
                        start_time = key_val
                    if duration_start == True and ((all_data[key_subID][key_datetime][key_val] == ("Off" or "Whisper" or "Reverb" or "Harmonize" or "Application Terminated") or (key_val == 'total session'))):
                        end_time = key_val
                        if key_val == "total session":
                            end_time = prev_key_val
                        start_minus_end = datetime.strptime(end_time, format) - datetime.strptime(start_time, format)
                        duration_toadd = start_minus_end.total_seconds()
                        total_durations_eachday_allusers[daynumber].append(duration_toadd)
                        total_durations_eachday_unaltered[daynumber].append(duration_toadd)
                        duration_start = False
                    prev_key_val = key_val;
                
                #Whisper
                for key_val in all_data[key_subID][key_datetime]:
                    if all_data[key_subID][key_datetime][key_val] == "Whisper":
                        duration_start = True
                        start_time = key_val
                    if duration_start == True and ((all_data[key_subID][key_datetime][key_val] == ("Off" or "Unaltered" or "Reverb" or "Harmonize" or "Application Terminated") or (key_val == 'total session'))):
                        end_time = key_val
                        if key_val == "total session":
                            end_time = prev_key_val
                        start_minus_end = datetime.strptime(end_time, format) - datetime.strptime(start_time, format)
                        duration_toadd = start_minus_end.total_seconds()
                        total_durations_eachday_allusers[daynumber].append(duration_toadd)
                        total_durations_eachday_whisper[daynumber].append(duration_toadd)
                        duration_start = False
                    prev_key_val = key_val;
                    
                #Reverb
                for key_val in all_data[key_subID][key_datetime]:
                    if all_data[key_subID][key_datetime][key_val] == "Reverb":
                        duration_start = True
                        start_time = key_val
                    if duration_start == True and ((all_data[key_subID][key_datetime][key_val] == ("Off" or "Unaltered" or "Whisper" or "Harmonize" or "Application Terminated") or (key_val == 'total session'))):
                        end_time = key_val
                        if key_val == "total session":
                            end_time = prev_key_val
                        start_minus_end = datetime.strptime(end_time, format) - datetime.strptime(start_time, format)
                        duration_toadd = start_minus_end.total_seconds()
                        total_durations_eachday_allusers[daynumber].append(duration_toadd)
                        total_durations_eachday_reverb[daynumber].append(duration_toadd)
                        duration_start = False
                    prev_key_val = key_val;
                    
                #Harmonize
                for key_val in all_data[key_subID][key_datetime]:
                    if all_data[key_subID][key_datetime][key_val] == "Harmonize":
                        duration_start = True
                        start_time = key_val
                    if duration_start == True and ((all_data[key_subID][key_datetime][key_val] == ("Off" or "Whisper" or "Reverb" or "Unaltered" or "Application Terminated") or (key_val == 'total session'))):
                        end_time = key_val
                        if key_val == "total session":
                            end_time = prev_key_val
                        start_minus_end = datetime.strptime(end_time, format) - datetime.strptime(start_time, format)
                        duration_toadd = start_minus_end.total_seconds()
                        total_durations_eachday_allusers[daynumber].append(duration_toadd)
                        total_durations_eachday_harmonize[daynumber].append(duration_toadd)
                        duration_start = False
                    prev_key_val = key_val;
                
                    
#                     value_list.append(all_data[key_subID][key_datetime][key_val])
#                     time_list.append(key_val);
#                 for
#                     if 'Unaltered' in all_data[key_subID][key_datetime][key_val]:
#                         print(value_list)
                        #convert time to seconds
                        
                        
#                         for i in range(iteration-1,-1,-1):
#                             if value_list[i] == 'Unaltered' or value_list[i] == 'Whisper' or value_list[i] == 'Reverb' or value_list[i] == 'Harmonize':
#                                 mode_string = value_list[i]
#                                 break;
#                         if mode_string == 'Unaltered':
#                             question0_rating_unaltered.append(int(all_data[key_subID][key_datetime][key_val][13]));
#                         if mode_string == 'Whisper':
#                             question0_rating_whisper.append(int(all_data[key_subID][key_datetime][key_val][13]));
#                         if mode_string == 'Reverb':
#                             question0_rating_reverb.append(int(all_data[key_subID][key_datetime][key_val][13]));
#                         if mode_string == 'Harmonize':
#                             question0_rating_harmonize.append(int(all_data[key_subID][key_datetime][key_val][13]));
                            
for i in range(0,len(total_durations_eachday_allusers)):
    if total_durations_eachday_allusers[i] == []:
        total_durations_eachday_allusers[i] = [0]
for i in range(0,len(total_durations_eachday_unaltered)):
    if total_durations_eachday_unaltered[i] == []:
        total_durations_eachday_unaltered[i] = [0]
for i in range(0,len(total_durations_eachday_whisper)):
    if total_durations_eachday_whisper[i] == []:
        total_durations_eachday_whisper[i] = [0]
for i in range(0,len(total_durations_eachday_reverb)):
    if total_durations_eachday_reverb[i] == []:
        total_durations_eachday_reverb[i] = [0]
for i in range(0,len(total_durations_eachday_harmonize)):
    if total_durations_eachday_harmonize[i] == []:
        total_durations_eachday_harmonize[i] = [0]

q1= []
q2 =[]
q3 = []
for i in range(0,len(total_durations_eachday_allusers)):
    q1.append(np.quantile(total_durations_eachday_allusers[i], .25,interpolation='nearest'))
    q2.append(np.quantile(total_durations_eachday_allusers[i], .50,interpolation='nearest'))
    q3.append(np.quantile(total_durations_eachday_allusers[i], .75,interpolation='nearest'))
    
iqr = np.array(q3)-np.array(q1)
upper_iqr = np.array(q3) + 1.5*np.array(iqr)
lower_iqr = list(np.array(q1) - 1.5*np.array(iqr))

#outliers
outliers = [ [] for _ in range(dayssincestart)]
dates_outliers = [ [] for _ in range(dayssincestart)]
for i in range(0,len(total_durations_eachday_allusers)):
    for j in range(0,len(total_durations_eachday_allusers[i])):
        if total_durations_eachday_allusers[i][j] > upper_iqr[i] or total_durations_eachday_allusers[i][j] < lower_iqr[i]:
            outliers[i].append(total_durations_eachday_allusers[i][j])
            dates_outliers[i].append(dates[i])

#lengths of stems - max and min, up to 1.5*iqr
upper = []
lower = []
for i in range(0,len(total_durations_eachday_allusers)):
    max_val = max(list(compress(total_durations_eachday_allusers[i],total_durations_eachday_allusers[i] <= upper_iqr[i])))
    min_val = min(list(compress(total_durations_eachday_allusers[i],total_durations_eachday_allusers[i] >= lower_iqr[i])))
    upper.append(max_val)
    lower.append(min_val)
    
#find # sessions above 30 seconds
total_session_count = 0
total_above30s_count = 0
for i in range(0,7):
    for j in total_durations_eachday_allusers[i]:
        if j > 0:
            total_session_count = total_session_count + 1;
            if j > 30:
                total_above30s_count = total_above30s_count + 1;
    
#figure
title_string = ("Total Session Duration Per Day, Excluding Outliers - median, Q1, Q2, max, min (s)")
p = figure(plot_width = 1000, plot_height = 400,x_range=dates,title=(title_string))
p.title.align = 'center'

# stems
p.segment(dates, upper, dates, q3, line_color="black")
p.segment(dates, lower, dates, q1, line_color="black")

# boxes
p.vbar(dates, 0.7, q2, q3, fill_color="blue", line_color="black")
p.vbar(dates, 0.7, q1, q2, fill_color="blue", line_color="black")

# whiskers (almost-0 height rects simpler than segments)
p.rect(dates, lower, 0.2, 0.01, line_color="black")
p.rect(dates, upper, 0.2, 0.01, line_color="black")

# dates_outliers_flat_list = [item for sublist in dates_outliers for item in sublist]
# outliers_flat_list = [item for sublist in outliers for item in sublist]
# p.circle(dates_outliers_flat_list, outliers_flat_list, size=8, fill_alpha=0.6)
p.xaxis.major_label_orientation = math.pi/2
p.xaxis.axis_label = 'Date'
             
#show(p)
export_png(p, filename=(today_save_filepath + 'Fig3.png'))

#4. Mode Usage

unaltered_mode_totaluses = np.zeros(dayssincestart);
whisper_mode_totaluses = np.zeros(dayssincestart);
reverb_mode_totaluses = np.zeros(dayssincestart);
harmonize_mode_totaluses = np.zeros(dayssincestart);


#look through all users
for key_subID in all_data:
    #check if the subject is a Developer
    sub_developer = 0;
    for key_datetime in all_data[key_subID]:
        for key_time_of_use in all_data[key_subID][key_datetime]:
            if  "Developer Application" in all_data[key_subID][key_datetime][key_time_of_use]:
                sub_developer = 1;


    if sub_developer == 0:
        
        for key_datetime in all_data[key_subID]:
            
            #retrieve date
            key_datetime_object = datetime.strptime(key_datetime, '%Y-%m-%d %H:%M:%S +0000')
            key_date_object = key_datetime_object.date()
   
            # if the date is within the last 7 days
            if ((today - key_date_object).days < dayssincestart+1) and ((today - key_date_object).days > 0) :
                daynumber = dayssincestart - (today - key_date_object).days;
                    
                #retrieve all Mode usage
                for key_val in all_data[key_subID][key_datetime]:
                    if all_data[key_subID][key_datetime][key_val] == 'Unaltered':
                        unaltered_mode_totaluses[daynumber] = unaltered_mode_totaluses[daynumber] + 1;
                    if all_data[key_subID][key_datetime][key_val] == 'Whisper':
                        whisper_mode_totaluses[daynumber] = whisper_mode_totaluses[daynumber] + 1;
                    if all_data[key_subID][key_datetime][key_val] == 'Reverb':
                        reverb_mode_totaluses[daynumber] = reverb_mode_totaluses[daynumber] + 1;
                    if all_data[key_subID][key_datetime][key_val] == 'Harmonize':
                        harmonize_mode_totaluses[daynumber] = whisper_mode_totaluses[daynumber] + 1;
#print(unaltered_mode_totaluses)
#print(whisper_mode_totaluses)
#print(reverb_mode_totaluses)
#print(harmonize_mode_totaluses)

p = figure(plot_width = 1000, plot_height = 400,x_range=dates,title=("Total Number of Mode Uses: "+str(sum(unaltered_mode_totaluses)+sum(whisper_mode_totaluses)+sum(reverb_mode_totaluses)+sum(harmonize_mode_totaluses))))
p.title.align = 'center'
p.xaxis.axis_label = 'Date'
p.yaxis.axis_label = 'Number of Uses'
p.line(dates,unaltered_mode_totaluses,line_width = 2, color = "blue",legend_label="Unaltered",line_alpha = 0.7)
p.line(dates,whisper_mode_totaluses,line_width = 2, color = "green",legend_label="Whisper",line_alpha = 0.7)
p.line(dates,reverb_mode_totaluses,line_width = 2, color = "orange",legend_label="Reverb",line_alpha = 0.7)
p.line(dates,harmonize_mode_totaluses,line_width = 2, color = "pink",legend_label="Harmonize",line_alpha = 0.7)
p.legend.location = "top_right"
p.xaxis.major_label_orientation = math.pi/2
#show(p)
export_png(p, filename=(today_save_filepath + 'Fig4.png'))


#Add time of change to log
current_datetime_string = str(current_datetime)
add_to_log = "Updated images on: " + current_datetime_string + "\n"

log = open("log.txt", "a")
log.write(add_to_log)
log.close()

#Push changes to Github
#os.system('/usr/bin/git -C /Users/alishakodibagkar/MIT/Mumble_Melody_Firebase/MumbleMelody_Dashboards add .')
#os.system('/usr/bin/git -C /Users/alishakodibagkar/MIT/Mumble_Melody_Firebase/MumbleMelody_Dashboards commit -m "update figures today"')
#os.system('/usr/bin/git -C /Users/alishakodibagkar/MIT/Mumble_Melody_Firebase/MumbleMelody_Dashboards push')

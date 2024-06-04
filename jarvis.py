import datetime as dt
import wikipedia as wp
import pyttsx3 #Library for Text to Speech 
import speech_recognition as sr
import webbrowser as web
from googlesearch import search
import os
import random
import smtplib as smt # for sending the emails
import csv #Saving the contacts in an excel file 
from email.message import EmailMessage #For creating a email message
import ssl #Standard technology for keeping the connection over internet secure
import requests
import gemini #Used Google Gemini API for generating AI responses
import googleapiclient.discovery as gd
from config_youtube import api_youtube
from pytube import YouTube #for retriving the duration for any youtube video
import time

engine= pyttsx3.init('sapi5') #Object Creation for text to speech 
voices=engine.getProperty('voices')
engine.setProperty('voices',voices[0].id) #Setting male voice for JARVIS

def speak(line):
    print(line)
    engine.say(line)
    engine.runAndWait()

def greet():
    #this function will greet you every time you start a new execution based on the current time
    hour=int(dt.datetime.now().hour)

    if hour>=0 and hour<12:
        speak("Good Morning Abhinav")
        speak("JARVIS in Action Sir!!. How can I help you?")
    
    elif hour>=12 and hour<18:
        speak("Good Afternoon Abhinav")
        speak("JARVIS in Action Sir!!. How can I help you?")
    
    else:
        speak("Good Evening Abhinav")
        speak("JARVIS in Action Sir!!. How can I help you?")

def command():
    # The command function is taking input from the user and returning the string output of the said command.

    r=sr.Recognizer()
    with sr.Microphone() as comm:
        #Taking input from the user through microphone 
        print("Listening.... ")
        r.pause_threshold=1
        r.energy_threshold=1000 # you have to speak a little loud so that it does not detect the background voices
        audio=r.listen(comm)

    try:
        #For recognizing the command that is being said by the user 
        print("Recognizing....")
        query=r.recognize_google(audio,language='en-in')
        print(f"Abhinav said: {query}")

    except Exception as ex:
        #If the code doesn't able to recognise the command 
        speak("Please say that again..")
        return ""
    
    return(query)

def  ai(prompt):
    try:
        response = gemini.chat_session.send_message(prompt)
        if "*" in response.text:
            response.text.replace("*","")
        speak(response.text)

    except Exception as ex:
        speak("Some error occurred while generating A.I. response. Make sure you are connected to internet")

def email(to):
    #Function for sending Emails
    try:
        s_mail='abhinavmaurya2464@gmail.com' #Sender's Email address 
        speak("Tell the subject")
        sub=command().title() #Subject for the Email
        speak("Tell the body of the email")
        body=command() #Body for the Email
        em=EmailMessage() #Creating an object for constructing email messages 
        em['From']=s_mail
        em['To']=to
        em['Subject']=sub
        em.set_content(body)
        with open ("pass.txt",'r') as file:
            password=file.read()
        
        d_con=ssl.create_default_context()
        with smt.SMTP_SSL('smtp.gmail.com',465,context=d_con) as send:
            send.login(s_mail,password)
            send.sendmail(s_mail,to,em.as_string())
        speak("Email has been sent")
    except Exception as ex:
        speak("Some Error occured during the process.Please try again. Make sure you are connected to internet")

def weather():
    try:
        from config_weather import api_weather
        base_url="https://api.openweathermap.org/data/2.5/weather?" #this is the base url and question mark is used for adding more parameters
        apikey=api_weather

        url_loca="http://ipinfo.io/json" #For extracting the live location of the user 
        data=requests.get(url_loca).json()
        city=data['city']
        country=data['country'].lower()
        url=base_url+"q="+city+","+country+"&APPID="+apikey #Creating the url for extracting the weather updates
        response=requests.get(url).json()
        speak(f"Temperature in {city} is {round(response['main']['temp']-273.15,2)} Celcius")
        speak(f"Temperature in {city} feels like {round(response['main']['feels_like']-273.15,2)}")
        speak(f"Humidity in {city} is {response['main']['humidity']}%")
        speak(f"General Weather in {city}: {response['weather'][0]['description']}")
    
    except Exception as ex:
        speak("Unable to fetch weather updates. Please try again. Make sure you are connected to internet")

def youtube_music(input):
    try:
        apikey=api_youtube
        youtube=gd.build("youtube","v3",developerKey=apikey) #making an object to communicate with the YouTube Data API
        request=youtube.search().list(
            part="snippet",
            q=input,
            maxResults=2
        )

        response=request.execute() #Executing for search
        video_id=[]
        for item in response['items']:
            video_id.append(item['id']['videoId']) #Extracting the video id from the results
        
        url="https://www.youtube.com/watch?v="+video_id[0]
        web.open_new_tab(url)
        
        yt=YouTube(url)
        length=yt.length
        
        time.sleep(length+30) #The program will stop untill the music video is played completely 30sec are additionally added for the ads on YouTube
        speak("Hope you liked the song sir")

    except Exception as ex:
        speak("Some error occured while processing. Make sure you are connected to internet. This feature of the program only works for music searches")

def remem(text):
    with open ("remember.txt","a") as file:
        file.write(text)
        file.write("\n")

def remem_read():
    with open ("remember.txt","r") as file:
        text=file.read()
        text=text.replace(" my "," your ")
        text=text.replace(" i "," you ")
        speak("You told me to remember that: ")
        speak(text)

def main():
    global random
    greet()
    
    while True:
        query=command().lower()
    
        if "search for" in query: #searching any thing on google
            query=query.replace("search for","")
            speak("Serching on Google...")

            # for Searching on google it takes the first url
            for web_page in search(query, tld="co.in", num=1, stop=1, pause=2):
                web.open_new_tab(web_page)

        elif "open youtube" in query: #open youtube
            speak("Doing that sir")
            web.open_new_tab("https://youtube.com")

        elif "open google" in query: #open google.com
            speak("Doing that sir")
            web.open_new_tab("https://google.com")

        elif "play" in query: #play any music video on youtube by saying its name 
            youtube_music(query.replace("play",""))

        elif "play music" in query: #play music that are saved in the system
            # os.open("C:\Users\Technia\Desktop\Songs\Satranga")
            music="C:\\Users\\Technia\\Desktop\\Songs"
            songs=os.listdir(music)
            num=random.randrange(0,len(songs))
            os.startfile(os.path.join(music , songs[num]))

        elif "time" in query: #tell the current time 
            time=dt.datetime.now().strftime("%H:%M:%S")
            speak(f"The time is {time}")

        elif "send" and "email" in query: #sends email to a person that is present in the contacts
            speak("Tell the receiver's name")
            to=command().lower()
            with open ("contacts.csv", mode='r+') as f:
                data = csv.reader(f)
                for line in data:
                    # print(line)
                    if line!=[]:
                        if line[0].lower() == to:
                            email(line[1])
                            break

                else:
                    speak("Person name is not present in your contacts file. Please first add the details of the person")
        
        elif "add" and "contacts" in query: #add the person details if its not present in the contacts file
            speak("Tell the person's name that to be added in your contacts")
            name=command().title()
            speak("Tell the E-mail ID")
            id=command().lower().replace(" ","")

            with open ("contacts.csv",mode='+a') as file:
                w=csv.writer(file)
                w.writerow([name,id])

        elif "weather" in query: #Tell the weather update based on your live location
            weather()

        elif "activate" and "ai" in query: #Activate A.I. that uses Google's Gemini API
            speak("Jarvis A.I. Activated Sir !!")
            speak("Now the responses will be generated by the A.I.")
            while True:
                prompt=command().lower()
                ai(prompt)

                if "deactivate" in prompt: #for Deactivating the A.I.
                    speak("Jarvis A.I. Deactivated Sir !!")
                    speak("Hope we'll meet again")
                    break

        elif "jarvis remember that" in query: #Save your message in a text file 
            query=query.replace("jarvis remember that","")
            speak("Sure sir I will remember this")
            remem(query)
        
        elif "what i told you to remember" in query: #Returns the message said by you to remember
            remem_read()
            
        elif "exit" in query: #for exiting the program
            speak("Okay! Have a nice day sir")
            exit()

#For waking up the desktop assistant
speak("Say the wake word for activating you desktop assistant")
wake=command().lower()
c=3
while "jarvis" not in wake:
    c=c-1
    if c==0:
        speak("No more chances")
        exit()
    speak(f"Incorrect Wake Word. You still have {c} chances")
    wake=command().lower()

main()
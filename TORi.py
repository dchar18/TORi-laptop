import speech_recognition as sr     # records audio and turns it into text
# requires internet
from gtts import gTTS               # converts text to speech - allows program to respond
import os
import subprocess
import cv2                          # for facial recognition and possibly autonomous actions
import pickle
import numpy as np
from PIL import Image
import requests, json               # for weather API
import imaplib                      # for determining num of unread emails?
# libraries for Google searches
# for searches
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
# for gmail login
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# libraries for application launch
# from elasticsearch import Elasticsearch
# from elasticsearch.helpers import bulk
#
# es = Elasticsearch(['localhost:9200'])
# bulk(es, records, index='voice_assistant', doc_type='text', raise_on_error=True)


def greeting():
    verified = False
    failed_attempts = 0
    say("Running facial biometrics")
    while verified is False and failed_attempts < 3:
        user = facial_recognition()
        if user == '':
            say("No match")
            failed_attempts += 1
            say(str(failed_attempts) + " failed attempts")
        else:
            verified = True

    if verified is True:
        say("Hello " + user + ", how may I assist you?")
        return verified
    if failed_attempts == 3:
        say("Access denied")
        return False


def facial_train():
    say("Creating facial recognition dataset")
    base_directory = os.path.dirname(os.path.abspath(__file__))
    image_dir = os.path.join(base_directory, "images")

    face_cascade = cv2.CascadeClassifier('cascades/data/haarcascade_frontalface_default.xml')

    recognizer = cv2.face.LBPHFaceRecognizer_create()

    current_id = 0
    label_ids = {}
    y_labels = []
    x_train = []

    for root, dirs, files in os.walk(image_dir):
        for file in files:
            if file.endswith("png") or file.endswith("jpg"):
                path = os.path.join(root, file)
                label = os.path.basename(root).replace(" ", "-").lower()
                if label not in label_ids:
                    label_ids[label] = current_id
                    current_id += 1

                id_ = label_ids[label]
                # print(label_ids)
                pil_image = Image.open(path).convert("L")  # convert to grayscale
                image_array = np.array(pil_image, 'uint8')
                faces = face_cascade.detectMultiScale(image_array, scaleFactor=1.1, minNeighbors=5)

                for (x, y, w, h) in faces:
                    # roi = image_array[y:y+h, x:x+w]
                    x_train.append(image_array[y:y+h, x:x+w])
                    y_labels.append(id_)

    # with open("pickles/face-labels.pickle", 'wb') as f:
    with open("labels.pickle", 'wb') as file:
        pickle.dump(label_ids, file)

    recognizer.train(x_train, np.array(y_labels))
    recognizer.save("trainer.yml")
    say("Dataset created")


def facial_recognition():  # TODO
    face_cascade = cv2.CascadeClassifier('cascades/data/haarcascade_frontalface_default.xml')
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read("trainer.yml")

    labels = {}
    with open("labels.pickle", 'rb') as file:
        original_labels = pickle.load(file)
        labels = {value: key for key, value in original_labels.items()}

    video = cv2.VideoCapture(0)
    frame_num = 0
    # prediction = 2

    while True:
        frame_num = frame_num + 1
        check, frame = video.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        face = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        for (x, y, w, h) in face:
            prediction, confidence = recognizer.predict(gray[y:y+h, x:x+w])
            print(str(prediction) + " conf: " + str(confidence))
            if confidence >= 75:  # TODO - improve accuracy
                id_ = prediction
                print("ID: " + str(id_))
                user = labels[id_]  # TODO - set user name
                return user
                # if labels[id_] == 'damian':
                #     return True

        if frame_num == 15:
            return ''


def speak(phrase):  # vocal response - slower/unused
    myobj = gTTS(text=phrase, lang='en', slow=False)
    myobj.save("speak.mp3")
    os.system("mpg321 speak.mp3")
    print("TORi: " + phrase)


def say(text):  # vocal response - faster generation of speech
    subprocess.call(['say', text])
    print("TORi: " + text)


def activate():
    phrase = 'hey tori '
    r = sr.Recognizer()
    mic = sr.Microphone()

    while True:
        with mic as source:
            print("Listening")
            r.adjust_for_ambient_noise(source, duration=0.75)
            r.pause_threshold = 1  # may need to adjust - TEST
            audio = r.listen(source)
            try:
                transcript = r.recognize_google(audio)
                print("Understood: " + transcript)
                # if transcript.lower() == phrase:
                if phrase in transcript.lower():
                    return transcript.lower().split(phrase)[-1]
            except sr.RequestError:
                # API was unreachable or unresponsive
                return "API unavailable"
            except sr.UnknownValueError:
                # speech was unintelligible
                return "No command received"


def command():  # receive command
    r = sr.Recognizer()
    microphone = sr.Microphone(chunk_size=1024)

    with microphone as source:
        r.adjust_for_ambient_noise(source, duration=0.75)
        r.pause_threshold = 1  # may need to adjust - TEST
        print("Speak now")
        audio = r.listen(source)

    try:
        transcription = r.recognize_google(audio)
        return transcription
    # try recognizing the speech in the recording
    # if a RequestError or UnknownValueError exception is caught,
    # update the response object accordingly
    except sr.RequestError:
        # API was unreachable or unresponsive
        return "API unavailable"
    except sr.UnknownValueError:
        # speech was unintelligible
        return "No command received"
    # return "No command received"


def search_google_images(query):
    chrome_path = "/usr/local/bin/chromedriver"
    browser = webdriver.Chrome(chrome_path)
    browser.get('https://www.google.com/imghp?hl=en')
    search = browser.find_element_by_name('q')
    search.send_keys(query)
    search.send_keys(Keys.RETURN)
    # images_tab = browser.find_element_by_name('Images')
    #     # images_tab.click()


def search_google(query):
    chrome_path = "/usr/local/bin/chromedriver"
    browser = webdriver.Chrome(chrome_path)
    browser.get('http://www.google.com')
    search = browser.find_element_by_name('q')
    search.send_keys(query)
    search.send_keys(Keys.RETURN)

    # imagesButton = browser.find_element_by_id('images')
    # imagesButton.click()


def search():
    print("Searching Google")
    search = command_received.lower().split('look up')[-1]
    images_trigger = 'images of '
    if images_trigger in search:
        image_search = search.split(images_trigger)[-1]
        search_google_images(image_search)
    else:
        search_google(search)
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)


def check_email():
    email_login = 'dncharczuk81800@gmail.com'
    email_user = 'dncharczuk81800'
    password_login = 'DCgoogle!800'
    chrome_path = "/usr/local/bin/chromedriver"
    browser = webdriver.Chrome(chrome_path)
    browser.get(('https://accounts.google.com/ServiceLogin?'
                 'service=mail&continue=https://mail.google'
                 '.com/mail/#identifier'))

    username = browser.find_element_by_id('identifierId')
    username.send_keys(email_login)

    nextButton = browser.find_element_by_id('identifierNext')
    nextButton.click()

    password = WebDriverWait(browser, 20).until(
        EC.presence_of_element_located((By.NAME, "password")))
    try:
        password.send_keys(password_login)
        signInButton = browser.find_element_by_id('passwordNext')
        signInButton.click()
    except:
        print("Unable to enter password")

    # say how many unread emails
    try:
        obj = imaplib.IMAP4_SSL('imap.gmail.com', '993')
        obj.login(email_login, password_login)
        obj.select("inbox", True)
        return_code, mail_ids = obj.search(None, 'UnSeen')
        count = len(mail_ids[0].split(" "))
        print("Count: " + str(count))
    except:
        print("Unable to access email count")


def open_page_parse():
    website = command_received.split('navigate to ')[-1]
    open_page(website)


def open_page(website):
    chrome_path = "/usr/local/bin/chromedriver"
    browser = webdriver.Chrome(chrome_path)
    browser.get('http://www.' + website)
    if browser == 'weather.com':
        location = "Arlington Heights"
        location_input = browser.find_element_by_class_name("theme__inputElement__4bZUj input__inputElement__1GjGE")
        location_input.send_keys(location)


def kelvin_to_F(kelvin):
    return int((kelvin - 273.15) * 1.8 + 32)


def weather_data(location):  # use weather API to recite local weather data
    print("In weather date()")
    api_key = "2070c00d32fdfeaac43d863f958634a8"
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    location = location + " "
    complete_url = base_url + "appid=" + api_key + "&q=" + location

    response = requests.get(complete_url)
    x = response.json()

    if x["cod"] != "404":
        # store the value of "main"
        # key in variable y
        y = x["main"]

        curr_temp_kelvin = y["temp"]  # value is in Kelvin
        curr_temp_F = kelvin_to_F(curr_temp_kelvin) # convert to degrees F
        temp_low = kelvin_to_F(y["temp_min"])
        temp_high = kelvin_to_F(y["temp_max"])

        current_pressure = y["pressure"]  # in hPa
        current_humidity = y["humidity"]  # percentage

        z = x["weather"]
        weather_description = z[0]["description"]  # description of weather

        print("\nCurrent temperature: " + str(curr_temp_F) + "°F")
        print("High: " + str(temp_high) + "°F")
        print("Low: " + str(temp_low) + "°F")
        print("Condition: " + weather_description)
        print("Atmospheric pressure: " + str(current_pressure) + " hPa")
        print("Humidity: " + str(current_humidity) + "%\n")

        temp_range_text = " with a high of " + str(temp_high) + " and a low of " + str(temp_low)
        temp_text = "The temperature in " + location + "is " \
                    + str(curr_temp_F) + " degrees fahrenheit " + temp_range_text
        weather_descript_text = "with a " + weather_description
        atm_pressure_text = "The atmospheric pressure is " + str(current_pressure) \
                            + " Hectopascal Pressure Units "
        humidity_text = "The humidity is at " + str(current_humidity) + " percent"

        subprocess.call(['say', temp_text + weather_descript_text])
        subprocess.call(['say', atm_pressure_text])
        subprocess.call(['say', humidity_text])
    else:
        say("City not found")


def question():
    question_trigger = command_received.split("what is ")[-1]
    weather = "weather"
    if weather in question_trigger:
        if "the weather in" in question_trigger:
            location = question_trigger.split("the weather in ")[-1]
            weather_data(location)  # pull weather json to parse and read out daily data
        elif "the weather for this week" in question_trigger:
            open_page("weather.com")  # search online websites for visual data


def bluetooth(started):  # TODO
    if started:
        say("Ending connection")
        # TODO - disconnect bluetooth
    else:
        say("Initializing connection")
        # TODO - start connection


def start_car():  # TODO
    bluetooth(False)
    say("Starting car")
    car_command = command()
    while car_command != "turn off the car":
        if "turn left" in car_command:
            say("Signaling left")
        elif "turn right" in car_command:
            say("Signaling right")
        elif "pull up the sensor data" in car_command:
            say("Opening graphs now")
        car_command = command()
    say("Turning off the car")
    bluetooth(True)


def pause_play():  # pause/play song on spotify TODO
    lol = 4


def search_spotify():  # look up songs on spotify TODO
    lol = 1


def spotify_controls():
    print("\nSpotify controls:")
    print("Enter: pause/play")  # alternates between pausing and playing
    print("Space: search new song")  # pause and listen for new search
    print("q: quit Spotify commands")  # program releases control and moves on
    print("/: quit Spotify")  # close Spotify and exit function
    print(">", end=" ")
    spotify_input = input()  # can't use dictionary due to last 2 commands
    while spotify_input != 'q' or spotify_input != '/':
        print(spotify_input)
        if spotify_input == '':
            pause_play()
            print("Pausing")
        elif spotify_input == ' ':
            search_spotify()
            print("Searching")
        elif spotify_input == 'q':
            # exit function but continue playback
            break
        elif spotify_input == '/':
            # close spotify and exit function
            break
        print(">", end=" ")
        spotify_input = input()
    say("Exiting Spotify controls")


def open_app():
    app = command_received.split('open ')[-1]
    d = '/Applications'
    os.system('open ' + d + '/%s.app' % app.replace(' ', '\ '))
    if app == 'spotify':
        spotify_controls()


def create_file():  # creates and opens new sublime text file - TODO
    print("Creating file")
    text_file = command_received.lower().split(command_received)[-1]


def shut_down():
    say("Have a good day")


user = ' '
triggers = {"look": search,
            "what": question,
            "star": start_car,
            "open": open_app,
            "chec": check_email,
            "navi": open_page_parse,
            "crea": create_file,
            "that": shut_down}
# facial_train()
verified = greeting()
keep_going = True

while not verified:
    say("Try again?")
    command_received = command()
    # command_received = input("Enter command: ")
    if command_received == "yes":
        user = greeting()
        if user != ' ':
            print("User: " + user)
            verified = True
    else:
        say("Shutting down")
        break

if verified:
    while keep_going:
        # print("In loop")
        command_received = command()
        # command_received = input("Enter command: ")
        print("> " + command_received)

        if command_received != "No command received":
            parse_command = command_received[0:4]

            if parse_command not in triggers:
                say("I don't understand what you mean")
                continue

            command_name = triggers.get(parse_command, "Not valid command")
            if command_name == shut_down:
                command_name()
                keep_going = False
            else:
                command_name()

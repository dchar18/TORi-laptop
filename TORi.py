import speech_recognition as sr     # records audio and turns it into text
# requires internet
from gtts import gTTS               # converts text to speech - allows program to respond
import os
import subprocess
import cv2                          # for facial recognition and possibly autonomous actions
import pickle
import numpy as np
from PIL import Image

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
    say("Running facial biometrics scan")
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
                print(label_ids)
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
    email_login = "dncharczuk81800@gmail.com"
    password_login = "DCgoogle!800"
    chrome_path = "/usr/local/bin/chromedriver"
    browser = webdriver.Chrome(chrome_path)
    browser.get(('https://accounts.google.com/ServiceLogin?'
                 'service=mail&continue=https://mail.google'
                 '.com/mail/#identifier'))

    username = browser.find_element_by_id('identifierId')
    username.send_keys(email_login)

    nextButton = browser.find_element_by_id('identifierNext')
    nextButton.click()

    password = WebDriverWait(browser, 12).until(
        EC.presence_of_element_located((By.NAME, "password")))
    password.send_keys(password_login)

    signInButton = browser.find_element_by_id('passwordNext')
    signInButton.click()
    # say how many unread emails


def open_page():
    website = command_received.split('navigate to ')[-1]
    chrome_path = "/usr/local/bin/chromedriver"
    browser = webdriver.Chrome(chrome_path)
    browser.get('http://www.' + website)


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


def open_app():
    app = command_received.split('open ')[-1]
    d = '/Applications'
    os.system('open ' + d + '/%s.app' % app.replace(' ', '\ '))


def create_file():  # creates and opens new sublime text file - TODO
    print("Creating file")
    text_file = command_received.lower().split(command_received)[-1]


def shut_down():
    say("Have a good day")


user = ''
triggers = {"look": search,
            "star": start_car,
            "open": open_app,
            "chec": check_email,
            "navi": open_page,
            "crea": create_file,
            "that": shut_down}
facial_train()
verified = greeting()
keep_going = True

while not verified:
    say("Try again?")
    command_received = command()
    # command_received = input("Enter command: ")
    if command_received == "yes":
        user = greeting()
        if user != '':
            verified = True
    else:
        say("Shutting down")
        break

if verified:
    while keep_going:
        print("In loop")
        # command_received = command()
        command_received = input("Enter command: ")
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

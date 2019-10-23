import speech_recognition as sr     # records audio and turns it into text
# requires internet
from gtts import gTTS               # converts text to speech - allows program to respond
import os
import subprocess
import cv2                        # for facial recognition and possibly autonomous actions

# libraries for Google searches
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

# libraries for application launch
# from elasticsearch import Elasticsearch
# from elasticsearch.helpers import bulk
#
# es = Elasticsearch(['localhost:9200'])
# bulk(es, records, index='voice_assistant', doc_type='text', raise_on_error=True)


def greeting(verified):
    if verified:
        say("Hello Damian, how may I assist you?")
        return verified
    else:
        say("Hello. Authentication please")
        verified = facial_recognition()
        print("Verified: " + str(verified))
        greeting(verified)  # in case not verified, keep trying
        return verified


def facial_recognition():  # TODO - need to install openCV
    # cap = cv2.VideoCapture(0)
    #
    # while(True):
    #     ret, frame = cap.read()
    #     cv2.imshow('frame', frame)
    #     if cv2.waitKey(20) & 0xFF == ord('q'):
    #         break
    #
    # cap.release()
    # cv2.destroyAllWindows()
    return True


def speak(phrase):  # vocal response - slower/unused
    myobj = gTTS(text=phrase, lang='en', slow=False)
    myobj.save("speak.mp3")
    os.system("mpg321 speak.mp3")
    print("TORi: " + phrase)


def say(text):  # vocal response - faster generation of speech
    subprocess.call(['say', text])
    print("TORi: " + text)


def activate():
    phrase = 'hey Tori '
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
        print("Speak now")
        r.pause_threshold = 1  # may need to adjust - TEST
        audio = r.listen(source)

    # try recognizing the speech in the recording
    # if a RequestError or UnknownValueError exception is caught,
    #     update the response object accordingly
    try:
        transcription = r.recognize_google(audio)
        return transcription
    except sr.RequestError:
        # API was unreachable or unresponsive
        return "API unavailable"
    except sr.UnknownValueError:
        # speech was unintelligible
        return "No command received"
    # return "No command received"


# def response():
#     # text_response = 'Hello. Authentication please'
#     # text_response = 'Good morning, Damian. What would you like me to do?'
#     responses = ("Hello", "Good morning Damian. How are you doing today?",
#                  "Good afternoon Damian. How are you doing today?",
#                  "Good evening Damian. How are you doing today?",
#                  "Hello. Authentication please")
#     # text_response = random.choice(responses)
#
#     if command_received == "facial":
#         text_response = "Initializing facial recognition"
#     else:
#         text_response = responses[4]
#
#     speak(text_response)


# def search_es(query):
#     res = es.search(index="voice_assistant", doc_type="text", body={
#         "query": {
#             "match": {
#                 "voice_command": {
#                     "query": query,
#                     "fuzziness": 2
#                 }
#             }
#         },
#     })
#     return res['hits']['hits'][0]['_source']['sys_command']


def search_google(query):
    chrome_path = "/usr/local/bin/chromedriver"
    browser = webdriver.Chrome(chrome_path)
    browser.get('http://www.google.com')
    search = browser.find_element_by_name('q')
    search.send_keys(query)
    search.send_keys(Keys.RETURN)


def search():
    print("Searching Google")
    search = command_received.lower().split('look up')[-1]
    search_google(search)
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)


def bluetooth(started):  # TODO
    if started:
        say("Ending connection")
    else:
        say("Initializing connection")


def start_car():
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
    app = command_received.lower().split('open ')[-1]
    d = '/Applications'
    os.system('open ' + d + '/%s.app' % app.replace(' ', '\ '))


def create_file():  # creates and opens new sublime text file - TODO
    print("Creating file")
    text_file = command_received.lower().split(command_received)[-1]


def shut_down():
    say("Shutting down")


verified = False
triggers = {"look": search,
            "star": start_car,
            "open": open_app,
            "crea": create_file,
            "that": shut_down}
verified = greeting(verified)
keep_going = True
if verified:
    while keep_going:
        print("In loop")
        command_received = command()
        # command_received = input("Enter command: ")
        print("> " + command_received)
        if command_received != "No command received":
            parse_command = command_received[0:4]
            command_name = triggers.get(parse_command, "Not valid command")
            if command_name == shut_down:
                command_name()
                keep_going = False
            else:
                command_name()

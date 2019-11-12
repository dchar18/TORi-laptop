# TORi
Python Virtual Assitant

Python libraries:
- SpeechRecognition - for recording commands
- PyAudio - for recording commands
- Gtts - for voice responses
- Selenium - query searches via Google
- OpenCV - facial recognition
- Pillow
- Pickle - for storing image dataset for facial recognition
- OpenWeatherMap API - pulling local weather data

Primary functions:
- Personal assistance
	- Command-response
	- Security
		- User Authentication
			- Via facial recognition
- Control
	- Drone
	- Car
	- LEDs (in room, not planned yet)
- Productivity
	- Set reminders
	- Timers
	- Perform tasks
		- Search internet
	- Open apps
	- Create new notes
		- Ask what program to use
		- Create new file
		- Speech to text?
		- Google keep?
			
Secondary functions:
- Personality change
	- Serious <-> Lighthearted

Trigger words:
- 'look up' = open new chrome window and look up search query
- 'open' = open specified application
- 'create a new text file' = creates new text file in Sublime Text
- 'start the car' = initializes bluetooth connection with Ardulego car, 
	which enables TORi to control the car via voice commands

Currently able to...
- initiate and complete facial biometric scan
	- does not allow further interaction unless match found
- recognize command and response 
	- receives vocal commands, converts it to text, and processes the command
	- converts text to speech as a response to command
- autonomously open new Google window and...
	- look up search queries
		- directly finds images if asked to look up an image
		- else performs standard search
	- sign into Gmail
	- navigate directly to specified website
- launch applications downloaded on machine
- pull weather data from OpenWeatherMap API, parse it, and read it out upon request

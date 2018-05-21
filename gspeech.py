from socket import *
from select import *
from time import ctime
import sys
import io
import os
import time
import json

def is_number(number):
	try:
		float(number)
		return True
	except ValueError:
		return False

class GspeechHandler(object):

	HOST = "223.171.33.71"
	PORT = 8080
	ADDR = (HOST, PORT)

	RECORD_DURATION = 5

	PHRASES = ["action", "offboard", "arm", "disarm", "takeoff", "land", "go home"]

	INTENTS = ["action", "go", "turn"]
	ACTIONS = ["arm", "disarm", "takeoff", "land", "gohome"]
	DIRECTIONS = ["forward", "backward", "right", "left"]

	def __init__(self):

		self.sock = socket(AF_INET, SOCK_STREAM)
		
		try:
			self.sock.connect(ADDR)
		except socket.error, msg:
			print "Couldnt connect with the socket-server: %s\n terminating program" % msg
			sys.exit(1)

		try:
			from google.cloud import speech
		except ImportError:
			print("Error speech import error")
			exit(255)
		from google.cloud.speech import enums
		from google.cloud.speech import types

		self.gclient = speech.SpeechClient()

	def record_voice(self):
		print ("Record for %d seconds" % RECORD_DURATION)
		os.system('arecord -t raw -c 1 -d %d -f S16_LE -r 16000 temprec.raw' % RECORD_DURATION)       
		speech_file = os.path.join(os.path.dirname(__file__),'temprec.raw')
		return speech_file

	def transcribe_file(self, speech_file):
		#Transcribe the given audio file.
		

		with io.open(speech_file, 'rb') as audio_file:
			content = audio_file.read()

		audio = types.RecognitionAudio(content=content)
		config = types.RecognitionConfig(
			encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
			sample_rate_hertz=16000,
			language_code = 'en_US',
			speech_contexts = [speech.types.SpeechContext(
				phrases = PHRASES,
			)],
		)

		response = self.gclient.recognize(config, audio)
		transcript = ""
		for result in response.results:
			print('Transcript: {}' .format(result.alternatives[0].transcript))
			transcript = transcript + result.alternatives[0].transcript

		return transcript

	def build_message(self, voice_text):

		voice_text.lower()
		voice_texts = voice_texts.split()

		intent = voice_texts[0]

		if not intent in INTENTS:
			print "Wrong intention: %s" % intent
			print "The first word have to be in %s" % INTENTS
			return

		if intent == "action":
			action = " ".join(voice_texts[1:])

			if not action in ACTIONS:
				print "Wrong action: %s" % action
				print "Action should be one of %s" % ACTIONS
				return

			msg = {
				"command": "action",
				"content": msg,
			}

			self.send_msg(msg.dumps())

		elif intent == "go":

			direction = voice_texts[1]

			if direction not in DIRECTIONS:
				print "Wrong direction: %s" % direction
				print "Direction should be one of %s" % DIRECTIONS
				return

			if direction == "forward":

				distance = voice_texts[2]

				if is_number(distance):


					msg = {
						"command": "offboard",
						"content": {
							"vx": "1",
							"vy": "0",
							"vz": "0",
							"va": "0",
							"duration": distance,
						},
					}
				else:
					print "Wrong distance: %s" % distance
					print "Distance should be a number"

			elif direction == "backward":
				distance = voice_texts[2]

				if is_number(distance):


					msg = {
						"command": "offboard",
						"content": {
							"vx": "1",
							"vy": "0",
							"vz": "0",
							"va": "0",
							"duration": distance,
						},
					}
				else:
					print "Wrong distance: %s" % distance
					print "Distance should be a number"

			elif direction == "right":
				distance = voice_texts[2]

				if is_number(distance):


					msg = {
						"command": "offboard",
						"content": {
							"vx": "1",
							"vy": "0",
							"vz": "0",
							"va": "0",
							"duration": distance,
						},
					}
				else:
					print "Wrong distance: %s" % distance
					print "Distance should be a number"

			elif direction == "left":
				distance = voice_texts[2]

				if is_number(distance):


					msg = {
						"command": "offboard",
						"content": {
							"vx": "1",
							"vy": "0",
							"vz": "0",
							"va": "0",
							"duration": distance,
						},
					}
				else:
					print "Wrong distance: %s" % distance
					print "Distance should be a number"

			elif intent == "turn":
				distance = voice_texts[2]

				if is_number(distance):


					msg = {
						"command": "offboard",
						"content": {
							"vx": "0",
							"vy": "0",
							"vz": "0",
							"va": "0",
							"duration": distance,
						},
					}
				else:
					print "Wrong angle: %s" % distance
					print "angle should be a number"

	def send_msg(self, msg):
		pass




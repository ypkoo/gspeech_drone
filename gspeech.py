import socket
from time import ctime
import sys
import io
import os
import time
import json

try:
	from google.cloud import speech
except ImportError:
	print("Error speech import error")
	exit(255)
from google.cloud.speech import enums
from google.cloud.speech import types

def is_number(number):
	try:
		float(number)
		return True
	except ValueError:
		return False

HOST = "223.171.33.71"
# HOST = "0.0.0.0"
PORT = 8080
ADDR = (HOST, PORT)

RECORD_DURATION = 5

PHRASES = ["action", "Action", "offboard", "arm", "disarm", "takeoff", "land", "go home", "go", "forward", "backward", "right", "left", "turn", "meters", "degrees"]

INTENTS = ["action", "go", "turn", "Action", "Go", "Turn"]
ACTIONS = ["arm", "disarm", "takeoff", "land", "gohome", "take off", "go home"]
DIRECTIONS = ["forward", "backward", "right", "left"]

class GspeechHandler(object):

	

	def __init__(self):


		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		
		try:
			print "connecting to GCS..."
			self.sock.connect(ADDR)
			print "Successfully connected to GCS."
		except socket.error, msg:
			print "Couldnt connect with the socket-server: %s\n terminating program" % msg
			sys.exit(1)

		

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


		voice_text = voice_text.lower()
		voice_texts = voice_text.split()

		intent = voice_texts[0]

		msg = None

		if not intent in INTENTS:
			print "Wrong intention: %s" % intent
			print "The first word have to be in %s" % INTENTS
			return

		if intent == "action":
			action = "".join(voice_texts[1:])

			if not action in ACTIONS:
				print "Wrong action: %s" % action
				print "Action should be one of %s" % ACTIONS
				return

			msg = {
				"command": "action",
				"content": action,
			}



		elif intent == "go":

			direction = voice_texts[1]

			if direction not in DIRECTIONS:
				print "Wrong direction: %s" % direction
				print "Direction should be one of %s" % DIRECTIONS
				return

			if direction == "forward":

				try:

					distance = int(voice_texts[2])
				except ValueError:
					print "Wrong distance: %s" % distance
					print "Distance should be a number"

					return


				msg = {
					"command": "offboard",
					"content": {
						"vx": 1,
						"vy": 0,
						"vz": 0,
						"va": 0,
						"duration": distance,
					},
				}

				

			elif direction == "backward":

				try:

					distance = int(voice_texts[2])
				except ValueError:
					print "Wrong distance: %s" % distance
					print "Distance should be a number"

					return


				msg = {
					"command": "offboard",
					"content": {
						"vx": -1,
						"vy": 0,
						"vz": 0,
						"va": 0,
						"duration": distance,
					},
				}

				

			elif direction == "right":
				try:
					distance = int(voice_texts[2])
				except ValueError:
					print "Wrong distance: %s" % distance
					print "Distance should be a number"

					return


				msg = {
					"command": "offboard",
					"content": {
						"vx": 0,
						"vy": 1,
						"vz": 0,
						"va": 0,
						"duration": distance,
					},
				}

				

			elif direction == "left":
				try:

					distance = int(voice_texts[2])
				except ValueError:
					print "Wrong distance: %s" % distance
					print "Distance should be a number"

					return


				msg = {
					"command": "offboard",
					"content": {
						"vx": 0,
						"vy": -1,
						"vz": 0,
						"va": 0,
						"duration": distance,
					},
				}

				

		elif intent == "turn":
			angle = voice_texts[1]
			try:
				angle = int(angle)
			except ValueError:
				print "Wrong angle: %s" % angle
				print "angle should be a number"

				return


			msg = {
				"command": "offboard",
				"content": {
					"vx": 0,
					"vy": 0,
					"vz": 0,
					"va": 10,
					"duration": angle/10,
				},
			}

			

		return msg

	def send_msg(self, msg):
		self.sock.send(json.dumps(msg))
		print "Message sent: \n", json.dumps(msg, indent=4)



if __name__ == '__main__':
	g_handler = GspeechHandler()

	while True:
		opt = raw_input("input the option: ")

		if opt == "v":
			speech_file = g_handler.record_voice()
			text = g_handler.transcribe_file(speech_file)
			msg = g_handler.build_message(text)

			if msg:
				g_handler.send_msg(msg)
		elif opt == 'q':
			print ("Finish the program!")
			sleep(2)
			try:
				g_handler.sock.close()
				print "program finish!"
				break
			except:
				print ("Socket close failed!")
				exit()
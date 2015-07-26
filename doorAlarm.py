#!/usr/bin/env python
import time
import RPi.GPIO as io
import pygame
import paho.mqtt.client as mqtt

##### GPIO setup #####
# set the pin numbering 
io.setmode(io.BCM)

# assign GPIO pins
doorPin = 23
alarmPin = 25
disarmPin = 12
# reed switch goes pin 23 to ground
# piezo goes pin 25 to ground
# disarm button goes pin12 to button to ground

# set each pin as input or output, pull up resistors needed for switches
io.setup(doorPin, io.IN, pull_up_down=io.PUD_UP)
io.setup(alarmPin, io.OUT)
io.setup(disarmPin, io.IN, pull_up_down=io.PUD_UP)
io.output(alarmPin, 0)

##### MQTT setup #####
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("door")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

#initialize client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Broker ip, Port, timeout
client.connect("192.168.8.100", 1883, 60)

#initial door closed status
client.publish('backDoorStatus',payload='closed',qos=0,retain=False)

#subscribe to alarm armed status from openhab
subscribe([('alarmNoDelay', qos=0), ('alarmWDelay', qos=0)])



##### MUSIC setup #####
# itialize the pygame music player for the alarm file
pygame.mixer.init()
pygame.mixer.music.load("siren.ogg")

def musicStart():
    pygame.mixer.music.play(-1,0)
    print("music start")

def musicStop():
    pygame.mixer.music.stop()
    print("music stop")

##### Main alarm function #####
def alarm():
    print("door alarm")
    client.publish('backDoorStatus',payload='0',qos=0,retain=False)
    while io.input(disarmPin):
        io.output(alarmPin, 1)
        musicStart()
        if (io.input(disarmPin) == False):
            #time.sleep(10) 
            io.output(alarmPin, 0)
            client.publish('backDoorStatus',payload='1',qos=0,retain=False)
            musicStop()
            break

# Creates non-blocking loop for paho mqqt client to run
client.loop_start()

#try finally allows program to cleanup GPIO 
try:
    while True:
        if io.input(doorPin):
            alarm()
        time.sleep(0.1)
finally:
    io.cleanup()

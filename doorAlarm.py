#!/usr/bin/env python
import time
import RPi.GPIO as io
import pygame
import paho.mqtt.client as mqtt

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("door")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Broker ip, Port, timeout
client.connect("192.168.8.100", 1883, 60)
client.publish('backDoorStatus',payload='closed',qos=0,retain=False)

io.setmode(io.BCM)

doorPin = 23
alarmPin = 25
disarmPin = 12
##reed switch goes pin 23 to ground
##piezo goes pin 25 to ground
##disarm button goes pin12 to button to ground

io.setup(doorPin, io.IN, pull_up_down=io.PUD_UP)
io.setup(alarmPin, io.OUT)
io.setup(disarmPin, io.IN, pull_up_down=io.PUD_UP)

io.output(alarmPin, 0)

pygame.mixer.init()
pygame.mixer.music.load("siren.ogg")

def musicStart():
    pygame.mixer.music.play(-1,0)
    print("music start")

def musicStop():
    pygame.mixer.music.stop()
    print("music stop")

def alarm():
    print("door alarm")
    client.publish('backDoorStatus',payload='open',qos=0,retain=False)
    while io.input(disarmPin):
        io.output(alarmPin, 1)
        musicStart()
        if (io.input(disarmPin) == False):
            time.sleep(10)
            io.output(alarmPin, 0)
            client.publish('backDoorStatus',payload='closed',qos=0,retain=False)
            musicStop()
            break

client.loop_start()

try:
    while True:
        if io.input(doorPin):
            alarm()
        time.sleep(0.1)
finally:
    io.cleanup()

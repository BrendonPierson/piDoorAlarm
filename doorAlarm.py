#!/usr/bin/env python
import time
import RPi.GPIO as io
import pygame
import mqtt


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
            musicStop()
            break
try:
    while True:
        if io.input(doorPin):
            alarm()
        time.sleep(0.1)
finally:
    io.cleanup()

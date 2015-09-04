# Simple Door Alarm Using RasperryPi and Python

###Dependecies:
1. RPi.GPIO
2. paho.mqtt.client (if you plan to use any mqtt functionality that is currently commented out)

###Features:
1. Reed switch door sensor 
2. Piezo buzzer 
3. Two modes: 
  * Armed and no delay (used when you are home)
  * Armed with delay (used when going out so that alarm doesn't sound immediately upon opening the door
4. Arming switch
5. Disarm button
6. Email debugging 

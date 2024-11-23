from libre_link_up import LibreLinkUpClient
import os
import dotenv
import json
import RPi.GPIO as GPIO
import threading
import time
import math
import sys

# GPIO Setup
RED_PIN = 1
GREEN_PIN = 2
BLUE_PIN = 3

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(RED_PIN, GPIO.OUT)
GPIO.setup(GREEN_PIN, GPIO.OUT)
GPIO.setup(BLUE_PIN, GPIO.OUT)

# Create PWM objects
red_pwm = GPIO.PWM(RED_PIN, 100)    # 100 Hz frequency
green_pwm = GPIO.PWM(GREEN_PIN, 100)
blue_pwm = GPIO.PWM(BLUE_PIN, 100)

# Start PWM with 0% duty cycle
red_pwm.start(0)
green_pwm.start(0)
blue_pwm.start(0)

# Global variables for thread control
current_color = None
breathing_speed = None
stop_thread = False
breathing_thread = None


def getGlucoseData():
   glucose_data = client.get_latest_reading()
   str= glucose_data.model_dump_json()
   data = json.loads(str)
   return data['value_in_mg_per_dl']


def breathing_effect(color, speed):
    """
    Generate breathing effect for RGB LED
    Note: For common anode RGB LED, PWM values are inverted (0 = full brightness, 100 = off)
    """
    while not stop_thread:
        # Breathing effect using sine wave
        for i in range(0, 360, 2):
            if stop_thread:
                break
                
            # Calculate brightness value (0-100)
            brightness = math.sin(math.radians(i)) * 50 + 50
            # Invert for common anode (0 = full brightness, 100 = off)
            duty_cycle = 100 - brightness
            
            if color == "violet":
                red_pwm.ChangeDutyCycle(duty_cycle)
                blue_pwm.ChangeDutyCycle(duty_cycle)
                green_pwm.ChangeDutyCycle(100)  # Off
            elif color == "green":
                green_pwm.ChangeDutyCycle(duty_cycle)
                red_pwm.ChangeDutyCycle(100)    # Off
                blue_pwm.ChangeDutyCycle(100)   # Off
            elif color == "orange":
                red_pwm.ChangeDutyCycle(duty_cycle)
                #print("Duty cycle=",duty_cycle)
                green_pwm.ChangeDutyCycle(duty_cycle*0.95)  # Less green for orange
                blue_pwm.ChangeDutyCycle(100)   # Off
            elif color == "red":
                red_pwm.ChangeDutyCycle(duty_cycle)
                green_pwm.ChangeDutyCycle(100)  # Off
                blue_pwm.ChangeDutyCycle(100)   # Off
                
            # Adjust speed of breathing
            time.sleep(speed)

def start_breathing(value):
    """
    Start breathing effect based on input value
    """
    global stop_thread, breathing_thread, current_color, breathing_speed
    
    # Stop existing breathing thread if running
    if breathing_thread and breathing_thread.is_alive():
        stop_thread = True
        breathing_thread.join()
    
    # Reset stop flag
    stop_thread = False
    
    # Determine color and speed based on value
    if value < 70:
        current_color = "violet"
        breathing_speed = 0.01  # Fast
    elif 70 <= value < 170:
        current_color = "green"
        breathing_speed = 0.04  # Slow
    elif 170 <= value < 240:
        current_color = "orange"
        breathing_speed = 0.02  # Medium
    else:
        current_color = "red"
        breathing_speed = 0.01  # Fast
    
    # Start new breathing thread
    breathing_thread = threading.Thread(target=breathing_effect, 
                                     args=(current_color, breathing_speed))
    breathing_thread.start()

def cleanup():
    """
    Clean up GPIO and stop threads
    """
    global stop_thread
    stop_thread = True
    if breathing_thread:
        breathing_thread.join()
    red_pwm.stop()
    green_pwm.stop()
    blue_pwm.stop()
    GPIO.cleanup()

def main():
    dotenv.load_dotenv()
    global client
    client = LibreLinkUpClient(
        username=os.environ["LIBRE_LINK_UP_USERNAME"],
        password=os.environ["LIBRE_LINK_UP_PASSWORD"],
        url=os.environ["LIBRE_LINK_UP_URL"],
        version="4.7.0",
    )
    client.login()

    try:
        while True:
                # Get user input
                value = getGlucoseData()
                #value=200
                print("Glucose: ",value)
                start_breathing(value)
                time.sleep(60)
                
    finally:
        cleanup()

if __name__ == "__main__":
    main()

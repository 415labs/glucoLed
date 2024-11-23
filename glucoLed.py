"""Glucose monitoring system with RGB LED indicators.

This module interfaces with LibreLink Up to fetch glucose data and displays
different colors on an RGB LED based on glucose levels.
"""

from libre_link_up import LibreLinkUpClient
import os
import dotenv
import json
import RPi.GPIO as GPIO
import threading
import time
import math
import sys

# GPIO pin definitions
RED_PIN = 1
GREEN_PIN = 2
BLUE_PIN = 3

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(RED_PIN, GPIO.OUT)
GPIO.setup(GREEN_PIN, GPIO.OUT)
GPIO.setup(BLUE_PIN, GPIO.OUT)

# PWM setup
red_pwm = GPIO.PWM(RED_PIN, 100)    # 100 Hz frequency
green_pwm = GPIO.PWM(GREEN_PIN, 100)
blue_pwm = GPIO.PWM(BLUE_PIN, 100)

# Initialize PWM with 0% duty cycle
red_pwm.start(0)
green_pwm.start(0)
blue_pwm.start(0)

# Thread control variables
_current_color = None
_breathing_speed = None
_stop_thread = False
_breathing_thread = None


def get_glucose_data():
    """Fetches latest glucose reading from LibreLink Up.

    Returns:
        float: Glucose value in mg/dL.
    """
    glucose_data = client.get_latest_reading()
    data_str = glucose_data.model_dump_json()
    data = json.loads(data_str)
    return data['value_in_mg_per_dl']


def breathing_effect(color, speed):
    """Generates breathing effect for RGB LED.
    
    For common anode RGB LED, PWM values are inverted (0 = full brightness, 100 = off)
    
    Args:
        color: String indicating LED color ('violet', 'green', 'orange', or 'red')
        speed: Float controlling the breathing animation speed
    """
    while not _stop_thread:
        for i in range(0, 360, 2):
            if _stop_thread:
                break
                
            # Calculate brightness using sine wave
            brightness = math.sin(math.radians(i)) * 50 + 50
            duty_cycle = 100 - brightness  # Invert for common anode
            
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
                green_pwm.ChangeDutyCycle(duty_cycle * 0.95)  # Less green
                blue_pwm.ChangeDutyCycle(100)   # Off
            elif color == "red":
                red_pwm.ChangeDutyCycle(duty_cycle)
                green_pwm.ChangeDutyCycle(100)  # Off
                blue_pwm.ChangeDutyCycle(100)   # Off
                
            time.sleep(speed)


def start_breathing(value):
    """Starts breathing effect based on glucose value.
    
    Args:
        value: Float glucose value in mg/dL that determines LED color and animation speed
    """
    global _stop_thread, _breathing_thread, _current_color, _breathing_speed
    
    # Stop existing breathing thread if running
    if _breathing_thread and _breathing_thread.is_alive():
        _stop_thread = True
        _breathing_thread.join()
    
    _stop_thread = False
    
    # Determine color and speed based on glucose value
    if value < 70:
        _current_color = "violet"
        _breathing_speed = 0.01  # Fast
    elif 70 <= value < 170:
        _current_color = "green"
        _breathing_speed = 0.04  # Slow
    elif 170 <= value < 240:
        _current_color = "orange"
        _breathing_speed = 0.02  # Medium
    else:
        _current_color = "red"
        _breathing_speed = 0.01  # Fast
    
    _breathing_thread = threading.Thread(
        target=breathing_effect,
        args=(_current_color, _breathing_speed)
    )
    _breathing_thread.start()


def cleanup():
    """Cleans up GPIO resources and stops threads."""
    global _stop_thread
    _stop_thread = True
    if _breathing_thread:
        _breathing_thread.join()
    red_pwm.stop()
    green_pwm.stop()
    blue_pwm.stop()
    GPIO.cleanup()


def main():
    """Main program loop."""
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
            value = get_glucose_data()
            print(f"Glucose: {value}")
            start_breathing(value)
            time.sleep(60)
                
    finally:
        cleanup()


if __name__ == "__main__":
    main()

"""
Move Servo
This script moves servo using Raspberry pi GPIO pwm functionality 
"""

import RPi.GPIO as GPIO

from time import sleep

pin = 17

def kettle():
	"""
	activates the servo pressing down the kettle switch
	"""
	def setAngle(angle):
        	duty = angle / 18 + 2
        	GPIO.output(pin,True)
        	pwm.ChangeDutyCycle(duty)
        	sleep(1)
        	GPIO.output(pin, False)
        	pwm.ChangeDutyCycle(0)

	GPIO.setmode(GPIO.BCM)

	GPIO.setup(pin,GPIO.OUT)

	pwm=GPIO.PWM(pin,50)
	pwm.start(0)

	setAngle(0)
	sleep(1)
	setAngle(45)
	pwm.stop()
	GPIO.cleanup()

if __name__=='__main__':
	setAngle(120)
	sleep(3)
	setAngle(45)
	pwm.stop()
	GPIO.cleanup()

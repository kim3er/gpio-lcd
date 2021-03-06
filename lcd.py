#!/usr/bin/python

# The wiring for the LCD is as follows:
# 1 : GND
# 2 : 5V
# 3 : Contrast (0-5V)*
# 4 : RS (Register Select)
# 5 : R/W (Read Write)       - GROUND THIS PIN
# 6 : Enable or Strobe
# 7 : Data Bit 0             - NOT USED
# 8 : Data Bit 1             - NOT USED
# 9 : Data Bit 2             - NOT USED
# 10: Data Bit 3             - NOT USED
# 11: Data Bit 4
# 12: Data Bit 5
# 13: Data Bit 6
# 14: Data Bit 7
# 15: LCD Backlight +5V**
# 16: LCD Backlight GND

#import
import RPi.GPIO as GPIO
import time

# Define GPIO to LCD mapping
LCD_RS = 7
LCD_E  = 8
LCD_D4 = 25 
LCD_D5 = 24
LCD_D6 = 23
LCD_D7 = 18
LED_ON = 15

# Define some device constants
LCD_WIDTH = 20    # Maximum characters per line
LCD_CHR = True
LCD_CMD = False

LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line
LCD_LINE_3 = 0x94 # LCD RAM address for the 3rd line
LCD_LINE_4 = 0xD4 # LCD RAM address for the 4th line

# Timing constants
E_PULSE = 0.00005
E_DELAY = 0.00005

left = 1
center = 2
right = 3

class Lcd:


	def __init__(self, setmode = True):
		if setmode:
			GPIO.setmode(GPIO.BCM)       # Use BCM GPIO numbers

		GPIO.setup(LCD_E, GPIO.OUT)  # E
		GPIO.setup(LCD_RS, GPIO.OUT) # RS
		GPIO.setup(LCD_D4, GPIO.OUT) # DB4
		GPIO.setup(LCD_D5, GPIO.OUT) # DB5
		GPIO.setup(LCD_D6, GPIO.OUT) # DB6
		GPIO.setup(LCD_D7, GPIO.OUT) # DB7
		GPIO.setup(LED_ON, GPIO.OUT) # Backlight enable
		GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # LED Light Switch

		# Initialise display
		self.lcd_init()

		# Toggle backlight off-on
		GPIO.output(LED_ON, False)
		time.sleep(1)
		GPIO.output(LED_ON, True)

		# LED Light Switch Event
		self.led_state = True
		self.led_last_event = time.time()
		GPIO.add_event_detect(4, GPIO.RISING, bouncetime=700)
		GPIO.add_event_callback(4, self.toggle_light)

		print "LCD Initialised"

	def __del__(self):
		self.clear()
		GPIO.output(LED_ON, False)
		GPIO.cleanup()
		print "LCD destroyed"

	def toggle_light(self, arg):
		if (time.time() - self.led_last_event) > 0.7:
			self.led_state = not self.led_state
			GPIO.output(LED_ON, self.led_state)
			self.led_last_event = time.time()

	def lcd_init(self):
		# Initialise display
		self.lcd_byte(0x33,LCD_CMD)
		self.lcd_byte(0x32,LCD_CMD)
		self.lcd_byte(0x28,LCD_CMD)
		self.lcd_byte(0x0C,LCD_CMD)  
		self.lcd_byte(0x06,LCD_CMD)
		self.lcd_byte(0x01,LCD_CMD)  

	def lcd_string(self, message, style):
		# Send string to display
		# style=1 Left justified
		# style=2 Centred
		# style=3 Right justified

		if style==1:
			message = message.ljust(LCD_WIDTH," ")  
		elif style==2:
			message = message.center(LCD_WIDTH," ")
		elif style==3:
			message = message.rjust(LCD_WIDTH," ")

		for i in range(LCD_WIDTH):
			self.lcd_byte(ord(message[i]),LCD_CHR) # 178 is an empty box

	def lcd_byte(self, bits, mode):
		# Send byte to data pins
		# bits = data
		# mode = True  for character
		#        False for command

		GPIO.output(LCD_RS, mode) # RS

		# High bits
		GPIO.output(LCD_D4, False)
		GPIO.output(LCD_D5, False)
		GPIO.output(LCD_D6, False)
		GPIO.output(LCD_D7, False)
		if bits&0x10==0x10:
			GPIO.output(LCD_D4, True)
		if bits&0x20==0x20:
			GPIO.output(LCD_D5, True)
		if bits&0x40==0x40:
			GPIO.output(LCD_D6, True)
		if bits&0x80==0x80:
			GPIO.output(LCD_D7, True)

		# Toggle 'Enable' pin
		time.sleep(E_DELAY)    
		GPIO.output(LCD_E, True)  
		time.sleep(E_PULSE)
		GPIO.output(LCD_E, False)  
		time.sleep(E_DELAY)      

		# Low bits
		GPIO.output(LCD_D4, False)
		GPIO.output(LCD_D5, False)
		GPIO.output(LCD_D6, False)
		GPIO.output(LCD_D7, False)
		if bits&0x01==0x01:
			GPIO.output(LCD_D4, True)
		if bits&0x02==0x02:
			GPIO.output(LCD_D5, True)
		if bits&0x04==0x04:
			GPIO.output(LCD_D6, True)
		if bits&0x08==0x08:
			GPIO.output(LCD_D7, True)

		# Toggle 'Enable' pin
		time.sleep(E_DELAY)    
		GPIO.output(LCD_E, True)  
		time.sleep(E_PULSE)
		GPIO.output(LCD_E, False)  
		time.sleep(E_DELAY)

	def write_line(self, message, line = LCD_LINE_1, style = left):
		self.lcd_byte(line, LCD_CMD)
		self.lcd_string(message, style)

	def clear(self):
		# Blank display
		self.write_line("", LCD_LINE_1)
		self.write_line("", LCD_LINE_2)
		self.write_line("", LCD_LINE_3)
		self.write_line("", LCD_LINE_4)

	def animate_left(self, message, line = LCD_LINE_1):
		animated_message = ""
		i = 1
		l = len(message)
		while i <= LCD_WIDTH:
			if i > l:
				animated_message = animated_message + " "
			else:
				animated_message = message[:i]

			self.write_line(animated_message, line, right)
			i = i + 1
			time.sleep(.5)

	def animate_right(self, message, line = LCD_LINE_1):
		animated_message = ""
		i = LCD_WIDTH
		l = len(message)
		d = LCD_WIDTH - l
		while i >= 0:
			if i - d < 0:
				animated_message = " " + animated_message
			else:
				animated_message = message[i - d:]

			self.write_line(animated_message, line, left)
			i = i - 1
			time.sleep(.5)

	def animate_down(self, message, style = center, trail = False, how_many_lines = 4):
		lines = [LCD_LINE_1, LCD_LINE_2, LCD_LINE_3, LCD_LINE_4]
		i = 0
		for line in lines:
			if not trail:
				self.write_line("", lines[i - 1])

			self.write_line(message, line, style)
			i = i + 1

			if i  == how_many_lines:
				break
			time.sleep(.5)
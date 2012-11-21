#!/usr/bin/python
# -*- coding: utf-8 -*-

import lcd
import time
from datetime import datetime

my_lcd = lcd.Lcd()

while True:
	my_lcd.animate_down("test")
	my_lcd.animate_down("Disco", lcd.center, True, 3)
	my_lcd.animate_left(datetime.now().strftime('%T'))
	my_lcd.animate_right(datetime.now().strftime('%T'), lcd.LCD_LINE_2)
	time.sleep(60)
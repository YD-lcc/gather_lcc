#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Gather: Modify by WillzenZou
# BakeBit example for the basic functions of BakeBit 128x64 OLED (http://wiki.friendlyarm.com/wiki/index.php/BakeBit_-_OLED_128x64)
#

from __future__ import print_function
import ssd1306_128_64_oled as oled
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import sys
import os

global width
width=128
global height
height=64

oled.init()  #initialze SEEED OLED display
oled.setNormalDisplay()      #Set display to normal mode (i.e non-inverse mode)
oled.setHorizontalMode()
#oled.setVerticalMode()

global image
image = Image.new('1', (width, height))
global draw
draw = ImageDraw.Draw(image)
global fontb24
fontb24 = ImageFont.truetype('DejaVuSansMono-Bold.ttf', 24);
global font14
font14 = ImageFont.truetype('DejaVuSansMono.ttf', 14);
global smartFont
smartFont = ImageFont.truetype('DejaVuSansMono.ttf', 10);
global fontb14
fontb14 = ImageFont.truetype('DejaVuSansMono-Bold.ttf', 14);
global font11
font11 = ImageFont.truetype('DejaVuSansMono.ttf', 11);

oled.clearDisplay()
image0 = Image.open('logo.png').convert('1')
oled.drawImage(image0)

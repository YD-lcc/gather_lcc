#!/usr/bin/env python
#
# BakeBit library for the basic functions of BakeBit 128x64 OLED (http://wiki.friendlyarm.com/wiki/index.php/BakeBit_-_OLED_128x64)
# v1.0
#
# The BakeBit connects the NanoPi NEO and BakeBit sensors.
# You can learn more about BakeBit here:  http://wiki.friendlyarm.com/BakeBit
#
# Have a question about this example?  Ask on the forums here:  http://www.friendlyarm.com/Forum/
#
#
'''
## License

The MIT License (MIT)

BakeBit: an open source platform for connecting BakeBit Sensors to the NanoPi NEO.
Copyright (C) 2016 FriendlyARM

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
'''

import smbus
import time
import math
import struct

bus = smbus.SMBus(0)
address=0x3c
addressingMode= None
SeeedOLED_Width			=128 #128 Pixels
SeeedOLED_Height		=64  #64  Pixels
SeeedOLED_Max_X                 =SeeedOLED_Width
SeeedOLED_Max_Y                 =SeeedOLED_Height
                                
PAGE_MODE                       =0x01
HORIZONTAL_MODE                 =0x02
VERTICAL_MODE                 =0x03
                                                            
SeeedOLED_Address               =0x3d
SeeedOLED_Command_Mode          =0x00
SeeedOLED_Data_Mode             =0x40 #####
SeeedOLED_Display_Off_Cmd       =0xAE #####
SeeedOLED_Display_On_Cmd        =0xAF #####
SeeedOLED_Normal_Display_Cmd    =0xA6
SeeedOLED_Inverse_Display_Cmd   =0xA7
SeeedOLED_Activate_Scroll_Cmd   =0x2F
SeeedOLED_Dectivate_Scroll_Cmd  =0x2E
SeeedOLED_Set_Brightness_Cmd    =0x81

Scroll_Left             =0x00
Scroll_Right            =0x01
                        
Scroll_2Frames          =0x7
Scroll_3Frames          =0x4
Scroll_4Frames          =0x5
Scroll_5Frames          =0x0
Scroll_25Frames         =0x6
Scroll_64Frames         =0x1
Scroll_128Frames        =0x2
Scroll_256Frames        =0x3

BasicFont = [[0 for x in range(8)] for x in range(10)]
BasicFont=[[0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00],
[0x00,0x00,0x5F,0x00,0x00,0x00,0x00,0x00],
[0x00,0x00,0x07,0x00,0x07,0x00,0x00,0x00],
[0x00,0x14,0x7F,0x14,0x7F,0x14,0x00,0x00],
[0x00,0x24,0x2A,0x7F,0x2A,0x12,0x00,0x00],
[0x00,0x23,0x13,0x08,0x64,0x62,0x00,0x00],
[0x00,0x36,0x49,0x55,0x22,0x50,0x00,0x00],
[0x00,0x00,0x05,0x03,0x00,0x00,0x00,0x00],
[0x00,0x1C,0x22,0x41,0x00,0x00,0x00,0x00],
[0x00,0x41,0x22,0x1C,0x00,0x00,0x00,0x00],
[0x00,0x08,0x2A,0x1C,0x2A,0x08,0x00,0x00],
[0x00,0x08,0x08,0x3E,0x08,0x08,0x00,0x00],
[0x00,0xA0,0x60,0x00,0x00,0x00,0x00,0x00],
[0x00,0x08,0x08,0x08,0x08,0x08,0x00,0x00],
[0x00,0x60,0x60,0x00,0x00,0x00,0x00,0x00],
[0x00,0x20,0x10,0x08,0x04,0x02,0x00,0x00],
[0x00,0x3E,0x51,0x49,0x45,0x3E,0x00,0x00],
[0x00,0x00,0x42,0x7F,0x40,0x00,0x00,0x00],
[0x00,0x62,0x51,0x49,0x49,0x46,0x00,0x00],
[0x00,0x22,0x41,0x49,0x49,0x36,0x00,0x00],
[0x00,0x18,0x14,0x12,0x7F,0x10,0x00,0x00],
[0x00,0x27,0x45,0x45,0x45,0x39,0x00,0x00],
[0x00,0x3C,0x4A,0x49,0x49,0x30,0x00,0x00],
[0x00,0x01,0x71,0x09,0x05,0x03,0x00,0x00],
[0x00,0x36,0x49,0x49,0x49,0x36,0x00,0x00],
[0x00,0x06,0x49,0x49,0x29,0x1E,0x00,0x00],
[0x00,0x00,0x36,0x36,0x00,0x00,0x00,0x00],
[0x00,0x00,0xAC,0x6C,0x00,0x00,0x00,0x00],
[0x00,0x08,0x14,0x22,0x41,0x00,0x00,0x00],
[0x00,0x14,0x14,0x14,0x14,0x14,0x00,0x00],
[0x00,0x41,0x22,0x14,0x08,0x00,0x00,0x00],
[0x00,0x02,0x01,0x51,0x09,0x06,0x00,0x00],
[0x00,0x32,0x49,0x79,0x41,0x3E,0x00,0x00],
[0x00,0x7E,0x09,0x09,0x09,0x7E,0x00,0x00],
[0x00,0x7F,0x49,0x49,0x49,0x36,0x00,0x00],
[0x00,0x3E,0x41,0x41,0x41,0x22,0x00,0x00],
[0x00,0x7F,0x41,0x41,0x22,0x1C,0x00,0x00],
[0x00,0x7F,0x49,0x49,0x49,0x41,0x00,0x00],
[0x00,0x7F,0x09,0x09,0x09,0x01,0x00,0x00],
[0x00,0x3E,0x41,0x41,0x51,0x72,0x00,0x00],
[0x00,0x7F,0x08,0x08,0x08,0x7F,0x00,0x00],
[0x00,0x41,0x7F,0x41,0x00,0x00,0x00,0x00],
[0x00,0x20,0x40,0x41,0x3F,0x01,0x00,0x00],
[0x00,0x7F,0x08,0x14,0x22,0x41,0x00,0x00],
[0x00,0x7F,0x40,0x40,0x40,0x40,0x00,0x00],
[0x00,0x7F,0x02,0x0C,0x02,0x7F,0x00,0x00],
[0x00,0x7F,0x04,0x08,0x10,0x7F,0x00,0x00],
[0x00,0x3E,0x41,0x41,0x41,0x3E,0x00,0x00],
[0x00,0x7F,0x09,0x09,0x09,0x06,0x00,0x00],
[0x00,0x3E,0x41,0x51,0x21,0x5E,0x00,0x00],
[0x00,0x7F,0x09,0x19,0x29,0x46,0x00,0x00],
[0x00,0x26,0x49,0x49,0x49,0x32,0x00,0x00],
[0x00,0x01,0x01,0x7F,0x01,0x01,0x00,0x00],
[0x00,0x3F,0x40,0x40,0x40,0x3F,0x00,0x00],
[0x00,0x1F,0x20,0x40,0x20,0x1F,0x00,0x00],
[0x00,0x3F,0x40,0x38,0x40,0x3F,0x00,0x00],
[0x00,0x63,0x14,0x08,0x14,0x63,0x00,0x00],
[0x00,0x03,0x04,0x78,0x04,0x03,0x00,0x00],
[0x00,0x61,0x51,0x49,0x45,0x43,0x00,0x00],
[0x00,0x7F,0x41,0x41,0x00,0x00,0x00,0x00],
[0x00,0x02,0x04,0x08,0x10,0x20,0x00,0x00],
[0x00,0x41,0x41,0x7F,0x00,0x00,0x00,0x00],
[0x00,0x04,0x02,0x01,0x02,0x04,0x00,0x00],
[0x00,0x80,0x80,0x80,0x80,0x80,0x00,0x00],
[0x00,0x01,0x02,0x04,0x00,0x00,0x00,0x00],
[0x00,0x20,0x54,0x54,0x54,0x78,0x00,0x00],
[0x00,0x7F,0x48,0x44,0x44,0x38,0x00,0x00],
[0x00,0x38,0x44,0x44,0x28,0x00,0x00,0x00],
[0x00,0x38,0x44,0x44,0x48,0x7F,0x00,0x00],
[0x00,0x38,0x54,0x54,0x54,0x18,0x00,0x00],
[0x00,0x08,0x7E,0x09,0x02,0x00,0x00,0x00],
[0x00,0x18,0xA4,0xA4,0xA4,0x7C,0x00,0x00],
[0x00,0x7F,0x08,0x04,0x04,0x78,0x00,0x00],
[0x00,0x00,0x7D,0x00,0x00,0x00,0x00,0x00],
[0x00,0x80,0x84,0x7D,0x00,0x00,0x00,0x00],
[0x00,0x7F,0x10,0x28,0x44,0x00,0x00,0x00],
[0x00,0x41,0x7F,0x40,0x00,0x00,0x00,0x00],
[0x00,0x7C,0x04,0x18,0x04,0x78,0x00,0x00],
[0x00,0x7C,0x08,0x04,0x7C,0x00,0x00,0x00],
[0x00,0x38,0x44,0x44,0x38,0x00,0x00,0x00],
[0x00,0xFC,0x24,0x24,0x18,0x00,0x00,0x00],
[0x00,0x18,0x24,0x24,0xFC,0x00,0x00,0x00],
[0x00,0x00,0x7C,0x08,0x04,0x00,0x00,0x00],
[0x00,0x48,0x54,0x54,0x24,0x00,0x00,0x00],
[0x00,0x04,0x7F,0x44,0x00,0x00,0x00,0x00],
[0x00,0x3C,0x40,0x40,0x7C,0x00,0x00,0x00],
[0x00,0x1C,0x20,0x40,0x20,0x1C,0x00,0x00],
[0x00,0x3C,0x40,0x30,0x40,0x3C,0x00,0x00],
[0x00,0x44,0x28,0x10,0x28,0x44,0x00,0x00],
[0x00,0x1C,0xA0,0xA0,0x7C,0x00,0x00,0x00],
[0x00,0x44,0x64,0x54,0x4C,0x44,0x00,0x00],
[0x00,0x08,0x36,0x41,0x00,0x00,0x00,0x00],
[0x00,0x00,0x7F,0x00,0x00,0x00,0x00,0x00],
[0x00,0x41,0x36,0x08,0x00,0x00,0x00,0x00],
[0x00,0x02,0x01,0x01,0x02,0x01,0x00,0x00],
[0x00,0x02,0x05,0x05,0x02,0x00,0x00,0x00]]

def sendCommand(byte):
    try:
        block=[]
        block.append(byte)
        return bus.write_i2c_block_data(address,SeeedOLED_Command_Mode,block)
    except IOError:
        print("IOError")
        return -1

def sendData(byte):
    try:
        block=[]
        block.append(byte)
        return bus.write_i2c_block_data(address,SeeedOLED_Data_Mode,block)
    except IOError:
        print("IOError")
        return -1

def sendArrayData(array):
    try:
        return bus.write_i2c_block_data(address,SeeedOLED_Data_Mode,array)
    except IOError:
        print("IOError")
        return -1    

def multi_comm(commands):
    for c in commands:
        sendCommand(c)

def base_init():
        sendCommand(0x00)    #set lower column address
        sendCommand(0x10)    #set higher column address
  
        sendCommand(0x40)    #set display start line
  
        sendCommand(0xB0)    #set page address
  
        sendCommand(0x81)
        sendCommand(0xCF)    #0~255????????????????
  
        sendCommand(0xA1)    #set segment remap
  
        sendCommand(0xA6)    #normal / reverse
  
        sendCommand(0xA8)    #multiplex ratio
        sendCommand(0x3F)    #duty = 1/64
  
        sendCommand(0xC8)    #Com scan direction
  
        sendCommand(0xD3)    #set display offset
        sendCommand(0x00);
  
        sendCommand(0xD5)    #set osc division
        sendCommand(0x80);
  
        sendCommand(0xD9)    #set pre-charge period
        sendCommand(0xF1);
  
        sendCommand(0xDA)    #set COM pins
        sendCommand(0x12);
  
        sendCommand(0xDB)    #set vcomh
        sendCommand(0x40);
  
        sendCommand(0x8D)    #set charge pump enable
        sendCommand(0x14);

# Init function of the OLED
def init():
        sendCommand(0xAE)    #display off

        sendCommand(0xD5)    #set osc division
        sendCommand(0x80);
 
        sendCommand(0xA8)    #multiplex ratio
        sendCommand(0x3F)    #duty = 1/64

        sendCommand(0xD3)    #set display offset
        sendCommand(0x38);      #0x38 0x20

        sendCommand(0x40 | 0x0)    #set display start line

        sendCommand(0x8D)    #set charge pump enable
        sendCommand(0x14);

        sendCommand(0xA0 | 0x1)    #set segment remap (0xA1)

        sendCommand(0xC8)    #set Com scan output direction

        sendCommand(0xDA)    #set COM pins hardware configuration
        sendCommand(0x12);

        sendCommand(0xD9)    #set pre-charge period
        sendCommand(0xF1);

        sendCommand(0xDB)    #set vcomh seselect level
        sendCommand(0x40);

        sendCommand(0x00)    #set lower column address
        sendCommand(0x10)    #set higher column address

        sendCommand(0x40)    #set page address

        sendCommand(0x81)    # set gamma
        sendCommand(0xCF)    #0~255????????????????

        # Entrie Display ON
        sendCommand(0xA4)    #Resume to RAM content display. Output follows RAM content
        sendCommand(0xA6)    #normal / reverse
        sendCommand(0xAF)    #display ON

#	sendCommand(SeeedOLED_Display_Off_Cmd)     #display off
#	time.sleep(.005) 
#	sendCommand(SeeedOLED_Display_On_Cmd)  	#display on
#	time.sleep(.005) 
#	sendCommand(SeeedOLED_Normal_Display_Cmd)  #Set Normal Display (default)

def setBrightness(Brightness):
   sendCommand(SeeedOLED_Set_Brightness_Cmd)
   sendCommand(Brightness)
  
def setHorizontalMode():
	global addressingMode
	addressingMode = HORIZONTAL_MODE
	sendCommand(0x20)          #set addressing mode
	sendCommand(0x00)          #set horizontal addressing mode

def setVerticalMode():
	global addressingMode
	addressingMode = VERTICAL_MODE
	sendCommand(0x20)          #set addressing mode
	sendCommand(0x01)          #set vertical addressing mode

def setPageMode():
	global addressingMode
	addressingMode = PAGE_MODE
	sendCommand(0x20)          #set addressing mode
	sendCommand(0x02)          #set page addressing mode

def setTextXY(Column,Row):
    sendCommand(0xB0 + Row)           #set page address
    sendCommand(0x00 + (8*Column & 0x0F))  #set column lower address
    sendCommand(0x10 + ((8*Column>>4)&0x0F))   #set column higher address

def clearDisplay():
	sendCommand(SeeedOLED_Display_Off_Cmd)   #display off
	for j in range(8):
		setTextXY(0,j)    
		for i in range(16):  #clear all columns
			putChar(' ')    
	sendCommand(SeeedOLED_Display_On_Cmd)    #display on
	setTextXY(0,0)    

def putChar(C):
	C_add=ord(C)
	if C_add<32 or C_add>127:     # Ignore non-printable ASCII characters
		C=' '
		C_add=ord(C)

	for i in range(8):
		data=(BasicFont[C_add-32][i])
		sendData(data)
	
    # for i in range(0,8,2):
        # for j in range(0,8):
            # c=0x00
            # bit1=((BasicFont[C_add-32][i])>>j)&0x01
            # bit2=((BasicFont[C_add-32][i+1])>>j)&0x01
            # if bit1:
                # c=c|grayH
            # else:
                # c=c|0x00
            # if bit2:
                # c=c|grayL
            # else:
                # c=c|0x00
            # sendData(c)

def putString(s):
    for i in range(len(s)):
        putChar(s[i])

def drawImage(image):
    """Set buffer to value of Python Imaging Library image.  The image should
    be in 1 bit mode and a size equal to the display size.
    """
    if image.mode != '1':
        raise ValueError('Image must be in mode 1.')
    imwidth, imheight = image.size
    if imwidth != SeeedOLED_Width or imheight != SeeedOLED_Height:
        raise ValueError('Image must be same dimensions as display ({0}x{1}).' \
            .format(SeeedOLED_Width, SeeedOLED_Height))
    # Grab all the pixels from the image, faster than getpixel.
    pix = image.load()
    # Iterate through the memory pages
    bitList = []
    pages=SeeedOLED_Height/8
    for page in range(int(pages)):
        # Iterate through all x axis columns.
        for x in range(SeeedOLED_Width):
            # Set the bits for the column of pixels at the current position.
            bits = 0
            # Don't use range here as it's a bit slow
            for bit in [0, 1, 2, 3, 4, 5, 6, 7]:
                bits = bits << 1
                bits |= 0 if pix[x, page*8+7-bit] == 0 else 1
            bitList.append(bits)

    for chunk in chunks(bitList, 32):
        sendArrayData(chunk)

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]
		
def putNumber(long_num):
	char_buffer[10]=None
	i = 0
	f = 0

	if (long_num < 0) :
		f=1
		putChar('-')
		long_num = -long_num
		
	elif (long_num == 0) :
		f=1
		putChar('0')
		return f
	
	while (long_num > 0):
		char_buffer[i] = long_num % 10
		long_num /= 10
		i+=1

	f=f+i
	while(i>0):
		putChar('0'+ char_buffer[i - 1])
		i-=1
	return f


def setHorizontalScrollProperties(direction,startPage, endPage, scrollSpeed):

	'''
	Use the following defines for 'direction' :
	Scroll_Left            
	Scroll_Right           
	Use the following defines for 'scrollSpeed' :
	Scroll_2Frames     
	Scroll_3Frames
	Scroll_4Frames
	Scroll_5Frames 
	Scroll_25Frames
	Scroll_64Frames
	Scroll_128Frames
	Scroll_256Frames
	'''

	if(Scroll_Right == direction):
		#Scroll Right
		sendCommand(0x26)
	else:
		#Scroll Left  
		sendCommand(0x27)

	sendCommand(0x00)
	sendCommand(startPage)
	sendCommand(scrollSpeed)
	sendCommand(endPage)
	sendCommand(0x00)
	sendCommand(0xFF)


def activateScroll():
    sendCommand(SeeedOLED_Activate_Scroll_Cmd)

def deactivateScroll():
    sendCommand(SeeedOLED_Dectivate_Scroll_Cmd)

def setNormalDisplay():
    sendCommand(SeeedOLED_Normal_Display_Cmd)

def setInverseDisplay():
    sendCommand(SeeedOLED_Inverse_Display_Cmd)

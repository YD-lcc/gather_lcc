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
import time
import sys
import subprocess
import threading
import signal
import os
import socket
import fcntl
import struct
import json

global width
width=128
global height
height=64

#config
netCount = 5
batthight = 680
battlow = 200
battlast = 27000

global upspeedtext, downspeedtext
upspeedtext = "N/a"
downspeedtext = "N/a"

global batper
batper = 0

oled.init()  #initialze SEEED OLED display
oled.setNormalDisplay()      #Set display to normal mode (i.e non-inverse mode)
oled.setHorizontalMode()
#oled.setVerticalMode()

global drawing
drawing = False

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

global lock
lock = threading.Lock()

def get_lanspeed():
    global upspeedtext, downspeedtext
    while True:
        try:
            #cmd = "vnstat --add -i br-lan"
            #temp = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
            cmd = "vnstat -i br-lan -s -tr 2 --json" #vnstat -5 -i br-lan -s --oneline -ru
            temp = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
            #temp = temp.split(";")
            temp = json.loads(temp)
            downspeedtext = temp['tx']['ratestring'].replace("KiB","K").replace("MiB", "M").replace("GiB", "G").replace("TiB", "T").replace("/s", "").replace(" ", "").replace("it", "")
            upspeedtext = temp['rx']['ratestring'].replace("KiB","K").replace("MiB", "M").replace("GiB", "G").replace("TiB", "T").replace("/s", "").replace(" ", "").replace("it", "")
        except:
            upspeedtext = "N/a"
            downspeedtext = "N/a"
            print("except")

t = threading.Thread(target=get_lanspeed)
t.setDaemon(True)
t.start()

def get_batt():
    global batper, battlast
    batper = 0
    batmove = 0
    while True:
        try:
            voltage = 0
            for i in range(10):
                cmd = "cat /sys/bus/iio/devices/iio\:device0/in_voltage0-voltage1_raw"
                voltage += int(subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore"))
            if int(voltage / 10) < 3000:
                battlast = 2400
            else:
                battlast = 27000
            batcalc = batthight - battlow
            if (batper > 0 and batper < 10):
                batcalc = battlow * 10
                voltage = int(voltage / 10) - battlast
            else:
                voltage = int(voltage / 10) - battlast - battlow
            if batper == 0:
                batper = int(float(voltage) / float(batcalc) * 100)
            elif batper > 0:
                temp = int(float(voltage) / float(batcalc) * 100)
                if temp - batper > 0:
                    batmove += 1
                elif temp - batper < 0:
                    batmove -= 1
                if ( batmove > 10 or batmove < -10):
                    batper = temp
                    batmove = 0
            print(str(batmove) +"\n"+ str(batper) + " \n " + str(voltage))
        except:
            voltage = 0
            print("except")
        time.sleep(1)

tb = threading.Thread(target=get_batt)
tb.setDaemon(True)
tb.start()

def draw_logo():
    #wanol = Image.open('./imgs/wan-online.png').convert('1')
    #draw.bitmap((0,0), wanol, fill=255)
    up = Image.open('./imgs/up.png').convert('1')
    draw.bitmap((0,16), up, fill=255)
    down = Image.open('./imgs/down.png').convert('1')
    draw.bitmap((0,32), down, fill=255)
    server = Image.open('./imgs/ecs.png').convert('1')
    draw.bitmap((0,48), server, fill=255)

def draw_net(ifname, info):
    net = '0' if ifname == 'eth1' else ('1' if ifname == 'usb0' else ('2' if ifname == 'usb1' else ('3' if ifname == 'usb2' else ('4' if ifname == 'usb3' else ('5' if ifname == 'usb4' else '')))))
    x_logo = int(net)*22
    y_logo = 0
    if net == "":
        return
    if info == "up":
        if ifname == 'eth1':
            netlogo = Image.open('./imgs/wan-online.png').convert('1')
            draw.bitmap((x_logo,y_logo), netlogo, fill=255)
        else:
            netlogo = Image.open('./imgs/wan'+net+'.png').convert('1')
            draw.bitmap((x_logo,y_logo), netlogo, fill=255)
    elif info == "down":
        if ifname == 'eth1':
            netlogo = Image.open('./imgs/wan-err.png').convert('1')
            draw.bitmap((x_logo,y_logo), netlogo, fill=255)
        else:
            netlogo = Image.open('./imgs/'+net+'-0-0.png').convert('1')
            draw.bitmap((x_logo,y_logo), netlogo, fill=255)
    else:
        pre_fn = '0-0' if info <= 0 else '0-25' if info <= 25 else '25-50' if info <= 50 else '50-75' if info <= 75 else '75-100' if info <= 100 else '0-0'
        netlogo = Image.open('./imgs/' + net + '-' + pre_fn + '.png').convert('1')
        draw.bitmap((x_logo,y_logo), netlogo, fill=255)

def draw_page():
    global drawing
    global image
    global draw
    global oled
    global font
    global font14
    global smartFont
    global width
    global height
    global lock

    lock.acquire()
    is_drawing = drawing
    lock.release()

    if is_drawing:
        return

    lock.acquire()
    drawing = True
    lock.release()

    # Draw a black filled box to clear the image.
    draw.rectangle((0,0,width,height), outline=0, fill=0)

    text = 'NET'
    draw_logo()
    for i in range(1, netCount + 1):
        try:
            cmd = "uci get network.wan" + str(i) + ".ifname | tr -d '\n'"
            ifname = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
            cmd = "ip -4 -br addr ls dev " + ifname + " | awk -F '[ /]+' '{print $3}' | tr -d '\n'"
            temp = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
            if temp != "":
                #text += " " + str(i)
                #cmd = "ping -w 1 -c 1 -I " + ifname + " " + temp + " | grep ' 0% packet loss' || true"
                #temp = subprocess.check_output(cmd, shell = True).decode("utf-8", errors="ignore")
                cmd = "uci get openmptcprouter.wan" + str(i) + ".state | tr -d '\n'"
                print(cmd)
                temp = subprocess.check_output(cmd, shell = True).decode("utf-8", errors="ignore")
                if temp == "up":
                    draw_net(ifname, "up")
                else:
                    draw_net(ifname, "down")
        except:
            text += "  "
    # text = time.strftime("%a %e %b %Y")
    #draw.text((0,0),text,font=font14,fill=255)
    draw.text((20,17),upspeedtext,font=font14,fill=255)
    draw.text((20,33),downspeedtext,font=font14,fill=255)

    text = ""
    try:
        cmd = "uci get openmptcprouter.omr.detected_ss_ipv4"
        temp = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
        text += str(temp)
    except:
        text += "Wating Server"
    draw.text((20,49),text,font=font14,fill=255)

    #year=time.strftime('%Y')
    #now=time.time()
    #start_date=time.mktime(time.strptime(year, '%Y'))
    #end_date=time.mktime(time.strptime(str(int(year)+1), '%Y'))
    #percent=int((now-start_date)/(end_date-start_date)*1000)/10.0
    percent= 100 if batper > 100 else ( 0 if batper < 0 else batper )
    bar = str(int(round(percent/20, 0))*20)
    print(bar)
    batlogo = Image.open('./imgs/bat' + bar + '.png' ).convert('1')
    draw.bitmap((110,18), batlogo, fill=255)
    #text = "Batt: " + bar * u'\u2588' + (10 - bar) * u'\u2591' # + str(percent) + '%'
    #draw.text((0,46),text,font=font14,fill=255)

    oled.drawImage(image)

    lock.acquire()
    drawing = False
    lock.release()

oled.clearDisplay()
image0 = Image.open('logo.png').convert('1')
oled.drawImage(image0)
time.sleep(2)

while True:
    try:
        draw_page()
        time.sleep(1)
    except KeyboardInterrupt:
        break
    except IOError:
        print ("Error")

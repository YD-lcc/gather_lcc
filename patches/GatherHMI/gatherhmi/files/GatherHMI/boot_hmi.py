#!/usr/bin/python3
import serial
import threading
import time
import re
import subprocess
import json

ser = None
def connectSerial():
    global ser
    while True:
        ser = serial.Serial("/dev/ttyS1", 9600, 8, "N", 1,timeout=5)
        flag = ser.is_open
        if flag:
            print("success")
            ser.write(b"prints baud,0\xff\xff\xff")
            ser.write(b"printh 0a\xff\xff\xff")
            if ser.readline().hex()=="802500000a":
                ser.write(b"baud=115200\xff\xff\xff")
            ser.close()
            ser = serial.Serial("/dev/ttyS1", 115200, 8, "N", 1,timeout=5)
            flag = ser.is_open
            if flag:
                ser.write(b"prints baud,0\xff\xff\xff")
                ser.write(b"printh 0a\xff\xff\xff")
                if ser.readline().hex()=="1affffff0a":
                    break
        else:
            print("open error")

# 全局网速检测
global upspeedtext, downspeedtext
upspeedtext = "N/a"
downspeedtext = "N/a"

def getwanspeed(device):
    while True:
        try:
            cmd = "vnstat -i "+device+" -s -tr 2 --json" #vnstat -5 -i br-lan -s --oneline -ru
            temp = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
            #temp = temp.split(";")
            temp = json.loads(temp)
            page.nettotal[device+'up'] = temp['tx']['ratestring'].replace("kib","Kb").replace("mib", "Mb").replace("gib", "Gb").replace("tib", "Tb").replace(" ", "").replace("/s", "ps").replace("it", "")
            page.nettotal[device+'down'] = temp['rx']['ratestring'].replace("kib","Kb").replace("mib", "Mb").replace("gib", "Gb").replace("tib", "Tb").replace(" ", "").replace("/s", "ps").replace("it", "")
            if device!="eth1":
                cmd = "timeout 1 uqmi -d /dev/cdc-wdm"+device[-1]+" --get-capabilities | grep lte | awk '{print $1}' | tr -d '\n' || true"
                temp = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
                if temp=="\"lte\"":
                    page.nettotal[device+'type']="4g"
                else:
                    page.nettotal[device+'type']="null"
        except:
            pass
    
wwanthread=[None,None,None,None,None]
def get_lanspeed():
    global upspeedtext, downspeedtext,wwanthread
    while True:
        try:
            cmd = "vnstat --add -i br-lan && /etc/init.d/vnstat_backup reload && /etc/init.d/vnstat restart || true"
            temp = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
            # 如果接口起来了，启动各个接口的网速检测
            i=0
            for device in "wwan0 wwan1 wwan2 wwan3 eth1".split():
                cmd = "ip -4 -br addr ls dev " + device + " || true"
                temp = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
                if temp != "":
                    cmd = "vnstat --add -i "+ device +" && /etc/init.d/vnstat_backup reload && /etc/init.d/vnstat restart || true"
                    temp = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
                    if wwanthread[i]==None or wwanthread[i].is_alive()==False:
                        wwanthread[i]=threading.Thread(target=getwanspeed, args=(device,))
                        wwanthread[i].setDaemon(True)
                        wwanthread[i].start()
                i+=1
        except:
            pass
        try:
            cmd = "vnstat -i br-lan -s -tr 2 --json" #vnstat -5 -i br-lan -s --oneline -ru
            temp = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
            #temp = temp.split(";")
            temp = json.loads(temp)
            downspeedtext = temp['tx']['ratestring'].replace("kib","Kb").replace("mib", "Mb").replace("gib", "Gb").replace("tib", "Tb").replace(" ", "").replace("/s", "ps").replace("it", "")
            upspeedtext = temp['rx']['ratestring'].replace("kib","Kb").replace("mib", "Mb").replace("gib", "Gb").replace("tib", "Tb").replace(" ", "").replace("/s", "ps").replace("it", "")
            # 获取统计
            cmd = "vnstat -s -d 1 --json" #vnstat -5 -i br-lan -s --oneline -ru
            temp = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
            temp = json.loads(temp)
            for info in temp['interfaces']:
                if info['name'] == "eth1":
                    page.rj45traffic=info['traffic']['total']['rx'] + info['traffic']['total']['tx']
                    if page.rj45traffic/1024/1024 < 1000:
                        page.rj45traffic="%.1f M"%round(page.rj45traffic/1024/1024,1)
                    else:
                        page.rj45traffic="%.1f G"%round(page.rj45traffic/1024/1024/1024,1)
                elif info['name'] == "br-lan":
                    page.lantraffic=info['traffic']['total']['rx'] + info['traffic']['total']['tx']
                    if page.lantraffic/1024/1024 < 1000:
                        page.lantraffic="%.1f M"%round(page.lantraffic/1024/1024,1)
                    else:
                        page.lantraffic="%.1f G"%round(page.lantraffic/1024/1024/1024,1)
                else:
                    page.nettotal[info['name']+'count']=info['traffic']['total']['rx'] + info['traffic']['total']['tx']
                    if page.nettotal[info['name']+'count']/1024/1024 < 1000:
                        page.nettotal[info['name']+'count']="%.1fM"%round(page.nettotal[info['name']+'count']/1024/1024,1)
                    else:
                        page.nettotal[info['name']+'count']="%.1fG"%round(page.nettotal[info['name']+'count']/1024/1024/1024,1)
        except:
            upspeedtext = "N/a"
            downspeedtext = "N/a"
            #page.nettotal['wwan2count']="N/a"
            print("except")

t = threading.Thread(target=get_lanspeed)
t.setDaemon(True)
t.start()

# 第一页
class page:
    pageIndexStop=False # 检查首页的状态，确定首页信息刷新进程是否要停止
    isSetWifi=False # 设置wifi的状态，防止频繁点击的重复设置
    getpage=False # 检查是否获取page成功
    isSetMode=False # 设置模式的状态，防止频繁点击
    listSetPort=[] # 设置端口的队列，按队列处理端口
    isSetPort=False # 设置端口的状态，防止频繁点击
    isSetMptcp=False # 设置mptcp的状态，防止频繁点击
    isSetReset=False # 设置ResetPort的状态，防止频繁点击
    isSetRj45=False  # 设置ResetPort的状态，防止频繁点击
    lantraffic=0
    rj45traffic=0
    wwan2traffic=0
    nettotal={}
    getlanthread=None
    downinfo=None
    
    def getnetinfo(interface):
        try:
            cmd = "uci get network.wan" + str(interface) + ".proto | tr -d '\n'"
            temp = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
            ifname=""
            if temp == "qmi":
                cmd = "basename /sys/class/usbmisc/$(basename $(uci get network.wan" + str(interface) + ".device))/device/net/wwan* | tr -d '\n'"
                ifname = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
                if ifname.find("wwan") == -1:
                    return [interface, "err", "N/a"]
            else:
                cmd = "uci get network.wan" + str(interface) + ".device | tr -d '\n'"
                ifname = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
            cmd = "uci get openmptcprouter.wan" + str(interface) + ".latency | tr -d '\n' || true"
            latency = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
            cmd = "ip -4 r list dev " + ifname + " | grep default | awk '{print $3}' | tr -d '\n'"
            destaddr = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
            if destaddr == "":
                cmd = "ip -4 r list dev " + ifname + " | grep kernel | awk '/proto kernel/ {print $1}' | grep -v / | tr -d '\n'"
                destaddr = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
            if destaddr == "":
                cmd = "ip -4 -br addr ls dev " + ifname + " | awk -F '[ /]+' '{print $3}' | tr -d '\n'"
                destaddr = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
            if destaddr != "":
                #text += " " + str(interface)
                #cmd = "ping -w 1 -c 1 -I " + ifname + " " + destaddr + " | grep ' 0% packet loss' || true"
                #temp = subprocess.check_output(cmd, shell = True).decode("utf-8", errors="ignore")
                getsignal = False
                cmd = "(uci get openmptcprouter.wan" + str(interface) + ".manufacturer 2>/dev/null || uci get network.usbwan" + str(interface) + ".proto 2>/dev/null || uci get network.wan" + str(interface) + ".proto 2>/dev/null || true) | tr -d '\n' 2>/dev/null"
                temp = subprocess.check_output(cmd, shell = True).decode("utf-8", errors="ignore").replace("\n", "")
                if temp == "huawei":
                    cmd = "(omr-huawei-old " + destaddr + " all || true) | awk -F';' '{print $1}'"
                    temp = subprocess.check_output(cmd, shell = True).decode("utf-8", errors="ignore").replace("\n", "").replace("signal", "")
                    if temp == "":
                        temp = "ip -4 -br addr ls dev " + ifname + " | awk -F'[ /]+' '{print $3}' | tr -d '\n'"
                        hipaddr = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
                        cmd = "(omr-huawei " + hipaddr + " " + destaddr + " all || true) | awk -F';' '{print $1}'"
                        temp = subprocess.check_output(cmd, shell = True).decode("utf-8", errors="ignore").replace("\n", "").replace("signal", "")
                    if temp != "":
                        return [ifname, temp, latency]
                elif temp == "qmi":
                    cmd = "(uci get network.wan" + str(interface) + ".device || true) | tr -d '\n'"
                    device = subprocess.check_output(cmd, shell = True).decode("utf-8", errors="ignore").replace("\n", "")
                    cmd="ps | grep qmi.sh | grep " + device
                    temp = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
                    if device != "" and len(temp.split("\n"))<=2:
                        cmd = "!(ps | grep "+device+" | grep -q qmi.sh) && for i in $(ps | grep uqmi | grep "+device+" | awk '{print $1}');do echo kill$i; kill -9 $i; done || true"
                        temp = subprocess.check_output(cmd, shell = True).decode("utf-8", errors="ignore").replace("\n", "").replace("signal", "")
                        cmd = "(omr-qmi " + device + " all || true) | awk -F';' '{print $1}'"
                        temp = subprocess.check_output(cmd, shell = True).decode("utf-8", errors="ignore").replace("\n", "").replace("signal", "")
                        if temp != "":
                            return [ifname, temp, latency]
                        else:
                            # 尝试打开串口获取信号
                            card=None
                            try:
                                card = serial.Serial("/dev/card"+str(interface), 115200, 8, "N", 1,timeout=2)
                                card.write(b"AT+CSQ\x0d")
                                temp=card.readlines()
                                percent=int(int(temp[1].decode("utf-8",errors="ignore")[6:].split(",")[0])*100/31)
                                if percent>100 or percent<0:
                                    percent=0
                                return [ifname, percent, latency]
                                card.close()
                            except:
                                if card!=None:
                                    card.close()
                elif temp == "3g":
                    cmd = "(uci get network.wan" + str(interface) + ".device || true) | tr -d '\n'"
                    device = subprocess.check_output(cmd, shell = True).decode("utf-8", errors="ignore").replace("\n", "")
                    if device != "":
                        cmd = "(omr-3g " + device + " || true) | tr -d '\n'"
                        temp = subprocess.check_output(cmd, shell = True).decode("utf-8", errors="ignore").replace("\n", "").replace("signal", "")
                        if temp != "":
                            return [ifname, temp, latency]
                elif temp == "modemmanager":
                    cmd = "(uci get network.wan" + str(interface) + ".device || true) | tr -d '\n'"
                    device = subprocess.check_output(cmd, shell = True).decode("utf-8", errors="ignore").replace("\n", "")
                    if device != "":
                        cmd = "(omr-modemmanager " + device + " all || true) | awk -F';' '{print $1}'"
                        temp = subprocess.check_output(cmd, shell = True).decode("utf-8", errors="ignore").replace("\n", "").replace("signal", "")
                        if temp != "":
                            return [ifname, temp, latency]
                elif temp == "ncm":
                    cmd = "(uci get network.usbwan" + str(interface) + ".device || true) | tr -d '\n'"
                    device = subprocess.check_output(cmd, shell = True).decode("utf-8", errors="ignore").replace("\n", "")
                    if device != "":
                        cmd = "(omr-ncm " + device + " || true) | tr -d '\n'"
                        temp = subprocess.check_output(cmd, shell = True).decode("utf-8", errors="ignore").replace("\n", "").replace("signal", "")
                        if temp != "":
                            return [ifname, temp, latency]
                cmd = "uci get openmptcprouter.wan" + str(interface) + ".state | tr -d '\n'"
                temp = subprocess.check_output(cmd, shell = True).decode("utf-8", errors="ignore")
                if temp == "up":
                    return [ifname, "up", latency]
                elif temp == "down":
                    cmd = "ping -w 1 -c 1 -I " + ifname + " 114.114.114.114 | grep ' 0% packet loss' || true"
                    temp = subprocess.check_output(cmd, shell = True).decode("utf-8", errors="ignore")
                    if temp != "":
                        return [ifname, "up", latency]
                    else:
                        return [ifname, "down", latency]
                else:
                    cmd = "ping -w 1 -c 1 -I " + ifname + " 114.114.114.114 | grep ' 0% packet loss' || true"
                    temp = subprocess.check_output(cmd, shell = True).decode("utf-8", errors="ignore")
                    if temp != "":
                        return [ifname, "up", latency]
                    else:
                        cmd = "ping -w 1 -c 1 -I " + ifname + " www.baidu.com | grep ' 0% packet loss' || true"
                        temp = subprocess.check_output(cmd, shell = True).decode("utf-8", errors="ignore")
                        if temp != "":
                            return [ifname, "up", latency]
                        else:
                            return [ifname, "err", latency]
        except:
            return [interface, "err", "N/a"]
    
    def getnetinfothread():
        page.nettotal['wan2']=page.getnetinfo(2)
        page.nettotal['wan3']=page.getnetinfo(3)
        page.nettotal['wan4']=page.getnetinfo(4)
        page.nettotal['wan5']=page.getnetinfo(5)
        page.nettotal['wan1']=page.getnetinfo(1)
    
    def pageindex():
        a=0
        while not page.pageIndexStop:
            try:
                if page.getlanthread==None or page.getlanthread.is_alive()==False:
                    page.getlanthread=threading.Thread(target=page.getnetinfothread)
                    page.getlanthread.setDaemon(True)
                    page.getlanthread.start()
                    ser.write(b"boot0.val=1\xff\xff\xff")
                    ser.write(b"vis boot26,0\xff\xff\xff")
            except:
                pass
            a+=1
            # omr ip信息
            txt="Waiting Server..."
            try:
                cmd = "uci get openmptcprouter.vps.admin_error || true"
                omrerr = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore").replace("\n", "")
                cmd = "uci get openmptcprouter.omr.detected_ss_ipv4 || true"
                temp = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore").replace("\n", "")
                if omrerr == "0" and temp != "":
                    txt = str(temp)
                elif omrerr == "0":
                    cmd = "uci get openmptcprouter.omr.detected_public_ipv4"
                    temp = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore").replace("\n", "")
                    txt = str(temp)
                else:
                    txt = "Waiting Server..."
            except:
                txt = "Waiting Server..."
            ser.write(b"t0.txt=\"%s\"\xff\xff\xff"%txt.encode("utf-8"))
            ser.write(b"t1.txt=\"%b\"\xff\xff\xff"%upspeedtext.encode("utf-8")) #allupload
            ser.write(b"t2.txt=\"%s\"\xff\xff\xff"%downspeedtext.encode("utf-8")) #alldownload
            ser.write(b"t13.txt=\"%s\"\xff\xff\xff"%page.lantraffic.encode("utf-8")) #all usedcount

            #sim1 status
            wwaninfo=None
            try:
                wwaninfo=page.nettotal['wan2']
                if wwaninfo==None:
                    wwaninfo=["2", "err", "N/a"]
            except:
                wwaninfo=["2", "err", "N/a"]
            if wwaninfo[1]=="up":
                ser.write(b"vis p6,0\xff\xff\xff")
                ser.write(b"vis p10,0\xff\xff\xff") # hide signal
            elif wwaninfo[1]=="down":
                ser.write(b"vis p6,1\xff\xff\xff")
                txt=6 #sim1 status
                ser.write(b"p6.pic=%d\xff\xff\xff"%txt)
                ser.write(b"vis p10,0\xff\xff\xff") # hide signal
            elif wwaninfo[1]=="err":
                ser.write(b"vis p6,1\xff\xff\xff")
                txt=7 #sim1 status
                ser.write(b"p6.pic=%d\xff\xff\xff"%txt)
                ser.write(b"vis p10,0\xff\xff\xff") # hide signal
            else:
                info=wwaninfo[1]
                try:
                    pre_fn = 0 if int(info) <= 0 else 1 if int(info) <= 25 else 2 if int(info) <= 50 else 3 if int(info) <= 75 else 4 if int(info) <= 255 else 0
                    if pre_fn == 0:
                        ser.write(b"vis p6,1\xff\xff\xff")
                        txt=7 #sim1 status
                        ser.write(b"p6.pic=%d\xff\xff\xff"%txt)
                        ser.write(b"p10.pic=8\xff\xff\xff")
                        ser.write(b"vis p10,0\xff\xff\xff") # hide signal
                    else:
                        ser.write(b"vis p10,1\xff\xff\xff") # show signal
                        txt=pre_fn+8 #sim1 signal
                        ser.write(b"p10.pic=%d\xff\xff\xff"%txt)
                        ser.write(b"vis p6,0\xff\xff\xff")
                except:
                    ser.write(b"vis p6,0\xff\xff\xff")
                    ser.write(b"vis p10,0\xff\xff\xff") # hide signal
            # 获取上下行
            try:
                # 获取网络设备
                cmd = "uci get network.wan2.device | tr -d '\n'"
                ifname = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
                txt=3 if page.nettotal['wwan'+ifname[-1]+'type']=="3g" else 4 if page.nettotal['wwan'+ifname[-1]+'type']=="4g" else 5 if page.nettotal['wwan'+ifname[-1]+'type']=="5g" else 4 #sim1 mode
                ser.write(b"p2.pic=%d\xff\xff\xff"%txt)
                txt= page.nettotal['wwan'+ifname[-1]+'up'] #sim1 upload
                ser.write(b"t4.txt=\"%s\"\xff\xff\xff"%txt.encode("utf-8"))
                txt=page.nettotal['wwan'+ifname[-1]+'down'] #sim1 download
                ser.write(b"t3.txt=\"%s\"\xff\xff\xff"%txt.encode("utf-8"))
            except:
                ser.write(b"t4.txt=\"N/a\"\xff\xff\xff") #sim1 upload
                ser.write(b"t3.txt=\"N/a\"\xff\xff\xff") #sim1 download
            txt="%s"%(page.nettotal['wwan'+ifname[-1]+'count'] if 'wwan'+ifname[-1]+'count' in page.nettotal else "N/a") #sim1 count
            ser.write(b"t14.txt=\"%s\"\xff\xff\xff"%txt.encode("utf-8"))
            txt="%s ms"%wwaninfo[2] #sim1 delay
            ser.write(b"t15.txt=\"%s\"\xff\xff\xff"%txt.encode("utf-8"))
            
            #sim2 status
            wwaninfo=None
            try:
                wwaninfo=page.nettotal['wan3']
                if wwaninfo==None:
                    wwaninfo=["3", "err", "N/a"]
            except:
                wwaninfo=["3", "err", "N/a"]
            if wwaninfo[1]=="up":
                ser.write(b"vis p9,0\xff\xff\xff")
                ser.write(b"vis p12,0\xff\xff\xff") # hide signal
            elif wwaninfo[1]=="down":
                ser.write(b"vis p9,1\xff\xff\xff")
                txt=6 #sim2 status
                ser.write(b"p9.pic=%d\xff\xff\xff"%txt)
                ser.write(b"vis p12,0\xff\xff\xff") # hide signal
            elif wwaninfo[1]=="err":
                ser.write(b"vis p9,1\xff\xff\xff")
                txt=7 #sim2 status
                ser.write(b"p9.pic=%d\xff\xff\xff"%txt)
                ser.write(b"vis p12,0\xff\xff\xff") # hide signal
            else:
                info=wwaninfo[1]
                try:
                    pre_fn = 0 if int(info) <= 0 else 1 if int(info) <= 25 else 2 if int(info) <= 50 else 3 if int(info) <= 75 else 4 if int(info) <= 255 else 0
                    if pre_fn == 0:
                        ser.write(b"vis p9,1\xff\xff\xff")
                        txt=7 #sim2 status
                        ser.write(b"p9.pic=%d\xff\xff\xff"%txt)
                        ser.write(b"p12.pic=8\xff\xff\xff")
                        ser.write(b"vis p12,0\xff\xff\xff") # hide signal
                    else:
                        ser.write(b"vis p12,1\xff\xff\xff") # show signal
                        txt=pre_fn+8 #sim2 signal
                        ser.write(b"p12.pic=%d\xff\xff\xff"%txt)
                        ser.write(b"vis p9,0\xff\xff\xff")
                except:
                    ser.write(b"vis p9,0\xff\xff\xff")
                    ser.write(b"vis p12,0\xff\xff\xff") # hide signal
            # 获取上下行
            try:
                # 获取网络设备
                cmd = "uci get network.wan3.device | tr -d '\n'"
                ifname = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
                txt=3 if page.nettotal['wwan'+ifname[-1]+'type']=="3g" else 4 if page.nettotal['wwan'+ifname[-1]+'type']=="4g" else 5 if page.nettotal['wwan'+ifname[-1]+'type']=="5g" else 4 #sim2 mode
                ser.write(b"p4.pic=%d\xff\xff\xff"%txt) # sim2 mode
                txt= page.nettotal['wwan'+ifname[-1]+'up'] #sim2 upload
                ser.write(b"t6.txt=\"%s\"\xff\xff\xff"%txt.encode("utf-8"))
                txt=page.nettotal['wwan'+ifname[-1]+'down'] #sim2 download
                ser.write(b"t5.txt=\"%s\"\xff\xff\xff"%txt.encode("utf-8"))
            except:
                ser.write(b"t6.txt=\"N/a\"\xff\xff\xff") #sim2 upload
                ser.write(b"t5.txt=\"N/a\"\xff\xff\xff") #sim2 download
            txt="%s"%(page.nettotal['wwan'+ifname[-1]+'count'] if 'wwan'+ifname[-1]+'count' in page.nettotal else "N/a") #sim2 count
            ser.write(b"t21.txt=\"%s\"\xff\xff\xff"%txt.encode("utf-8"))
            txt="%s ms"%wwaninfo[2] #sim2 delay
            ser.write(b"t20.txt=\"%s\"\xff\xff\xff"%txt.encode("utf-8"))
            
            #sim3 status
            wwaninfo=None
            try:
                wwaninfo=page.nettotal['wan4']
                if wwaninfo==None:
                    wwaninfo=["4", "err", "N/a"]
            except:
                wwaninfo=["4", "err", "N/a"]
            if wwaninfo[1]=="up":
                ser.write(b"vis p7,0\xff\xff\xff")
                ser.write(b"vis p11,0\xff\xff\xff") # hide signal
            elif wwaninfo[1]=="down":
                ser.write(b"vis p7,1\xff\xff\xff")
                txt=6 #sim3 status
                ser.write(b"p7.pic=%d\xff\xff\xff"%txt)
                ser.write(b"vis p11,0\xff\xff\xff") # hide signal
            elif wwaninfo[1]=="err":
                ser.write(b"vis p7,1\xff\xff\xff")
                txt=7 #sim3 status
                ser.write(b"p7.pic=%d\xff\xff\xff"%txt)
                ser.write(b"vis p11,0\xff\xff\xff") # hide signal
            else:
                info=wwaninfo[1]
                try:
                    pre_fn = 0 if int(info) <= 0 else 1 if int(info) <= 25 else 2 if int(info) <= 50 else 3 if int(info) <= 75 else 4 if int(info) <= 255 else 0
                    if pre_fn == 0:
                        ser.write(b"vis p7,1\xff\xff\xff")
                        txt=7 #sim3 status
                        ser.write(b"p7.pic=%d\xff\xff\xff"%txt)
                        ser.write(b"p11.pic=8\xff\xff\xff")
                        ser.write(b"vis p11,0\xff\xff\xff") # hide signal
                    else:
                        ser.write(b"vis p11,1\xff\xff\xff") # show signal
                        txt=pre_fn+8 #sim3 signal
                        ser.write(b"p11.pic=%d\xff\xff\xff"%txt)
                        ser.write(b"vis p7,0\xff\xff\xff")
                except:
                    ser.write(b"vis p7,0\xff\xff\xff")
                    ser.write(b"vis p11,0\xff\xff\xff") # hide signal
            # 获取上下行
            try:
                # 获取网络设备
                cmd = "uci get network.wan4.device | tr -d '\n'"
                ifname = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
                txt=3 if page.nettotal['wwan'+ifname[-1]+'type']=="3g" else 4 if page.nettotal['wwan'+ifname[-1]+'type']=="4g" else 5 if page.nettotal['wwan'+ifname[-1]+'type']=="5g" else 4 #sim3 mode
                ser.write(b"p3.pic=%d\xff\xff\xff"%txt) # sim3 mode
                txt= page.nettotal['wwan'+ifname[-1]+'up'] #sim3 upload
                ser.write(b"t9.txt=\"%s\"\xff\xff\xff"%txt.encode("utf-8"))
                txt=page.nettotal['wwan'+ifname[-1]+'down'] #sim3 download
                ser.write(b"t10.txt=\"%s\"\xff\xff\xff"%txt.encode("utf-8"))
            except:
                ser.write(b"t9.txt=\"N/a\"\xff\xff\xff") #sim3 upload
                ser.write(b"t10.txt=\"N/a\"\xff\xff\xff") #sim3 download
            txt="%s"%(page.nettotal['wwan'+ifname[-1]+'count'] if 'wwan'+ifname[-1]+'count' in page.nettotal else "N/a") #sim3 count
            ser.write(b"t16.txt=\"%s\"\xff\xff\xff"%txt.encode("utf-8"))
            txt="%s ms"%wwaninfo[2] #sim3 delay
            ser.write(b"t17.txt=\"%s\"\xff\xff\xff"%txt.encode("utf-8"))
            
            #sim4 status
            wwaninfo=None
            try:
                wwaninfo=page.nettotal['wan5']
                if wwaninfo==None:
                    wwaninfo=["5", "err", "N/a"]
            except:
                wwaninfo=["5", "err", "N/a"]
            if wwaninfo[1]=="up":
                ser.write(b"vis p8,0\xff\xff\xff")
                ser.write(b"vis p13,0\xff\xff\xff") # hide signal
            elif wwaninfo[1]=="down":
                ser.write(b"vis p8,1\xff\xff\xff")
                txt=6 #sim4 status
                ser.write(b"p8.pic=%d\xff\xff\xff"%txt)
                ser.write(b"vis p13,0\xff\xff\xff") # hide signal
            elif wwaninfo[1]=="err":
                ser.write(b"vis p8,1\xff\xff\xff")
                txt=7 #sim4 status
                ser.write(b"p8.pic=%d\xff\xff\xff"%txt)
                ser.write(b"vis p13,0\xff\xff\xff") # hide signal
            else:
                info=wwaninfo[1]
                try:
                    pre_fn = 0 if int(info) <= 0 else 1 if int(info) <= 25 else 2 if int(info) <= 50 else 3 if int(info) <= 75 else 4 if int(info) <= 255 else 0
                    if pre_fn == 0:
                        ser.write(b"vis p8,1\xff\xff\xff")
                        txt=7 #sim4 status
                        ser.write(b"p8.pic=%d\xff\xff\xff"%txt)
                        ser.write(b"p13.pic=8\xff\xff\xff")
                        ser.write(b"vis p13,0\xff\xff\xff") # hide signal
                    else:
                        ser.write(b"vis p13,1\xff\xff\xff") # show signal
                        txt=pre_fn+8 #sim4 signal
                        ser.write(b"p13.pic=%d\xff\xff\xff"%txt)
                        ser.write(b"vis p8,0\xff\xff\xff")
                except:
                    ser.write(b"vis p8,0\xff\xff\xff")
                    ser.write(b"vis p13,0\xff\xff\xff") # hide signal
            # 获取上下行
            try:
                # 获取网络设备
                cmd = "uci get network.wan5.device | tr -d '\n'"
                ifname = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
                txt=3 if page.nettotal['wwan'+ifname[-1]+'type']=="3g" else 4 if page.nettotal['wwan'+ifname[-1]+'type']=="4g" else 5 if page.nettotal['wwan'+ifname[-1]+'type']=="5g" else 4 #sim4 mode
                ser.write(b"p5.pic=%d\xff\xff\xff"%txt) # sim4 mode
                txt= page.nettotal['wwan'+ifname[-1]+'up'] #sim4 upload
                ser.write(b"t8.txt=\"%s\"\xff\xff\xff"%txt.encode("utf-8"))
                txt=page.nettotal['wwan'+ifname[-1]+'down'] #sim4 download
                ser.write(b"t7.txt=\"%s\"\xff\xff\xff"%txt.encode("utf-8"))
            except:
                ser.write(b"t8.txt=\"N/a\"\xff\xff\xff") #sim4 upload
                ser.write(b"t7.txt=\"N/a\"\xff\xff\xff") #sim4 download
            txt="%s"%(page.nettotal['wwan'+ifname[-1]+'count'] if 'wwan'+ifname[-1]+'count' in page.nettotal else "N/a") #sim4 count
            ser.write(b"t19.txt=\"%s\"\xff\xff\xff"%txt.encode("utf-8"))
            txt="%s ms"%wwaninfo[2] #sim4 delay
            ser.write(b"t18.txt=\"%s\"\xff\xff\xff"%txt.encode("utf-8"))
            
            #rj45 status
            rj45info=None
            try:
                rj45info=page.nettotal['wan1']
                if page.nettotal['wan1']==None:
                    rj45info=["1", "err", "N/a"]
            except:
                rj45info=["1", "err", "N/a"]
            if rj45info[1]=="up":
                ser.write(b"vis p14,0\xff\xff\xff")
            elif rj45info[1]=="down":
                ser.write(b"vis p14,1\xff\xff\xff")
                txt=6 #rj45 status
                ser.write(b"p14.pic=%d\xff\xff\xff"%txt)
            else:
                ser.write(b"vis p14,1\xff\xff\xff")
                txt=7 #rj45 status
                ser.write(b"p14.pic=%d\xff\xff\xff"%txt)
            try:
                txt="%s"%page.nettotal['eth1up'] #rj45 upload
                ser.write(b"t12.txt=\"%s\"\xff\xff\xff"%txt.encode("utf-8"))
                txt="%s"%page.nettotal['eth1down'] #rj45 download
                ser.write(b"t11.txt=\"%s\"\xff\xff\xff"%txt.encode("utf-8"))
            except:
                ser.write(b"t12.txt=\"N/a\"\xff\xff\xff") #rj45 upload
                ser.write(b"t11.txt=\"N/a\"\xff\xff\xff") #rj45 download
            ser.write(b"t23.txt=\"%s\"\xff\xff\xff"%page.rj45traffic.encode("utf-8")) #rj45 count
            txt="%s ms"%rj45info[2] #rj45 delay
            ser.write(b"t22.txt=\"%s\"\xff\xff\xff"%txt.encode("utf-8"))
            
            txt=a%6+16 #battery
            ser.write(b"p28.pic=%d\xff\xff\xff"%txt)
            if a>65535:
                a=0
            time.sleep(0.5)
    
    def setwifi(readline):
        if page.isSetWifi==False:
            page.isSetWifi=True
            ser.write(b"p1.pic=40\xff\xff\xff")
            wifiinfo=readline.decode("utf-8","ignore").split(",")
            print(wifiinfo)
            if wifiinfo[2]==wifiinfo[3] and wifiinfo[4] == wifiinfo[5]:
                #try:
                cmd = "/sbin/uci set wireless.default_radio0.ssid='%s' && /sbin/uci set wireless.default_radio0.key='%s' && /sbin/uci commit wireless"%(wifiinfo[2], wifiinfo[4])
                temp = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
                if wifiinfo[6]=="5G":
                    cmd = "/sbin/uci set wireless.radio0.htmode='VHT80' && /sbin/uci set wireless.radio0.hwmode='11a' && /sbin/uci set wireless.radio0.channel='44' && /sbin/uci commit wireless"
                    temp = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
                elif wifiinfo[6]=="2.4G":
                    cmd = "/sbin/uci set wireless.radio0.hwmode='11g' && /sbin/uci set wireless.radio0.channel='auto' && /sbin/uci commit wireless"
                    temp = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
                cmd = "/bin/ubus call network reload && /sbin/wifi reload"
                temp = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
            time.sleep(2)
            ser.write(b"p1.pic=28\xff\xff\xff")
            page.isSetWifi=False
        else:
            ser.write(b"p1.pic=40\xff\xff\xff")
    def setmode(readline):
        if page.isSetMode==False:
            page.isSetMode=True
            ser.write(b"p1.pic=40\xff\xff\xff")
            modeinfo=readline.decode("utf-8","ignore").split(",")
            print(modeinfo)
            #time.sleep(2)
            mode=""
            if modeinfo[1]=="Blest":
                mode="blest"
            elif modeinfo[1]=="Round_rond":
                mode="roundrobin"
            elif modeinfo[1]=="Redundant":
                mode="redundant"
            elif modeinfo[1]=="ECF":
                mode="ecf"
            cmd = "uci set network.globals.mptcp_scheduler='%s' && uci commit network && exit 1"%mode
            temp = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
            ser.write(b"p1.pic=28\xff\xff\xff")
            page.isSetMode=False
        else:
            ser.write(b"p1.pic=40\xff\xff\xff")
    def setport():
        page.isSetPort=True
        while len(page.listSetPort)>0:
            ser.write(b"p1.pic=40\xff\xff\xff")
            nowset = page.listSetPort.pop(0)
            print("set: ",end="")
            port=nowset.split(",")
            if port[1] != port[2] or port[4] != port[5]:
                continue
            for i in range(4,8):
                cmd = "uci get firewall.@redirect["+ str(i) +"]"
                try:
                    temp = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
                except:
                    cmd = "uci add firewall redirect"
                    temp = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
            cmd = "uci set firewall.@redirect["+ str(int(port[0][-1])+3) +"].target='DNAT'"
            temp = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
            cmd = "uci set firewall.@redirect["+ str(int(port[0][-1])+3) +"].src='vpn'"
            temp = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
            cmd = "uci set firewall.@redirect["+ str(int(port[0][-1])+3) +"].dest='vpn'"
            temp = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
            
            cmd = "uci set firewall.@redirect["+ str(int(port[0][-1])+3) +"].name='%s'"%port[1]
            temp = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
            cmd = "uci set firewall.@redirect["+ str(int(port[0][-1])+3) +"].src_dport='%s'"%port[1]
            temp = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
            cmd = "uci set firewall.@redirect["+ str(int(port[0][-1])+3) +"].dest_port='%s'"%port[1]
            temp = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
            
            cmd = "uci set firewall.@redirect["+ str(int(port[0][-1])+3) +"].dest_ip='%s'"%port[4]
            temp = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
            cmd = "uci commit firewall"
            temp = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
            #time.sleep(2)
        ser.write(b"p1.pic=28\xff\xff\xff")
        page.isSetPort=False
    def setmptcp(readline):
        if page.isSetMptcp==False:
            page.isSetMptcp=True
            ser.write(b"p1.pic=40\xff\xff\xff")
            modeinfo=readline.decode("utf-8","ignore").split(",")
            print(modeinfo)
            if modeinfo[1]==modeinfo[2] and modeinfo[3]==modeinfo[4]:
                print("set mptcp")
                cmd = "/usr/share/GatherHMI/setmptcp.sh "+modeinfo[1] + " openmptcprouter " + modeinfo[3]
                temp = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
                print("setdone: " + temp)
            time.sleep(2)
            ser.write(b"p1.pic=28\xff\xff\xff")
            page.isSetMptcp=False
        else:
            ser.write(b"p1.pic=40\xff\xff\xff")
    def getupdate():
        ser.write(b"t0.txt=\"%s\"\xff\xff\xff"%"正在检查更新".encode("gb2312"))
        ser.write(b"vis p2,0\xff\xff\xff")
        ser.write(b"vis c0,0\xff\xff\xff")
        ser.write(b"vis t4,0\xff\xff\xff")
        cmd = "/usr/share/system/uciuci get | tr -d '\n'"
        try:
            page.downinfo = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
            page.downinfo=page.downinfo.split(";")
            if len(page.downinfo) >= 3:
                cmd = "uci get openmptcprouter.settings.version | tr -d '\n'"
                currentVersion = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
                #and page.downinfo[1][0]==currentVersion[0]
                if len(currentVersion)>0 and page.downinfo[1]>currentVersion:
                    ser.write(b"t0.txt=\"%s%s\"\xff\xff\xff"%("发现新版本：".encode("gb2312"), page.downinfo[1][1:].encode("gb2312")))
                    ser.write(b"vis p2,1\xff\xff\xff")
                    ser.write(b"vis c0,1\xff\xff\xff")
                    ser.write(b"vis t4,1\xff\xff\xff")
                else:
                    ser.write(b"t0.txt=\"%s\"\xff\xff\xff"%"未发现新版本，请稍后再试.".encode("gb2312"))
                    ser.write(b"vis p2,0\xff\xff\xff")
                    ser.write(b"vis c0,0\xff\xff\xff")
                    ser.write(b"vis t4,0\xff\xff\xff")
            else:
                ser.write(b"t0.txt=\"%s\"\xff\xff\xff"%"获取不到更新，请再试一次.".encode("gb2312"))
                ser.write(b"vis p2,0\xff\xff\xff")
                ser.write(b"vis c0,0\xff\xff\xff")
                ser.write(b"vis t4,0\xff\xff\xff")
        except:
            ser.write(b"t0.txt=\"%s\"\xff\xff\xff"%"获取更新出错，请检查网络！".encode("gb2312"))
            ser.write(b"vis p2,0\xff\xff\xff")
            ser.write(b"vis c0,0\xff\xff\xff")
            ser.write(b"vis t4,0\xff\xff\xff")
        #ser.write(b"page index\xff\xff\xff")
    def updatesystem(isclean):
        if page.downinfo!=None:
            print(isclean)
            cmd = "uci get openmptcprouter.settings.version | tr -d '\n'"
            currentVersion = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
            # and page.downinfo[1][0]==currentVersion[0]
            if len(currentVersion)>0 and page.downinfo[1]>currentVersion:
                ser.write(b"page load\xff\xff\xff")
                try:
                    cmd = "i=0 && while !(wget " + page.downinfo[0] + " -O /tmp/update.img) && [ $i -le 10 ]; do i=$((i+1)) && echo try$i && sleep 2; done"
                    temp = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
                    cmd = "md5sum /tmp/update.img | grep -q" + page.downinfo[2]
                    temp = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
                    if (isclean == "clean"):
                        cmd = "sysupgrade -n /tmp/update.img"
                    else:
                        cmd = "sysupgrade /tmp/update.img"
                    temp = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
                except:
                    ser.write(b"t0.txt=\"%s\"\xff\xff\xff"%"下载更新失败，请检查网络并重试.".encode("gb2312"))
                    print("d1 failed")
                    time.sleep(5)
                    pass
            print(page.downinfo)
        time.sleep(2)
        ser.write(b"page index\xff\xff\xff")
    def setresetport(readline):
        if page.isSetReset==False:
            page.isSetReset=True
            ser.write(b"vis g0,1\xff\xff\xff")
            ser.write(b"g0.en=1\xff\xff\xff")
            obj=re.match(r'\S+restart card(\d) set',readline.decode("utf-8","ignore"),flags=0)
            if obj:
                print("restart card in: "+obj.group(1))
                card = serial.Serial("/dev/card"+obj.group(1), 115200, 8, "N", 1,timeout=2)
                # Disable modem
                try:
                    card.write(b"AT+CFUN=0\x0d")
                    info=card.readlines()
                    i=0
                    while not (b"AT+CFUN=0\r\r\n" in info and b"OK\r\n" in info):
                        card.write(b"AT+CFUN=0\x0d")
                        info=card.readlines()
                        i+=1
                        if i>5:
                            print("Failed to reset 0 for card"+obj.group(1))
                            ser.write(b"g0.txt=\"%s\"\xff\xff\xff"%"重置模块异常".encode("gb2312"))
                            time.sleep(5)
                            break
                except:
                    ser.write(b"g0.txt=\"%s\"\xff\xff\xff"%"模块返回数据异常".encode("gb2312"))
                    time.sleep(5)
                # Enable modem
                try:
                    card.write(b"AT+CFUN=1\x0d")
                    info=card.readlines()
                    while not (b"AT+CFUN=1\r\r\n" in info and b"OK\r\n" in info):
                        card.write(b"AT+CFUN=1\x0d")
                        info=card.readlines()
                        i+=1
                        if i>5:
                            print("Failed to enable 1 for card"+obj.group(1))
                            break
                    if b"+CPIN: NOT INSERTED\r\n" in info:
                        print("card is not insert")
                        ser.write(b"g0.txt=\"%s\"\xff\xff\xff"%"请注意，可能未插卡...".encode("gb2312"))
                        time.sleep(5)
                    if b"+CPIN: READY\r\n" in info and b"+QUSIM: 1\r\n" in info:
                        print("card is ok")
                except:
                    ser.write(b"g0.txt=\"%s\"\xff\xff\xff"%"模块返回数据异常".encode("gb2312"))
                    time.sleep(5)
                card.close() # 关闭串口
                wandev="wan"+str(int(obj.group(1))+1)
                try:
                    cmd = "/bin/kill $(ps | grep qmi | grep " + wandev + " | awk '{print $1}' || true)"
                    temp = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
                except:
                    print("error in kill "+ wandev)
                try:
                    cmd = "/sbin/ifdown "+wandev
                    temp = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
                    cmd = "/usr/bin/killall uqmi || true"
                    temp = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
                    cmd = "/sbin/ifup "+wandev
                    temp = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
                except:
                    print("error in updown "+ wandev)
                    cmd = "/sbin/ifup "+wandev
                    temp = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
                print("reset card success: "+ wandev)
                ser.write(b"g0.txt=\"%s\"\xff\xff\xff"%"重启成功，正在注册网络...".encode("gb2312"))
            else:
                print("no match restart card")
                ser.write(b"g0.txt=\"%s\"\xff\xff\xff"%"匹配卡错误".encode("gb2312"))
                time.sleep(5)
        else:
            pass
        time.sleep(2)
        ser.write(b"page index\xff\xff\xff")
        page.isSetReset=False
    def setrj45(readline):
        if page.isSetRj45==False:
            page.isSetRj45=True
            temp=readline.decode("utf-8","ignore").split(",")
            if temp[1]=="static" and len(temp)>=8 and temp[2]==temp[3] and temp[4]==temp[5] and temp[6]==temp[7]:
                # 接收的信息格式：prj45,static,ip,ip,mask,mask,gateway,gateway,set
                print("set rj45 static ip:%s, mask: %s, gateway: %s"%(temp[2],temp[4],temp[6]))
                #try:
                if True:
                    cmd = "/sbin/uci set network.wan1.proto='static'"
                    setstatic = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
                    cmd = "/sbin/uci set network.wan1.ipaddr='%s' && /sbin/uci set network.wan1.gateway='%s' && /sbin/uci set network.wan1.broadcast='%s'" % (temp[2],temp[6],temp[4])
                    setstatic = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
                #except:
                    print("set static")
                    pass
            elif temp[1]=="dhcp":
                # 接收的信息格式：prj45,dhcp,set
                print("set rj45 dhcp")
                try:
                    cmd = "/sbin/uci set network.wan1.proto='dhcp' && /sbin/uci del network.wan1.ipaddr && /sbin/uci del network.wan1.gateway && /sbin/uci del network.wan1.broadcast"
                    temp = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
                except:
                    print("set static")
                    pass
            cmd = "/sbin/ifdown wan1 && /sbin/ifup wan1"
            try:
                temp = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
            except:
                pass
            time.sleep(2)
        page.isSetRj45=False

def recvserial():
    while True:
        readline=ser.readline()
        print("get:"+readline.decode("utf-8","ignore"))
        if re.search(r"page index in", readline.decode("utf-8","ignore")):
            print("in")
            page.pageIndexStop=False
            pageindexthread = threading.Thread(target=page.pageindex)
            if not pageindexthread.is_alive():
                pageindexthread.start()
        elif re.search(r"page index needout",readline.decode("utf-8","ignore")):
            print("needout")
            ser.write(b"page menu\xff\xff\xff")
        elif re.search(r"page index out",readline.decode("utf-8","ignore")):
            print("out")
            page.pageIndexStop=True
        elif re.search(r"page menu in",readline.decode("utf-8","ignore")):
            print("menuin")
            page.pageIndexStop=True
        elif re.search(r"page wifi in",readline.decode("utf-8","ignore")):
            print("wifiin")
            page.pageIndexStop=True
            cmd = "uci get wireless.default_radio0.ssid | tr -d '\n'"
            temp = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
            ser.write(b"t2.txt=\"%s\"\xff\xff\xff"%temp.encode("utf-8"))
            cmd = "uci get wireless.default_radio0.key | tr -d '\n'"
            temp = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
            ser.write(b"t5.txt=\"%s\"\xff\xff\xff"%temp.encode("utf-8"))
        elif re.search(r"wwifi save in",readline.decode("utf-8","ignore")):
            print("wifisavein: ")
            page.pageIndexStop=True
            pagewifithread = threading.Thread(target=page.setwifi,args=(readline,))
            if not pagewifithread.is_alive():
                pagewifithread.start()
        elif re.search(r"67657470616765", readline.hex()):
            print("getpagein: ")
            page.getpage=True
            if re.search(r"6765747061676500", readline.hex()):
                print("in")
                page.pageIndexStop=False
                pageindexthread = threading.Thread(target=page.pageindex)
                if not pageindexthread.is_alive():
                    pageindexthread.start()
            else:
                page.pageIndexStop=True
        elif re.search(r"changemode in",readline.decode("utf-8","ignore")):
            print("page changemode in: ")
            page.pageIndexStop=True
            cmd = "uci get network.globals.mptcp_scheduler | tr -d '\n'"
            temp = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
            if temp=="blest":
                ser.write(b"r0.val=0\xff\xff\xff")
                ser.write(b"r1.val=0\xff\xff\xff")
                ser.write(b"r2.val=1\xff\xff\xff")
                ser.write(b"r3.val=0\xff\xff\xff")
            elif temp=="roundrobin":
                ser.write(b"r0.val=1\xff\xff\xff")
                ser.write(b"r1.val=0\xff\xff\xff")
                ser.write(b"r2.val=0\xff\xff\xff")
                ser.write(b"r3.val=0\xff\xff\xff")
            elif temp=="redundant":
                ser.write(b"r0.val=0\xff\xff\xff")
                ser.write(b"r1.val=1\xff\xff\xff")
                ser.write(b"r2.val=0\xff\xff\xff")
                ser.write(b"r3.val=0\xff\xff\xff")
            elif temp=="ecf":
                ser.write(b"r0.val=0\xff\xff\xff")
                ser.write(b"r1.val=0\xff\xff\xff")
                ser.write(b"r2.val=0\xff\xff\xff")
                ser.write(b"r3.val=1\xff\xff\xff")
        elif re.search(r"changeport in",readline.decode("utf-8","ignore")):
            print("page changeport in: ")
            page.pageIndexStop=True
            for i in range(0,4):
                cmd = "uci get firewall.@redirect["+ str(i+4) +"]"
                try:
                    temp = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
                    cmd = "uci get firewall.@redirect["+ str(i+4) +"].src_dport | tr -d '\n'"
                    port = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
                    if port==None or port=="":
                        continue
                    ser.write(b"t%d.txt=\"%s\"\xff\xff\xff"%(i*4+2, port.encode("utf-8")))
                    cmd = "uci get firewall.@redirect["+ str(i+4) +"].dest_ip | tr -d '\n'"
                    ipaddr = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
                    if ipaddr==None or ipaddr=="":
                        continue
                    ser.write(b"t%d.txt=\"%s\"\xff\xff\xff"%(i*4+4, ipaddr.encode("utf-8")))
                    ser.write(b"port%d.txt=\"%s,%s\"\xff\xff\xff"%(i+1, port.encode("utf-8"), ipaddr.encode("utf-8")))
                    print(b"port%d.txt=\"%s,%s\"\xff\xff\xff"%(i+1, port.encode("utf-8"), ipaddr.encode("utf-8")))
                except:
                    continue
        elif re.search(r"mmode",readline.decode("utf-8","ignore")):
            print("setmodein: ")
            page.pageIndexStop=True
            pagemodethread = threading.Thread(target=page.setmode,args=(readline,))
            if not pagemodethread.is_alive():
                pagemodethread.start()
        elif re.search(r"pport",readline.decode("utf-8","ignore")) and re.search(r"paddr",readline.decode("utf-8","ignore")):
            print("setportin: ")
            page.pageIndexStop=True
            portinfo=readline.decode("utf-8","ignore")
            if not portinfo in page.listSetPort:
                page.listSetPort.append(portinfo)
            if len(page.listSetPort)>0 and not page.isSetPort:
                pageportthread = threading.Thread(target=page.setport)
                if not pageportthread.is_alive():
                    pageportthread.start()
        elif re.search(r"pmptcp",readline.decode("utf-8","ignore")):
            print("setmptcpin: ")
            page.pageIndexStop=True
            pagemptcpthread = threading.Thread(target=page.setmptcp,args=(readline,))
            if not pagemptcpthread.is_alive():
                pagemptcpthread.start()
        elif re.search(r"reset gsystem",readline.decode("utf-8","ignore")):
            print("reset system in: ")
            page.pageIndexStop=True
            ser.write(b"page load\xff\xff\xff")
            try:
                cmd = "echo 'FACTORY RESET' > /dev/console || true"
                temp = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
                cmd = "jffs2reset -y && reboot &"
                temp = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
            except:
                pass
            time.sleep(2)
            ser.write(b"page index\xff\xff\xff")
        elif re.search(r"page update",readline.decode("utf-8","ignore")):
            print("page update in: ")
            page.pageIndexStop=True
            page.getupdate()
        elif re.search(r"update firmware",readline.decode("utf-8","ignore")):
            print("update firmware set: ")
            page.pageIndexStop=True
            try:
                page.updatesystem(readline.decode("utf-8","ignore").split(",")[1])
            except:
                pass
        elif re.search(r"restart rsystem",readline.decode("utf-8","ignore")):
            print("restart system in: ")
            page.pageIndexStop=True
            ser.write(b"page load\xff\xff\xff")
            cmd = "reboot || true"
            temp = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
            time.sleep(2)
            ser.write(b"page index\xff\xff\xff")
        elif re.search(r"restart card\d set",readline.decode("utf-8","ignore")):
            print("restart card in")
            page.pageIndexStop=True
            resetportthread = threading.Thread(target=page.setresetport,args=(readline,))
            if not resetportthread.is_alive():
                resetportthread.start()
        elif re.search(r"prj45",readline.decode("utf-8","ignore")):
            print("rj45 set in")
            rj45setthread = threading.Thread(target=page.setrj45,args=(readline,))
            if not rj45setthread.is_alive():
                rj45setthread.start()
        elif re.search(r"page rj45 in",readline.decode("utf-8","ignore")):
            print("page rj45 in")
            page.pageIndexStop=True
            try:
                cmd="/sbin/uci get network.wan1.proto | tr -d '\n'"
                temp = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
                if temp == "dhcp":
                    ser.write(b"r0.val=0\xff\xff\xff")
                    ser.write(b"r1.val=1\xff\xff\xff")
                    ser.write(b"tsw rj2,0\xff\xff\xff")
                    ser.write(b"tsw rj5,0\xff\xff\xff")
                    ser.write(b"tsw rj9,0\xff\xff\xff")
                    ser.write(b"rj2.bco=46518\xff\xff\xff")
                    ser.write(b"rj5.bco=46518\xff\xff\xff")
                    ser.write(b"rj9.bco=46518\xff\xff\xff")
                    cmd="/sbin/ifstatus wan1"
                    temp = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
                    temp = json.loads(temp)
                    # dhcp获取到的ip地址
                    ipaddrv4=temp['ipv4-address'][0]['address']
                    print("ipv4addr4:"+ipaddrv4)
                    ser.write(b"rj2.txt=\"%s\"\xff\xff\xff" % ipaddrv4.encode("utf-8"))
                    # 掩码
                    cidr=int(temp['ipv4-address'][0]['mask'])
                    # cidr转netmask
                    mask = (0xffffffff >> (32 - cidr)) << (32 - cidr)
                    netmask=str((0xff000000 & mask) >> 24)   + '.' + str((0x00ff0000 & mask) >> 16)   + '.' + str((0x0000ff00 & mask) >> 8)    + '.' + str((0x000000ff & mask))
                    print("netmask:"+netmask)
                    ser.write(b"rj5.txt=\"%s\"\xff\xff\xff" % netmask.encode("utf-8"))
                    # 网关
                    if len(temp['route'])>0:
                        gateway=temp['route'][0]['nexthop']
                    else:
                        gateway=temp['inactive']['route'][0]['nexthop']
                    ser.write(b"rj9.txt=\"%s\"\xff\xff\xff" % gateway.encode("utf-8"))
                    print("gateway:"+gateway)
                elif temp == "static":
                    ser.write(b"r0.val=1\xff\xff\xff")
                    ser.write(b"r1.val=0\xff\xff\xff")
                    ser.write(b"tsw rj2,1\xff\xff\xff")
                    ser.write(b"tsw rj5,1\xff\xff\xff")
                    ser.write(b"tsw rj9,1\xff\xff\xff")
                    ser.write(b"rj2.bco=65535\xff\xff\xff")
                    ser.write(b"rj5.bco=65535\xff\xff\xff")
                    ser.write(b"rj9.bco=65535\xff\xff\xff")
                    cmd="/sbin/uci get network.wan1.ipaddr | tr -d '\n'"
                    ipaddrv4 = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
                    ser.write(b"rj2.txt=\"%s\"\xff\xff\xff" % ipaddrv4.encode("utf-8"))
                    cmd="/sbin/uci get network.wan1.broadcast | tr -d '\n'"
                    netmask = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
                    ser.write(b"rj5.txt=\"%s\"\xff\xff\xff" % netmask.encode("utf-8"))
                    cmd="/sbin/uci get network.wan1.gateway | tr -d '\n'"
                    gateway = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
                    ser.write(b"rj9.txt=\"%s\"\xff\xff\xff" % gateway.encode("utf-8"))
                cmd="/sbin/uci commit network"
                temp = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
                cmd="/sbin/ifdown wan1 && /sbin/ifup wan1"
                temp = subprocess.check_output(cmd, shell = True ).decode("utf-8", errors="ignore")
            except:
                print("err get ipinfo")
                pass

while True:
    try:
        connectSerial()
        readthread = threading.Thread(target=recvserial) # 新建线程
        readthread.start()  # 启动读取串口线程
        # 获取当前页面
        while not page.getpage:
            ser.write(b"prints \"getpage\",0\xff\xff\xff")
            ser.write(b"prints dp,0\xff\xff\xff")
            ser.write(b"printh 0a\xff\xff\xff")
            ser.write(b"boot0.val=1\xff\xff\xff")
            ser.write(b"vis boot26,0\xff\xff\xff")
            #ser.write(b"thsp=30\xff\xff\xff")
            #ser.write(b"thup=1\xff\xff\xff")
            #ser.write(b"lowpower=1\xff\xff\xff")
            time.sleep(1)

        readthread.join()   # 读取串口线程阻塞
        ser.close() # 关闭
    except:
        if ser:
            ser.close() # 关闭
        connectSerial()
        continue

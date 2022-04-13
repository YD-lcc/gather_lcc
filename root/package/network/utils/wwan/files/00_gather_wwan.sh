#!/bin/sh

[ "$ACTION" = add ] || exit 0
[ "${DEVNAME/[0-9]/}" = cdc-wdm ] || exit 0

. /lib/functions.sh
. /lib/netifd/netifd-proto.sh

echo "$ACTION devname:$DEVNAME devpath:$DEVPATH devicename:$DEVICENAME devnum:$DEVNUM driver:$DRIVER type:$TYPE product:$PRODUCT seqnum:$SEQNUM busnum:$BUSNUM major:$MAJOR $MINOR  $SUBSYSTEM" > /root/log${DEVNAME}.txt

if echo $DEVPATH | grep -q ff5c0000; then
	ifname=wwan
	card=card
	interface=wan
	if echo $DEVPATH | grep -q "2-1.2:1.4"; then
		ifname=wwan1
		card=card1
		interface=wan2
	elif echo $DEVPATH | grep -q "2-1.1:1.4"; then
		ifname=wwan2
		card=card2
		interface=wan3
	else
		exit 0
	fi
	#wwandevice=`ls "/sys/${DEVPATH}/../../net/" | tr -d "\n"`
	#[ "/dev/${DEVNAME}" != `readlink /dev/${card} | tr -d "\n"` ] && rm -f /dev/${card}
        #[ ! -f /dev/${card} ] && ln -sf /dev/$DEVNAME /dev/${card}
	echo $wwandevice | grep -q $ifname && echo "$DEVNAME $wwandevice device is already ok" >> /root/log${DEVNAME}.txt && exit 0
        logger -t "OMR-Rename" "Rename ${wwandevice} to ${ifname}"
	uci set network.${interface}.device="/dev/"$DEVNAME
	uci commit network
        #ip link set ${wwandevice} down 2>&1 >/dev/null
        #existif="0"
        #[ "$(ip link show ${ifname} 2>/dev/null)" != "" ] && {
        #        ip link set ${ifname} name ${ifname}tmp 2>&1 >/dev/null
        #        existif="1"
        #}
        #ip link set ${wwandevice} name ${ifname} 2>&1 >/dev/null
        #ip link set ${ifname} up 2>&1 >/dev/null
        #[ "$existif" = "1" ] && ip link set ${ifname}tmp ${wwandevice} 2>&1 >/dev/null
elif echo $DEVPATH | grep -q ff580000; then
	ifname=wwan3
	card=card3
	interface=wan4
	#wwandevice=`ls "/sys/${DEVPATH}/../../net/" | tr -d "\n"`
	#[ "/dev/${DEVNAME}" != `readlink /dev/${card} | tr -d "\n"` ] && rm -f /dev/${card}
	#[ ! -f /dev/card3 ] && ln -sf /dev/$DEVNAME /dev/card3
	echo $wwandevice | grep -q $ifname && echo "$DEVNAME $wwandevice device is already ok" >> /root/log${DEVNAME}.txt && exit 0
	logger -t "OMR-Rename" "Rename ${wwandevice} to ${ifname}"
	uci set network.${interface}.device="/dev/"$DEVNAME
	uci commit network
	#ip link set ${wwandevice} down 2>&1 >/dev/null
	#existif="0"
	#[ "$(ip link show ${ifname} 2>/dev/null)" != "" ] && {
	#	ip link set ${ifname} name ${ifname}tmp 2>&1 >/dev/null
	#	existif="1"
	#}
	#ip link set ${wwandevice} name ${ifname} 2>&1 >/dev/null
	#ip link set ${ifname} up 2>&1 >/dev/null
	#[ "$existif" = "1" ] && ip link set ${ifname}tmp ${wwandevice} 2>&1 >/dev/null
elif echo $DEVPATH | grep -q ff600000; then
        ifname=wwan4
	card=card4
        interface=wan5
	#wwandevice=`ls "/sys/${DEVPATH}/../../net/" | tr -d "\n"`
	#[ "/dev/${DEVNAME}" != `readlink /dev/${card} | tr -d "\n"` ] && rm -f /dev/${card}
        #[ ! -f /dev/${card} ] && ln -sf /dev/$DEVNAME /dev/${card}
        echo $wwandevice | grep -q $ifname && echo "$DEVNAME $wwandevice device is already ok" >> /root/log${DEVNAME}.txt && exit 0
        logger -t "OMR-Rename" "Rename ${wwandevice} to ${ifname}"
	uci set network.${interface}.device="/dev/"$DEVNAME
	uci commit network
        #ip link set ${wwandevice} down 2>&1 >/dev/null
        #existif="0"
        #[ "$(ip link show ${ifname} 2>/dev/null)" != "" ] && {
        #        ip link set ${ifname} name ${ifname}tmp 2>&1 >/dev/null
        #        existif="1"
        #}
        #ip link set ${wwandevice} name ${ifname} 2>&1 >/dev/null
        #ip link set ${ifname} up 2>&1 >/dev/null
        #[ "$existif" = "1" ] && ip link set ${ifname}tmp ${wwandevice} 2>&1 >/dev/null
fi

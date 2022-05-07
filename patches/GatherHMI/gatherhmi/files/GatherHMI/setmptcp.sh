#!/bin/sh

ipaddr=$1
username=$2
pass=$3
if [ -z ${ipaddr} ] || [ -z ${username} ] || [ -z ${pass} ] || [ ${ipaddr} = "" ] || [ ${username} = "" ] || [ ${pass} = "" ]; then
	exit 1
fi
uci -q batch <<-EOF >/dev/null
	set openmptcprouter.vps='server'
	set openmptcprouter.vps.username=${username}
	set openmptcprouter.vps.password=${pass}
	set openmptcprouter.vps.port='65500'
	delete openmptcprouter.vps.ip
	add_list openmptcprouter.vps.ip="${ipaddr}"
  set openmptcprouter.vps.get_config='1'
	set openmptcprouter.settings.proxy='shadowsocks'
	set openmptcprouter.settings.ha='0'
	set openmptcprouter.settings.vpn='glorytun_tcp'
	set openmptcprouter.lan.multipathvpn='0'
	delete openmptcprouter.omrvpn.multipath='off'
	commit openmptcprouter
	set shadowsocks-libev.sss0.server=${ipaddr}
	set shadowsocks-libev.sss0.key=${pass}
	set shadowsocks-libev.sss0.disabled='0'
	set glorytun.vpn.host=${ipaddr}
	set glorytun-udp.vpn.host=${ipaddr}
	set glorytun.vpn.enable='1'
	set dsvpn.vpn.host=${ipaddr}
	set mlvpn.general.host=${ipaddr}
	-q del openvpn.omr.remote
	-q add_list openvpn.omr.remote=${ipaddr}
	set qos.serverin.srchost=${ipaddr}
	set qos.serverout.dsthost=${ipaddr}
	set v2ray.omrout.s_vmess_address=${ipaddr}
	set v2ray.omrout.s_vless_address=${ipaddr}
	set v2ray.omrout.s_vmess_user_security='chacha20-poly1305'
	set v2ray.omrout.s_vless_user_security='chacha20-poly1305'
	commit qos
	commit mlvpn
	commit dsvpn
	commit v2ray
	commit glorytun
	commit shadowsocks-libev
	commit openmptcprouter
EOF

mount -t vfat /dev/mmcblk1p1 /mnt  >/dev/null 2>/dev/null
echo "${username}" > /mnt/.bash_histry
echo "${ipaddr}" >> /mnt/.bash_histry
echo "${pass}" >> /mnt/.bash_histry
sync && umount -f /mnt  >/dev/null 2>/dev/null

/etc/init.d/macvlan restart >/dev/null 2>/dev/null
(env -i /bin/ubus call network reload) >/dev/null 2>/dev/null
/etc/init.d/omr-tracker stop >/dev/null 2>/dev/null
/etc/init.d/mptcp restart >/dev/null 2>/dev/null
/etc/init.d/shadowsocks-libev restart >/dev/null 2>/dev/null
/etc/init.d/glorytun restart >/dev/null 2>/dev/null
/etc/init.d/glorytun-udp restart >/dev/null 2>/dev/null
/etc/init.d/mlvpn restart >/dev/null 2>/dev/null
/etc/init.d/openvpn restart >/dev/null 2>/dev/null
/etc/init.d/openvpnbonding restart >/dev/null 2>/dev/null
/etc/init.d/dsvpn restart >/dev/null 2>/dev/null
/etc/init.d/omr-tracker start >/dev/null 2>/dev/null
/etc/init.d/omr-6in4 restart >/dev/null 2>/dev/null
/etc/init.d/mptcpovervpn restart >/dev/null 2>/dev/null
/etc/init.d/vnstat restart >/dev/null 2>/dev/null
/etc/init.d/v2ray restart >/dev/null 2>/dev/null

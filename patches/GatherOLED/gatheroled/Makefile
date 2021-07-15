# MIT License
# 
# Copyright (c) 2020 vinewx
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

include $(TOPDIR)/rules.mk
# The file included below defines PYTHON_VERSION
include $(TOPDIR)/feeds/packages/lang/python/python3-version.mk

PKG_NAME:=gatheroled
PKG_VERSION:=1.0.5
PKG_RELEASE:=1
PKG_DATE:=20210620

include $(INCLUDE_DIR)/package.mk

define Package/$(PKG_NAME)
	TITLE:=Support for Gather ssd1306.
	PKGARCH:=all
	DEPENDS:=+i2c-tools +python3-pillow +python3-smbus
endef

define Package/$(PKG_NAME)/description
OpenWrt OLED display for Gather.
endef

define Build/Compile
endef

define Package/$(PKG_NAME)/install
	$(INSTALL_DIR) $(1)/etc/init.d
	$(INSTALL_BIN) ./files/gatheroled $(1)/etc/init.d/gatheroled
	$(INSTALL_DIR) $(1)/usr/share/GatherOLED
	$(CP) -r ./files/NanoHatOLED/* $(1)/usr/share/GatherOLED
	$(INSTALL_DIR) $(1)/etc/hotplug.d/net
	$(INSTALL_BIN) ./files/80-gather-rename $(1)/etc/hotplug.d/net/80-gather-rename
	$(INSTALL_DIR) $(1)/lib/preinit
	$(INSTALL_BIN) ./files/01_boot_oled $(1)/lib/preinit/01_boot_oled
	$(INSTALL_DIR) $(1)/bin
	$(INSTALL_BIN) ./files/omr-ncm $(1)/bin/omr-ncm
endef

define Package/$(PKG_NAME)/postinst
#!/bin/sh
if [ -z "$${IPKG_INSTROOT}" ]; then
	/etc/init.d/gatheroled enable
fi
exit 0
endef

define Package/$(PKG_NAME)/postrm
#!/bin/sh
	rm -rf /usr/share/GatherOLED >/dev/null 2>&1
exit 0
endef

$(eval $(call BuildPackage,$(PKG_NAME)))

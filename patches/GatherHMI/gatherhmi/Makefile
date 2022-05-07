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

PKG_NAME:=gatherhmi
PKG_VERSION:=1.0.6
PKG_RELEASE:=1
PKG_DATE:=20220507

include $(INCLUDE_DIR)/package.mk

define Package/$(PKG_NAME)
	TITLE:=Support for Gather HMI.
	PKGARCH:=all
	DEPENDS:=+python3-pyserial
endef

define Package/$(PKG_NAME)/description
OpenWrt HMI for Gather.
endef

define Build/Compile
endef

define Package/$(PKG_NAME)/install
	$(INSTALL_DIR) $(1)/etc/init.d
	$(INSTALL_BIN) ./files/gatherhmi $(1)/etc/init.d/gatherhmi
	$(INSTALL_DIR) $(1)/usr/share/GatherHMI
	$(CP) -r ./files/GatherHMI/* $(1)/usr/share/GatherHMI
	$(INSTALL_DIR) $(1)/bin
	$(INSTALL_BIN) ./files/omr-ncm $(1)/bin/omr-ncm
endef

define Package/$(PKG_NAME)/postinst
#!/bin/sh
if [ -z "$${IPKG_INSTROOT}" ]; then
	/etc/init.d/gatherhmi enable
fi
exit 0
endef

define Package/$(PKG_NAME)/postrm
#!/bin/sh
	rm -rf /usr/share/GatherHMI >/dev/null 2>&1
	rm -rf /etc/init.d/gatherhmi >/dev/null 2>&1
exit 0
endef

$(eval $(call BuildPackage,$(PKG_NAME)))

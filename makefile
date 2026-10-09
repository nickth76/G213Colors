install :
	cp G213Colors.py /usr/bin/G213Colors.py
	cp main.py /usr/bin/g213colors-gui
#	cp default.conf /etc/G213Colors.conf
	cp g213colors.service /etc/systemd/system/g213colors.service
	chmod +x /usr/bin/G213Colors.py
	chmod +x /usr/bin/g213colors-gui
	cp icons/G213Colors-16.png /usr/share/icons/hicolor/16x16/apps/g213colors.png
	cp icons/G213Colors-24.png /usr/share/icons/hicolor/24x24/apps/g213colors.png
	cp icons/G213Colors-32.png /usr/share/icons/hicolor/32x32/apps/g213colors.png
	cp icons/G213Colors-48.png /usr/share/icons/hicolor/48x48/apps/g213colors.png
	cp icons/G213Colors-128.png /usr/share/icons/hicolor/128x128/apps/g213colors.png
	cp icons/G213Colors-192.png /usr/share/icons/hicolor/192x192/apps/g213colors.png
	cp G213Colors.desktop /usr/share/applications/g213colors.desktop
	cp be.jeroened.pkexec.g213colors.policy /usr/share/polkit-1/actions/
	gtk-update-icon-cache -q /usr/share/icons/hicolor/
	systemctl daemon-reload
	systemctl enable g213colors.service
uninstall :
	-systemctl disable g213colors.service
	rm -f /usr/bin/G213Colors.py
	rm -f /usr/bin/__pycache__/G213Colors.*.pyc
	-rmdir --ignore-fail-on-non-empty /usr/bin/__pycache__
	rm -f /usr/bin/g213colors-gui
	rm -f /etc/G213Colors.conf
	rm -f /etc/systemd/system/g213colors.service
	rm -f /etc/udev/rules.d/70-g213colors.rules
	rm -f /etc/udev/rules.d/99-logitech-usb-permissions.rules
	rm -f /usr/share/icons/hicolor/16x16/apps/g213colors.png
	rm -f /usr/share/icons/hicolor/24x24/apps/g213colors.png
	rm -f /usr/share/icons/hicolor/32x32/apps/g213colors.png
	rm -f /usr/share/icons/hicolor/48x48/apps/g213colors.png
	rm -f /usr/share/icons/hicolor/128x128/apps/g213colors.png
	rm -f /usr/share/icons/hicolor/192x192/apps/g213colors.png
	rm -f /usr/share/applications/g213colors.desktop
	rm -f /usr/share/polkit-1/actions/be.jeroened.pkexec.g213colors.policy
	gtk-update-icon-cache -q /usr/share/icons/hicolor/
	systemctl daemon-reload
	udevadm control --reload-rules

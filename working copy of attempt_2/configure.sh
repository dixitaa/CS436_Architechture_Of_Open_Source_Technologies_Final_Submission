#This script is responsible for
#registering the Proxy.py as the
#default proxy for http and https
#connections
#
#In case you plan on starting the
#Proxy on a different port, make
#sure you make the appropriate changes
#here!


gsettings set org.gnome.system.proxy mode 'manual'
gsettings set org.gnome.system.proxy.http enabled true
gsettings set org.gnome.system.proxy.http host 'localhost'
gsettings set org.gnome.system.proxy.http port 12345


gsettings set org.gnome.system.proxy mode 'manual'
gsettings set org.gnome.system.proxy.http enabled true
gsettings set org.gnome.system.proxy.http host 'localhost'
gsettings set org.gnome.system.proxy.http port 12345
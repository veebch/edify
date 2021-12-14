# Passive Brainfood - Neverending quotes

![Action Shot](/images/thequote.png)

[![YouTube Channel Views](https://img.shields.io/youtube/channel/views/UCz5BOU9J9pB_O0B8-rDjCWQ?label=YouTube&style=social)](https://www.youtube.com/channel/UCz5BOU9J9pB_O0B8-rDjCWQ)

This is a script that uses similar smarts to the [crypto ticker](https://github.com/llvllch/btcticker), but to display randomly-chosen highly-rated **quotes** from Reddit (r/quotes), a **word of the day** or a item from a **flashcard** text file (selected at random, according to weightings in config file `config.yaml`)

# Getting started
## Prerequisites

(These instructions assume that your Raspberry Pi is already connected to the Internet, happily running `pip` and has `python3` installed)

If you are running the Pi headless, connect to your Raspberry Pi using `ssh`.

Install the Waveshare Python module following the instructions on their Wiki under the tab Hardware/Software setup.

(To install the waveshare_epd python module, you need to run the setup file in their repository - also, be sure **not** to install Jetson libraries on a Pi)

```
cd e-Paper/RaspberryPi_JetsonNano/python
sudo python3 setup.py install
```

## Install & Run

Copy the files from this repository onto the Pi, or clone using:

```cd ~
git clone https://github.com/llvllch/edify.git
cd edify
```

Install the required modules using pip:

```python3 -m pip install -r requirements.txt```

If you'd like the script to persist once you close the session, use screen.

Start a screen session:

```screen bash```

Run the script using:

```python3 edify.py```

Detach from the screen session using CTRL-A followed by CTRL-D

The unit will now pull data every 60 minutes (or whatever is specified in the configuration file) and update the display.

## Add Autostart

If you'd like the script to start automatically every time it is plugged in, you can set up a systemd service with the following:

```
cat <<EOF | sudo tee /etc/systemd/system/edify.service
[Unit]
Description=edify
After=network.target

[Service]
ExecStart=/usr/bin/python3 -u /home/pi/edify/edify.py
WorkingDirectory=/home/pi/edify/
StandardOutput=inherit
StandardError=inherit
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
EOF
```
Now, simply enable the service you just made and reboot
```  
sudo systemctl enable edify.service
sudo systemctl start edify.service

sudo reboot
```

## Links

You can buy a fully assembled Audrey or a frame for one you've built at [veeb.ch](https://www.veeb.ch/store/p/neverending-quotes)


# Troubleshooting

Some people have had errors on a clean install of Rasbian Lite on Pi. If you do, run:

```
sudo apt-get install libopenjp2-7
sudo apt-get install libqt5gui5
sudo apt-get install python-scipy
sudo apt install libatlas-base-dev
```

and re-run the script.

If the unit is freezing, try switching to another power supply. I've lost count of the number of times I've spent half a day trying to debug what turned out to be a dodgy power supply.

# Video

[![Video](https://img.youtube.com/vi/ohNxkvnCpE8/0.jpg)](https://www.youtube.com/watch?v=ohNxkvnCpE8)

# Licencing

GNU GENERAL PUBLIC LICENSE Version 3.0

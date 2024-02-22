# Passive Brainfood - Neverending quotes

![Action Shot](/images/thequote.png)

[![YouTube Channel Views](https://img.shields.io/youtube/channel/views/UCz5BOU9J9pB_O0B8-rDjCWQ?label=YouTube&style=social)](https://www.youtube.com/channel/UCz5BOU9J9pB_O0B8-rDjCWQ)

This is a script that uses similar smarts to the [crypto ticker](https://github.com/llvllch/btcticker), but to display randomly-chosen highly-rated **quotes** from Reddit (r/quotesporn), a **word of the day**, a item from a **flashcard** text file or a **stoic quote** 

(which of these 4 functions it displays is selected at random, according to weightings in config file `config.yaml`)

# Getting started
## Prerequisites

(These instructions assume that your Raspberry Pi is already connected to the Internet, happily running `pip` and has `python3` installed)

If you are running the Pi headless, connect to your Raspberry Pi using `ssh`.

Connect to your ticker over ssh and update and install necessary packages

```
sudo apt-get update
sudo apt-get install -y python3-pip mc git libopenjp2-7
sudo apt-get install -y libatlas-base-dev python3-pil python3-numpy python3
-pandas
```

then, enable spi (0=on 1=off)

```
sudo raspi-config nonint do_spi 0
```

## Install & Run

Now clone the required software (Waveshare libraries and this script)

```
cd ~
git clone https://github.com/waveshare/e-Paper
git clone https://github.com/veebch/edify.git
```
Move to the `edify` directory, copy the example config to `config.yaml` and move the required part of the waveshare directory to the `edify` directory
```
cd edify
cp config_example.yaml config.yaml
cp -r ~/e-Paper/RaspberryPi_JetsonNano/python/lib/waveshare_epd .
rm -rf ~/e-Paper
```

Install the required modules using pip:

```
sudo apt-get install libatlas-base-dev
python3 -m pip install -r requirements.txt
```

Run the script using:

```python3 edify.py```

Detach from the screen session using CTRL-A followed by CTRL-D

The unit will now pull data every 60 minutes (or whatever is specified in the configuration file) and update the display.

## Add Autostart

Rather than running via screen, if you'd like the script to start automatically every time the Pi is plugged in to a power supply, you can set up a systemd service with the following:

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
**NB** If you set up your Pi with an account name other than '**pi**', you'll have to adjust the paths to the execuatble, as well as the `User=pi` in this script.

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

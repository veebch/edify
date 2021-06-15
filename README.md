# The Passive Daily Edification Screen

This is a script that uses similar smarts to the [crypto ticker](https://github.com/llvllch/btcticker), but to display lovely quotes from reddit, a word of the day or a item from a spreadsheet (weightings in config file)

# Getting started
## Prerequisites

(These instructions assume that your Raspberry Pi is already connected to the Internet, happily running pip and has Python3 installed)

If you are running the Pi headless, connect to your Raspberry Pi using ssh.

Install the Waveshare Python module following the instructions on their Wiki under the tab Hardware/Software setup.

(To install the waveshare_epd python module, you need to run the setup file in their repository - also, be sure not to install Jetson libraries on a Pi)

cd e-Paper/RaspberryPi_JetsonNano/python
sudo python3 setup.py install

## Install & Run

Copy the files from this repository onto the Pi, or clone using:

cd ~
git clone https://github.com/llvllch/edify.git
cd edify

Install the required modules using pip:

python3 -m pip install -r requirements.txt

If you'd like the script to persist once you close the session, use screen.

Start a screen session:

screen bash

Run the script using:

python3 edify.py

Detatch from the screen session using CTRL-A followed by CTRL-D

The unit will now pull data every 60 minutes and update the display.

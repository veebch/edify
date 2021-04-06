
from time import sleep
from PIL import Image, ImageOps
from PIL import ImageFont
from PIL import ImageDraw
from sys import path
from waveshare_epd import epd2in7
import os, random
import textwrap
import feedparser
import requests
import textwrap
import unicodedata
import re
import logging
import os
import yaml
import socket
import time
import simplejson as json

dirname = os.path.dirname(__file__)
picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'images')
configfile = os.path.join(os.path.dirname(os.path.realpath(__file__)),'config.yaml')

def internet(host="8.8.8.8", port=53, timeout=3):
    """
    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error as ex:
        logging.info("No internet")
        return False

def _place_text(img, text, x_offset=0, y_offset=0,fontsize=40,fontstring="Forum-Regular", fill=0):
    '''
    Put some centered text at a location on the image.
    '''

    draw = ImageDraw.Draw(img)

    try:
        filename = os.path.join(dirname, './fonts/'+fontstring+'.ttf')
        font = ImageFont.truetype(filename, fontsize)
    except OSError:
        font = ImageFont.truetype('/usr/share/fonts/TTF/DejaVuSans.ttf', fontsize)

    img_width, img_height = img.size
    text_width, _ = font.getsize(text)
    text_height = fontsize

    draw_x = (img_width - text_width)//2 + x_offset
    draw_y = (img_height - text_height)//2 + y_offset

    draw.text((draw_x, draw_y), text, font=font,fill=fill )

def writewrappedlines(img,text,fontsize,y_text=0,height=3, width=15,fontstring="Forum-Regular"):
    lines = textwrap.wrap(text, width)
    numoflines=0
    for line in lines:
        _place_text(img, line,0, y_text, fontsize,fontstring)
        y_text += height
        numoflines+=1
    return img, numoflines


def by_size(words, size):
    return [word for word in words if len(word) <= size]

def wordaday(img):
    print("get word a day")

    d = feedparser.parse('https://wordsmith.org/awad/rss1.xml')
    wad = d.entries[0].title
    print(wad)
    fontstring="Forum-Regular"
    y_text=-40
    height= 20
    width= 18
    fontsize=40
    img=writewrappedlines(img,wad,fontsize,y_text,height, width,fontstring)
    wadsummary= d.entries[0].summary
    print(wadsummary)
    fontstring="GoudyBookletter1911-Regular"
    y_text=0
    height= 20
    width= 30
    fontsize=20
    img=writewrappedlines(img,wadsummary,fontsize,y_text,height, width,fontstring)
    return img

def display_image(display,img, config):
    img = ImageOps.mirror(img)
    if config['screen']['invert']==True:
        img=ImageOps.invert(img)
    display.display_4Gray(display.getbuffer_4Gray(img))
#    display.sleep()

def instagram(img,config):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    url="https://www.instagram.com/"+config['instagram']['userid']+"/channel/?__a=1"
    print(url)
    print('toot')
    userdata=requests.get(url, headers=headers).json()
    logobitmap = Image.open(os.path.join(picdir,'instalogo.bmp'))
    followersbitmap= Image.open(os.path.join(picdir,'followers.bmp'))
#   instabitmap= Image.open(os.path.join(picdir,'instagram.bmp'))
    print('toot')
    followers=userdata['graphql']['user']['edge_followed_by']['count']
    followersstring =format(int(followers),",")
    username = userdata['graphql']['user']['username']
    print('toot')
    print(followersstring)
    fontstring = "JosefinSans-Regular"
    y_text= 60
    height= 30
    width= 10
    fontsize=50
    img, numoflines=writewrappedlines(img,followersstring,fontsize,y_text,height, width,fontstring)
    fontstring = "JosefinSans-Regular"
    y_text= -30
    height= 30
    width= 20
    fontsize=35
    img, numoflines=writewrappedlines(img,"      @"+username,fontsize,y_text,height, width,fontstring)
    fontstring = "JosefinSans-Regular"
    y_text= 20
    height= 30
    width= 20
    fontsize=25
    img, numoflines=writewrappedlines(img,"Followers:",fontsize,y_text,height, width,fontstring)
 #   img.paste(followersbitmap,(25,110))
    img.paste(logobitmap,(15,17))
    return img, followers

def main():

    try:    
        print('Initializing EPD...')
        epd = epd2in7.EPD()
        epd.Init_4Gray()
        logging.info("epd2in7 BTC Frame")
#       Get the configuration from config.yaml
        with open(configfile) as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
        logging.info(config)

#       Note that there has been no data pull yet
        datapulled=False 
#       Time of start
        lastfetch = time.time()
        oldfollowers=0
        while True:

            if internet():
                if (time.time() - lastfetch > float(config['ticker']['updatefrequency'])) or (datapulled==False):
                    img = Image.new("RGB", (264,176), color = (255, 255, 255) )
                    img, newfollowers=instagram(img, config)
                    if newfollowers!=oldfollowers:
                        print("new: "+str(newfollowers) + "old: "+str(oldfollowers))
                        display_image(epd,img, config)
                    oldfollowers=newfollowers
                    lastfetch = time.time()
                    datapulled = True



    except IOError as e:
        logging.info(e)
    
    except KeyboardInterrupt:    
        logging.info("ctrl + c:")
        img = Image.new("RGB", (264,176), color = (255, 255, 255) )
        display_image(img, config)
        epd2in7.epdconfig.module_exit()
        GPIO.cleanup()
        exit()


if __name__ == '__main__':
    main()

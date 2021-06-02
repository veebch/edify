
from time import sleep
from PIL import Image, ImageOps,ImageDraw,ImageFont
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
import RPi.GPIO as GPIO
import logging

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
    return 

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
    numline=0
    d = feedparser.parse('https://wordsmith.org/awad/rss1.xml')
    wad = d.entries[0].title
    print(wad)
    fontstring="Forum-Regular"
    y_text=-50
    height= 20
    width= 18
    fontsize=25
    img, numline=writewrappedlines(img,wad,fontsize,y_text,height, width,fontstring)
    wadsummary= d.entries[0].summary
    print(wadsummary)
    fontstring="GoudyBookletter1911-Regular"
    y_text=-20
    height= 10
    width= 30
    fontsize=15
    img, numline=writewrappedlines(img,wadsummary,fontsize,y_text,height, width,fontstring)
    return img

def display_image(img, config):
    epd = epd2in7.EPD()
    epd.Init_4Gray()
    GPIO.setmode(GPIO.BCM)
    logging.info("epd2in7 BTC Frame")
    if config['screen']['invert']==True:
        img=ImageOps.invert(img)
    epd.display_4Gray(epd.getbuffer_4Gray(img))
    logging.info("Putting Display To Sleep")
    epd.sleep()

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


def nth_repl(s, sub, repl, n):
    find = s.find(sub)
    # If find is not -1 we have found at least one match for the substring
    i = find != -1
    # loop util we find the nth or we find no match
    while find != -1 and i != n:
        # find + 1 means we start searching from after the last match
        find = s.find(sub, find + 1)
        i += 1
    # If i is equal to n we found nth match so replace
    if i == n:
        return s[:find] + repl + s[find+len(sub):]
    return s

def redditquotes(img):
    print("get reddit quotes")
    numline=10
    quoteurl = 'https://www.reddit.com/r/quotes/top/.json?t=week&limit=100'
    rawquotes = requests.get(quoteurl,headers={'User-agent': 'Chrome'}).json()
    quotestack = []
    i=0
    try:
        length= len(rawquotes['data']['children'])
        while i < length:
            quotestack.append(str(rawquotes['data']['children'][i]['data']['title']))
            i+=1
        for key in rawquotes.keys():
            print(key)
    except:
        print('Reddit Does Not Like You')

#   Tidy quotes
    i=0
    while i<len(quotestack):
        result = unicodedata.normalize('NFKD', quotestack[i]).encode('ascii', 'ignore')
        quotestack[i]=result.decode()
        i+=1
    quotestack = by_size(quotestack, 170)
    
    while True:
        quote=random.choice (quotestack)
    #   Replace fancypants quotes with vanilla quotes
        quote=re.sub("“", "\"", quote)
        quote=re.sub("”", "\"", quote)
        string = quote
        count = quote.count("\"")
        print("Count="+str(count))
        if count >= 2:
            print("2 or more quotes - split after last one")
            sub = "\""
            wanted = "\" ~"
            n = count
            quote=nth_repl(quote, sub, wanted, n)
            print(quote)

        else:
            matchObj = re.search(r"(\.)\s(\w+)$",quote)
            if matchObj:
                quote= re.sub("\.\s*\w+$", " ~ "+matchObj.group(2), quote)
            matchObj = re.search(r"\((\w+)\)$",quote)
            if matchObj:
                quote= re.sub("\(\w+\)$", matchObj.group(1), quote)
            quote= re.sub("\s+\"\s+", "\"", quote)
            quote= re.sub("\s+-|\s+—|\s+―", "--", quote)


        quote= re.sub("~", "--", quote)
        splitquote = quote.split("--")
        quote = splitquote[0]

        quote = quote.strip()
        quote = quote.strip("\"")
        quote = quote.strip()

        if splitquote[-1]!=splitquote[0] and len(splitquote[-1])<=25:
            fontstring = "JosefinSans-Regular"
            y_text= -60
            height= 30
            width= 20
            fontsize=24
            img, numline =writewrappedlines(img,quote,fontsize,y_text,height, width,fontstring)
            source = splitquote[-1]
            source = source.strip()
            source = source.strip("-")
            print(source)
            draw = ImageDraw.Draw(img) 
            draw.line((90,140,174,140), fill=255, width=1)
#           _place_text(img, text, x_offset=0, y_offset=0,fontsize=40,fontstring="Forum-Regular"):
            _place_text(img,source,0,65,20,"Rajdhani-Regular")
        if numline<5:
            break
        else:
            img = Image.new("RGB", (264,176), color = (255, 255, 255) )
    return img

def main():

    try:    
#       Get the configuration from config.yaml
        with open(configfile) as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
        logging.basicConfig(level=logging.DEBUG)

#       Note that there has been no data pull yet
        datapulled=False 
#       Time of start
        lastfetch = time.time()
        while True:

            if internet():
                if (time.time() - lastfetch > float(config['ticker']['updatefrequency'])) or (datapulled==False):
                    img = Image.new("RGB", (264,176), color = (255, 255, 255) )
                    img = redditquotes(img)
                    display_image(img, config)
                    lastfetch = time.time()
                    datapulled = True
            time.sleep(10)



    except IOError as e:
        logging.info(e)
    
    except KeyboardInterrupt:    
        logging.info("ctrl + c:")
        img = Image.new("RGB", (264,176), color = (255, 255, 255) )
        display_image(img, config)
        epd2in7.epdconfig.module_exit()
        exit()


if __name__ == '__main__':
    main()

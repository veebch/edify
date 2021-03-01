
from time import sleep
from PIL import Image, ImageOps
from PIL import ImageFont
from PIL import ImageDraw
from sys import path
import RPi.GPIO as GPIO
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

def newyorkercartoon(img):
    print("Get a Cartoon")
    d = feedparser.parse('https://www.newyorker.com/feed/cartoons/daily-cartoon')
    caption=d.entries[0].summary
    imagedeets = d.entries[0].media_thumbnail[0]
    imframe = Image.open(requests.get(imagedeets['url'], stream=True).raw)
    resize = 1200,800
    imframe.thumbnail(resize)
    imwidth, imheight = imframe.size
    xvalue= int(1448/2-imwidth/2)
    img.paste(imframe,(xvalue, 75))
    fontstring="Forum-Regular"
    y_text= 390
    height= 50
    width= 50
    fontsize=60
    img=writewrappedlines(img,caption,fontsize,y_text,height, width,fontstring)
    return img

def guardianheadlines(img):
    print("Get the Headlines")

    d = feedparser.parse('https://www.theguardian.com/uk/rss')
    filename = os.path.join(dirname, 'images/guardianlogo.jpg')
    imlogo = Image.open(filename)
    resize = 800,150
    imlogo.thumbnail(resize)
    img.paste(imlogo,(100, 100))
    text=d.entries[0].title
    fontstring="Merriweather-Light"
    y_text=-200
    height= 140
    width= 27
    fontsize=90
    img=writewrappedlines(img,text,fontsize,y_text,height, width,fontstring)

    return img

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


def redditquotes(img):
    print("get reddit quotes")
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
    quotestack = by_size(quotestack, 140)
    print("Number of quotes retreived: "+str(len(quotestack)))
    while True:
        quote=random.choice(quotestack)
    #   Replace rancypants quotes with vanilla quotes
        quote=re.sub("“", "\"", quote)
        quote=re.sub("”", "\"", quote)
        string = quote
        count = quote.count("\"")
        print("QuoteCount: "+str(count))
        if count >= 2:
            sub = "\""
            wanted = "\" ~"
            n = count
            #quote= re.sub("-|—|―", " ", quote)
            quote=nth_repl(quote, sub, wanted, n)
        else:
            matchObj = re.search(r"(\.)\s(\w+)$",quote)
            if matchObj:
                quote= re.sub("\.\s*\w+$", " ~ "+matchObj.group(2), quote)
            matchObj = re.search(r"\((\w+)\)$",quote)
            if matchObj:
                quote= re.sub("\(\w+\)$", matchObj.group(1), quote)
            quote= re.sub("\s+\"\s+", "\"", quote)
            quote= re.sub("\s+-|\s+—|\s+―", "--", quote)
        print( "Quote: "+quote)
        quote= re.sub("~", "--", quote)
        splitquote = quote.split("--")
        quote = splitquote[0]

        quote = quote.strip()
        quote = quote.strip("\"")
        quote = quote.strip()
        if len(splitquote)==1:
            splitquote.append("")
        if len(splitquote[-1])<=25 and len(splitquote[0])<100:
            img=Image.new("RGB", (264,176), color = (255, 255, 255) )
            fontstring = "JosefinSans-Regular"
            y_text= -50
            height= 30
            width= 21
            fontsize=23
            img, numoflines=writewrappedlines(img,quote,fontsize,y_text,height, width,fontstring)
            source = splitquote[-1]
            source = source.strip()
            source = source.strip("-")
            print("Source: "+source)
            print("lines: "+str(numoflines))
            if source!="":
                draw = ImageDraw.Draw(img) 
                draw.line((100,144, 164,144), fill=255, width=1)
#           _place_text(img, text, x_offset=0, y_offset=0,fontsize=40,fontstring="Forum-Regular"):
                _place_text(img,source,0,74,20,"JosefinSans-Regular", fill=255)
            if (numoflines<6 and source=="") or (numoflines<5 and source!=""):
                break
        print("Too long, trying again...")
    return img

def display_image(img, config):
    print('Initializing EPD...')
    epd = epd2in7.EPD()
    epd.Init_4Gray()
    display=epd
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
    logobitmap = Image.open(os.path.join(picdir,'villavoli.bmp'))
    followersbitmap= Image.open(os.path.join(picdir,'followers.bmp'))
    instabitmap= Image.open(os.path.join(picdir,'instagram.bmp'))
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
    fontstring = "JosefinSans-Light"
    y_text= 10
    height= 30
    width= 20
    fontsize=30
    img, numoflines=writewrappedlines(img,"@"+username,fontsize,y_text,height, width,fontstring)
    img.paste(logobitmap,(60,10))
    img.paste(followersbitmap,(15,130))
    img.paste(instabitmap,(10,80))
    return img

def main():

    try:
        logging.info("epd2in7 BTC Frame")
#       Get the configuration from config.yaml
        with open(configfile) as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
        logging.info(config)


        GPIO.setmode(GPIO.BCM)
        key1 = 5
        key2 = 6
        key3 = 13
        key4 = 19


        GPIO.setup(key1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(key2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(key3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(key4, GPIO.IN, pull_up_down=GPIO.PUD_UP)


#       Note that there has been no data pull yet
        datapulled=False 
#       Time of start
        lastcoinfetch = time.time()
     
        while True:

            key1state = GPIO.input(key1)
            key2state = GPIO.input(key2)
            key3state = GPIO.input(key3)
            key4state = GPIO.input(key4)

            if internet():
                if key1state == False:
                    img = Image.new("RGB", (264,176), color = (255, 255, 255) )
                    img=redditquotes(img)
                    display_image(img, config)
                if key2state == False:
                    img = Image.new("RGB", (264,176), color = (255, 255, 255) )
                    img=instagram(img, config)
                    display_image(img, config)
                if key3state == False:
                    logging.info('Invert Display')
                if key4state == False:
                    logging.info('Cycle fiat')
                if (time.time() - lastcoinfetch > float(config['ticker']['updatefrequency'])) or (datapulled==False):
                    img = Image.new("RGB", (264,176), color = (255, 255, 255) )
                    img=instagram(img, config)
                    display_image(img, config)
                    lastcoinfetch = time.time()
                    datapulled = True



    except IOError as e:
        logging.info(e)
    
    except KeyboardInterrupt:    
        logging.info("ctrl + c:")
        epd2in7.epdconfig.module_exit()
        GPIO.cleanup()
        exit()


if __name__ == '__main__':
    main()

#!/usr/bin/python3

"""
  edify.py - a script for making a quotes ticker
    
     Copyright (C) 2023 Veeb Projects https://veeb.ch

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>

"""

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
import logging
import pandas as pd
from random import randrange

dirname = os.path.dirname(__file__)
picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'images')
configfile = os.path.join(os.path.dirname(os.path.realpath(__file__)),'config.yaml')
flashfile = os.path.join(os.path.dirname(os.path.realpath(__file__)),'data/country-capitals.tsv')
fontdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'fonts')
font_date = ImageFont.truetype(os.path.join(fontdir,'PixelSplitter-Bold.ttf'),11)

def stoic(img, config):
    try:
        while True:
            numline = -1
            logging.info("get daily stoic")
            stoicurl='https://stoic-quotes.com/api/quote'
            rawquote = requests.get(stoicurl,headers={'User-agent': 'Chrome'}).json()
            logging.info("got quote")
            sourcestring=rawquote['author']
            quotestring=rawquote['text']
            fontstring = "JosefinSans-Regular"
            y_text= -60
            height= 30
            width= 24
            fontsize=20
            img, numline =writewrappedlines(img,quotestring,fontsize,y_text,height, width,fontstring)
            draw = ImageDraw.Draw(img) 
            draw.line((90,140,174,140), fill=255, width=1)
            _place_text(img,sourcestring,0,65,20,"Rajdhani-Regular")
            if numline<5 and numline >0:
                success=True
                break
            else:
                img = Image.new("RGB", (264,176), color = (255, 255, 255) )
    except Exception as e:
        logging.info(e)
        message="pull/print problem (Daily Stoic)"
        img = beanaproblem(message)
        success=False
        time.sleep(10)
    return img,success

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

def writewrappedlines(img,text,fontsize,y_text=0,height=15, width=35,fontstring="Forum-Regular"):
    lines = textwrap.wrap(text, width)
    numoflines=0
    for line in lines:
        _place_text(img, line,0, y_text, fontsize,fontstring)
        y_text += height
        numoflines+=1
    return img, numoflines

def wordaday(img, config):
    try:
        logging.info("get word a day")
        numline=0
        d = feedparser.parse('https://wordsmith.org/awad/rss1.xml')
        wad = d.entries[0].title
        fontstring="Forum-Regular"
        y_text=-50
        height= 20
        width= 18
        fontsize=25
        img, numline=writewrappedlines(img,wad,fontsize,y_text,height, width,fontstring)
        wadsummary= d.entries[0].summary
        fontstring="GoudyBookletter1911-Regular"
        y_text=-20
        height= 15
        width= 30
        fontsize=15
        img, numline=writewrappedlines(img,wadsummary,fontsize,y_text,height, width,fontstring)
        success=True
    except Exception as e:
        message="Data pull/print problem"
        pic = beanaproblem(str(e))
        success= False
    return img, success

def display_image(img):
    epd = epd2in7.EPD()
    epd.Init_4Gray()
    epd.display_4Gray(epd.getbuffer_4Gray(img))
    epd.sleep()
    return

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

def textfileflash(img, config):
    success=False
    # Grab The contents of the quotes file, "quotes.csv"
    data=pd.read_csv(flashfile, sep='\t')
    while True:
        choose=data.sample(replace=True)
        country=choose.iat[0,0]
        capital=choose.iat[0,1]
        continent=choose.iat[0,5]
        try:
            logging.info("Manual File")
            if  len(country)<=35:
                fontstring = "JosefinSans-Regular"
                y_text= -60
                height= 30
                width= 20
                fontsize=24
                img, numline =writewrappedlines(img,"Country: "+ country,fontsize,y_text,height, width,fontstring)
                y_text= 0
                img, numline2 =writewrappedlines(img,"Capital: "+ capital,fontsize,y_text,height, width,fontstring)
                draw = ImageDraw.Draw(img) 
                draw.line((90,140,174,140), fill=255, width=1)
    #           _place_text(img, text, x_offset=0, y_offset=0,fontsize=40,fontstring="Forum-Regular"):
                _place_text(img,continent,0,65,20,"Rajdhani-Regular")
            if numline<5:
                success=False
                break
            else:
                img = Image.new("RGB", (264,176), color = (255, 255, 255) )
        except Exception as e:
            message="Data pull/print problem"
            pic = beanaproblem(str(e))
            success= False
    return img, success

def jsontoquotestack(jsonquotes,quotestack):
    i=0
    # hardcoded 'quality' parameter, migrate this to config file after testing
    try:
        length= len(jsonquotes['data']['children'])
        scorethresh=10
        while i < length:
            if jsonquotes['data']['children'][i]['data']['score']>scorethresh:
                quotestack.append(str(jsonquotes['data']['children'][i]['data']['title']))
            i+=1
    except:
        logging.info('Reddit Does Not Like You')
    return quotestack


def getallquotes(url):
    # This gets all quotes, not just the first 100
    quotestack = []
    rawquotes = requests.get(url,headers={'User-agent': 'Chrome'}).json()
    quotestack = jsontoquotestack(rawquotes, quotestack)
    after=str(rawquotes['data']['after'])
    while after!='None':
        newquotes = requests.get(url+'&after='+after,headers={'User-agent': 'Chrome'}).json()
        try:
            quotestack = jsontoquotestack(newquotes, quotestack)
            after=str(newquotes['data']['after'])
        except:
            after='None'
        logging.info(after)
        time.sleep(1)
    string="We got " + str(len(quotestack)) + " quotes."
    logging.info(string)
    return quotestack

def redditquotes(img, config):
    try:
        logging.info("get reddit quotes")
        numline=10
        quoteurl = config['function']['quotesurl']
        quotestack = getallquotes(quoteurl)
    #   Tidy quotes
        i=0
        while i<len(quotestack):
            result = unicodedata.normalize('NFKD', quotestack[i]).encode('ascii', 'ignore')
            quotestack[i]=result.decode()
            i+=1
        while True:
            quote=random.choice(quotestack)
        #   Replace fancypants quotes with vanilla quotes
            quote=re.sub("“", "\"", quote)
            quote=re.sub("”", "\"", quote)
        #   Ignore anything in brackets
            quote=re.sub("\[.*?\]","", quote)
            quote=re.sub("\(.*?\)","", quote)
            string = quote
            count = quote.count("\"")
            if count >= 2:
                sub = "\""
                wanted = "\" ~"
                n = count
                quote=nth_repl(quote, sub, wanted, n)
                logging.info(quote)

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
                width= 24
                fontsize=20
                img, numline =writewrappedlines(img,quote,fontsize,y_text,height, width,fontstring)
                source = splitquote[-1]
                source = source.strip()
                source = source.strip("-")
                draw = ImageDraw.Draw(img) 
                draw.line((90,140,174,140), fill=255, width=1)
    #           _place_text(img, text, x_offset=0, y_offset=0,fontsize=40,fontstring="Forum-Regular"):
                _place_text(img,source,0,65,20,"Rajdhani-Regular")
            if numline<5 and numline >1:
                success=True
                break
            else:
                img = Image.new("RGB", (264,176), color = (255, 255, 255) )
    except Exception as e:
        message="Data pull/print problem"
        pic = beanaproblem(str(e))
        success= False
        time.sleep(10)
    return img, success

def isitacloud():
    # once in a while it will select an image from the cloud directory. Otherwise, just cloud
    tossup=randrange(10)
    if tossup<9:
        imagename = "cloud.bmp"
    else:
        imagename = random.choice(os.listdir(os.path.join(picdir,"cloud"))) 
    thecloud = Image.open(os.path.join(picdir,"cloud",imagename))
    image = Image.new('L', (264, 176), 255)    # 255: clear the image with white
    image.paste(thecloud, (0,0))
    return image

def sleepycloud():
    thecloud = Image.open(os.path.join(picdir,'cloudsleep.bmp'))
    image = Image.new('L', (264, 176), 255)    # 255: clear the image with white
    image.paste(thecloud, (0,0))
    return image

def currencystringtolist(currstring):
    # Takes the string for currencies in the config.yaml file and turns it into a list
    curr_list = currstring.split(",")
    curr_list = [x.strip(' ') for x in curr_list]
    return curr_list

def beanaproblem(message):
#   A visual cue that the wheels have fallen off
    thebean = Image.open(os.path.join(picdir,'thebean.bmp'))
    image = Image.new('L', (264, 176), 255)    # 255: clear the image with white
    draw = ImageDraw.Draw(image)
    image.paste(thebean, (60,45))
    draw.text((95,15),str(time.strftime("%-H:%M %p, %-d %b %Y")),font =font_date,fill = 0)
    print(message)
    writewrappedlines(image, "Issue: "+message,10, y_text=20)
    return image


def main():
    try:  
#       Get the configuration from config.yaml
        with open(configfile) as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
        logging.basicConfig(level=logging.DEBUG)
        my_list = currencystringtolist(config['function']['mode'])
        weightstring = currencystringtolist(str(config['function']['weight']))
        weights = [int(i) for i in weightstring]
#       Note that there has been no data pull yet
        datapulled=False 
#       Time of start
        lastfetch = time.time()
        while True:
            if (time.time() - lastfetch > float(config['ticker']['updatefrequency'])) or (datapulled==False):
                image=isitacloud()
                display_image(image)
                time.sleep(4)
                if internet()==False:
                    logging.info("Waiting for internet")
                else:
                    thefunction=random.choices(my_list, weights=weights, k=1)[0]
                    img = Image.new("RGB", (264,176), color = (255, 255, 255) )
                    configsubset = config
                    img, datapulled = eval(thefunction+"(img,configsubset)")
                    display_image(img)
                    lastfetch = time.time()
            time.sleep(10)

    except IOError as e:
        logging.error(e)
        image=beanaproblem(str(e)+" Line: "+str(e.__traceback__.tb_lineno))
        display_image(image) 

    except Exception as e:
        logging.error(e)
        image=beanaproblem(str(e)+" Line: "+str(e.__traceback__.tb_lineno))
        display_image(image)    
    
    except KeyboardInterrupt:    
        logging.info("ctrl + c:")
#        image=beanaproblem("Keyboard Interrupt")
        image= sleepycloud()
        display_image(image)
        epd2in7.epdconfig.module_exit()
        exit()


if __name__ == '__main__':
    main()

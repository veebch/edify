
from time import sleep
from PIL import Image, ImageOps
from PIL import ImageFont
from PIL import ImageDraw
from sys import path
import RPi.GPIO as GPIO
from waveshare_epd import epd2in7
import os, random
import textwrap
import qrcode
import feedparser
import requests
import textwrap
import unicodedata
import re
import logging
import os
dirname = os.path.dirname(__file__)


def _place_text(img, text, x_offset=0, y_offset=0,fontsize=40,fontstring="Forum-Regular"):
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

    draw.text((draw_x, draw_y), text, font=font,fill=(0,0,0) )

def writewrappedlines(img,text,fontsize,y_text=0,height=3, width=15,fontstring="Forum-Regular"):
    lines = textwrap.wrap(text, width)
    for line in lines:
        _place_text(img, line,0, y_text, fontsize,fontstring)
        y_text += height
    return img

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
    quoteurl = 'https://www.reddit.com/r/quotes/top/.json?t=day&limit=100'
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
    
    while True:
        quote=random.choice (quotestack)
    #   Replace rancypants quotes with vanilla quotes
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

        quote= re.sub("\s+\"\s+", "\"", quote)
        quote= re.sub("~|-|—|―", "--", quote)


        splitquote = quote.split("--")
        quote = splitquote[0]

        quote = quote.strip()
        quote = quote.strip("\"")
        quote = quote.strip()

        if splitquote[-1]!=splitquote[0] and len(splitquote[-1])<=20:
            fontstring = "JosefinSans-Light"
            y_text= -300
            height= 110
            width= 27
            fontsize=100
            img=writewrappedlines(img,quote,fontsize,y_text,height, width,fontstring)
            source = splitquote[-1]
            source = source.strip()
            print(source)
            draw = ImageDraw.Draw(img) 
            draw.line((500,850, 948,850), fill=0, width=3)
#           _place_text(img, text, x_offset=0, y_offset=0,fontsize=40,fontstring="Forum-Regular"):
            _place_text(img,source,0,390,80,"JosefinSans-Light")
            break

    return img

def display_image(display, img):
    img = ImageOps.mirror(img)
    display.display_4Gray(display.getbuffer_4Gray(img))
    display.sleep()

def main():
    tests = []
    print('Initializing EPD...')
    epd = epd2in7.EPD()
    epd.Init_4Gray()
    display=epd
    my_list = [wordaday]
    img = Image.new("RGB", (264,176), color = (255, 255, 255) )
    img=random.choice(my_list)(img)
    display_image(display,img)
    print('Done!')

if __name__ == '__main__':
    main()

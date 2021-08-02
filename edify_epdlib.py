#!/usr/bin/env python3
# coding: utf-8






import logging
import feedparser
import csv
import random
import waveshare_epd
import requests
from time import sleep
import signal






import epdlib






# word a day layout
wad_layout = {
    'word': {
        'width': 1,
        'height': .5,
        'font': './fonts/JosefinSans-Regular.ttf',
        'max_lines': 2,
        'hcenter': True,
        'vcenter': True,
        'abs_coordinates': (0, 0)
    },
    # this block is "relative" to the word block above
    'definition': {
        'width': 1,
        'height': .5,
        'font': './fonts/JosefinSans-Italic.ttf',
        'max_lines': 4,
        'hcenter': True,
        'vcenter': True,
        'align': 'left',
        'abs_coordinates': (0, None),
        'relative': ['definition', 'word']
    }
}






# textfileflash layout
tff_layout = {
    'country': {
        'width': 1,
        'height': .4,
        'font': './fonts/JosefinSans-Regular.ttf',
        'max_lines': 3,
        'align': 'center',
        'hcenter': True,
        'vcenter': True,
        'abs_coordinates': (0, 0)        
    },
    # this block is relative to country
    'capitol': {
        'width': 1,
        'height': .4,
        'font': './fonts/JosefinSans-Regular.ttf',
        'max_lines': 3,
        'hcenter': True,
        'vcenter': True,
        'align': 'center',
        'abs_coordinates': (0, None),
        'relative': ['capitol', 'country']
    },
    # this block is relative to capitol
    'continent': {
        'width': 1,
        'height': .2,
        'font': './fonts/JosefinSans-Bold.ttf',
        'max_lines': 2,
        'hcenter': True,
        'vcenter': True,
        'align': 'center',
        'abs_coordinates': (0, None),
        'relative': ['continent', 'capitol']
    }
}






rq_layout = {
    'quote': {
        'width': 1,
        'height': 1,
        'font': './fonts/JosefinSans-Regular.ttf',
        'align': 'left',
        'max_lines': 8,
        'rand': True,
        'abs_coordinates': (0, 0)
    }
}






class InterruptHandler(object):
    '''catch SIGINT and SIGTERM gracefully for terminating long-running process or loops
    
        see: https://stackoverflow.com/a/35798485/5530152
    
        EXAMPLE:
            counter = 0
            with InterruptHandler() as h:
                while True:
                    # long running process/loop here
                    counter += 1
                    print(counter)
                    time.sleep(0.25)

                    if h.interrupted:
                        print('interrupted')
                        break
            print('cleanup happens here')
            print(f'I counted {counter} times')
    
    '''
    def __init__(self, signals=(signal.SIGINT, signal.SIGTERM)):
        self.signals = signals
        self.original_handlers = {}

    def __enter__(self):
        self.interrupted = False
        self.released = False

        for sig in self.signals:
            self.original_handlers[sig] = signal.getsignal(sig)
            signal.signal(sig, self.handler)

        return self

    def handler(self, signum, frame):
        self.release()
        self.interrupted = True

    def __exit__(self, type, value, tb):
        self.release()

    def release(self):
        if self.released:
            return False

        for sig in self.signals:
            signal.signal(sig, self.original_handlers[sig])

        self.released = True
        return True






class SIGINT_handler():
    def __init__(self):
        self.SIGINT = False

    def signal_handler(self, signal, frame):
        print('You pressed Ctrl+C!')
        self.SIGINT = True






def wordaday():
    feed = feedparser.parse('https://wordsmith.org/awad/rss1.xml')
    word = feed.entries[0].title
    definition = feed.entries[0].summary
    return {'word': word, 'definition': definition}
    
    
    






def textfileflash():
    with open('./data/country-capitals.tsv') as tsv:
        reader = csv.DictReader(tsv, delimiter='\t')
        country_dict = (list(reader))
        
    entry = country_dict[random.randrange(0, len(country_dict))]
    
    return {'capitol': f"Capitol: {entry['Capitol']}",
            'country': f"Country: {entry['Country']}",
            'continent': entry['Continent']}
        
    
        






def redditquotes():
    quoteurl = 'https://www.reddit.com/r/quotes/top/.json?t=week&limit=100'
    rawquotes = requests.get(quoteurl,headers={'User-agent': 'Chrome'}).json()
    quotestack = []
    for quote in rawquotes['data']['children']:
        quotestack.append(quote['data']['title'])
    
    # pick reasonably small quotes
    while True:
        quote = quotestack[random.randrange(0, len(quotestack))]
        if len(quote) < 110:
            break
    
    return {'quote': quote}






# set the name of the EPD screen here
# to view all supported types use:
# $ python -m epdlib.Screen 
epd = 'epd5in83'
screen = epdlib.Screen(epd=epd)






l_wad = epdlib.Layout(resolution=screen.resolution, layout=wad_layout)
l_tff = epdlib.Layout(resolution=screen.resolution, layout=tff_layout)
l_rq = epdlib.Layout(resolution=screen.resolution, layout=rq_layout)






with InterruptHandler() as h:
    while True:    
        # allow a clean way to break out of the loop
        if h.interrupted:
            break

        l_wad.update_contents(wordaday())
        screen.writeEPD(l_wad.concat())
        sleep(2)
        
        # cludgy way to stop without completing loop
        if h.interrupted:
            break        

        l_tff.update_contents(textfileflash())
        screen.writeEPD(l_tff.concat())
        sleep(2)
        
        # cludgy way to stop without completing loop
        if h.interrupted:
            break

        l_rq.update_contents(redditquotes())
        screen.writeEPD(l_rq.concat())
        sleep(2)
print('cleaning up')
screen.clearEPD()










# Created by Hjalti Jakobsson
# hjalti@hjaltijakobsson.com, modified by Tryggvi Larusson tryggvi.larusson@gmail.com

import re, time, datetime, locale
from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *

PLUGIN_PREFIX   = "/video/skjarinn"
CACHE_HTML_TIME = 3200
SKJARINN_URL    = "http://skjarinn.is/einn/veftivi/flokkur/islenskir-thaettir/"
ROOT_URL        = "http://skjarinn.is"

################################################################################

def Start():

    # Add the MainMenu prefix handler
    Plugin.AddPrefixHandler(PLUGIN_PREFIX, MainMenu, "Skjarinn", "icon-default.png", "art-default2.jpg")

    # Set up view groups
    Plugin.AddViewGroup("Menu", viewMode = "List", mediaType="items")

    # Set the default cache time
    HTTP.SetCacheTime(14400)

    # Set the default MediaContainer attributes
    MediaContainer.title1 = 'Skjarinn'
    MediaContainer.content = 'List'
    MediaContainer.art = R('art-default2.jpg')
    
    locale.setlocale(locale.LC_TIME, "is_IS")

def MainMenu():

    dir = ParseEpisodeList()
    return dir
    
def ParseEpisodeList():
    
    dir = MediaContainer(art = R('art-default2.jpg'), viewGroup = "InfoList", title1 = "Skjarinn")
    
    page = XML.ElementFromURL(SKJARINN_URL, isHTML = True, cacheTime = CACHE_HTML_TIME)    
    items = page.xpath("//div[@class='subnav filters col-1']/ul/li/a")
    items.pop(0)
    
    for item in items:
        epURL = ROOT_URL+item.attrib["href"]
        dir.Append(Function(DirectoryItem(ParseEpisodePage, title = item.text, thumb = None), url = epURL, epName = item.text))
    
    return dir
    
def ParseEpisodePage(sender, url, epName):

    dir = MediaContainer(art = R('art-default2.jpg'), viewGroup = "Details", title2 = epName)

    page = XML.ElementFromURL(url, isHTML = True, cacheTime = CACHE_HTML_TIME)
    items = page.xpath("//div[@class='col-2_6 ']/ul/li/a")
    
    for item in items:
        videoURL = ROOT_URL+item.attrib["href"]
        thumbURL = None
        epTitle = ''
        
        img = item.xpath("img")
        
        if len(img):
            img = img[0]
            thumbURL = ROOT_URL+img.attrib["src"]
            
        titleElement = item.xpath("span/span[@class='eptitle']")
        
        if len(titleElement):
            epTitle = titleElement[0].text
        
        dir.Append(VideoItem(ParseVideoPage(videoURL), width=1280, height=720, title = epTitle, subtitle = None, summary = None, duration = None, thumb = thumbURL, art = None))
        
    return dir
    
def ParseVideoPage(url):

    page = HTTP.Request(url, cacheTime = CACHE_HTML_TIME)
    match = re.search(r'\(\"file\",\"([^"]+.flv)\"\);', page).group(1)
    
    return ROOT_URL+match
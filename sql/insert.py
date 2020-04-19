#use this file to crawl the page, cache the content and insert data into DB

from bs4 import BeautifulSoup
import requests
import sqlite3
import os
import json
import time

BASE_URL = "https://www.anime-planet.com"
ANIME_URL = "https://www.anime-planet.com/anime"
CACHE_FILENAME = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'anime.json')
DB_FILENAME = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'var', 'anime.sqlite3')
CRAWL_DELAY = 1
CRAWL_PAGE_NUMBER = 35
class Anime:
    '''attribute:
    name : str

    description : str

    imgUrl : string
        url of image of this anime
    relatedManga : list of manga object

    tags : list of string
        list of tags for this anime
    stuffs : list of stuff object

    relatedAnime : list of anime name
    '''
    def __init__(self, name, description, imgUrl, relatedManga, tags, stuffs, relatedAnime):
        self.name = name
        self.description = description
        self.imgUrl = imgUrl
        self.relatedManga = relatedManga
        self.tags = tags
        self.stuffs = stuffs
        self.relatedAnime = relatedAnime

class Stuff:
    '''attributes:
    name : str 
    title : str
    '''
    def __init__(self, name, title):
        self.name = name
        self.title = title

class Manga:
    '''attributes:
    name : str
    description : str
    imgUrl : str
        url of the image of this manga
    '''
    def __init__(self, name, imgUrl):
        self.name = name
        self.imgUrl = imgUrl

def open_cache():
    ''' opens the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary.
    if the cache file doesn't exist, creates a new cache dictionary
    Parameters
    ----------
    None
    Returns
    -------
    The opened cache
    '''
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict

def save_cache(cache_dict):
    ''' saves the current state of the cache to disk
    Parameters
    ----------
    cache_dict: dict
        The dictionary to save
    Returns
    -------
    None
    '''
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILENAME,"w")
    fw.write(dumped_json_cache)
    fw.close() 

def getAnimeListUrl():
    '''return a url for all anime
    '''
    cacheDict = open_cache()
    if ANIME_URL in cacheDict:
        print("using cache to get list url")       
    else:
        print("using request to get list url")
        response = requests.get(ANIME_URL)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        url = soup.find('div', class_ = "pure-1 md-3-5").find('a', class_ = "button")['href']
        #only cache the needed url for this page
        cacheDict[ANIME_URL] = BASE_URL + url
        save_cache(cacheDict)

    return cacheDict[ANIME_URL]

def crawlListAndInsert():
    '''crawl each page in the listurl and load the data into database
    Returns
    -------
    list of anime object
    '''
    animeList = []
    listUrl = getAnimeListUrl()
    for pageNumber in range(1, 1 + CRAWL_PAGE_NUMBER):
        params = {
            "page" : pageNumber
        }
        pageIdentifier = listUrl + str(pageNumber)
        cacheDict = open_cache()
        if pageIdentifier in cacheDict:
            print("using cache for get ", pageIdentifier)
        else:
            print("using request for get ", pageIdentifier)
            response = requests.get(listUrl, params)
            soup = BeautifulSoup(response.text, 'html.parser')
            listTag = soup.find('ul', class_ = "cardDeck cardGrid")

            allAnimeTag = listTag.find_all('li')
            animeUrlList = []
            #for each anime li tag in the unordered list
            for animeTag in allAnimeTag:
                animeUrl = BASE_URL + animeTag.find('a')['href'] 
                animeUrlList.append(animeUrl)
            
            #only cache the required anime url list for this page
            cacheDict[pageIdentifier] = animeUrlList
            save_cache(cacheDict)
        for eachAnimeUrl in cacheDict[pageIdentifier]:
            #delay 2 second between build each crawl particular anime page
            time.sleep(CRAWL_DELAY)
            buildAnimeClass(eachAnimeUrl, animeList)

    return animeList

def buildAnimeClass(animeUrl, animeList):
    '''use input url to crawl corresponding page and build anime class,
    then append this object to given anime object list
    '''
    cacheDict = open_cache()
    if animeUrl in cacheDict:
        print("using cache to get ", animeUrl)
    else:
        print("using request to get ", animeUrl)
        response = requests.get(animeUrl).text
        cacheDict[animeUrl] = response
        save_cache(cacheDict)
    soup = BeautifulSoup(cacheDict[animeUrl], 'html.parser')
    name = soup.find('h1', itemprop = "name").text.strip()
    try:
        description = soup.find('div', itemprop = "description").find('p').text.strip()
    except:
        description = "no description"
    imgUrl = BASE_URL + soup.find("div", class_ = "mainEntry").find('img')['src']

    mangaList = []
    try:
        for mangaTag in soup.find('div', id = "tabs--relations--manga--same_franchise").find_all('div', recursive = False):
            mangaName = mangaTag.find('p', class_ = "RelatedEntry__name rounded-card__title").text
            mangaImgUrl = BASE_URL + mangaTag.find('img', class_ = "RelatedEntry__image")['src']
            mangaList.append(Manga(mangaName, mangaImgUrl))
    except:
        print(f"{animeUrl} has no related manga")
    
    tagList = []
    for tagTag in soup.find('div', class_ = "tags").find_all('li'):
        tagList.append(tagTag.find('a').text.strip())
    
    stuffList = []
    try:
        for stuffTag in (soup.find('section', class_ = "EntryPage__content__section EntryPage__content__section__staff castaff")
                        .find('div', class_ = "pure-g pure-gutter--15").find_all('div', recursive = False)):
            stuffName = stuffTag.find('div', class_ = "CharacterCard__content").find('strong').text
            stuffTitle = stuffTag.find('div', class_ = "CharacterCard__content").find('div').text
            stuffList.append(Stuff(stuffName, stuffTitle))
    except:
        print(f"{animeUrl} has no related stuff")
    
    relatedAnime = []
    try:
        for animeTag in soup.find('ul', class_ = "cardDeck cardGrid cardGrid7").find_all('li', recursive = False):
            relatedAnime.append(animeTag.find('h3', class_ = "cardName").text.strip())
    except:
        print(f"{animeUrl} has no related anime")
    animeList.append(Anime(name, description, imgUrl, mangaList, tagList, stuffList, relatedAnime))
    
def loadDB():
    '''load the crawled data to DB
    Parameters
    ----------
    animeList : list of anime object
    '''
    animeNameSet = set()
    tagSet = set()
    stuffNameSet = set()
    mangaNameSet = set()
    relatedAnimePairSet = set()
    conn = sqlite3.connect(DB_FILENAME)
    animeList = crawlListAndInsert()
    
    for anime in animeList:

        print("insert ", anime.name)
        #insert this anime to anime table
        animeNameSet.add(anime.name)
        # insertAnimeQuery = '''insert into anime values(null, '{anime.name}', '{anime.description}', '{anime.imgUrl}')'''
        insertAnimeQuery = "insert into anime values(null, ?, ?, ?)"
        conn.execute(insertAnimeQuery, (anime.name, anime.description, anime.imgUrl))
        #for each tag for this anime
        for tag in anime.tags:
            #if we already see this tag
            if tag in tagSet:
                pass
            else:
                tagSet.add(tag)
                conn.execute("insert into tags values(null, ?)", (tag,))
            conn.commit()
            insertAnimeTagQuery = '''insert into animeTag values(
                                      (select tagID from tags where content = ?),
                                      (select animeID from anime where animeName = ?)
                                      
            )'''
            conn.execute(insertAnimeTagQuery, (tag, anime.name))
        #for each stuff in this anime's stuff list
        for stuff in anime.stuffs:
            if stuff.name in stuffNameSet:
                pass
            else:
                stuffNameSet.add(stuff.name)
                conn.execute("insert into stuffs values(null, ?, ?)", (stuff.name, stuff.title))
            conn.commit()
            insertProduceQuery = '''insert into produce values(
                                     (select stuffID from stuffs where stuffName = ?),
                                     (select animeID from anime where animeName = ?)
            )
            '''
            conn.execute(insertProduceQuery, (stuff.name, anime.name))
        #for each manga in this anime's manga list
        for manga in anime.relatedManga:
            if manga.name in mangaNameSet:
                pass
            else:
                mangaNameSet.add(manga.name)
                conn.execute("insert into mangas values(null, ?, ?)", (manga.name, manga.imgUrl))
            conn.commit()
            insertRelatedMangaQuery = '''insert into relatedManga values(
                                          (select mangaID from mangas where mangaName = ?),
                                          (select animeID from anime where animeName = ?)
            )
            '''
            conn.execute(insertRelatedMangaQuery, (manga.name, anime.name))
    
    conn.commit()
    for anime in animeList:
        print("insert ", anime.name, "'s related anime")
        #for each related in this anime's related anime list
        for animeName in anime.relatedAnime:
            #if we had added this anime into database
            if animeName in animeNameSet:
                animeID1 = int(conn.execute("select animeID from anime where animeName = ?", (anime.name, )).fetchone()[0])
                animeID2 = int(conn.execute("select animeID from anime where animeName = ?", (animeName, )).fetchone()[0])
                if animeID1 > animeID2:
                    temp = animeID1
                    animeID1 = animeID2
                    animeID2 = temp
                identifier = str(animeID1) + " " + str(animeID2)
                #if we already added this pair
                if identifier in relatedAnimePairSet:
                    pass
                else:
                    relatedAnimePairSet.add(identifier)
                    conn.execute("insert into relatedAnime values(?, ?)", (animeID1, animeID2))
            #if we have not added this anime, we can't put this in db
            else:
                pass
    conn.commit()
    conn.close()

        

if __name__ == "__main__":
    loadDB()
    

    
    
    

    
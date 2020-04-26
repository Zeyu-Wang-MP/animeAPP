'''anime app main view file'''

import flask
import anime

@anime.app.route('/', methods = ['GET', 'POST'])
def index():
    if flask.request.method == 'POST':
        animeName = flask.request.form['animeName']
        if animeName == '':
            return flask.render_template('index.html')
        
        return flask.redirect(flask.url_for('search', name = animeName))
    
    return flask.render_template('index.html')

def idListToAnimeList(animeIDList):
    '''helper function
    Parameters
    ----------
    animeIDList : list of Dict {"animeID": <id>}

    Returns
    -------
    animeList : list of animeDict object
    '''
    conn = anime.model.getDB()
    #this list is list of animeDict object
    animeList = []
    for animeID in animeIDList:
        animeDict = {}

        #add this anime's information
        cursor = conn.execute(
            '''select animeName, animeDescription, imgUrl
            from anime where animeId = ?
            ''', (animeID['animeID'], )
        ).fetchone()
        animeDict['name'] = cursor['animeName']
        animeDict['description'] = cursor['animeDescription']
        animeDict['imgUrl'] = cursor['imgUrl']

        #add the this anime's tag information
        tagList = conn.execute(
            '''select T.content
            from (select tagId
                  from animeTag
                  where animeID = ?) AT
            inner join tags T on AT.tagId = T.tagID
            ''', (animeID['animeID'], )
        ).fetchall()
        tags = []
        for eachDict in tagList:
            tags.append(eachDict['content'])
        animeDict['tagList'] = tags

        #add the stuff information
        stuffDictList = conn.execute(
            '''select S.stuffName, S.title
            from (select stuffID
                  from produce 
                  where animeID = ?) P
            inner join stuffs S on P.stuffID = S.stuffID
            ''', (animeID['animeID'], )
        ).fetchall()
        animeDict['stuffList'] = stuffDictList

        #add the related manga info
        mangaDictList = conn.execute(
            '''select M.mangaName, M.imgUrl
            from (select mangaID
                  from relatedManga
                  where animeID = ?) RM
            inner join mangas M on RM.mangaID = M.mangaID
            ''', (animeID['animeID'], )
        ).fetchall()
        animeDict['MangaList'] = mangaDictList

        #add the related anime info
        relatedAnimeDictList = conn.execute(
            '''select A.animeName, A.animeDescription, A.imgUrl
            from 
               (select animeID2
                from relatedAnime
                where animeID1 = ?
                union
                select animeID1
                from relatedAnime
                where animeID2 = ?
                ) RA
            inner join anime A on RA.animeID2 = A.animeID
            ''', (animeID['animeID'], animeID['animeID'])
        ).fetchall()
        animeDict['relatedAnimeList'] = relatedAnimeDictList
        animeList.append(animeDict)

    conn.close()
    return animeList

@anime.app.route('/anime/search/<path:name>/')
def search(name):
    
    conn = anime.model.getDB()
    cursor = conn.execute(
        '''select animeID from anime 
        where animeName like ?
        ''', (name + "%", )
    )
    animeIDList = cursor.fetchall()
    conn.close()
    animeList = idListToAnimeList(animeIDList)
    resultLength = len(animeList)
    
    return flask.render_template('search.html', animeList = animeList, searchName = name, len = resultLength)

@anime.app.route('/anime/<path:name>/')
def animeName(name):
    print(name)
    conn = anime.model.getDB()
    cursor = conn.execute(
        '''select animeID from anime
        where animeName = ?
        ''', (name, )
    )
    animeIDList = cursor.fetchall()
    conn.close()
    try:
        thisAnime = idListToAnimeList(animeIDList)[0]
    except:
        flask.abort(404)
    
    return flask.render_template('anime.html', animeInfo = thisAnime)

@anime.app.route('/anime/popular/')
def popular():
    '''one page will have 20 animes
    '''
    conn = anime.model.getDB()
    page = flask.request.args.get('page', default = 0, type = int)
    cursor = conn.execute(
        '''select animeID
        from anime
        order by animeID asc
        limit ? offset ?
        ''', (20, page * 20)
    )
    animeIDList = cursor.fetchall()
    conn.close()
    animeList = idListToAnimeList(animeIDList)
    return flask.render_template('popular.html', currPage = page, animeList = animeList)

@anime.app.route('/anime/tag/<string:tag>/')
def animeTag(tag):
    '''one page will have 20 animes
    '''
    conn = anime.model.getDB()
    page = flask.request.args.get('page', default = 0, type = int)
    cursor = conn.execute(
        '''select AT.animeID
        from (
            select tagid
            from tags 
            where content = ?
        ) T inner join animeTag AT 
        on T.tagID = AT.tagID
        limit ? offset ?
        ''', (tag, 20, page * 20)
    )
    animeIDList = cursor.fetchall()
    conn.close()
    animeList = idListToAnimeList(animeIDList)
    return flask.render_template('tag.html', tag = tag, animeList = animeList, currPage = page)


@anime.app.route('/anime/stuff/<string:stuff>/')
def animeStuff(stuff):
    conn = anime.model.getDB()
    cursor = conn.execute(
        '''select P.animeID
        from (
            select stuffID
            from stuffs 
            where stuffName = ?
        ) S inner join produce P 
        on S.stuffID = P.stuffID
        ''', (stuff, )
    )
    animeIDList = cursor.fetchall()
    conn.close()
    animeList = idListToAnimeList(animeIDList)
    return flask.render_template('stuff.html', stuff = stuff, animeList = animeList)
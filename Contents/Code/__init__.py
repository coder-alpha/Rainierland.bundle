######################################################################################
#
#	Rainierland.com - v0.01
#
######################################################################################
import re

TITLE = "Rainierland"
PREFIX = "/video/rainierland"
ART = "art-default.jpg"
ICON = "icon-rainierland.png"
ICON_LIST = "icon-list.png"
ICON_COVER = "icon-cover.png"
ICON_SEARCH = "icon-search.png"
ICON_NEXT = "icon-next.png"
ICON_MOVIES = "icon-movies.png"
ICON_SERIES = "icon-series.png"
ICON_QUEUE = "icon-queue.png"
ICON_UNAV = "MoviePosterUnavailable.jpg"
BASE_URL = "http://www.rainierland.com"

######################################################################################
# Set global variables

def Start():

	ObjectContainer.title1 = TITLE
	ObjectContainer.art = R(ART)
	DirectoryObject.thumb = R(ICON_LIST)
	DirectoryObject.art = R(ART)
	VideoClipObject.thumb = R(ICON_MOVIES)
	VideoClipObject.art = R(ART)
	
	#HTTP.CacheTime = CACHE_1HOUR
	HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0'
	HTTP.Headers['Referer'] = 'http://rainierland.com/'
	HTTP.Headers['Cookie'] = '__cfduid=df95bdf30de2e9993177b68dc253bef201433472926; cf_clearance=9eaeca712f6666a69413cbcd63eaf593e2bf6581-1433472935-86400'
	
######################################################################################
# Menu hierarchy

@handler(PREFIX, TITLE, art=ART, thumb=ICON)
def MainMenu():
	
	oc = ObjectContainer(title2=TITLE)
	oc.add(DirectoryObject(key = Callback(ShowMenu, title = 'Movies / TV Shows'), title = 'Movies / TV Shows', thumb = R(ICON_MOVIES)))
	oc.add(DirectoryObject(key = Callback(Bookmarks, title="My Movie Bookmarks"), title = "My Movie Bookmarks", thumb = R(ICON_QUEUE)))
	#oc.add(PrefsObject(title = 'Preferences', thumb = R('icon-prefs.png')))
	oc.add(DirectoryObject(key = Callback(SearchQueueMenu, title = 'Search Queue'), title = 'Search Queue', summary='Search using saved search terms', thumb = R(ICON_SEARCH)))
	oc.add(InputDirectoryObject(key = Callback(Search, page_count=1), title='Search', summary='Search Movies', prompt='Search for...'))

	return oc

@route(PREFIX + "/searchQueueMenu")
def SearchQueueMenu(title):
	oc2 = ObjectContainer(title2='Search Using Term')
	#add a way to clear bookmarks list
	oc2.add(DirectoryObject(
		key = Callback(ClearSearches),
		title = "Clear Search Queue",
		thumb = R(ICON_SEARCH),
		summary = "CAUTION! This will clear your entire search queue list!"
		)
	)
	for each in Dict:
		query = Dict[each]
		#Log("each-----------" + each)
		#Log("query-----------" + query)
		if each.find(TITLE.lower()) != -1 and 'MyCustomSearch' in each and query != 'removed':
			oc2.add(DirectoryObject(key = Callback(Search, query = query, page_count=1), title = query, thumb = R(ICON_SEARCH))
		)

	return oc2

	
@route(PREFIX + "/showMenu")
def ShowMenu(title):

	data = HTTP.Request(BASE_URL)
	#Log("page ------" + data)
	
	oc2 = ObjectContainer(title2=title)
	oc2.add(DirectoryObject(key = Callback(SortMenu, title = 'Newest', page_count = 0), title = 'Newest', thumb = R(ICON_MOVIES)))
	oc2.add(DirectoryObject(key = Callback(SortMenu, title = 'Categories', page_count = 0), title = 'Categories', thumb = R(ICON_MOVIES)))
	oc2.add(DirectoryObject(key = Callback(SortMenu, title = 'Browse By Genre', page_count = 0), title = 'Browse By Genre', thumb = R(ICON_MOVIES)))
	oc2.add(DirectoryObject(key = Callback(SortMenu, title = 'Browse All', page_count = 1), title = 'Browse All', thumb = R(ICON_MOVIES)))
	
	return oc2
	

@route(PREFIX + "/sortMenu")
def SortMenu(title, page_count):
	oc = ObjectContainer(title2=title)
	
	if title == 'Browse All':
		page_data = HTML.ElementFromURL(BASE_URL + '/browse')
		elem = page_data.xpath(".//div[@class='nag cf']//div[contains(@class, 'post-')]")
		for each in elem:
			url = each.xpath(".//div[@class='thumb']//@href")[0]
			#Log("url -------- " + url)
			title = each.xpath(".//div[@class='thumb']//a//@title")[0]
			#Log("title -------- " + title)
			thumb = each.xpath(".//div[@class='thumb']//img//@src")[0]
			#Log("thumb -------- " + thumb)
			summary = each.xpath(".//div[@class='data']//p[@class='entry-summary']//text()")[0]
			#Log("summary -------- " + summary)
			
			oc.add(DirectoryObject(
				key = Callback(EpisodeDetail, title = title, url = url, thumb = thumb, summary = summary),
				title = title,
				summary = summary,
				thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback='MoviePosterUnavailable.jpg')
				)
			)
		page_n = page_data.xpath(".//div[@class='wp-pagenavi']//span[@class='pages']//text()")[0]
		oc.add(NextPageObject(
			key = Callback(ShowCategory, title = title, url = BASE_URL + '/browse', page_count = int(page_count) + 1, search=''),
			title = page_n + " >>",
			thumb = R(ICON_NEXT)
			)
		)
	else:
		page_data = HTML.ElementFromURL(BASE_URL)
		if title == 'Newest':
			elem = page_data.xpath(".//div[@class='nag cf']//div[contains(@class, 'post-')]")

			for each in elem:
				url = each.xpath(".//div[@class='thumb']//@href")[0]
				#Log("url -------- " + url)
				title = each.xpath(".//div[@class='thumb']//a//@title")[0]
				#Log("title -------- " + title)
				thumb = each.xpath(".//div[@class='thumb']//img//@src")[0]
				#Log("thumb -------- " + thumb)
				summary = each.xpath(".//div[@class='data']//p[@class='entry-summary']//text()")[0]
				#Log("summary -------- " + summary)
				oc.add(DirectoryObject(
					key = Callback(EpisodeDetail, title = title, url = url, thumb = thumb, summary = summary),
					title = title,
					summary = summary,
					thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback='MoviePosterUnavailable.jpg')
					)
				)
		elif title == 'Browse By Genre':
			elem = page_data.xpath(".//div[@class='tagcloud']//a")
			for each in elem:
				url = each.xpath(".//@href")[0]
				title = each.xpath(".//text()")[0] + ' (' + each.xpath(".//@title")[0].replace('topics','items') + ')'
				oc.add(DirectoryObject(
					key = Callback(ShowCategory, title = title, url = url, page_count = int(page_count) + 1, search=''),
					title = title
					)
				)
		elif title == 'Categories':
			elem = page_data.xpath(".//div[@id='categories-2']//ul//li")
			for each in elem:
				url = each.xpath(".//a//@href")[0]
				title = each.xpath(".//text()")[0]
				oc.add(DirectoryObject(
					key = Callback(ShowCategory, title = unicode(title), url = url, page_count = int(page_count) + 1, search=''),
					title = title
					)
				)

	return oc
	
######################################################################################
# Creates page url from category and creates objects from that page

@route(PREFIX + "/showcategory")	
def ShowCategory(title, url, page_count, search):

	oc = ObjectContainer(title2 = title)
	page_n = ''
	try:
		furl = url
		if page_count > 1:
			furl = furl + '/page/' + str(page_count)
			
		page_data = HTML.ElementFromURL(furl)
		elem = page_data.xpath(".//div[@class='nag cf']//div[contains(@class, 'post-')]")

		for each in elem:
			furl = each.xpath(".//div[@class='thumb']//@href")[0]
			#Log("furl -------- " + furl)
			title = each.xpath(".//div[@class='thumb']//a//@title")[0]
			#Log("title -------- " + title)
			thumb = each.xpath(".//div[@class='thumb']//img//@src")[0]
			#Log("thumb -------- " + thumb)
			summary = each.xpath(".//div[@class='data']//p[@class='entry-summary']//text()")[0]
			#Log("summary -------- " + summary)
			oc.add(DirectoryObject(
				key = Callback(EpisodeDetail, title = title, url = furl, thumb = thumb, summary = summary),
				title = title,
				summary = summary,
				thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback='MoviePosterUnavailable.jpg')
				)
			)
		page_n = page_data.xpath(".//div[@class='wp-pagenavi']//span[@class='pages']//text()")[0]
	except:
		url = url
	
	oc.add(NextPageObject(
		key = Callback(ShowCategory, title = title, url = url, page_count = int(page_count) + 1, search=search),
		title = page_n + " >>",
		thumb = R(ICON_NEXT)
			)
		)
	oc.add(DirectoryObject(
		key = Callback(ShowMenu, title = title),
		title = 'Back to Home Menu',
		thumb = R(ICON)
			)
		)
	
	if len(oc) == 2:
		return ObjectContainer(header=title, message='No More Videos Available')
	return oc

######################################################################################

@route(PREFIX + "/episodedetail")
def EpisodeDetail(title, url, thumb, summary):
	
	thumb = 'http://www.taylored-media.com/wp-content/uploads/2011/11/unavailable_poster.jpg'
	title = unicode(title)
	oc = ObjectContainer(title2 = title)
	
	page_data = HTML.ElementFromURL(url)
	fvidUrl = page_data.xpath(".//div[@class='screen fluid-width-video-wrapper']//script//@src")[0]
	page_data0 = HTTP.Request(BASE_URL + '/' + fvidUrl.replace('/js','js')).content
	Log(unicode(page_data0))
	try:
		page_data = page_data0
		page_data = page_data.replace('var v=\'','')
		page_data = page_data.replace('\';document.write(v);','')
		#page_data = page_data.replace('<video id="MY_VIDEO_1" class="video-js vjs-default-skin" controls autoplay preload="auto" oncontextmenu="return false" data-setup="{}">','')
		elem_data = HTML.ElementFromString(page_data)
		vidUrl = elem_data.xpath(".//source")
		for eachVid in vidUrl:
			vUrl = eachVid.xpath(".//@src")[0]
			if 'http' in vUrl:
				#Log(vUrl)
				res = '720p'
				try:
					res = eachVid.xpath(".//@data-res")[0]
				except:
					res = '720p'
				try:
					oc.add(VideoClipObject(
						url = vUrl + '&VidRes=' + res,
						title = title + ' ' + res,
						thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback='MoviePosterUnavailable.jpg'),
						summary = summary
					)
				)
				except:
					vidUrl = ""
	except:
		vidUrl = ""
	
	if len(oc) == 0:
		try:
			page_data = page_data0
			page_data = page_data.replace('%2F','/')
			page_data = page_data.replace('%3A',':')
			page_data = page_data.replace('%3F','?')
			page_data = page_data.replace('%3D','=')
			page_data = page_data.replace('%26','&')
			page_data = page_data.replace('%252C',',')
			
			#Log(page_data)
			vidUrl = page_data.split(';')
			for eachVid in vidUrl:
				vUrl = eachVid
				if 'http' in vUrl:
					
					vUrl = vUrl.replace('fmt_stream_map=18%7C','')
					vUrl = vUrl.replace('&amp','')
					res = '720p'
					try:
						oc.add(VideoClipObject(
							url = vUrl + '&VidRes=' + res,
							title = title + ' ' + res,
							thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback='MoviePosterUnavailable.jpg'),
							summary = summary
						)
					)
					except:
						vidUrl = ""
		except:
			vidUrl = ""
	
	if Check(title=title,url=url):
		oc.add(DirectoryObject(
			key = Callback(RemoveBookmark, title = title, url = url),
			title = "Remove Bookmark",
			summary = 'Removes the current movie from the Boomark que',
			thumb = R(ICON_QUEUE)
		)
	)
	else:
		oc.add(DirectoryObject(
			key = Callback(AddBookmark, title = title, url = url),
			title = "Bookmark Video",
			summary = 'Adds the current movie to the Boomark que',
			thumb = R(ICON_QUEUE)
		)
	)

	return oc
####################################################################################################
	
######################################################################################
# Loads bookmarked shows from Dict.  Titles are used as keys to store the show urls.

@route(PREFIX + "/bookmarks")	
def Bookmarks(title):

	oc = ObjectContainer(title1 = title)
	
	for each in Dict:
		url = Dict[each]
		#Log("url-----------" + url)
		if url.find(TITLE.lower()) != -1 and 'http' in url:
			page_data = HTML.ElementFromURL(url)
			movies = page_data.xpath(".//div[@class='video-object-wrapper']")
	
			for each in movies:
				#Log("Each--------" + str(movies[0]))
			
				ffurl = each.xpath("a/@href")[0].lstrip('..')
				#Log("ffurl--------" + str(ffurl))
				title = str(each.xpath(".//div//div//h1//a//text()")[0])
				#title = unicode(each.xpath("div/a/img/@alt"))
				#Log("title--------" + title)
				thumb = BASE_URL + str(each.xpath('.//a//img//@src')[1]).lstrip('..')
				#Log("thumb--------" + str(thumb))
				summary = unicode(each.xpath("div//div//p[@class='desc_body']//text()")[0])
				#Log("summary--------" + str(summary))

				oc.add(DirectoryObject(
					key = Callback(EpisodeDetail, title = title, url = ffurl, thumb = thumb, summary = summary),
					title = title,
					summary = summary,
					thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback='MoviePosterUnavailable.jpg')
					)
				)
	
	#add a way to clear bookmarks list
	oc.add(DirectoryObject(
		key = Callback(ClearBookmarks),
		title = "Clear Bookmarks",
		thumb = R(ICON_QUEUE),
		summary = "CAUTION! This will clear your entire bookmark list!"
		)
	)
	
	if len(oc) == 1:
		return ObjectContainer(header=title, message='No Bookmarked Videos Available')
	return oc

######################################################################################
# Checks a show to the bookmarks list using the title as a key for the url
@route(PREFIX + "/checkbookmark")	
def Check(title, url):
	bool = False
	url = Dict[title]
	#Log("url-----------" + url)
	if url != None and (url.lower()).find(TITLE.lower()) != -1:
		bool = True
	
	return bool

######################################################################################
# Adds a show to the bookmarks list using the title as a key for the url
	
@route(PREFIX + "/addbookmark")
def AddBookmark(title, url):
	
	Dict[title] = url
	Dict.Save()
	return ObjectContainer(header=title, message='This show has been added to your bookmarks.')
######################################################################################
# Removes a show to the bookmarks list using the title as a key for the url
	
@route(PREFIX + "/removebookmark")
def RemoveBookmark(title, url):
	
	Dict[title] = 'removed'
	Dict.Save()
	return ObjectContainer(header=title, message='This show has been removed from your bookmarks.')	
######################################################################################
# Clears the Dict that stores the bookmarks list
	
@route(PREFIX + "/clearbookmarks")
def ClearBookmarks():

	for each in Dict:
		if each.find(TITLE.lower()) != -1 and 'http' in each:
			Dict[each] = 'removed'
	Dict.Save()
	return ObjectContainer(header="My Bookmarks", message='Your bookmark list will be cleared soon.')

######################################################################################
# Clears the Dict that stores the search list
	
@route(PREFIX + "/clearsearches")
def ClearSearches():

	for each in Dict:
		if each.find(TITLE.lower()) != -1 and 'MyCustomSearch' in each:
			Dict[each] = 'removed'
	Dict.Save()
	return ObjectContainer(header="Search Queue", message='Your Search Queue list will be cleared soon.')
	
####################################################################################################
@route(PREFIX + "/search")
def Search(query, page_count):

	Dict[TITLE.lower() +'MyCustomSearch'+query] = query
	Dict.Save()
	oc = ObjectContainer(title2='Search Results')
	
	page_n = ''
	try:
		furl = BASE_URL
		if page_count > 1:
			furl = BASE_URL + '/page/' + str(page_count)
			
		data = HTTP.Request(furl + '/?s=%s' % String.Quote(query, usePlus=True), headers="").content
		page_data = HTML.ElementFromString(data)
		elem = page_data.xpath(".//div[@class='nag cf']//div[contains(@class, 'post-')]")

		for each in elem:
			furl = each.xpath(".//div[@class='thumb']//@href")[0]
			Log("furl -------- " + furl)
			title = each.xpath(".//div[@class='thumb']//a//@title")[0]
			Log("title -------- " + title)
			thumb = each.xpath(".//div[@class='thumb']//img//@src")[0]
			Log("thumb -------- " + thumb)
			summary = each.xpath(".//div[@class='data']//p[@class='entry-summary']//text()")[0]
			Log("summary -------- " + summary)
			oc.add(DirectoryObject(
				key = Callback(EpisodeDetail, title = title, url = furl, thumb = thumb, summary = summary),
				title = title,
				summary = summary,
				thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback='MoviePosterUnavailable.jpg')
				)
			)
		page_n = page_data.xpath(".//div[@class='wp-pagenavi']//span[@class='pages']//text()")[0]
	except:
		url = BASE_URL
	
	oc.add(NextPageObject(
		key = Callback(Search, query = query, page_count = int(page_count) + 1),
		title = page_n + " >>",
		thumb = R(ICON_NEXT)
			)
		)
	
	if len(oc) == 1:
		return ObjectContainer(header='Search Results', message='No More Videos Available')
	return oc
	
####################################################################################################

######################################################################################
#
#	Rainierland.com
#
######################################################################################
from io import open
import common
import updater
import shutil
import requests
import cfscrape
import re
import urllib2

global_request_timeout = 10

GOOD_RESPONSE_CODES = ['200','206']

TITLE = common.TITLE
PREFIX = common.PREFIX
ART = "art-default.jpg"
ICON = "icon-rainierland.png"
ICON_LIST = "icon-list.png"
ICON_COVER = "icon-cover.png"
ICON_SEARCH = "icon-search.png"
ICON_PLEX_SEARCH = "icon-plex-search.png"
ICON_NEXT = "icon-next.png"
ICON_MOVIES = "icon-movies.png"
ICON_SERIES = "icon-series.png"
ICON_QUEUE = "icon-queue.png"
ICON_UNAV = "MoviePosterUnavailable.jpg"
ICON_PREFS = "icon-prefs.png"
ICON_UPDATE = "icon-update.png"
ICON_UPDATE_NEW = "icon-update-new.png"
ICON_DEL = "icon-delete.png"
BASE_URL = "http://rainierland.com"

######################################################################################
# Set global variables

def Start():

	ObjectContainer.title1 = TITLE
	ObjectContainer.art = R(ART)
	DirectoryObject.thumb = R(ICON_LIST)
	DirectoryObject.art = R(ART)
	VideoClipObject.thumb = R(ICON_MOVIES)
	VideoClipObject.art = R(ART)
	
	HTTP.ClearCache()
	HTTP.Headers['User-Agent'] = "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36"
	HTTP.Headers['Referer'] = 'http://rainierland.com/'
	Log(common.TITLE + ' v.' + common.VERSION)

######################################################################################
# Menu hierarchy

@handler(PREFIX, TITLE, art=ART, thumb=ICON)
def MainMenu():

	SetupCache()

	oc = ObjectContainer(title2=TITLE)
	oc.add(DirectoryObject(key = Callback(ShowMenu, title = 'Movies / TV Shows'), title = 'Movies / TV Shows', thumb = R(ICON_MOVIES)))
	oc.add(DirectoryObject(key = Callback(Bookmarks, title="My Movie Bookmarks"), title = "My Movie Bookmarks", thumb = R(ICON_QUEUE)))
	oc.add(DirectoryObject(key = Callback(SearchQueueMenu, title = 'Search Queue'), title = 'Search Queue', summary='Search using saved search terms', thumb = R(ICON_SEARCH)))
	oc.add(InputDirectoryObject(key = Callback(Search, page_count=1), title='Search', summary='Search Movies', prompt='Search for...', thumb=R(ICON_PLEX_SEARCH)))
	#oc.add(DirectoryObject(key = Callback(updater.menu, title='Update Plugin'), title = 'Update Plugin', thumb = R(ICON_UPDATE)))
	oc.add(DirectoryObject(key = Callback(DeleteDownloadThumb), title = 'Delete Thumbnails', summary = 'Deletes all Cached Thumbnail images from the disk', thumb = R(ICON_DEL)))
	#oc.add(PrefsObject(title = 'Preferences', thumb = R(ICON_PREFS)))
	if updater.update_available()[0]:
		oc.add(DirectoryObject(key = Callback(updater.menu, title='Update Plugin'), title = 'Update (New Available)', thumb = R(ICON_UPDATE_NEW)))
	else:
		oc.add(DirectoryObject(key = Callback(updater.menu, title='Update Plugin'), title = 'Update (Running Latest)', thumb = R(ICON_UPDATE)))

	return oc

######################################################################################
@route(PREFIX + "/showMenu")
def ShowMenu(title):

	oc2 = ObjectContainer(title2=title)
	oc2.add(DirectoryObject(key = Callback(SortMenu, title = 'Newest', page_count = 0), title = 'Newest', thumb = R(ICON_MOVIES)))
	oc2.add(DirectoryObject(key = Callback(SortMenu, title = 'Categories', page_count = 0), title = 'Categories', thumb = R(ICON_MOVIES)))
	oc2.add(DirectoryObject(key = Callback(SortMenu, title = 'Browse By Genre', page_count = 0), title = 'Browse By Genre', thumb = R(ICON_MOVIES)))
	oc2.add(DirectoryObject(key = Callback(SortMenu, title = 'Browse All', page_count = 1), title = 'Browse All', thumb = R(ICON_MOVIES)))

	return oc2

######################################################################################
@route(PREFIX + "/sortMenu")
def SortMenu(title, page_count):
	oc = ObjectContainer(title2=title)

	if title == 'Browse All':
		page_data = HTML.ElementFromURL(BASE_URL + '/browse')			
		elem = page_data.xpath(".//div[@class='nag cf']//div[contains(@class, 'post-')]")
		for each in elem:
			url = each.xpath(".//div[@class='thumb']//@href")[0]
			#Log("url -------- " + url)
			ttitle = each.xpath(".//div[@class='thumb']//a//@title")[0]
			#Log("ttitle -------- " + ttitle)
			thumb = each.xpath(".//div[@class='thumb']//img//@src")[0]
			#Log("thumb -------- " + thumb)
			summary = each.xpath(".//div[@class='data']//p[@class='entry-summary']//text()")[0]
			#Log("summary -------- " + summary)

			oc.add(DirectoryObject(
				key = Callback(EpisodeDetail, title = ttitle, url = url, thumb = thumb, summary = summary),
				title = ttitle,
				summary = summary,
				thumb = Resource.ContentsOfURLWithFallback(url = '', fallback=DownloadThumbAndReturnLink(thumb))
				)
			)
		page_n = page_data.xpath(".//div[@class='wp-pagenavi']//span[@class='pages']//text()")[0]
		oc.add(NextPageObject(
			key = Callback(ShowCategory, title = title, url = BASE_URL + '/browse', page_count = int(page_count) + 1, search='', cat = title),
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

				#response = requests.get(thumb, stream=True, headers=HTTP.Headers)
				#Log("response code: " + str(response.status_code))
				#if response.status_code == 200:
				#	response.encoding = 'UTF-8'
				#	response.raw.decode_content = True
				#	mythumb = response.text

				summary = each.xpath(".//div[@class='data']//p[@class='entry-summary']//text()")[0]
				#Log("summary -------- " + summary)
				oc.add(DirectoryObject(
					key = Callback(EpisodeDetail, title = title, url = url, thumb = thumb, summary = summary),
					title = title,
					summary = summary,
					thumb = Resource.ContentsOfURLWithFallback(url = '', fallback=DownloadThumbAndReturnLink(thumb))
					)
				)
		elif title == 'Browse By Genre':
			elem = page_data.xpath(".//div[@class='tagcloud']//a")
			for each in elem:
				url = each.xpath(".//@href")[0]
				title = each.xpath(".//text()")[0] + ' (' + each.xpath(".//@title")[0].replace('topics','items') + ')'
				oc.add(DirectoryObject(
					key = Callback(ShowCategory, title = title, url = url, page_count = int(page_count) + 1, search='', cat = title),
					title = title
					)
				)
		elif title == 'Categories':
			elem = page_data.xpath(".//div[@id='categories-2']//ul//li")
			for each in elem:
				url = each.xpath(".//a//@href")[0]
				title = each.xpath(".//text()")[0]
				oc.add(DirectoryObject(
					key = Callback(ShowCategory, title = unicode(title), url = url, page_count = int(page_count) + 1, search='', cat = title),
					title = title
					)
				)

	return oc

######################################################################################
# Creates page url from category and creates objects from that page

@route(PREFIX + "/showcategory")
def ShowCategory(title, url, page_count, search, cat):

	oc = ObjectContainer(title2 = cat)
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
			ttitle = each.xpath(".//div[@class='thumb']//a//@title")[0]
			#Log("ttitle -------- " + ttitle)
			thumb = each.xpath(".//div[@class='thumb']//img//@src")[0]
			#Log("thumb -------- " + thumb)
			summary = each.xpath(".//div[@class='data']//p[@class='entry-summary']//text()")[0]
			#Log("summary -------- " + summary)
			oc.add(DirectoryObject(
				key = Callback(EpisodeDetail, title = ttitle, url = furl, thumb = thumb, summary = summary),
				title = ttitle,
				summary = summary,
				thumb = Resource.ContentsOfURLWithFallback(url = '', fallback=DownloadThumbAndReturnLink(thumb))
				)
			)
		page_n = page_data.xpath(".//div[@class='wp-pagenavi']//span[@class='pages']//text()")[0]
	except:
		url = url

	oc.add(NextPageObject(
		key = Callback(ShowCategory, title = cat, url = url, page_count = int(page_count) + 1, search=search, cat = cat),
		title = page_n + " >>",
		thumb = R(ICON_NEXT)
			)
		)
	oc.add(DirectoryObject(
		key = Callback(ShowMenu, title = cat),
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

	summary = re.sub(r'[^0-9a-zA-Z \-/.,\':+&!()]', '?', summary)
	title = title.replace('–',' : ')
	title = unicode(title)
	rthumb = DownloadThumbAndReturnLink(thumb)
	oc = ObjectContainer(title2 = title)

	page_data = HTML.ElementFromURL(url)

	try:
		fvidUrl = page_data.xpath(".//div[@class='screen fluid-width-video-wrapper']//script//@src")[0]
		if 'http' not in fvidUrl:
			fvidUrl = BASE_URL + fvidUrl
		page_data0 = HTTP.Request(fvidUrl).content
	except:
		try:
			page_data0 = page_data.xpath(".//div[@class='screen fluid-width-video-wrapper']//script//text()")[0]
		except:
			pass
			
	#Log(page_data0)

	try:
		page_data = page_data0
		if 'blogspot.com' in page_data:
			page_data = page_data.replace('var v=\'','')
			page_data = page_data.replace('\';document.write(v);','')
			elem_data = HTML.ElementFromString(page_data)
			vidUrl = elem_data.xpath(".//source")
			for eachVid in vidUrl:
				vUrl = eachVid.xpath(".//@src")[0]

				if 'http' in vUrl and 'rainierland' not in vUrl:
					#Log("vUrl ---------- " + vUrl)
					status = ' [Offline]'
					if GetHttpStatus(vUrl) in GOOD_RESPONSE_CODES:
						status = ' [Online]'
					res = '720p'
					try:
						res = eachVid.xpath(".//@data-res")[0]
					except:
						res = '720p'

					try:
						oc.add(VideoClipObject(
							url = vUrl + '&VidRes=' + res + '&VidRes=' + title + '&VidRes=' + summary + '&VidRes=' + rthumb,
							title = title + ' ' + res + status,
							thumb = R(rthumb),
							art = R(rthumb),
							summary = summary
						)
					)
					except:
						vidUrl = ""
	except:
		vidUrl = ""

	try:
		page_data = page_data0
		if 'googlevideo' in page_data and 'fmt_stream_map' not in page_data:
			page_data = page_data.replace('var v=\'','')
			page_data = page_data.replace('\';document.write(v);','')
			elem_data = HTML.ElementFromString(page_data)
			vidUrl = elem_data.xpath(".//source")
			for eachVid in vidUrl:
				vUrl = eachVid.xpath(".//@src")[0]

				if 'http' in vUrl and 'rainierland' not in vUrl:
					#Log("vUrl ---------- " + vUrl)
					status = ' [Offline]'
					if GetHttpStatus(vUrl) in GOOD_RESPONSE_CODES:
						status = ' [Online]'
					res = '720p'
					try:
						res = eachVid.xpath(".//@data-res")[0]
					except:
						res = '720p'

					try:
						oc.add(VideoClipObject(
							url = vUrl + '&VidRes=' + res + '&VidRes=' + title + '&VidRes=' + summary + '&VidRes=' + rthumb,
							title = title + ' ' + res + status,
							thumb = R(rthumb),
							art = R(rthumb),
							summary = summary
						)
					)
					except:
						vidUrl = ""
	except:
		vidUrl = ""


	try:
		page_data = page_data0
		if 'googleusercontent' in page_data:
			page_data = page_data.replace('var v=\'','')
			page_data = page_data.replace('\';document.write(v);','')
			elem_data = HTML.ElementFromString(page_data)
			vidUrl = elem_data.xpath(".//source")
			#Log("vidUrl ---------- " + vidUrl)
			for eachVid in vidUrl:
				vUrl = eachVid.xpath(".//@src")[0]
				if 'http' in vUrl and 'rainierland' not in vUrl:
					#Log("vUrl ---------- " + vUrl)
					status = ' [Offline]'
					if GetHttpStatus(vUrl) in GOOD_RESPONSE_CODES:
						status = ' [Online]'
					res = '720p'
					try:
						res = eachVid.xpath(".//@data-res")[0]
					except:
						res = '720p'
					try:
						oc.add(VideoClipObject(
							url = vUrl + '&VidRes=' + res + '&VidRes=' + title + '&VidRes=' + summary + '&VidRes=' + rthumb,
							title = title + ' ' + res + status,
							thumb = R(rthumb),
							art = R(rthumb),
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
			if 'googlevideo' in page_data and 'fmt_stream_map' in page_data:
				page_data = String.Unquote(page_data)
				#page_data = page_data.replace('%2F','/')
				#page_data = page_data.replace('%3A',':')
				#page_data = page_data.replace('%3F','?')
				#page_data = page_data.replace('%3D','=')
				#page_data = page_data.replace('%26','&')
				#page_data = page_data.replace('%252C',',')
				page_data = page_data.replace('%2C',',')
				page_data = page_data.replace('fmt_stream_map=',',')

				rem_str = Regex(r'(?s)key=ck2(.*?)http').findall(page_data)
				for rem in rem_str:
					page_data = page_data.replace(rem, '|')
					#Log("removed ----- " + rem)

				page_parts = page_data.split(';')
				fmts = page_parts[0]
				#Log(fmts)
				fmts = fmts.replace('var flv=\'fmt_list=','')
				fmts = fmts.replace('&amp','')

				fmts = fmts.split(',')
				page_data = page_parts[1]
				vidUrl = page_data.split('|')

				c=0
				for eachVid in vidUrl:
					vUrl = eachVid.replace('&amp','')
					if 'http' in vUrl and 'rainierland' not in vUrl:

						keys = fmts[c].split('/')
						#Log("vUrl ---------- " + vUrl)
						status = ' [Offline]'
						if GetHttpStatus(vUrl) in GOOD_RESPONSE_CODES:
							status = ' [Online]'
						
						res_wh = keys[1]
						res_h = res_wh.split('x')[1]
						res = 'sd'

						if res_h == '1080':
							res = '1080p'
						elif res_h == '720':
							res = '720p'

						#Log(res_wh)
						c = c+1
						try:
							oc.add(VideoClipObject(
								url = vUrl + '&VidRes=' + res + '&VidRes=' + title + '&VidRes=' + summary + '&VidRes=' + rthumb,
								title = title + ' (' + res_wh + ')' + status,
								thumb = R(rthumb),
								art = R(rthumb),
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
			page_data = page_data.replace('var i=\'','')
			page_data = page_data.replace('\';document.write(i);','')
			page_data = unicode(page_data)
			#Log(page_data)
			if 'openload.io' in page_data or 'openload.co' in page_data:
				elem_data = HTML.ElementFromString(page_data)
				vUrl = elem_data.xpath(".//@src")[0]
				#Log("vUrl ---------- " + vUrl)
				if 'http' in vUrl and 'rainierland' not in vUrl:
					status = ' [Offline]'
					if GetHttpStatus(vUrl) in GOOD_RESPONSE_CODES:
						status = ' [Online]'
					res = '720p'
					try:
						oc.add(VideoClipObject(
							url = vUrl + '&VidRes=' + res + '&VidRes=' + title + '&VidRes=' + summary + '&VidRes=' + rthumb,
							title = title + ' ' + res + status,
							thumb = Resource.ContentsOfURLWithFallback(url='', fallback=DownloadThumbAndReturnLink(thumb)),
							art = DownloadThumbAndReturnLink(thumb),
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
			if 'googlevideo' in page_data:
				#Log(page_data)
				page_data = page_data.replace('var v=\'','')
				page_data = page_data.replace('\';document.write(v);','')
				vidUrl = page_data.split(';')
				for eachVid in vidUrl:
					vUrl = eachVid
					if 'http' in vUrl and 'rainierland' not in vUrl:

						res = '720p'
						vUrl = vUrl.replace('\n','')

						if '1080p' in vUrl:
							res = '1080p'
						elif '720p' in vUrl:
							res = '720p'
						elif '480p' in vUrl:
							res = '480p'

						vUrl = vUrl.replace('var vsrc1080p = \'','')
						vUrl = vUrl.replace('var vsrc720p = \'','')
						vUrl = vUrl.replace('var vsrc480p = \'','')
						vUrl = vUrl.replace('\n','')
						vUrl = vUrl.replace('\'','')
						vUrl = vUrl.lstrip()

						#Log(vUrl)
						status = ' [Offline]'
						if GetHttpStatus(vUrl) in GOOD_RESPONSE_CODES:
							status = ' [Online]'
						try:
							oc.add(VideoClipObject(
								url = vUrl + '&VidRes=' + res + '&VidRes=' + title + '&VidRes=' + summary + '&VidRes=' + rthumb,
								title = title + ' ' + res + status,
								thumb = R(rthumb),
								art = R(rthumb),
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

######################################################################################
# Loads bookmarked shows from Dict.  Titles are used as keys to store the show urls.

@route(PREFIX + "/bookmarks")
def Bookmarks(title):

	oc = ObjectContainer(title1=title)

	for each in Dict:
		try:
			url = Dict[each]
			url.find(TITLE.lower())
		except Exception as e:
			Log.Warn(str(e))
			continue

		#Log("url-----------" + url)
		if url.find(TITLE.lower()) != -1 and 'http' in url:
			html = HTML.ElementFromURL(url)
			if html.xpath('//body[starts-with(@class, "single")]'):
				#Log('this is a movie or single episode')
				stitle = html.xpath('//h1[@class="entry-title"]/text()')[0].strip()
				summary = html.xpath('//div[starts-with(@class, "entry-content")]')[0].text_content().strip()

				oc.add(DirectoryObject(
					key=Callback(EpisodeDetail, title=stitle, url=url, thumb='', summary=summary),
					title=stitle, summary=summary
					)
				)
			else:
				#Log('this is a show list')
				ctitle = html.xpath('//title/text()')[0].split('| Rainierland')[0].strip()
				oc.add(DirectoryObject(
					key=Callback(ShowCategory, title=ctitle, url=url, page_count=1, search='', cat = title),
					title=ctitle
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
	url = Dict[title]
	#Log("url-----------" + url)
	if url != None and (url.lower()).find(TITLE.lower()) != -1:
		return True
	return False

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
	del Dict[title]
	Dict.Save()
	return ObjectContainer(header=title, message='This show has been removed from your bookmarks.', no_cache=True)

######################################################################################
# Clears the Dict that stores the bookmarks list

@route(PREFIX + "/clearbookmarks")
def ClearBookmarks():

	remove_list = []
	for each in Dict:
		try:
			url = Dict[each]
			if url.find(TITLE.lower()) != -1 and 'http' in url:
				remove_list.append(each)
		except:
			continue

	for bookmark in remove_list:
		try:
			del Dict[bookmark]
		except Exception as e:
			Log.Error('Error Clearing Bookmarks: %s' %str(e))
			continue

	Dict.Save()
	return ObjectContainer(header="My Bookmarks", message='Your bookmark list will be cleared soon.', no_cache=True)

######################################################################################
# Clears the Dict that stores the search list

@route(PREFIX + "/clearsearches")
def ClearSearches():

	remove_list = []
	for each in Dict:
		try:
			if each.find(TITLE.lower()) != -1 and 'MyCustomSearch' in each:
				remove_list.append(each)
		except:
			continue

	for search_term in remove_list:
		try:
			del Dict[search_term]
		except Exception as e:
			Log.Error('Error Clearing Searches: %s' %str(e))
			continue

	Dict.Save()
	return ObjectContainer(header="Search Queue", message='Your Search Queue list will be cleared soon.', no_cache=True)

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
				thumb = Resource.ContentsOfURLWithFallback(url = '', fallback=DownloadThumbAndReturnLink(thumb))
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
		try:
			if each.find(TITLE.lower()) != -1 and 'MyCustomSearch' in each and query != 'removed':
				oc2.add(DirectoryObject(key = Callback(Search, query = query, page_count=1), title = query, thumb = R(ICON_SEARCH))
			)
		except:
			pass

	return oc2

####################################################################################################
@route(PREFIX + "/downloadthumbandreturnlink")
def DownloadThumbAndReturnLink(url):

	try:
		filename = url.split('/')
		filename = filename[len(filename)-1]
	except:
		filename = 'temp.jpg'

	filename = 'cache_'+filename

	file_path = Core.storage.join_path(Core.bundle_path, 'Contents', 'Resources', filename)

	if (not Core.storage.file_exists(file_path)) or (Core.storage.file_size(file_path) == 0):
		try:
			resp = requests.get(url, headers=HTTP.Headers, stream=True)
			if (int(resp.status_code) == 200):
				with open(file_path, 'wb') as f:
					resp.raw.decode_content = True
					shutil.copyfileobj(resp.raw, f)
				#Log("File downloaded from : ------ " + url + " to " + downloadLocation)
			else:
				Log.Warn('Error caching thumb, HTTP Error %s' %str(resp.status_code))
		except Exception as e:
			Log.Critical("Error caching thumb - %s" %str(e))
			return ICON_UNAV
	else:
		pass
		#Log("Previous downloaded file : ------ " + url + " available " + downloadLocation)
	return filename


####################################################################################################
@route(PREFIX + "/deletedownloadthumb")
def DeleteDownloadThumb():

	tempDir = Core.storage.join_path(Core.bundle_path, 'Contents', 'Resources')

	onlyfiles = [i for i in Core.storage.list_dir(tempDir) if not Core.storage.dir_exists(Core.storage.join_path(tempDir, i)) and i.startswith('cache_')]

	msg='All Cached Thumbnail files deleted'
	for f in onlyfiles:

		file = Core.storage.join_path(tempDir, str(f))
		#Log("file --------------- " + file)

		if f.startswith('cache_'):
			try:
				Core.storage.remove( file )
				#Log("file deleted --------------- " + file)
			except:
				#Log("file NOT deleted --------------- " + file)
				msg='Cached Thumbnail files NOT deleted'
				continue

	return ObjectContainer(header="Cached Thumbnails", message=msg)
	
####################################################################################################
# Get HTTP response code (200 == good)
@route(PREFIX + '/gethttpstatus')
def GetHttpStatus(url):
	try:
		conn = urllib2.urlopen(url, timeout = global_request_timeout)
		resp = str(conn.getcode())
	except StandardError:
		resp = '0'
	#Log(url + " : " + resp)
	return resp

####################################################################################################
def SetupCache():
	"""Cookie Cache handler"""

	current_timestamp = Datetime.TimestampFromDatetime(Datetime.Now())
	if not Dict['cookies']:
		Dict['cookies'] = {'expire': '1466626689', 'current_cookies': 'na'}
	
	if current_timestamp >= int(Dict['cookies']['expire']):
		HTTP.ClearCookies()
		Log('Updating Cookies')
		cookies, ua = cfscrape.get_cookie_string(BASE_URL + '/', HTTP.Headers['User-Agent'])
		Dict['cookies']['current_cookies'] = cookies
		Log(cookies)
		r_cf_clearance = Regex(r'cf_clearance\=.*\-(\d+)\-(\d+)').search(cookies)

		if r_cf_clearance:
			date = int(r_cf_clearance.group(1))
			expire = date + int(r_cf_clearance.group(2))
		else:
			Log.Warn('SetupCache Warning: cookies have no "cf_clearance" cookie')
			expire = Datetime.TimestampFromDatetime(Datetime.Now())

		HTTP.Headers['Cookie'] = cookies
		Dict['cookies']['expire'] = '%i' %expire
		Dict.Save()
	else:
		Log('Loading Saved Cookies into Global HTTP Headers')
		HTTP.Headers['Cookie'] = Dict['cookies']['current_cookies']

		current_datetime = Datetime.FromTimestamp(int(current_timestamp))
		expire_datetime = Datetime.FromTimestamp(int(Dict['cookies']['expire']))

		Log('Time left until Cookies need to be updated = %s' %str(expire_datetime - current_datetime))
		
	#Log("Current system time: " + str(current_timestamp))
	#Log("Current cookie time: " + (Dict['cookies']['expire']))

	return

Rainierland.bundle - - - DISCONTINUED (NO LONGER MAINTAINED)
===================

This is a plugin that creates a new channel in Plex Media Server to view content indexed by the website www.rainierland.com

[Plex Support Thread] (https://forums.plex.tv/discussion/165757/rel-rainierland-channel)

System Requirements
===================

- **Plex Media Server:**
	- Tested Working:
		- Windows
		- Linux (Ubuntu) Installation of a Javascript runtime may be required
		  sudo apt-get install nodejs (installs nodejs)
- **Plex Clients:**
	- Tested Working:
		- Plex Home Theater
		- Plex/Web
		- Samsung Plex App
		- Android Kit-Kat (Samsung Galaxy S3)
		- iOS (Apple iPhone6)

How To Install
==============

- Download the latest version of the plugin.
- Unzip and rename folder to "Rainierland.bundle"
- Delete any previous versions of this bundle
- Copy Rainierland.bundle into the PMS plugins directory under your user account:
	- Windows 7, Vista, or Server 2008:
	C:\Users[Your Username]\AppData\Local\Plex Media Server\Plug-ins
	- Windows XP, Server 2003, or Home Server:
	C:\Documents and Settings[Your Username]\Local Settings\Application Data\Plex Media Server\Plug-ins
	- Mac/Linux:
        ~/Library/Application Support/Plex Media Server/Plug-ins
- Restart PMS

Known Issues
==============
- ~~Thumbnails of items are not fetched due to 302 redirection (cookie/header not being used)~~ Thumbnails are now cached into the Resource folder and can be deleted via the plugin.
- Some movies will not play, currently depending on where hosted or removed. Source is now marked with [Online]/[Offline] using a file checker.
- Bookmarks do not store thumbnails, so videos accessed by Bookmark list will have no thumbs
  - Also the video page does not host a thumbnail, so cannot parse for one
  - Bookmarks would need to be re-done to include more metadata for the thumb to be included

Acknowledgements
==============
- Thanks to [jwsolve](https://github.com/jwsolve) for inputs
- Credits to [Twoure] (https://github.com/coder-alpha/Rainierland.bundle/pull/1) for fixes and improvements [Check out his fork here] (https://github.com/Twoure/Rainierland.bundle)

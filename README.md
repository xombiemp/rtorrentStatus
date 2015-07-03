# rtorrentStatus
This script will return the status of a torrent in rTorrent. It will match the status that ruTorrent gives because the logic is taken from ruTorrent.  
The script relies on the xmlrpc utility that comes with the xmlrpc-c source code. http://xmlrpc-c.sourceforge.net/doc/xmlrpc.html Compile and install it from the xmlrpc-c/tools/xmlrpc directory.  
This script takes a torrent hash as an argument and will return the status for that torrent.

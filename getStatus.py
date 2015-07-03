#!/usr/bin/python

import sys
import subprocess
import re
import math

# this script utilizes the xmlrpc utility to make the rpc calls http://xmlrpc-c.sourceforge.net/doc/xmlrpc.html
# set the location of your rtorrent rpc endpoint here
rpcEndpoint = 'localhost/rutorrent/plugins/httprpc/action.php'

def saveBash(cmd):
  p = subprocess.Popen(cmd, shell=True, executable="/bin/bash", stdout=subprocess.PIPE)
  out = p.stdout.read().strip()
  return out  #This is the stdout from the shell command

def xmlrpc(cmd, torrentHash):
  rawResult = saveBash("xmlrpc " + rpcEndpoint + " " + cmd + " " + torrentHash)
  result = re.split('Result:\n\n.+?:\s', rawResult)
  if (result[1].startswith("'")) and (result[1].endswith("'")):
    return result[1][1:-1]
  else:
    return result[1]

def setGlobals(torrentHash):
  global dStatus
  global is_open
  global get_state
  global is_active
  global get_hashing
  global is_hash_checking
  global message
  global get_completed_chunks
  global get_hashed_chunks
  global get_size_chunks
  dStatus = { 'started' : 1, 'paused' : 2, 'checking' : 4, 'hashing' : 8, 'error' : 16 }
  is_open = xmlrpc('d.is_open', torrentHash)
  get_state = xmlrpc('d.state', torrentHash)
  is_active = xmlrpc('d.is_active', torrentHash)
  get_hashing = xmlrpc('d.hashing', torrentHash)
  is_hash_checking = xmlrpc('d.is_hash_checking', torrentHash)
  message = xmlrpc('d.message', torrentHash)
  get_completed_chunks = xmlrpc('d.completed_chunks', torrentHash)
  get_hashed_chunks = xmlrpc('d.chunks_hashed', torrentHash)
  get_size_chunks = xmlrpc('d.size_chunks', torrentHash)

def getState():
  # https://github.com/Novik/ruTorrent/blob/master/js/rtorrent.js#L1003
  state = 0
  if (is_open != '0'):
    state |= dStatus['started']
    if (get_state=='0') or (is_active=='0'):
      state |= dStatus['paused']
  if (get_hashing != '0'):
    state |= dStatus['hashing']
  if (is_hash_checking != '0'):
    state |= dStatus['checking']
  if (len(message)) and (message != "Tracker: [Tried all trackers.]"):
    state |= dStatus['error']
  return state

def getCompleted():
  # https://github.com/Novik/ruTorrent/blob/master/js/rtorrent.js#L1021
  chunks_processing = get_completed_chunks if is_hash_checking == '0' else get_hashed_chunks
  done = int(math.floor((float(chunks_processing) / float(get_size_chunks)) * 1000))
  return done

def main():
  args = sys.argv[1:]
  if not args or len(args[0]) != 40 :
    print 'usage: ' + sys.argv[0] + ' torrentHash'
    sys.exit(1)

  setGlobals(args[0])

  # https://github.com/Novik/ruTorrent/blob/master/js/webui.js#L1660
  state = getState()
  completed = getCompleted()
  status = ""
  if (state & dStatus['checking']):
    status = "Checking"
  elif (state & dStatus['hashing']):
    status = "Queued"
  elif (state & dStatus['started']):
    if (state & dStatus['paused']):
      status = "Pausing"
    else:
      status = "Seeding" if completed == 1000 else "Downloading"
  if (completed == 1000) and (status == ""):
    status = "Finished"
  if (completed < 1000) and (status == ""):
    status = "Stopped"

  print 'is_open: ' + is_open
  print 'get_state: ' + get_state
  print 'is_active: ' + is_active
  print 'get_hashing: ' + get_hashing
  print 'is_hash_checking: ' + is_hash_checking
  print 'message: ' + message
  print 'get_completed_chunks: ' + get_completed_chunks
  print 'get_hashed_chunks: ' + get_hashed_chunks
  print 'get_size_chunks: ' + get_size_chunks
  print 'state: ' + str(state)
  print 'completed: ' + str(completed)
  print 'status: ' + status

if __name__ == '__main__':
  main()
	
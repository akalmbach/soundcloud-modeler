import soundcloud, urllib2, sys, string, os, wavifier, Queue, time, codecs
from unidecode import unidecode

fail_tracks = []

def loadFails(fails_fn):
  f = open(fails_fn, 'r')
  for line in f:
    try:
      fail_tracks.append(int(line[:-1]))
    except:
      continue
    
def saveFails(fails_fn):
  f = open(fails_fn, 'w')
  for track in fail_tracks:
    f.write(str(track) + "\n")
  f.close()
   
class Log(object):
  def __init__(self, name, path):
    self.total_wav_bytes = 0
    self.total_time_ms = 0
    self.name = fnameSafify(name)
    self.path = pathSlash(path)
    if not os.path.exists(path):
      os.makedirs(path)
    self.entries = {}
    
  def ustr(self):
    out = u'TrackID\tTrackTitle\tArtistID\tArtistName\tWavFile\tMFCCsFile\tWordsFile\tURL\tParentID\n'
    for entry in self.entries:
      out += self.entries[entry].ustr()
    out += "\n"
    out += "Path: " + str(self.path) + "\tBytes: " + str(self.total_wav_bytes) + "\t ms: " + str(self.total_time_ms)
    out += "\n Minutes: " + str(self.total_time_ms/(1000*60))
    return out
    
  def wavFilesStr(self):
    out = ""
    for entry in self.entries:
      if self.entries[entry].wav_fn != None:
	out += self.path + self.entries[entry].wav_fn + " "
      else:
	print "Skipping " + str(self.entries[entry].track.id)
    return out
      
  def wordsFilesStr(self):
    out = ""
    for entry in self.entries:
      if self.entries[entry].words_fn != None:
	out += self.path+self.entries[entry].words_fn + " "
      else:
	print "Skipping " + str(self.entries[entry].track.id)
    return out
  
  def mfccsFilesStr(self):
      out = ""
      for entry in self.entries:
	if self.entries[entry].mfccs_fn != None:
	  out += self.path+self.entries[entry].mfccs_fn + " "
	else:
	  print "Skipping " + str(self.entries[entry].track.id)
      return out
	
  def sigmaStr(self):
    out = self.ustr()
    out+= "\n"
    for entry in self.entries:
      out += "\n"
      out += self.entries[entry].sigmaStr()
    return out
    
  def genMFCCs(self, vocab_fn):
    for entry in self.entries:
      if self.entries[entry].mfccs_fn == None:
	mfcc_fn = fnameSafify(self.entries[entry].wav_fn[:-4] + "_" + vocab_fn[:-4] + "_MFCC_RAW.txt")
	cmd = "./MFCC/genMFCC " + self.path + mfcc_fn + " " + self.path+self.entries[entry].wav_fn + " &"
	print cmd
	os.system(cmd)
	self.entries[entry].mfccs_fn = mfcc_fn
    raw_input(">>")
    for entry in self.entries:
      if self.entries[entry].mfccs_fn != None:
	kmfccs_fn = self.entries[entry].wav_fn[:-4] + "KMFCCs.txt"
	words_fn = self.entries[entry].wav_fn[:-4] + "_WORDS.txt"
	cmd = "./applyDict " + vocab_fn + " " + self.path+self.entries[entry].mfccs_fn + " " + self.path+kmfccs_fn + " " + self.path+words_fn + " 100000 > /dev/null &"
	print cmd
	os.system(cmd)
	self.entries[entry].words_fn = words_fn
    raw_input(">>")
    cmd = "cat " + self.wordsFilesStr() + "> " + self.path + self.name + "_ALLWORDS.txt"
    print cmd
    os.system(cmd)
  
  def save(self, extended=False):
    f = codecs.open(self.path + self.name + ".txt", encoding='utf-8', mode='w')
    if not extended:
      f.writelines(self.ustr())
    else:
      f.writelines(self.sigmaStr())
    
  def addEntry(self, newEntry, bytes):
    self.entries[newEntry.track.id] = newEntry
    self.total_wav_bytes += bytes
    self.total_time_ms += newEntry.track.duration
    
  def __add__(self, other):
    """assumes no duplicates for now!"""
    n = Log()
    n.total_time_ms = self.total_time_ms + other.total_time_ms
    n.total_wav_bytes = self.total_wav_bytes + other.total_wav_bytes
    n.entries = dict(self.entries + other.entries)
    n.name = self.name
    n.path = self.path

class LogEntry(object):
  def __init__(self, track, parent=None):
    self.track = track
    self.wav_fn = None
    self.mp3_fn = None
    self.artist = client.get('/users/'+str(track.user_id))
    self.followings = client.get('/users/'+str(self.artist.id) +'/followings')
    self.parent = parent
    self.generatingQuery = None
    self.mfccs_fn = None
    self.words_fn = None
        
  def ustr(self):
    out = str(self.track.id) + "\t"
    out += self.track.title + "\t"
    out += str(self.artist.id) + "\t"
    out += self.artist.full_name + "\t"
    out += str(self.wav_fn) + "\t"
    out += str(self.mfccs_fn) + "\t"
    out += str(self.words_fn) + "\t"
    out += str(self.track.permalink_url) + "\t"
    out += str(self.parent.id) + "\n"
    return out
    
client = soundcloud.Client(client_id='ef553ea9bbb7541955873e5569f0bc90')
    
def fnameSafify(fname_unsafe):
  safechars = '_-.' + string.digits + string.ascii_letters
  allchars = string.maketrans('', '')
  deletions = ''.join(set(allchars) - set(safechars))
  fname_safe = ''.join(c for c in fname_unsafe if c in safechars)
  fname_safe = unidecode(fname_safe)
  return fname_safe

def BtoMB(B):
  return B >> 20
  
def pathSlash(path):
  if (path[-1] != '/'):
    path += '/'
  return path
  
def download(url, filename):
  print url
  u = urllib2.urlopen(url)
  f = open(filename, 'wb')
  meta = u.info()
  file_size = int(meta.getheaders("Content-Length")[0])
  print "Downloading: %s Bytes: %s" % (filename, file_size)
  file_size_dl = 0
  block_sz = 8192
  while True:
    buffer = u.read(block_sz)
    if not buffer:
      break
    file_size_dl += len(buffer)
    f.write(buffer)
    status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
    status = status + chr(8)*(len(status)+1)
    print status,
  f.close()
  
def getTrack(track, path):
  if any(fail == track.id for fail in fail_tracks):
    print "Previously Failed " + track.title + ". Skipping"
    return [None, 0]
  if not track.downloadable:
    print track.title + " is not downloadable. Skipping."
    return [None, 0]
  print "Downloading " + track.title
  url = track.permalink_url + "/download"
  fname = fnameSafify(track.title) + ".mp3"
  if not os.path.isfile(path + fname):
    download(url, path + fname)
  wav = wavifier.wavify(path + fname)
  if (wav[1] > os.stat(path + fname).st_size):
    thisLog = LogEntry(track)
    thisLog.mp3_fn = path + fname
    thisLog.wav_fn = wav[0].split("/")[-1]
    return [thisLog, wav[1]]
  else:
    print "ERROR CONVERTING! DISCARDING TRACK"
    fail_tracks.append(track.id)
    os.system("rm " + wav[0] + " " + path + fname)
    return [None, 0]
   
def doVocabQuery(vocab, path, mygenres, dictSizeMB, maxLengthMin):
  reps = 0
  maxLength = maxLengthMin*60*1000
  while BtoMB(vocab.total_wav_bytes) < dictSizeMB:
    for genre in mygenres:
      if BtoMB(vocab.total_wav_bytes) >= dictSizeMB:
	break
      [track] = client.get('/tracks', genres=genre, duration={'to' : maxLength}, filter='downloadable', order='hotness', limit=1, offset=reps)
      [entry, size] = getTrack(track, path)
      if entry != None:
	vocab.addEntry(entry, size)
	print "Got " + str(len(vocab.entries)) + " tracks (" + str(BtoMB(vocab.total_wav_bytes)) + " MB)."
	reps += 1
  return vocab
	    
def createVocab(path, vocabname, genres, k):
  path = pathSlash(path)
  vocab = Log("_".join(genres)+ "_K" + str(k) + "_vocab", path)
  vocab = doVocabQuery(vocab, path, genres, 300, 10)
  cmd = "./MFCC/genDict " + path + vocabname + " " + str(k) + " " + vocab.wavFilesStr()
  print cmd
  os.system(cmd)
  return vocab
	     
def doBFSQuery(path, name, maxReps, maxLengthMin, totalLengthMin):
  path = pathSlash(path)
  users = client.get('/users', q=name)
  maxLength = maxLengthMin*60*1000
  totalLength = totalLengthMin*60*1000
  log = Log(name + str(totalLengthMin) + "", path)
  for user in users:
    print unidecode(user.full_name)
    if unidecode(user.full_name) == name:
      print "Found Root User: " + user.full_name
      log = BFSQueryHelper(path, user, log, maxReps, maxLength, totalLength)
      return log
  return None

def BFSQueryHelper(path, user, log, maxReps, maxLength, totalLength):
  q = Queue.Queue()
  i = 0
  parent = user
  while(log.total_time_ms < totalLength):
    print "Expanding User: " + user.full_name
    tracks = client.get('/users/'+str(user.id)+'/tracks')
    reps = 0
    
    for track in tracks:
      if (track.duration <= maxLength and track.downloadable):
	[entry, size] = getTrack(track, path)
	if entry != None:
	  entry.parent = parent
	  log.addEntry(entry, size)
	  i += 1
	if i >= maxReps or log.total_time_ms >= totalLength:
	  break
	
    followings = client.get('/users/'+str(user.id)+'/followings')
    print unidecode(log.ustr())
    for child in followings:
      if child.full_name == "":
	continue
      q.put([child, user])
      
    if q.empty():
      break
    [user, parent] = q.get()    
  return log

import os, math, array, codecs, sys
from matUtils import *

def runLDA(n, k, allWords_fn):
  f = open(allWords_fn, 'r')
  l = f.readlines()
  f.close()
  docs = len(l)
  l.insert(0, str(docs) + '\n')
  f = open(allWords_fn, 'w')
  f.writelines(l)
  cmd = "/home/arnold/Projects/soundcloud-modeler/GibbsLDA++-0.2/src/lda -est -alpha 0.1 -beta 0.1"
  cmd += " -ntopics " + str(k)
  cmd += " -niters " + str(n)
  cmd += " -savestep " + str(n) + " -dfile " + allWords_fn
  print cmd
  os.system(cmd)


def readTheta(filename):
  f = open(filename, 'r')
  theta = []
  for doc in f:
    topics_string = doc.split(" ")
    topics_distro = []
    sum = 0
    for topic in topics_string[:-1]:
      topics_distro.append(float(topic))
      sum += topics_distro[-1]
    for i in range(0, len(topics_distro)):
      topics_distro[i] /= sum
    theta.append(topics_distro)
  f.close()
  return theta
  
def genGraph(theta, log):
  all = []
  trxtr = genTracksxTracks(theta)
  print "tracks x tracks"
  printMat(trxtr, sys.stdout)
  
  toxto = genTopicsxTopics(theta)
  print "topics x topics"
  printMat(toxto, sys.stdout)
  
  axa = genArtistsxArtists(log)
  print "artists x artists"
  printMat(axa, sys.stdout)
  
  trxa = genTracksxArtists(log)
  print "tracks x artists"
  printMat(trxa, sys.stdout)
  
  axtr = transposeMat(trxa)
  print "artists x tracks"
  printMat(axtr, sys.stdout)
  
  axto = genArtistsxTopics(log, theta)
  print "artists x topics"
  printMat(axto, sys.stdout)
  
  toxa = transposeMat(axto)
  print "topics x artists"
  printMat(toxa, sys.stdout)
  
  trxto = theta
  print "tracks x topics"
  printMat(trxto, sys.stdout)
  
  toxtr = transposeMat(trxto)
  print "topics x tracks"
  printMat(toxtr, sys.stdout)
  '''
    | to | tr | a
  to|
  tr|
   a|
  '''
  nodes = len(theta[0]) + len(theta) + len(log.artists)
  adj = []
  for i in range(0, nodes):
    adj.append(array.array('f',(0.0,)*(nodes)))
  adj = copyToRegion(toxto, adj, 0, 0)
  adj = copyToRegion(toxtr, adj, 0, len(theta[0]))
  adj = copyToRegion(toxa, adj, 0, len(theta[0]) + len(theta))
  adj = copyToRegion(trxto, adj, len(theta[0]), 0)
  adj = copyToRegion(trxtr, adj, len(theta[0]), len(theta[0]))
  adj = copyToRegion(trxa, adj, len(theta[0]), len(theta[0])+ len(theta))
  adj = copyToRegion(axto, adj, len(theta[0]) + len(theta), 0)
  adj = copyToRegion(axtr, adj, len(theta[0]) + len(theta), len(theta[0]))
  adj = copyToRegion(axa, adj, len(theta[0])+len(theta), len(theta[0])+len(theta))
  labels = []
  for i in range(0, len(theta[0])):
    labels.append({'title':'t'+str(i), 'trackid':i, 'r':50, 'g':50, 'b':50, 'a':0.75})
    labels.append({'id':i, 'type':'topic', 'label':'T'+str(i), 'link':'none', 'name':'Topic ' + str(i)})
  for entry in log.entries:
    track = log.entries[entry].track
    labels.append({'title': '   ', 'trackid':track.id, 'r':180, 'g':20, 'b':20, 'a':0.8})
    labels.append({'id':track.id, 'type':'track', 'label':'    ', 'link':track.permalink_url, 'name':track.title})
  for artist in log.artists:
    labels.append({'id':artist.id, 'type':'artist', 'label':artist.username, 'link':artist.permalink_url, 'name':artist.username})
  return adj, labels
  
def genTracksxTracks(theta):
  adj = []
  for i in range(0, len(theta)):
    adj.append(array.array('f',(0.0,)*(len(theta))))
  return adj
  
def genTopicsxTopics(theta):
  adj = []
  for i in range(0, len(theta[0])):
    adj.append(array.array('f',(0.0,)*(len(theta[0]))))
  return adj
  
def genArtistsxArtists(log):
  adj = []
  for i in range(0, len(log.artists)):
    adj.append(array.array('f',(0.0,)*(len(log.artists))))
  for i in range(0, len(log.artists)):
    for j in range(0, len(log.artists)):
      if any(log.entries[entry].artist.id == log.artists[i].id and 
      log.entries[entry].parent.id == log.artists[j].id
      for entry in log.entries):
	adj[i][j] = 1.0
	print "found parent"
  return adj

def genTracksxArtists(log):
  adj = []
  for i in range(0, len(log.entries)):
    adj.append(array.array('f',(0.0,)*(len(log.artists))))
  for i in range(0, len(log.entries)):
    for j in range(0, len(log.artists)):
      if log.entries.values()[i].artist.id == log.artists[j].id:
	print "hit track artist"
	adj[i][j] = 1.0
  return adj
  
def genArtistsxTopics(log, theta):
  adj = []
  for i in range(0, len(log.artists)):
    adj.append(array.array('f', (0.0,)*len(theta[0])))
  return adj
  
def thetaToGraph(th):
  numTopics = len(th[0])
  numDocs = len(th)
  adj = []

  for i in range(0, numTopics+numDocs):
    adj.append(array.array('f',(0.0,)*(numTopics+numDocs)))
  print "T:" + str(numTopics)
  print "D:" + str(numDocs)
  print "Theta (" + str(len(th)) + " X " + str(len(th[0])) + ")"
  print "Adj (" + str(len(adj)) + " X " + str(len(adj[0])) + ")"
  for i in range(0, numTopics+numDocs):
    for j in range(0, numTopics+numDocs):
      print "i,j " + str(i) + "," + str(j)
      if i < numTopics and j < numTopics:
	print "Topic x Topic"
	adj[i][j] = 0
      elif i >= numTopics and j >= numTopics:
	print "Doc x Doc"
	adj[i][j] = 0
      elif i >= numTopics and j < numTopics:
	print "Doc x Topic"
	adj[i][j] = th[i-numTopics][j]
      else:
	# i < numTopics and j >= numTopics
	print "Topic x Doc"
	adj[i][j] = th[j-numTopics][i]
  return adj
  
def loadLog(log_fn):
  f = codecs.open(log_fn, encoding='utf-8', mode='r')
  l = f.readlines()
  artists = []
  parents = []
    
  for line in l[1:]:
    if line == '\n':
      break
    split = line.split("\t")
    artists.append(int(split[2]))
    parents.append(int(split[-1]))
  
  return [artists, parents]

def parentsToSigma(p, a):
  S = []
  for i in range(0, len(a)):
    S.append([])
    for j in range(0, len(a)):
      if a[i] == a[j]:
	S[-1].append(1.0)
      elif a[i] == p[j]:
	S[-1].append(0.8)
      else:
	S[-1].append(0.0)
  return S
 

def sameArtistSigma(artists):
  S = []
  for artist1 in artists:
    S.append([])
    for artist2 in artists:
      if artist1 == artist2:
	S[-1].append(1)
      else:
	S[-1].append(0)
  return S
   
def addSigmaToGraph(sigma, adj, numTopics):
  if numTopics + len(sigma) != len(adj):
    print "Dimension Mismatch!"
    print "Sigma " + str(len(sigma))
    print "Num topics " + str(numTopics)
    print "Adj " + str(len(adj))
    return None
  for i in range(0, len(sigma)):
    for j in range(0, len(sigma)):
      adj[i+numTopics][j+numTopics] += sigma[i][j]
  return adj
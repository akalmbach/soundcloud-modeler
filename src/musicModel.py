import os, math, array, codecs
from matUtils import *

def runLDA(n, k, allWords_fn):
  f = open(allWords_fn, 'r')
  l = f.readlines()
  f.close()
  docs = len(l)
  l.insert(0, str(docs) + '\n')
  f = open(allWords_fn, 'w')
  f.writelines(l)
  cmd = "~/Research/arnold/GibbsLDA++-0.2/src/lda -est -alpha 0.1 -beta 0.1"
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
  
def readPhiIntoTheta(filename, numTopics):
  f = open(filename, 'r')
  theta = []
  for doc in f:
    topics_string = doc.split(",")
    topics_distro = array.array('i',(0,)*numTopics)
    norm_distro = []
    sum = 0
    for topic in topics_string[:-1]:
      if topic >= numTopics:
	print topic
      topics_distro[int(topic)] += 1
      sum += 1
    for i in range(0, len(topics_distro)):
      norm_distro.append(topics_distro[i] / float(sum))
    for i in range(0, len(norm_distro)):
      if norm_distro[i] < 0.0001:
	norm_distro[i] = 0.0001
    theta.append(norm_distro)
  f.close()
  return theta
  
def KLDiv(theta):
  #NB the matrix is symmetric which means I'm doing twice the work I have to here!
  div = []
  for P in theta:
    div.append([])
    for Q in theta:
      lsum = 0
      rsum = 0
      for i in range(0, len(P)):
	lsum += math.log(P[i]/Q[i])*P[i]
	rsum += math.log(Q[i]/P[i])*Q[i]
      div[-1].append(lsum + rsum)
  return div
  
def divToPercent(div):
  maxsofar = 0
  for row in div:
    for col in row:
      if col > maxsofar:
	maxsofar = col
  percent = div
  for i in range(0, len(div)):
    for j in range(0, len(div[i])):
      percent[i][j] = float(div[i][j])/maxsofar
  return percent  
  
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
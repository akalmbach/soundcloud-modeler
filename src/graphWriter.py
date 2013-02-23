import codecs, pystache
from matUtils import *

def loadTrackIds(log_fn):
  f = codecs.open(log_fn, encoding='utf-8', mode='r')
  lines = f.readlines()
  tracks = []
  for line in lines[1:]:
    if line == "\n":
      return tracks
    else:
      track = {}
      split = line.split("\t")
      track['trackid'] = int(split[0])
      track['title'] = split[1]
      track['url'] = split[-2]
      track['r'] = 180
      track['g'] = 20
      track['b'] = 20
      track['a'] = 0.8
      tracks.append(track)
  print "Error in reading log file"
  return None
  
  
def writePage(index_fn, g_fn, tpl_fn, log_fn, num_topic_nodes):
  # Add one node per topic
  nodes = []
  for i in range(0, num_topic_nodes):
    topic_node_dict = {'title':"t"+str(i), 'trackid':i, 'r':50, 'g':50, 'b':50, 'a':0.75}
    nodes.insert(0, topic_node_dict)
  
  # Get the track nodes
  nodes.extend(loadTrackIds(log_fn))
  
  # Read in the adjacency matrix
  adjs = []
  G = readMat(g_fn)
  for i in range(0, len(G)):
    edges = []
    for j in range(0, len(G[0])):
      if G[i][j] > 0.25:
	edge_dict = {'node_j_id':nodes[j]['trackid'], 'weight':G[i][j]}
	edges.append(edge_dict)
    adj_dict = {'node_i_id':nodes[i]['trackid'], 'edge':edges}
    adjs.append(adj_dict)
      
  tpl = "".join(open(tpl_fn, 'r').readlines())
  page = pystache.render(tpl, {'canvas_width':1280, 'canvas_height':500, 'node':nodes, 'adjacency':adjs})
  f = codecs.open(index_fn, encoding='utf-8', mode='w')
  f.writelines(page)
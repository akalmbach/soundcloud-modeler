import pystache, codecs

def writePage(index_fn, adj, labels, tpl_fn):
  adjs = []
  for i in range(0, len(adj)):
    edges = []
    for j in range(0, len(adj[0])):
      if adj[i][j] > 0.25:
	edge_dict = {'node_j_id':labels[j]['trackid'], 'weight':adj[i][j]}
	edges.append(edge_dict)
    adj_dict = {'node_i_id':labels[i]['trackid'], 'edge':edges}
    adjs.append(adj_dict)
      
  tpl = "".join(open(tpl_fn, 'r').readlines())
  page = pystache.render(tpl, {'canvas_width':1280, 'canvas_height':500, 'node':labels, 'adjacency':adjs})
  f = codecs.open(index_fn, encoding='utf-8', mode='w')
  f.writelines(page)
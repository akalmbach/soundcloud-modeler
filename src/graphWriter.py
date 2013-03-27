import pystache, codecs

def writePage(index_fn, adj, labels, tpl_fn):
  adjs = []
  for i in range(0, len(adj)):
    edge_list = []
    for j in range(0, len(adj[0])):
      if adj[i][j] > 0.25:
	edge_dict = {'j_id':labels[j]['id'], 'weight':adj[i][j]}
	edge_list.append(edge_dict)
    edges_dict = {'i_id':labels[i]['id'], 'edge':edge_list}
    edges.append(edges_dict)
      
  tpl = "".join(open(tpl_fn, 'r').readlines())
  page = pystache.render(tpl, {'canvas_width':1280, 'canvas_height':500, 'node':labels, 'edges':edges})
  f = codecs.open(index_fn, encoding='utf-8', mode='w')
  f.writelines(page)
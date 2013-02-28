<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN"
  "http://www.w3.org/TR/html4/strict.dtd">

<html lang="en">
  <head>
      <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
  </head>
  <body>
  <canvas id="viewport" width="{{canvas_width}}" height="{{canvas_height}}"></canvas>

  <script src="./resources/jquery.min.js"></script>
  <script src="./resources/arbor.js"></script>
  <script src="./resources/graphics.js"></script>
  <script src="./renderer.js"></script> 
  <script src="http://connect.soundcloud.com/sdk.js"></script>

  <script language="javascript" type="text/javascript">
    SC.initialize({
      client_id: 'ef553ea9bbb7541955873e5569f0bc90'
    });
    var sys = arbor.ParticleSystem(500, 250, 0.98);
    sys.parameters({gravity:true});
    sys.renderer = Renderer("#viewport", SC);
    
    var data = {
      nodes:{
	{{#node}}
	{{trackid}}:{'color':'rgba({{r}},{{g}},{{b}},{{a}})',
	  'shape':'rect',
	  'label':'{{title}}',
	  'link':'{{url}}'},
	{{/node}}
      },
      edges:{
	{{#adjacency}}
	{{node_i_id}}:{
	  {{#edge}}
	  {{node_j_id}}:{'weight':{{weight}}},
	  {{/edge}} },
	{{/adjacency}}
      }
    };
  
  sys.graft(data);
  </script>
  </body>
</html>
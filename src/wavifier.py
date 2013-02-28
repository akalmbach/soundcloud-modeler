import sys, os, glob

def wavify(location):
  path = location.rsplit("/", 1)[0] + "/"
  in_fn = location.rsplit("/", 1)[1]
  out_fn = "_" + in_fn.rsplit(".", 1)[0] + ".wav"
  if not os.path.isfile(path + out_fn):
    tmp_fn = out_fn[1:-3]+"mp3"
    os.system("cp " + path + in_fn + " " + path + tmp_fn)
    tmp_fn2 = "tmp" + out_fn
    print "Attempting to convert " + path + in_fn + "to a wav file ( " + path + tmp_fn2 + " )."
    st = os.system("avconv -i "+ path + tmp_fn + " " + path + tmp_fn2)
    print "avconv returned " + str(st)
    size = audioFormat(path + tmp_fn2, path + out_fn)
    os.system("rm " + path + tmp_fn2 + " " + path + tmp_fn)
  else:
    size = os.stat(path + out_fn).st_size
    st = 0
  return [path + out_fn, size, st]
  
def audioFormat(in_fn, out_fn):
  # make sure its 44kHz & single channel
  if not os.path.isfile(out_fn):
    print "Mixing down to 44.1 kHz Mono"
    os.system("sox -r 44100 " + in_fn + " " + out_fn + " channels 1")
  try:
    size = os.stat(out_fn).st_size
  except:
    size = None
  return size

def checkIfWavFile(filename):
  try:
    f = open(filename, 'r')
  except:
    print "Failed to open " + filename
    return False
  for i in range(0, 5):
    line = f.readline()
    if line.upper().find("WAV") > 0:
      print "Found a wav file"
      return True
  return False

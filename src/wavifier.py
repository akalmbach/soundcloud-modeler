import sys, os, glob

def wavify(argv):
  source = argv.rsplit("/", 1)[1]
  out = "_" + source[:-3] + "wav"
  path = argv.rsplit("/", 1)[0] + "/"
  print "path: " + path + " input: " + source + " output: " + out
  if not os.path.isfile(path + out):
    if (source[-3:] == "mp3"): 
	# convert the input mp3 to a wav file
	os.system("lame --decode " + path + source + " ./tmp.wav")
    elif (source[-3:] == "wav"):
	os.system("cp " + path + source + " tmp.wav")
    else:
	print "Only formats mp3 and wav files"
	sys.exit()

    # make sure its 44kHz & single channel
    os.system("sox -r 44100 tmp.wav " + path + out + " channels 1")
    # get rid of the temporary file
    os.system("rm " + "./tmp.wav")
  size = None
  try:
    size = os.stat(path + out).st_size
  except:
    pass
  return [path + out, size]

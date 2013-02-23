import math, array

def readMat(filename):
  f = open(filename, 'r')
  mat = []
  for line in f.readlines():
    this_row = []
    split = line.split(" ")
    for entry in split:
      if entry == '\n':
	continue
      if entry[-1] == '\n':
	this_row.append(float(entry[:-1]))
      else:
	this_row.append(float(entry))
    mat.append(this_row)
  return mat
  
def printMat(mat, filename):
  f = open(filename, 'w')
  for doc1 in mat:
    for doc2 in doc1:
      f.write(str(doc2) + " ")
    f.write("\n")
    
def scaleMat(mat, scale):
  for i in range(0, len(mat)):
    for j in range(0, len(mat[i])):
      mat[i][j] *= scale
  return mat
  
def greaterThanThresh(mat, value):
  for i in range(0, len(mat)):
    for j in range(0, len(mat[i])):
      if mat[i][j] < value:
	mat[i][j] = 0
  return mat
      
def addMats(mat1, mat2):
  mat3 = mat1
  for i in range(0, len(mat1)):
    for j in range(0, len(mat1[i])):
      try:
	mat3[i][j] = mat1[i][j] + mat2[i][j]
      except:
	print "Matrix dimensions must agree"
	print "M1: " + str(len(mat1)) + "x" + str(len(mat1[0]))
	print "M2: " + str(len(mat2)) + "x" + str(len(mat2[0]))
	return None
  return mat3
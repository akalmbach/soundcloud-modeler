#include <stdio.h>
#include "opencv2/imgproc/imgproc.hpp"
#include "opencv2/highgui/highgui.hpp"

using namespace cv;

void kMeansDict(vector<vector<vector<double> > > in, int k, int totalWords, char * dictFname);

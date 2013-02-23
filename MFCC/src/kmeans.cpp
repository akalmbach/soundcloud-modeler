#include "./kmeans.h"

void kMeansDict(vector<vector<vector<double> > > in, int k, int totalWords, char * dictFname){
    int dims = in[0][0].size();
    int numFiles = in.size();
    Mat inFlat(totalWords, dims, CV_32FC1);
    Mat labels;
    Mat centers(k, dims, CV_32FC1);
    int wordsAssigned = 0;
    for (int i = 0; i < numFiles; i++){
        for (int j = 0; j < in[i].size(); j++){
            for (int x = 0; x < dims; x++){
                inFlat.at<float>(wordsAssigned, x) = (float)in[i][j][x];
            }
            wordsAssigned++;
        }
    }
    cv::kmeans(inFlat, k, labels, cvTermCriteria( CV_TERMCRIT_ITER+CV_TERMCRIT_EPS, 30, FLT_EPSILON ), 3, KMEANS_PP_CENTERS, centers);

    //find all the centroids
    vector<double> empty(dims, 0.0);
    vector<vector<double> > centroids(k, empty);
    vector <int> numsAssigned(k, 1);
    for (int i = 0; i < totalWords; i++){
        int j = labels.at<int>(i, 1);
        for (int x = 0; x < dims; x++){
            centroids[j][x] += (double) inFlat.at<float>(i, x);
        }
        numsAssigned[j]++;
    }
    for (int i = 0; i < k; i++){
        for (int x = 0; x < dims; x++){
            centroids[i][x] /= (double) numsAssigned[i];
        }
    }

    FILE * dictfile = fopen(dictFname, "w");
    for (int i = 0; i < k; i++){
        fprintf(dictfile, "%d:", i);
        for (int j = 0; j < dims; j++){
            fprintf(dictfile, "%f ", centroids[i][j]);
        }
        fprintf(dictfile, "\n");
    }

    fclose(dictfile);
}

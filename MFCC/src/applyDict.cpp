#include <vector>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

using namespace std;

float euDist(vector<float> v1, vector<float> v2){
    float dist = 0.0;
    for (int i = 0; i < v1.size(); i++){
        dist += (v2[i] - v1[i])*(v2[i] - v1[i]);
    }
    dist = sqrt(dist);
    return dist;
}

int main(int argc, char * argv[]){
    /*if (argc != 5){
        printf("please enter a dictionary, a raw mfcc file, an mfcc output filename, a lda output filename, and a doc time");
        exit(0);
    }*/
    FILE * dict_f, *mfcc_raw_f, *mfcc_out_f, *words_out_f, *nums_words_f;
    dict_f = fopen(argv[1], "r");
    mfcc_raw_f = fopen(argv[2], "r");
    mfcc_out_f = fopen(argv[3], "w");
    words_out_f = fopen(argv[4], "w");
    float docTime;
    sscanf(argv[5], "%f", &docTime);
    printf("opened files\n");

    vector <vector <float> > dict;
    vector <vector <float> > mfcc_raw;
    int numCoeff = 13;
    float trash;
    while( !feof(dict_f) ){
        vector <float> curMFCC;
        fscanf(dict_f, "%f:", &trash);
        for (int i = 0; i < numCoeff; i++){
            float curCoeff;
            fscanf(dict_f, "%f.", &curCoeff);
            curMFCC.push_back(curCoeff);
        }
        dict.push_back(curMFCC);
    }
    fclose(dict_f);
    int nums_words[1024] = {0};
    int cur_doc = 0;
    int num = 0;
    float time, lastTime;
    lastTime = 0;
    time = 0;
    while( !feof(mfcc_raw_f) ){
        fscanf(mfcc_raw_f, "%f:", &time);
        vector <float> curMFCC;
        for (int i = 0; i < numCoeff; i++){
            float curCoeff;
           fscanf(mfcc_raw_f, "%f.", &curCoeff);
            curMFCC.push_back(curCoeff);
        }
        mfcc_raw.push_back(curMFCC);
        if (time < lastTime + docTime){
            num += 1;
        }
        else{
            lastTime = time;
            nums_words[cur_doc] = num;
            cur_doc++;
            num = 0;
        }
	printf("wrote time %f\n", time);
    }
    nums_words[cur_doc] = num;
    fclose(mfcc_raw_f);

    printf("Read %d docs with %d total words\n", cur_doc, mfcc_raw.size());
    int totalDocs = cur_doc + 1;
    int checksum = 0;
    for (int i = 0; i <= cur_doc; i++){
        printf("doc %d: %d words\n", i, nums_words[i]);
        checksum += nums_words[i];
    }
    printf("checksum: %d = %d total\n", checksum, mfcc_raw.size());
    
    printf("writing mfccs file\n");
    cur_doc = 0;
    int word_count = 0;
    for (int i = 0; i < mfcc_raw.size(); i++){
        if (i%5000 == 0) printf("%f pct \n", ((float)(i))/((float)mfcc_raw.size()));
        int best_j = 0;
        float best_d = 10000;
        for (int j = 0; j < dict.size(); j++){
            if (euDist(mfcc_raw[i], dict[j]) < best_d){
                best_j = j;
                best_d = euDist(mfcc_raw[i], dict[j]);
                //printf("reset best %d to %f\n", j, best_d);
            }
        }
        //printf("d %f\n", best_d);
        for (int k = 0; k < dict[best_j].size(); k++){
            fprintf(mfcc_out_f, "%f ", dict[best_j][k]);
        }
        fprintf(words_out_f, "%d ", best_j);
        word_count++;
        if (word_count >= nums_words[cur_doc] && cur_doc < totalDocs){ 
            fprintf(words_out_f, "\n");
            printf("doc %d\n", cur_doc);
            word_count = 0;
            cur_doc++;
        }
        fprintf(mfcc_out_f, "\n");
    }
    fclose(mfcc_out_f);
    fclose(words_out_f);
}

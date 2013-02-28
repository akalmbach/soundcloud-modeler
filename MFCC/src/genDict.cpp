#include <stdio.h>
#include <stdlib.h>
#include <sndfile.h>
#include <fftw3.h>
#include <string.h>
#include "./libmfcc/libmfcc.h"
#include "./kmeans.h"

using namespace std;

#define FFT_BUF_SIZE 4096 // 4096~92 ms, also 2^12 samples
#define HOP_SIZE (FFT_BUF_SIZE/2)
#define WORD_SIZE 13

double hamming[FFT_BUF_SIZE];

void initWindow(void){
    for (int i = 0; i < FFT_BUF_SIZE; i++){
        hamming[i] = 0.54 - 0.46*cos((2*M_PI*i)/(FFT_BUF_SIZE - 1));
    }
}

vector<vector<double> > calcMFCC(double ** wav_p, int blocks_read, int mfcc_order, int sr=44100){
    //COMPUTE THE FFTs
    fftw_complex *out;
    double *in;
    double *wav = *wav_p;
    vector<vector<double> > mfccResult;
    fftw_plan p;

    double spectrum[FFT_BUF_SIZE];
    double curCoeff;

    in = (double*) fftw_malloc(sizeof(double)*FFT_BUF_SIZE);
    out = (fftw_complex*) fftw_malloc(sizeof(fftw_complex)*(FFT_BUF_SIZE/2+1));
    p = fftw_plan_dft_r2c_1d(FFT_BUF_SIZE, in, out, FFTW_MEASURE);

    int printInterval = blocks_read/(HOP_SIZE*100);
    int pos;
    int win_num = 0;
    for (pos = 0; pos < blocks_read - FFT_BUF_SIZE; pos += HOP_SIZE){
        vector <double> curMFCC;
        win_num++;
        int i;
        for (i = 0; i < FFT_BUF_SIZE; i++){
            in[i] = wav[pos+i]*hamming[i];
        }
        fftw_execute(p);
        for (i = 0; i < FFT_BUF_SIZE/2+1; i++){
            spectrum[i] = out[i][0]/FFT_BUF_SIZE;
        }
        int coeff;
        for(coeff = 0; coeff < mfcc_order; coeff++) {
            curCoeff = GetCoefficient(spectrum, sr, 48, 128, coeff);
            curMFCC.push_back(curCoeff);
        }
        mfccResult.push_back(curMFCC);
        if ((pos/HOP_SIZE)%printInterval == 0){
            printf("\r%f pct complete", (float)pos/blocks_read);
            fflush(stdout);
        }
    }
    printf("\n");
    return mfccResult;
}

int main(int argc, char * argv[]){
    //For reading the wav file
    initWindow();
    vector<vector<double> > mfccResult;
    vector<vector<vector<double> > > allMfccResult;
    int samplerate;
    char dictFname[128];
    sscanf(argv[1], "%s", dictFname);
    int numWords;
    sscanf(argv[2], "%d", &numWords);
    for (int i = 3; i < argc; i++){
        char fname[128];
        sscanf(argv[i], "%s", fname);
        printf("fname: %s\n", fname);
        SF_INFO info;
        SNDFILE *sf;
        int blocks_read;
        double *wav;
        sf = sf_open(fname, SFM_READ, &info);
        if (sf == NULL) {
            printf("Failed to open the file.\n");
            return(-1);
        }
        if(info.channels != 1){
            printf("Only tested on single channel audio.\n");
            return(-1);
        }
        samplerate = info.samplerate;
        wav = (double *) malloc(info.frames*sizeof(double));
        blocks_read = sf_read_double(sf, wav, info.frames);
        sf_close(sf);
        printf("Read %d blocks from %s.\n", blocks_read, fname);
        mfccResult = calcMFCC(&wav, info.frames, WORD_SIZE, info.samplerate);
        allMfccResult.push_back(mfccResult);
        free(wav);
    }

    printf("Computed MFCCs for %d files:\n", allMfccResult.size());
    int totalWords = 0;
    for (int i = 0; i < allMfccResult.size(); i++){
        totalWords += allMfccResult[i].size();
        printf("File %d: %d samples\n", i, allMfccResult[i].size());
    }

    printf("writing raw output to %s\n", dictFname);
    FILE * outfileraw = fopen(dictFname, "w");
    double time = 0;
    double interval = (double)HOP_SIZE/samplerate;
    for (int i = 0; i < allMfccResult.size(); i++){
        for (int j = 0; j < allMfccResult[i].size()-1; j++){
            fprintf(outfileraw, "%f:", time);
            for (int k = 0; k < allMfccResult[i][j].size(); k++){
                fprintf(outfileraw, "%f ", allMfccResult[i][j][k]);
            }
            fprintf(outfileraw, "\n");
            time += interval;
        }
        fprintf(outfileraw, "\n");
        time = 0;
    }
    fclose(outfileraw);

    strcat(dictFname, "-dict");
    if (totalWords > numWords){
        printf("writing (%d) kMeans dict to %s\n", numWords, dictFname);
        kMeansDict(allMfccResult, numWords, totalWords, dictFname);
    }

    return 0;
}

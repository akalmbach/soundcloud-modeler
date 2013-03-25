import musicModel, loader3, graphWriter, sys

# doBFSQuery(path, name, maxReps, maxLengthMin, totalLengthMin):
log = loader3.doBFSQuery('../LittleModels/Booma/', 'Booma', 32, 15, 180)
log.genMFCCs('../Vocabs/ExploreVocab/ExploreVocab-dict')
musicModel.runLDA(1000, 5, log.all_mfccs_fn)
theta = musicModel.readTheta(log.path + 'model-final.theta')
[adj, labels] = musicModel.genGraph(theta, log)
graphWriter.writePage('../site/booma.html', adj, labels, '../site/resources/index.tpl')

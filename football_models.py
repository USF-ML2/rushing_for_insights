from pyspark.mllib.regression import LabeledPoint
from pyspark.mllib.tree import RandomForest, RandomForestModel, DecisionTree, GradientBoostedTrees, GradientBoostedTreesModel
from pyspark.mllib.classification import LogisticRegressionWithLBFGS, LogisticRegressionModel, SVMWithSGD, SVMModel
from pyspark.mllib.util import MLUtils

acc_dict = dict()

def parsePoint(line):
    values = [float(x) for x in line.split(',')]
    return LabeledPoint(values[-1], values[0:9])


# PREPARE DATA
data = sc.textFile("nfl_pbp_data/plays.csv")
header = data.first()
data = data.filter(lambda x: x != header)
parsedData = data.map(parsePoint)
(trainingData, testData) = parsedData.randomSplit([0.8, 0.2])



# TRAIN MODELS
logit_model = LogisticRegressionWithLBFGS.train(trainingData)

svm_model = SVMWithSGD.train(trainingData, iterations=100)

rf_model = RandomForest.trainClassifier(trainingData, numClasses=2, categoricalFeaturesInfo={},
                                     numTrees=100, featureSubsetStrategy="auto",
                                     impurity='gini', maxDepth=10, maxBins=32)

dt_model = DecisionTree.trainClassifier(trainingData, numClasses=2, categoricalFeaturesInfo={},
                                     impurity='gini', maxDepth=30, maxBins=100)

gbt_model = GradientBoostedTrees.trainClassifier(trainingData,
                                             categoricalFeaturesInfo={}, numIterations=100)

models = [
	('logit' , logit_model), 
	('svm' , svm_model),
	('rf' , rf_model),
	('dt' , dt_model),
	('gbt' , gbt_model)
]

# ASSESS MODELS

for tup in models:
	key = tup[0]
	m = tup[1]
	train_preds = m.predict(trainingData.map(lambda x: x.features))
	test_preds = m.predict(testData.map(lambda x: x.features))
	train_labsNpreds = trainingData.map(lambda lp: lp.label).zip(train_preds)
	test_labsNpreds = testData.map(lambda lp: lp.label).zip(test_preds)
	trainErr = train_labsNpreds.filter(lambda (v, p): v != p).count() / float(trainingData.count())
	testErr = test_labsNpreds.filter(lambda (v, p): v != p).count() / float(testData.count())
	acc_dict[key] = {'test' : 1.0 - testErr, 'training' : 1.0 - trainErr}



#prints GBT diagram
#print(rf_model.toDebugString())


for k in acc_dict:
	print k, acc_dict[k]

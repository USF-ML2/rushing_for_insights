################ Logistic Regression #######################

from pyspark.mllib.classification import LogisticRegressionWithLBFGS, LogisticRegressionModel
from pyspark.mllib.regression import LabeledPoint

# Load and parse the data
def parsePoint(line):
    values = [float(x) for x in line.split(',')]
    return LabeledPoint(values[-1], values[0:9])



data = sc.textFile("/Users/mac/Desktop/USF/MSAnalytics/Spring1/ML2/ML Project/plays.csv")
header = data.first()
data = data.filter(lambda x: x != header)
parsedData = data.map(parsePoint)


# Build the model
logitmodel = LogisticRegressionWithLBFGS.train(parsedData)

# Evaluating the model on training data
labelsAndPreds = parsedData.map(lambda p: (p.label, logitmodel.predict(p.features)))
trainErr = labelsAndPreds.filter(lambda (v, p): v != p).count() / float(parsedData.count())
print("Training Error = " + str(trainErr))  ## 0.353992330848

############################ SVM ##############################

from pyspark.mllib.classification import SVMWithSGD, SVMModel
from pyspark.mllib.regression import LabeledPoint

# Build the model
SVMmodel = SVMWithSGD.train(parsedData, iterations=100)

# Evaluating the model on training data
labelsAndPreds = parsedData.map(lambda p: (p.label, SVMmodel.predict(p.features)))
trainErr = labelsAndPreds.filter(lambda (v, p): v != p).count() / float(parsedData.count())
print("Training Error = " + str(trainErr)) ## 0.555395278766

############################ Decision TREE ##############################

from pyspark.mllib.regression import LabeledPoint
from pyspark.mllib.tree import DecisionTree
from pyspark.mllib.util import MLUtils


def parsePoint(line):
    values = [float(x) for x in line.split(',')]
    return LabeledPoint(values[-1], values[0:9])

data = sc.textFile("/Users/mac/Desktop/USF/MSAnalytics/Spring1/ML2/ML Project/plays.csv")
header = data.first()
data = data.filter(lambda x: x != header)
parsedData = data.map(parsePoint)

model = DecisionTree.trainClassifier(parsedData, numClasses=2, categoricalFeaturesInfo={},
                                     impurity='gini', maxDepth=30, maxBins=100)

# Evaluate model on training instances and compute training error
predictions = model.predict(parsedData.map(lambda x: x.features))
labelsAndPredictions = parsedData.map(lambda lp: lp.label).zip(predictions)
trainErr = labelsAndPredictions.filter(lambda (v, p): v != p).count() / float(parsedData.count()) #0.09
print('Training Error = ' + str(trainErr))
print('Learned classification tree model:')
print(model)

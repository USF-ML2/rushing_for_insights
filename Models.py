import numpy as np
import csv
from sklearn.cross_validation import cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn import cross_validation
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegressionCV
from sklearn.cross_validation import train_test_split
from sklearn.grid_search import GridSearchCV
from sklearn.metrics import classification_report
from sklearn.linear_model import LogisticRegression
from sklearn import svm



with open('plays.csv', 'rb') as f:
    reader = csv.reader(f)
    my_list = list(reader)

my_list = np.array(my_list)
x = my_list[:, :len(my_list[0])-1]
y = my_list[:, len(my_list[0])-1]
X = x[1:, :]
y = y[1:]
X = X.astype(np.float)
y = y.astype(np.float)

##################### Logistic Reg CV ############

# For the grid of Cs values (that are set by default to be ten values in a logarithmic scale between 1e-4 and 1e4)
# If Cs is as an int, then a grid of Cs values are chosen in a logarithmic scale between 1e-4 and 1e4.
# Like in support vector machines, smaller values specify stronger regularization.

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0)

lr_cv = LogisticRegressionCV(Cs = 10, cv=5)
lr_cv = lr_cv.fit(X_train, y_train)
print 'Logistic Regression train accuracy', lr_cv.score(X_train, y_train)
print 'Logistic Regression CV test accuracy', lr_cv.score(X_test, y_test)

######### Logistic Regression Grid Search for C ############

print '******** Logistic Reg *********'

tuned_parameters = {'C': np.linspace(0.1, 10, 10)}

scores = ['precision', 'recall']

for score in scores:
    print("# Tuning hyper-parameters for %s" % score)
    clf = GridSearchCV(LogisticRegression(), tuned_parameters, cv=4, scoring='%s_weighted' % score)
    clf.fit(X_train, y_train)
    print("Best parameters set found on development set:")
    print(clf.best_params_)
    print("Grid scores on development set:")
    for params, mean_score, scores in clf.grid_scores_:
        print("%0.4f for %r" % (mean_score, params))

    print("Detailed classification report:")
    print("The model is trained on the full development set.")
    print("The scores are computed on the full evaluation set.")
    y_true, y_pred = y_test, clf.predict(X_test)
    print(classification_report(y_true, y_pred))

####################  TREES CV  ##################
X_train, X_test, y_train, y_test = cross_validation.train_test_split(X, y, test_size=0.3, random_state=0)

print '******* Decision tree Classifier *******'

clf = DecisionTreeClassifier(max_depth=None, min_samples_split=1,random_state=0)
scores = cross_val_score(clf, X_train, y_train)
print 'CV mean accuracy on test set', scores.mean()
clf.fit(X_train, y_train)
print 'accuracy on training set', clf.score(X_train, y_train)

print '******** Random Forest Classifier ********'
clf = RandomForestClassifier(n_estimators=10, max_depth=None, min_samples_split=1, random_state=0)
scores = cross_val_score(clf, X_train, y_train)
print 'CV score on test set', scores.mean()
clf.fit(X_train, y_train)
print 'accuracy on training set', clf.score(X_train, y_train)

print '******* Extra tree Classifier *********'

clf = ExtraTreesClassifier(n_estimators=10, max_depth=None, min_samples_split=1, random_state=0)
scores = cross_val_score(clf, X_train, y_train)
print 'CV score on test set', scores.mean()
clf.fit(X_train, y_train)
print 'accuracy on training set', clf.score(X_train, y_train)


############## ADABOOST ##############

print 'Output of Adaboost'

from sklearn.cross_validation import cross_val_score
from sklearn.ensemble import AdaBoostClassifier

clf = AdaBoostClassifier(base_estimator=RandomForestClassifier(), n_estimators=100)
scores = cross_val_score(clf, X_train, y_train)
print 'Adaboost score', scores.mean()


######## gradient boosting classifier ######

print 'Output of Gradient boosting'

clf = GradientBoostingClassifier(n_estimators=100, learning_rate=1.0,max_depth=1, random_state=0)
scores = cross_val_score(clf, X_train, y_train)
print 'Gradient boosting score', scores.mean()

#### SVM for optimal search of C #########

svc = svm.SVC(kernel='linear')
C_s = np.logspace(-10, 0, 10)

scores = list()
scores_std = list()
for C in C_s:
    svc.C = C
    this_scores = cross_validation.cross_val_score(svc, X, y, n_jobs=1)
    scores.append(np.mean(this_scores))
    scores_std.append(np.std(this_scores))

# Do the plotting
import matplotlib.pyplot as plt
plt.figure(1, figsize=(4, 3))
plt.clf()
plt.semilogx(C_s, scores)
plt.semilogx(C_s, np.array(scores) + np.array(scores_std), 'b--')
plt.semilogx(C_s, np.array(scores) - np.array(scores_std), 'b--')
locs, labels = plt.yticks()
plt.yticks(locs, list(map(lambda x: "%g" % x, locs)))
plt.ylabel('CV score')
plt.xlabel('Parameter C')
plt.ylim(0, 1.1)
plt.show()







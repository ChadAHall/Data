#!/usr/bin/python

import sys
import pickle
import pandas as pd
import numpy as np
import matplotlib
from collections import defaultdict
sys.path.append("../tools/")

from feature_format import featureFormat, targetFeatureSplit
#from tester import dump_classifier_and_data

### Task 1: Select what features you'll use.
### features_list is a list of strings, each of which is a feature name.
### The first feature must be "poi".
# You will need to use more features
features_list = ['poi']
### Load the dictionary containing the dataset
#pickle type error: needs to read binary with rb instead of r
#https://stackoverflow.com/questions/39146039/pickle-typeerror-a-bytes-like-object-is-required-not-str
def load_dataset():
    with open("final_project_dataset.pkl", "rb") as data_file:
        data_dict = pickle.load(data_file)
    return data_dict

### Task 2: Remove outliers
def plot_out(data_dict, feature_x, feature_y):
    data = featureFormat(data_dict, [feature_x, feature_y])
    for point in data:
        x = point[0]
        y = point[1]
        matplotlib.pyplot.scatter(x, y)
    matplotlib.pyplot.xlabel(feature_x)
    matplotlib.pyplot.ylabel(feature_y)
    matplotlib.pyplot.show()

def remove_outliers(data, feature):
    #this removes the outliers that are selected
    data.pop([feature])

### Task 3: Create new feature(s)
def make_fraction(numerator, denominator):
    try:
        fraction = numerator / denominator
    except TypeError:
        fraction = 'NaN'
    return fraction

def from_poi(person_values):
    #this function calculates the fraction of messages from POI to this person
    poi_messages = person_values['from_poi_to_this_person']
    all_messages = person_values['to_messages']
    return {'fraction_from_poi': make_fraction(poi_messages, all_messages)}

def to_poi(person_values):
    #function to calculate the fraction of messages from this person to poi
    poi_messages = person_values['from_this_person_to_poi']
    all_messages = person_values['from_messages']
    return {'fraction_to_poi': make_fraction(poi_messages, all_messages)}

def shared_poi(person_values):
    # this function is used to calculate the fraction that the person
    # sreceived from poi and how many shared recipient with a poi
    poi_messages = person_values['shared_receipt_with_poi']
    all_messages = person_values['to_messages']
    return {'fraction_shared': make_fraction(poi_messages, all_messages)}

# store created features in a list
#new_feature_func = [fraction_from_poi, fraction_to_poi, fraction_shared]

def new_feature_data(data_dict, new_feature_func):
#apply new features and add to dict
    for person, values in iter(data_dict.items()):
        for func in new_feature_func:
            data_dict[person].update(func(data_dict[person]))
    return data_dict


### Store to my_dataset for easy export below.

#my_dataset = enron_data

### Extract features and labels from dataset for local testing
#data = featureFormat(my_dataset, features_list, sort_keys = True)
#labels, features = targetFeatureSplit(data)
def feature_extractor(dataset, features_list):
    data = featureFormat(dataset, features_list)
    labels, features = targetFeatureSplit(data)
    return labels, features

### Task 4: Try a varity of classifiers
### Please name your classifier clf for easy export below.
### Note that if you want to do PCA or other multi-stage operations,
### you'll need to use Pipelines. For more info:
### http://scikit-learn.org/stable/modules/pipeline.html

# Provided to give you a starting point. Try a variety of classifiers.
from sklearn.naive_bayes import GaussianNB
clf = GaussianNB()

### Task 5: Tune your classifier to achieve better than .3 precision and recall
### using our testing script. Check the tester.py script in the final project
### folder for details on the evaluation method, especially the test_classifier
### function. Because of the small size of the dataset, the script uses
### stratified shuffle split cross validation. For more info:
### http://scikit-learn.org/stable/modules/generated/sklearn.cross_validation.StratifiedShuffleSplit.html

# Example starting point. Try investigating other evaluation techniques!
#from sklearn.model_selection import train_test_split
#features_train, features_test, labels_train, labels_test = \
#    train_test_split(features, labels, test_size=0.3, random_state=42)

### Task 6: Dump your classifier, dataset, and features_list so anyone can
### check your results. You do not need to change anything below, but make sure
### that the version of poi_id.py that you submit can be run on its own and
### generates the necessary .pkl files for validating your results.

#dump_classifier_and_data(clf, my_dataset, features_list)

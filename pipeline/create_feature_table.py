import pandas as pd
import numpy as np
import yaml
import copy

import feature_computation

def get_feats_to_compute(df):
	"""
	input: dataframe of cleaned student data
	output: zipped list with each item being a double. 
			The first element of each double is the feature name 
			The second element of each double is the dependencies for this feature
	"""

	#contains list of features in yml file
	feature_list = {}
	
	#include only those with incl:True flag set
	to_add = []

	#features native to the dataframe
	generated_feats = [i for i in df.columns]
	
	#this tells us which order to compute features in
	queue = copy.copy(generated_feats)

	#read the yml file
	stream = open("create_feature_table.yml", 'r')
	docs = yaml.load_all(stream)
	for doc in docs:
		feature_list[doc['name']] = {}
		for k,v in doc.items():
			if k == 'name':
				continue;
			#store all feature information (dependencies, include or not) in dictionary
			if k == 'deps':
				feature_list[doc['name']][k] = v.replace(' ','').split(',')
			else:
				feature_list[doc['name']][k] = v
	#get features to add
	for k,v in feature_list.items():
		if v['incl'] == True:
			to_add.append(k)
			
	#keep looping as long as we have not accounted for all features
	tgt_len = len(queue) + len(to_add)		
	while len(queue) != tgt_len:
		to_rem = []
		for feat in to_add:
			#if we get a feature to add, add it to the queue and mark it for removal from the to_add list
			if len([i for i in feature_list[feat]['deps'] if i in queue]) == len([i for i in feature_list[feat]['deps']]):
				queue.append(feat)
				to_rem.append(feat)
		#remove features in the to_rem list
		for feat in to_rem:
				to_add.remove(feat)
	#get features which we need to compute (not those native to the dataframe)		
	feats_to_compute = [i for i in queue if i not in generated_feats]
	#get the dependencies
	deps_to_apply = [feature_list[i]['deps'] for i in feats_to_compute]

	#return zipped list
	return zip(feats_to_compute, deps_to_apply)

def create_feat_table(df):
	"""
	input: dataframe of student data
	output: a csv containing the feature table
	"""

	#get features to generate and their dependencies
	feats_deps = get_feats_to_compute(df)
	
	#for each feature
	for feat_dep in feats_deps:
		#get the appropriate generation function
		func = getattr(feature_computation, feat_dep[0]+'_feature')
		#apply that function and add the resulting column to the dataframe
		df[feat_dep[0]] = func(df[feat_dep[1]])
	
	#generate feature table
	df.to_csv('feature_table.csv')
		
		
		
	
	
	

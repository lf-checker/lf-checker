#!/usr/bin/env python3
#import yaml
import os
import sys
#sys.path.append("/home/tong.wu/.local/lib/python3.6/site-packages")
from program_feature import *
#import pandas as pd
#from sklearn.ensemble import RandomForestClassifier
#from sklearn.model_selection import train_test_split
#from sklearn.metrics import accuracy_score
import pickle

def predict(vectors, model):
# print(model)
 loaded_model = pickle.load(open(model, 'rb'))
 #print(loaded_model)
 score = 5
 final_vector = []
 for vector in vectors:
  #print(vector)
  new_score = loaded_model.predict([vector])
 # print(new_score)
  if new_score < score:
   score = new_score
   final_vector = vector
# print(final_vector)
# print(score)
 return final_vector

def get_program_feature(file):
 feature = main(file)
 return feature
 
def get_file_from_yaml(yaml_file):
 with open(file, "r") as stream:
  dataMap = yaml.safe_load(stream)
 return dataMap['input_files']
  #bechmarks.append(dir + '/' + dataMap["input_files"])
 
def construct_feature_vector(feature):
 vector = []
 vector.append(feature.thread_create_num)
 vector.append(feature.max_thread_create_nested)
 vector.append(feature.thread_join_num)
 vector.append(feature.max_thread_join_nested)
 vector.append(feature.min_val_access_num)
 vector.append(feature.min_val_access_times)
 vector.append(feature.min_func_call_num)
 vector.append(feature.min_func_call_times)
 return vector

def get_commands(vector):
 commands = ' '
 solver = ['--z3 ', '--boolector ']
 encoding = ['--floatbv ', '--fixedbv ']
 context_bound = ['2 ', '3 ', '4 ', '5 ']
 strategy = [ '--incremental-bmc ', '--unwind ']
 k_step = ['1 ', '4 ', '64 ']
 max_step = ['50 ', '200 ', '1600 ']
 unwind = ['10 ', '40 ']
 if vector[8] != -1:
  commands += solver[vector[8]]

 if vector[9] != -1: 
  commands += encoding[vector[9]]
 if vector[10] != -1:
  commands += '--context-bound '
  commands += context_bound[vector[10] - 2]
# return commands
 if vector[11] == 1:
  commands += strategy[vector[11] - 1]
  commands += '--k-step '
  commands += k_step[vector[12] - 1]
  commands += '--max-k-step '
  commands += max_step[vector[12] - 1]
 else:
  commands += '--unwind '
  commands += str(vector[13]) + ' '

 if vector[14] != -1:
  commands += '--no-por '

 if vector[15] != -1:
  commands += '--no-goto-merge '

 if vector[16] != -1:
  commands += '--state-hashing '

 if vector[17] != -1:
  commands += '--add-symex-value-sets '
 return commands  

def run(commands):
 p = subprocess.run(commands, shell = True,  encoding='utf-8')
 return p

"""
options schema:
solver 0--z3, 1--boolector
encoding 0--floatbv, 1--fixedbv, 2--ir
context_bound = 1--1, 2--2, 3--3, 4--4, 5--5, -1--default
strategy = 1--k-induction, 2--incremental, -1--default
k_step: 1--1, 2--4, 3--64
max_step: 1--50, 2--200, 3--1600
unwind = 0--default
timeout 0--1min 1--5min
"""
def flag_predicts(benchmark, model):
 feature = get_program_feature(benchmark)
 solvers = [0, 1]
 encoding = [0, 1]
 context_bound = [2, 3, 4, 5]
 strategy = [1, 2]
 k_step =  [1, 2, 3]
 unwind = [10, 40]
 op1 = [-1, 1]
 op2 = [-1, 1]
 op3 = [-1, 1]
 op4 = [-1, 1]
 num = 0
 vectors = []
 for a in solvers:
  for b in encoding:
   for c in context_bound:
    for d in strategy:
     if d == 2:
      for e in unwind:
       for f in op1:
        for h in op2:
         for op33 in op3:
          for op44 in op4:
           vector = construct_feature_vector(feature)
           vector.append(a)
           vector.append(b)
           vector.append(c)
           vector.append(d)
           vector.append(-1)
           vector.append(e)
           vector.append(f)
           vector.append(h)
           vector.append(op33)
           vector.append(op44)
           vectors.append(vector)
           num += 1
     else:
      for i in k_step:
       for l in op1:
        for m in op2:
         for op33 in op3:
          for op44 in op4:
           vector = construct_feature_vector(feature)
           vector.append(a)
           vector.append(b)
           vector.append(c)
           vector.append(d)
           vector.append(i)
           vector.append(-1)
           vector.append(l)
           vector.append(m)
           vector.append(op33)
           vector.append(op44)
         # vector.append(h)
          #if g == 1:
          # vector.append(1)
          #elif g == 4:
          # vector.append(2)
          #elif g == 64:
           #vector.append(3)
          #vector.append(-1)
          #vector.append(i)
           vectors.append(vector)
           num += 1
#for ve in vectors:
# print (ve)

#print(num)
#exit(0)
 #print(sys.argv[1])
 options = predict(vectors, model)
 #print(options)
#exit(0)
#options = [3, 0, 3, 0, 2, 9, 2, 6, 0, 2, 5, 2, 3, -1, 0]
#ptions = [2, 0, 2, 0, 1, 3, 0, 0, 0, 1, 2, 2, 2, 10, 1, 1]
 commands = get_commands(options)
 return commands
 #for i in sys.argv[2:-1]:
  #commands = commands + i + ' '   
 #commands = commands + sys.argv[-1]
 #print(commands)
#exit(0)
 #run(commands)
 #print(commands)

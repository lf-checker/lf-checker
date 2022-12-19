#!/usr/bin/env python3
#import yaml
import os
import sys
#from b import *
#from findall import *

dep = str(os.path.split(os.path.abspath(__file__))[0]) + '/dependencies'
sys.path.append(dep)
from program_feature import *
#import pandas as pd
import pickle

def predict(vectors, model):
 loaded_model = pickle.load(open(model, 'rb'))
 score = 5
 final_vector = []
 for vector in vectors:
  new_score = loaded_model.predict([vector])
  if new_score < score:
   score = new_score
   final_vector = vector
 
 #vector_tran = final_vector
 #vector_tran[-3] = 1 
 #if score <= 3 and score == loaded_model.predict([vector_tran]):
  #return vector_tran
 print("predicted: "+ str(score))
 return final_vector

def get_program_feature(file):
 feature = main(file)
 return feature
 
def get_file_from_yaml(yaml_file):
 with open(file, "r") as stream:
  dataMap = yaml.safe_load(stream)
 return dataMap['input_files']
 
def construct_feature_vector(feature):
 vector = []
 vector.append(feature.thread_create_num)
 vector.append(feature.max_thread_num)
 vector.append(feature.thread_join_num)
 vector.append(feature.max_join_num)
 vector.append(feature.pthread_mutex)
 vector.append(feature.atomic)
 vector.append(feature.min_val_access_num)
 vector.append(feature.min_val_access_times)
 vector.append(feature.min_func_call_num)
 vector.append(feature.min_func_call_times)
 vector.append(feature.operator_num_inif)
 vector.append(feature.max_iter)
 vector.append(feature.nondet_num)
 vector.append(feature.max_loops)
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
 length = len(vector)
 if vector[length-10] != -1:
  commands += solver[vector[length-10]]

 if vector[length-9] != -1: 
  commands += encoding[vector[length-9]]
 if vector[length-8] != -1:
  commands += '--context-bound '
  commands += context_bound[vector[length-8] - 2]
# return commands
 if vector[length-7] == 1:
  commands += strategy[vector[length-7] - 1]
  commands += '--k-step '
  commands += k_step[vector[length-6] - 1]
  commands += '--max-k-step '
  commands += max_step[vector[length-6] - 1]
 else:
  commands += '--unwind '
  commands += str(vector[length-5]) + ' '

 if vector[length-4] != -1:
  commands += '--no-por '

 if vector[length-3] != -1:
  commands += '--no-goto-merge '

 if vector[length-2] != -1:
  commands += '--state-hashing '

 if vector[length-1] != -1:
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
           vectors.append(vector)
           num += 1
 options = predict(vectors, model)
 commands = get_commands(options)
 return commands, options
 
if __name__ == "__main__":
 files = findall()
 #print(files)
 #exit(0)
 list1, list2, list3 = data_lists('../../1025/rawData1.csv')
 #print(len(list3))
 correct = 0
 incorrect = 0
 incorrect_list = []
 for file in files:
  filel = []
  filel.append(file)
  if list3.count(filel) != 0:
   fullfile = '../../../benchmarks/2022/' + file
   com, flags = flag_predicts(fullfile, sys.argv[1])
   flags.insert(0,file)
   print(flags)
   #com, flags = flag_predicts(sys.argv[1])
   result = deter_verdit(flags, list1, list2)
   print("actual: "+ str(result))
   if result == 5:
    incorrect_list.append(flags)
    incorrect += 1
   elif result < 3:
    correct += 1
  print('correct: ' + str(correct))
  print('incorrect: ' + str(incorrect))
  print('')
 for item in incorrect_list:
  print(item)
 exit(0)
 com, flags = flag_predicts(sys.argv[1], sys.argv[2])
 print(com)
 print(flags)
 benchmark = sys.argv[1]
 benchmark = benchmark[benchmark.index("sv-benchmarks"):]
 print(benchmark)
 flags.insert(0,benchmark)
 print(flags)
 result = deter_verdit(flags, list1, list2) 
 print(result)

#!/usr/bin/python3
import subprocess
import sys
#from src.ClangAST import ProgramFeatures
from anytree import Node, RenderTree, NodeMixin, LevelOrderGroupIter, LevelOrderIter
from anytree.exporter import DotExporter

#dict_func_prev = {} #key: pre_address(pre_declare) value: curr_address


"""
class represents program features.
"""
class Feature():
 def __init__(self, thread_create_num, max_thread_create_nested, max_thread_num, thread_join_num, max_thread_join_nested, max_join_num, pthread_mutex, atomic, min_val_access_num, min_val_access_times, min_func_call_num, min_func_call_times, operator_num_inif, max_iter, nondet_num, max_loops):
  self.thread_create_num = thread_create_num
  self.max_thread_create_nested = max_thread_create_nested
  self.max_thread_num = max_thread_num
  self.thread_join_num = thread_join_num
  self.max_thread_join_nested = max_thread_join_nested
  self.max_join_num = max_join_num
  self.pthread_mutex = pthread_mutex
  self.atomic = atomic
  self.min_val_access_num = min_val_access_num
  self.min_val_access_times = min_val_access_times
  self.min_func_call_num = min_func_call_num
  self.min_func_call_times = min_func_call_times
  self.operator_num_inif = operator_num_inif
  
  self.max_iter = max_iter
  self.nondet_num = nondet_num
  self.max_loops = max_loops
  self.dict_func_prev = {} #key: pre_address(pre_declare) value: curr_address
  self.dict_val_access = {}
  self.dict_func_call = {}
  self.global_decl_list = []
  self.pthread_create_stmt_list = []
  self.pthread_join_stmt_list = []
  self.pthread_mutex_stmt_list = []
  self.main_func_stmt = ''
  self.global_decl_key_value = {}
     
"""
class represents a node in the ast-dump.
"""
class TreeNode(NodeMixin):
 def __init__(self, name, address, suffix, parent = None, children = None):
  self.name = name
  self.address = address
  self.suffix = suffix
  self.parent = parent
  if children:
   self.children = children

"""
class represents a function call or variable access, and its nested level.
level = 0 : the stmt not in a loop.
level = 1 : One loop.
level = 2 : Nested with two loops.
"""   
class stmt_nested():
 def __init__(self, address, level):
  self.address = address
  self.level = level

"""
class represents a function called by pthread_create().
Record the global variables read/write events, and function calls.
"""
class function_call():
 def __init__(self, address):
  val_list = []
  func_list = []
  self.address = address
  self.val_list = val_list
  self.func_list = func_list
  
 def add_val(self, val_address, nested_level_val):
  val_access = stmt_nested(val_address, nested_level_val)
  self.val_list.append(val_access)
  
 def add_func(self, function_address, nested_level_func):
  func_call = stmt_nested(function_address, nested_level_func)
  self.func_list.append(func_call)

"""
class represents a pthread_create() call stmt.
"""
class pthread_function_call(stmt_nested):
 def __init__(self, address, level):
  super(pthread_function_call, self).__init__(address, level)
  #func_call = stmt_nested(function_address, nested_level)
  #self.address = address
  #self.nested = nested
  self.func_call = ''
  
 def set_func_call(self, function_address):
  func_call = function_call(function_address)
  self.func_call = func_call

##################################################################################
def find_nested(feature, TreeNode):
 nest = 0
 num = 1
 while(TreeNode.parent is not None):
  if TreeNode.parent.name == "-DoStmt" or TreeNode.parent.name == "-WhileStmt" or TreeNode.parent.name == "-ForStmt":
   num = num  * find_iteration_nums(feature, TreeNode)
   nest += 1
  TreeNode = TreeNode.parent
 return nest, num 


"""
Return the time of iteration in nested loops
"""
def find_iteration_nums(feature, TreeNode):
 TreeNode = TreeNode.parent
 if(TreeNode.name == '-ForStmt'):
  for nodes in LevelOrderGroupIter(TreeNode, maxlevel=2):
   if len(nodes) > 1:
    for node in nodes:
     if node.suffix is not None and node.name == '-BinaryOperator' and node.suffix[-1] != '\'=\'':
      for children in LevelOrderGroupIter(node, maxlevel=2):
       childnum = 1
       for child in children:
        if '-IntegerLiteral' == child.name:
         return int(child.suffix[-1])
        #elif '-ImplicitCastExpr' == child.name:
        # if childnum == 2:
        #  for index, child1 in enumerate(LevelOrderGroupIter(child)):
         #  for child2 in child1:
          #  if index == 1:
           #  print(child2.suffix[child2.suffix.index('lvalue')+2])
             
         #else:
          #childnum += 1
  
 return 10
 #for pre, fill, node in RenderTree(TreeNode):
 # print(node.name, node.suffix)
# feature.max_thread_num = 10


def construct_global_decl(TreeNode, feature):
 for index, children in enumerate(LevelOrderGroupIter(TreeNode, maxlevel=3)):  
  for node in children:
   if index == 2 and node.name == "-FunctionDecl" or node.name == "-VarDecl":
    feature.global_decl_list.append(node.address)
 
def find_pthread_create_call(TreeNode, feature):
 if TreeNode.suffix is not None and "'pthread_create'" in TreeNode.suffix and "-DeclRefExpr" in TreeNode.name:
  nest, max_thread_num = find_nested(feature, TreeNode)
  feature.pthread_create_stmt_list.append(pthread_function_call(TreeNode.address, nest))
  feature.max_thread_num += max_thread_num
  
def find_pthread_mutex_call(TreeNode, feature):
 if TreeNode.suffix is not None and "'pthread_mutex_lock'" in TreeNode.suffix and "-DeclRefExpr" in TreeNode.name:
  ##nest, max_thread_num = find_nested(feature, TreeNode)
  feature.pthread_mutex_stmt_list.append(TreeNode.address)
    
def add_main_to_pthread(TreeNode, feature):
 if TreeNode.suffix is not None and TreeNode.name == '-FunctionDecl' and 'main' in TreeNode.suffix:
  nest = 0
  feature.pthread_create_stmt_list.append(pthread_function_call(TreeNode.address, nest))
  
def find_pthread_join_call(TreeNode, feature):
 if TreeNode.suffix is not None and "'pthread_join'" in TreeNode.suffix and "-DeclRefExpr" in TreeNode.name:
  nest, max_join_num = find_nested(feature, TreeNode)
  feature.pthread_join_stmt_list.append(pthread_function_call(TreeNode.address, nest))
  feature.max_join_num += max_join_num

"""
function gets the function address called by the pthread_createpython iterate two lists one by one
"""
def get_function_address(TreeNode):
 address = TreeNode.address
 while TreeNode.name != "-CallExpr":
  TreeNode = TreeNode.parent
 
 for pre, fill, node in RenderTree(TreeNode):
  if "Function" in node.suffix and node.address != address:
   return node

def func_address_match(feature, root):
 for li in feature.pthread_create_stmt_list:
  for pre, fill, node in RenderTree(root):
   if li.address == node.address:
    node = get_function_address(node)
    address = node.suffix[node.suffix.index("Function")+1] #The address here is pre_declared function
    if feature.dict_func_prev.get(address) is not None:
     address = feature.dict_func_prev.get(address) #The address of definition
    li.set_func_call(address)
    
# for pre, fill, node in RenderTree(root):
#  if feature.main_func_stmt.address == node.address:
#   print(node.address)
#   node = get_function_address(node)
#   address = node.suffix[node.suffix.index("Function")+1] #The address here is pre_declared function
#   if feature.dict_func_prev.get(address) is not None:
#    address = feature.dict_func_prev.get(address) #The address of definition
#   feature.main_func_stmt.set_func_call(address)


def genreate_features(feature):
 feature.thread_create_num = len(feature.pthread_create_stmt_list)
 feature.thread_join_num = len(feature.pthread_join_stmt_list)
 feature.pthread_mutex = len(feature.pthread_mutex_stmt_list)
 
 for stmt in feature.pthread_create_stmt_list:
  if stmt.level > feature.max_thread_create_nested:
   feature.max_thread_create_nested = stmt.level

 for stmt1 in feature.pthread_join_stmt_list:
  if stmt1.level > feature.max_thread_join_nested:
   feature.max_thread_join_nested = stmt1.level
   
 for item in feature.pthread_create_stmt_list:
  times = feature.max_thread_num
  for i in item.func_call.val_list:
   #print(i.address)
   if feature.dict_val_access.get(i.address) is None:
    feature.dict_val_access[i.address] = 1 * times
   else:
    feature.dict_val_access[i.address] += 1 * times
  for j in item.func_call.func_list:
   if feature.dict_func_call.get(j.address) is None:
    feature.dict_func_call[j.address] = 1 * times
   else:
    feature.dict_func_call[j.address] += 1 * times
# if feature.dict_val_access.get(feature.main_func_stmt.address) is None:
#  feature.dict_val_access[feature.main_func_stmt.address] = 1 
    
# if feature.dict_func_call.get(feature.main_func_stmt.address) is None:
#  feature.dict_func_call[feature.main_func_stmt.address] = 1
  

 for key, value in feature.dict_val_access.items():
  if value > 1:
   #print(value)
   feature.min_val_access_num += 1
   feature.min_val_access_times += value
  
 for key1, value1 in feature.dict_func_call.items():
  #print(key1, value1)
  if value1 > 1:
   #print(value)
   feature.min_func_call_num += 1
   feature.min_func_call_times += value1
   

def get_ast_dump(file):
 p = subprocess.check_output(["clang", "-Xclang", "-ast-dump", "-fsyntax-only", "-fno-diagnostics-color", file], encoding='utf-8', stderr=subprocess.DEVNULL)
 return p
 
          

def bulid_tree(p, feature):
 root = TreeNode("root", "", "", None)
 level_list = []
 father = root
 pre_index = -1
 #global
 for line in p.splitlines():
  level = line.find('-')
  attrbs = ''
  if level == -1:
   attrbs = line.split(" ")
  else:
   attrbs = line[level:].split(" ")
  name = attrbs[0]
 
  if len(attrbs) > 1:
   address = attrbs[1]
   suffix = attrbs[2:]
   if len(suffix) > 1 and suffix[0] == "prev":
    feature.dict_func_prev[suffix[1]] = address
  else:
   address = None
   suffix = None
  
  if not level in level_list:
   level_list.append(level)
   child = TreeNode(name, address, suffix, parent=father)
   find_pthread_create_call(child, feature)
   find_pthread_join_call(child, feature) 
   find_pthread_mutex_call(child, feature)
   father = child
   pre_index = level
  else:
   steps = level_list.index(level) - level_list.index(pre_index)
   if steps <= 0:
    father = father.parent
   while steps < 0 and father.parent is not None:
    father = father.parent
    steps += 1
  #child = Node(line, parent = father)
   child = TreeNode(name, address, suffix, parent=father)
   find_pthread_create_call(child, feature)
   find_pthread_join_call(child, feature)
   find_pthread_mutex_call(child, feature)
   father = child
   pre_index = level
   
 return root

def global_mem_access(feature, root):
 for ob in feature.pthread_create_stmt_list:
  for pre, fill, node in RenderTree(root):
   condi1 = node.address == ob.func_call.address
   #condi2 = node.address == feature.main_func_stmt.address
   condi2 = False
   if condi1 or condi2:
     for pre1, fill1, node1 in RenderTree(node):
      if node1.suffix is not None:
       if "Var" in node1.suffix or "ParmVar" in node1.suffix:
        #print(node1.suffix)
        for su in node1.suffix:
         if su in feature.global_decl_list:
          #print(node1.suffix)
          if condi1:
           nest,num = find_nested(feature, node1)
           ob.func_call.add_val(su, nest)
          #else:
           #feature.main_func_stmt.add_val(su, 0)
          #print(ob.func_call.val_list[0].address)
          #print(ob.func_call.val_list[0].level)

       if "Function" in node1.suffix:
        for su in node1.suffix:
         if su in feature.global_decl_list:
          #print(node1.suffix)
          if condi1:
           nest,num = find_nested(feature, node1)
           ob.func_call.add_func(su, nest)
          #else:
           #feature.main_func_stmt.add_func(su, 0)
          #print(ob.func_call.func_list[0].address)
          #print(ob.func_call.func_list[0].level)
    
    
    
def operators_in_if(feature, root):
 op_num = 0
 for pre, fill, node in RenderTree(root):
  if node.name == '-FunctionDecl' and 'main' in node.suffix:
#   feature.main_func_stmt = function_call(node.address)
   #print(feature.main_func_stmt.address)
   for index, children in enumerate(LevelOrderGroupIter(node)):
    for node1 in children:
     if node1.name == '-IfStmt':
      for index1, children1 in enumerate(LevelOrderGroupIter(node1)):
       for node2 in children1:
        if node2.name == '-BinaryOperator':
         #print(str(node2.suffix))
         if node2.suffix[3] == '\'>=\'' or node2.suffix[3] == '\'<=\'':
          op_num += 2
         else:
          op_num += 1
 #print(op_num)
 feature.operator_num_inif = op_num
   #if index == 2 and node.name == "-FunctionDecl" or node.name == "-VarDecl":
    #feature.global_decl_list.append(node.address)
     #print(node1.name)
  #print(node.suffix)

"""
determine the approximate iteration times in threads
**************should be optimized
"""
def iter_time_in_thread(feature, root):
 num = 1
 for stmt in feature.pthread_create_stmt_list:
  for pre, fill, node in RenderTree(root):
   if node.address == stmt.func_call.address:
    for pre1, fill1, node1 in RenderTree(node):   
     if node1.name == "-ForStmt" or node1.name == "-DoStmt" or node1.name == "-WhileStmt":
      for child in node1.children:
       if child is not None and child.name == '-BinaryOperator' and child.suffix[-1] != '\'=\'':
        for pre2, fill2, node2 in RenderTree(child):
         if node2.name == '-IntegerLiteral':
          if int(node2.suffix[-1]) > num:
           num = int(node2.suffix[-1])
 feature.max_iter = num


def nondet_in_thread(feature, root):
 num = 0
 
 for stmt in feature.pthread_create_stmt_list:
  for pre, fill, node in RenderTree(root):
   if node.address == stmt.func_call.address:
    for pre1, fill1, node1 in RenderTree(node):
     if node1.name == "-DeclRefExpr":
      if "__VERIFIER_nondet" in ' '.join(node1.suffix):
       num += 1
       
       
 for pre, fill, node in RenderTree(root):
  if node.suffix is not None and node.name == '-FunctionDecl' and 'main' in node.suffix:
   for pre1, fill1, node1 in RenderTree(node):
    if node1.name == "-DeclRefExpr":
     if "__VERIFIER_nondet" in ' '.join(node1.suffix):
      num += 1

 feature.nondet_num = num
         
def atomic_in_thread(feature, root):
 num = 0
 for stmt in feature.pthread_create_stmt_list:
  for pre, fill, node in RenderTree(root):
   if node.address == stmt.func_call.address:
    for pre1, fill1, node1 in RenderTree(node):
     if node1.name == "-DeclRefExpr":
      if "__VERIFIER_atomic_begin" in ' '.join(node1.suffix):
       num += 1
 feature.atomic = num
 
def loops_in_thread(feature, root):
 num = 0
 for stmt in feature.pthread_create_stmt_list:
  for pre, fill, node in RenderTree(root):
   if node.address == stmt.func_call.address:
    for pre1, fill1, node1 in RenderTree(node):
     if node1.name == "-DoStmt" or node1.name == "-WhileStmt" or node1.name == "-ForStmt":
      num += 1
 feature.max_loops = num
 
def operator_num_inif_in_thread(feature, root):
 num = 0
 for stmt in feature.pthread_create_stmt_list:
  for pre, fill, node in RenderTree(root):
   if node.address == stmt.func_call.address:
    #print(node.address)	
 
    return num


def construct_val_key_value(feature, root):
 for index, children in enumerate(LevelOrderGroupIter(root, maxlevel=3)):
  if index == 2:
   for child in children:
    if child.name == '-VarDecl':
     for pre2, fill2, node2 in RenderTree(child):
      if node2 is not None and node2.name == '-IntegerLiteral' and node2.suffix[-1] != '\'extern\'':
       feature.global_decl_key_value[node2.address] = int(node2.suffix[-1])

def print_features(features):
 print('thread_create_num: ' + str(features.thread_create_num))
 print('max_thread_create_nested: '+ str(features.max_thread_create_nested))
 print('max_thread_num: '+ str(features.max_thread_num))
 print('thread_join_num: '+ str(features.thread_join_num))
 print('max_thread_join_nested: '+ str(features.max_thread_join_nested))
 print('max_join_num: '+ str(features.max_join_num))
 print('pthread_mutex: ' + str(features.pthread_mutex))
 print('atomic: ' + str(features.atomic))
 print('min_val_access_num: '+ str(features.min_val_access_num))
 print('min_val_access_times: '+ str(features.min_val_access_times))
 print('min_func_call_num: '+ str(features.min_func_call_num))
 print('min_func_call_times: '+ str(features.min_func_call_times))
 print('operator_num_inif: ' + str(features.operator_num_inif))
 print('max_iter: ' + str(features.max_iter))
 print('nondet_num: ' + str(features.nondet_num))
 print('max_loops: ' + str(features.max_loops))
  
def main(file):
 features = Feature(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
 out = get_ast_dump(file)
 #print(out)
 root = bulid_tree(out, features)
 construct_global_decl(root, features) 
 construct_val_key_value(features, root)
 operators_in_if(features, root)  
 func_address_match(features, root)
 global_mem_access(features, root)
 genreate_features(features)
 iter_time_in_thread(features, root)
 nondet_in_thread(features, root)
 loops_in_thread(features, root)
 atomic_in_thread(features, root)
 print_features(features)
 operator_num_inif_in_thread(features, root)
 return features
   
if __name__ == "__main__":
 res = main(sys.argv[1])
 exit(0)

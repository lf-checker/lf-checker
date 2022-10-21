#!/usr/bin/python3
import subprocess
import sys
#from src.ClangAST import ProgramFeatures
from anytree import Node, RenderTree, NodeMixin, LevelOrderGroupIter
from anytree.exporter import DotExporter

#dict_func_prev = {} #key: pre_address(pre_declare) value: curr_address


"""
class represents program features.
"""
class Feature():
 def __init__(self, thread_create_num, max_thread_create_nested, thread_join_num, max_thread_join_nested, min_val_access_num, min_val_access_times, min_func_call_num, min_func_call_times):
  self.thread_create_num = thread_create_num
  self.max_thread_create_nested = max_thread_create_nested
  self.thread_join_num = thread_join_num
  self.max_thread_join_nested = max_thread_join_nested
  self.min_val_access_num = min_val_access_num
  self.min_val_access_times = min_val_access_times
  self.min_func_call_num = min_func_call_num
  self.min_func_call_times = min_func_call_times

  self.dict_func_prev = {} #key: pre_address(pre_declare) value: curr_address
  self.dict_val_access = {}
  self.dict_func_call = {}
  self.global_decl_list = []
  self.pthread_create_stmt_list = []
  self.pthread_join_stmt_list = []
 
     
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
def find_nested(TreeNode):
 nest = 0
 while(TreeNode.parent is not None):
  if TreeNode.parent.name == "-DoStmt" or TreeNode.parent.name == "-WhileStmt" or TreeNode.parent.name == "-ForStmt":
   nest += 1
  TreeNode = TreeNode.parent
 return nest 

def construct_global_decl(TreeNode, feature):
 for index, children in enumerate(LevelOrderGroupIter(TreeNode, maxlevel=3)):
  for node in children:
   if index == 2 and node.name == "-FunctionDecl" or node.name == "-VarDecl":
    feature.global_decl_list.append(node.address)
 
def find_pthread_create_call(TreeNode, feature):
 if TreeNode.suffix is not None and "'pthread_create'" in TreeNode.suffix and "-DeclRefExpr" in TreeNode.name:
  nest = find_nested(TreeNode)
  feature.pthread_create_stmt_list.append(pthread_function_call(TreeNode.address, nest))

def find_pthread_join_call(TreeNode, feature):
 if TreeNode.suffix is not None and "'pthread_join'" in TreeNode.suffix and "-DeclRefExpr" in TreeNode.name:
  nest = find_nested(TreeNode)
  feature.pthread_join_stmt_list.append(pthread_function_call(TreeNode.address, nest))

"""
function gets the function address called by the pthread_create
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

def genreate_features(feature):
 feature.thread_create_num = len(feature.pthread_create_stmt_list)
 feature.thread_join_num = len(feature.pthread_join_stmt_list)
 
 for stmt in feature.pthread_create_stmt_list:
  if stmt.level > feature.max_thread_create_nested:
   feature.max_thread_create_nested = stmt.level

 for stmt1 in feature.pthread_join_stmt_list:
  if stmt1.level > feature.max_thread_join_nested:
   feature.max_thread_join_nested = stmt1.level
   
 for item in feature.pthread_create_stmt_list:
  for i in item.func_call.val_list:
   #print(i.address)
   if feature.dict_val_access.get(i.address) is None:
    feature.dict_val_access[i.address] = 1
   else:
    feature.dict_val_access[i.address] += 1
  for j in item.func_call.func_list:
   if feature.dict_func_call.get(j.address) is None:
    feature.dict_func_call[j.address] = 1
   else:
    feature.dict_func_call[j.address] += 1
  
 #print(dict_func_call)
 for key, value in feature.dict_val_access.items():
  if value > 1:
   #print(value)
   feature.min_val_access_num += 1
   feature.min_val_access_times += value
  
 for key1, value1 in feature.dict_func_call.items():
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
   father = child
   pre_index = level
   
 return root

def global_mem_access(feature, root):
 for ob in feature.pthread_create_stmt_list:
  for pre, fill, node in RenderTree(root):
   if node.address == ob.func_call.address:
     for pre1, fill1, node1 in RenderTree(node):
      if node1.suffix is not None:
       if "Var" in node1.suffix or "ParmVar" in node1.suffix:
        #print(node1.suffix)
        for su in node1.suffix:
         if su in feature.global_decl_list:
          #print(node1.suffix)
          nest = find_nested(node1)
          ob.func_call.add_val(su, nest)
          #print(ob.func_call.val_list[0].address)
          #print(ob.func_call.val_list[0].level)

       if "Function" in node1.suffix:
        for su in node1.suffix:
         if su in feature.global_decl_list:
          #print(node1.suffix)
          nest = find_nested(node1)
          ob.func_call.add_func(su, nest)
          #print(ob.func_call.func_list[0].address)
          #print(ob.func_call.func_list[0].level)

def main(file):
 features = Feature(0,0,0,0,0,0,0,0)
 out = get_ast_dump(file)
 root = bulid_tree(out, features)
 construct_global_decl(root, features)   
 func_address_match(features, root)
 global_mem_access(features, root)
 genreate_features(features)
 #print(features.thread_create_num)
 #print(features.max_thread_create_nested)
 #print(features.thread_join_num)
 #print(features.max_thread_join_nested)
 #print(features.min_val_access_num)
 #print(features.min_val_access_times)
 #print(features.min_func_call_num)
 #print(features.min_func_call_times)
 return features
   
if __name__ == "__main__":
 res = main(sys.argv[1])
 exit(0)
 

# Ruby Parsing in sexp's
"""
class Test
  attr_accessor :test
end

test = Test.new
test.test = Test.new
test.test.test = 'test'

# test.test = 'test'
# ------------------
# s(:attrasgn,
#  s(:lvar, :test),
#  :test=,
#  s(:arglist, s(:str, "test")))

# test.test.test = 'test'
# -----------------------
# s(:attrasgn,
#  s(:call, s(:lvar, :test), :test, s(:arglist)),
#  :test=,
#  s(:arglist, s(:str, "test")))
"""

# Syntax
# hello = func {|name|
#   return 'Hello, ' + name + "!"
# }
# hello('John Smith')


# http://sourceforge.net/projects/simpleparse/files/simpleparse/2.1.1a2/SimpleParse-2.1.1a2.zip/download
#from 



from simpleparse.common import numbers, strings, comments

declaration2 = r'''# note use of raw string when embedding in python code...
file           :=  [ \t\n]*, section+
section        :=  '[',identifier!,']'!, ts,'\n', body
body           :=  statement*
statement      :=  (ts,semicolon_comment)/equality/nullline
nullline       :=  ts,'\n'
equality       :=  ts, identifier,ts,'=',ts,identified,ts,'\n'
identifier     :=  [a-zA-Z], [a-zA-Z0-9_]*
identified     :=  string/number/identifier
ts             :=  [ \t]*
'''







syntax = r'''
<ts>              := [ \t]*

# Variable delcarations
local_var         := [a-z], [a-z0-9_]*
global_var        := [A-Z], [a-z0-9_]+

# The chain of indexes and properties for objects
tail              := (index/property/func_call)+
index             := "[", expression, "]"
property          := ".", local_var
func_call         := ts, ("(", arg_list?, ")")/(" "+, arg_list, " "+), ts
arg_list          := ts, expression, ts, (",", arg_list)?

# Structure of the basic code
body              := [ \n\t]*, statement, (terminal, statement)*, terminal?, [ \n\t]*
<terminal>        := ts, ";"/"\n", ts
statement         := assignment/expression
assignment        := identifier, ts, '=', expression

# Basic expressions and grouping (identifiers are like special expressions for variables)
identifier        := local_var/global_var, tail?
expression        := ts, identifier/(expression_group/literal/block, tail?), ts, (operator, ts, expression)?
expression_group  := "(", ts, expression, ts, ")"

# Blocks and their assorted stuff
block             := "{", ("|", param_list, "|")?, body, "}"
param_list        := ts, local_var, ts, (",", param_list)?

operator          := math_op
<math_op>         := "+"/"-"/"*"/"/"

# Literals
literal           := string/number
number            := [1-9], [0-9]*, decimal?
string            := ("\"", -"\""+, "\"")/("'", -"'"+, "'")
<decimal>         := ".", [0-9]+
'''







#test = 'Spam.eggs = {|v| a = 2\nv * 2; }()\nspam.test = "1.0"\neggs = (spam.test + spam.eggs("2.0")("4.0") + ".0") + ".1"\n'
test = 'a = 1.0 + 1.0; Print(a)'

from simpleparse.parser import Parser
parser = Parser(syntax, 'body')

success, resultTrees, nextCharacter = parser.parse(test)

#print success
#print resultTrees
#print 'Next:   '+nextCharacter.__str__()
#print 'Length: '+test.__len__().__str__()+"\n"

def count_newlines(body, index):
  count = 0
  newlines = 1
  while count < index:
    if body[count] == "\n":
      newlines += 1
    count += 1
  return newlines

if nextCharacter != test.__len__():
  print "Parse error around:"
  start = nextCharacter - 10
  if start < 0:
    offset = abs(start)
    start = 0
  else:
    offset = 10
  print repr(test[start:nextCharacter + 10])
  print " " + (" " * offset) + "^ (line %s)" % count_newlines(test, nextCharacter)
  exit()

import pprint
pp = pprint.PrettyPrinter(indent=1)
#pp.pprint(resultTrees)

#def parse_result(body, tree, indent, parent):
#  acc = ''
#  
#  for s in tree:
#    acc += '\n'
#    name = s[0]
#    content = body[s[1]:s[2]]
#    if s[3]:
#      acc += ' ' * indent + '(' + name + ': ' + repr(content) + parse_result(body, s[3], indent + 1, tree) + ')'
#    else:
#      acc += ' ' * indent + '(' + name + ': ' + repr(content) + ')'
#  return acc

#print parse_result(test, resultTrees, 0, [])

import json
def parse_result_list(body, tree):
  acc = []
  
  for s in tree:
    name = s[0]
    content = body[s[1]:s[2]]
    if s[3]:
      acc.append([name, content, s[1], s[2], parse_result_list(body, s[3])])
    else:
      acc.append([name, content, s[1], s[2]])
  return acc

#pp.pprint(parse_result_list(test, resultTrees))

p = parse_result_list(test, resultTrees)
import interpreter
#interpreter.run(p)

interpreter.run(p)
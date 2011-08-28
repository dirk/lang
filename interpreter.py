import pprint
pp = pprint.PrettyPrinter(indent=1)



class TFunc(object):
  def __init__(self):
    self.type = 'func'

class TSFunc(TFunc):
  def __init__(self):
    TFunc.__init__(self)
    self.special = True

class TSPrint(TSFunc):
  def call(self, vals):
    # TODO: Implement primitives
    #print var.prim() # Prim is shorthand for primitive; gets simple version of value suited for output
    print ''.join(map(lambda val: str(val), vals))

class Globals(object):
  do_print = TSPrint()



class Scope(object):
  def __init__(self, parent, scope = {}):
    self.parent = parent
    self.scope = scope
  def interface(self, key):
    return ScopeInterface(self, key)

class ScopeInterface(object):
  def __init__(self, parent, key):
    self.parent = parent
    self.key = key
  def get(self):
    return self.parent.scope[self.key]
  def set(self, val):
    self.parent.scope[self.key] = val
    return val

class Program(object):
  def __init__(self, statements):
    self.statements = statements
    self.globals = Scope(self, {
      'Print': Globals.do_print
    })
    self.locals = Scope(self)
  def load(self):
    for index in range(len(self.statements)):
      self.statements[index] = Statement.new(self.statements[index], self, self)
    self.postload()
    return self
  def run(self):
    for s in self.statements:
      s.execute()
    return self
  def postload(self):
    for statement in self.statements:
      statement.postload()
  
  # Methods to make program act like a statement so that it can serve as a statement parent.
  def scope(self, is_global = False):
    # TODO: Implement global variables
    #if val != None:
    #  self._scope[var.to_s] = val
    #else:
    #  self._scope[var.to_s]
    #if not var.is_a('identifier'):
    #  raise Exception('Unexpected '+repr(var))
    #  return
    #
    #if is_global:
    #  raise Exception('Global variables unimplemented')
    #else:
    #  pointer = var.resolve(self._scope)
    #  if val != None:
    #    pointer.set(val)
    #    return val
    #  else:
    #    return pointer
    if is_global:
      return self.globals
    else:
      return self.locals
  def parent_count(self, s):
    return s - 1

class Statement(object):
  def __init__(self, parts, program, parent):
    # Defaults
    self.children = []
    self.parent = parent
    self.program = None
    self.type = None
    
    # parts ==~ ['statement', "a = b", 0, 4, list of sub-statements]
    self.name    = parts[0]
    self.body    = parts[1]
    self.start   = parts[2]
    self.end     = parts[3]
    
    if parts[4:]:
      for index in range(len(parts[4])):
        s = Statement.new(parts[4][index], self.program, self)
        self.children.append(s)
    self.program = program
  def load(self):
    pass
  def parent_count(self, s = 0):
    if self.parent:
      return self.parent.parent_count(s + 1)
    else:
      return s
  def execute(self):
    for c in self.children:
      c.execute()
  def postload(self):
    if self.type:
      t = 'T'
    else:
      t = None
    n = self.name
    if self.children and self.type:
      n += "(%s,%s)" % (len(self.children), t)
    elif self.type:
      n += "(%s)" % t
    elif self.children:
      n += "(%s)" % len(self.children)
    # DEBUG
    #print (self.parent_count() * ' ') + n.ljust(21) + ': ' + repr(self.body)
    for c in self.children: c.postload()
  
  #def scope(self, var, val = None, is_global = False):
  #  # TODO: Implement global variables
  #  if val != None:
  #    self._scope[var.to_s] = val
  #  else:
  #    self._scope[var.to_s]
  def scope(self, is_global = False): return self.parent.scope(is_global)
  def is_a(self, other):
    return self.type == other
  @classmethod
  def new(cls, slist, program, parent = None):
    #pp.pprint(slist)
    t = slist[0]
    if t == 'body':
      ifunc = SBody
    elif t == 'assignment':
      ifunc = SAssignment
    elif t == 'identifier':
      ifunc = SIdentifier
    elif t == 'expression':
      ifunc = SExpression
    elif t == 'literal':
      ifunc = SLiteral
    elif t == 'operator':
      ifunc = SOperator
    else:
      ifunc = Statement
    
    s = ifunc(slist, program, parent)
    s.load()
    return s


class SBody(Statement):
  def scope(self, is_global = False): return self.parent.scope(is_global)
  def __init__(self, parts, program, parent):
    Statement.__init__(self, parts, program, parent)
    self.type = 'body'
  
class SAssignment(Statement):
  def scope(self, is_global = False): return self.parent.scope(is_global)
  def __init__(self, parts, program, parent):
    Statement.__init__(self, parts, program, parent)
    self.type = 'assignment'
    self.left = self.children[0]
    self.right = self.children[1]
  def execute(self):
    result = self.right.execute()
    #identifier = self.left.execute()
    if not self.left.is_a('identifier'):
      raise Exception('Expected identifier')
    #self.parent.scope(identifier, result)
    self.left.resolve().set(result)
    return result




class ComplexScopeInterface(object):
  def get(self):
    return None
  def set(self, val):
    return val

class SIdentifier(Statement):
  def scope(self, is_global = False): return self.parent.scope(is_global)
  def __init__(self, parts, program, parent):
    Statement.__init__(self, parts, program, parent)
    self.type = 'identifier'
  def execute(self):
    return self.resolve().get()
  def resolve(self):
    #print self
    if self.children[0].name == 'local_var':
      scope = self.parent.scope(False) # Non-global scope
      return scope.interface(self.children[0].body)
    else:
      #raise Exception('Unsupported global variable')
      scope = self.parent.scope(True)
      if len(self.children) > 1:
        tail = self.children[1].children
        index = 0
        val = scope.interface(self.children[0].body).get()
        
        while tail[index:]:
          n = tail[index]
          if n.name == 'func_call':
            func_call = n
            args = map(lambda s: s.execute(), func_call.children[0].children)
            val.call(args)
          index += 1
        return ComplexScopeInterface()
      else:
        return scope.interface(self.children[0].body)
      
    

class SExpression(Statement):
  def scope(self, is_global = False): return self.parent.scope(is_global)
  def __init__(self, parts, program, parent):
    Statement.__init__(self, parts, program, parent)
    self.type = 'expression'
  def execute(self):
    #print self, self.body
    buf = self.children[0].execute()
    index = 1
    while self.children[index:]:
      if self.children[index].is_a('operator'):
        op = self.children[index]
        index += 1
        res = self.children[index].execute()
        if op.operator == 'plus':
          buf += res
        else:
          raise Exception('Unidentified operator: '+op.operator)
      index += 1
    return buf

class SLiteral(Statement):
  def scope(self, is_global = False): return self.parent.scope(is_global)
  def __init__(self, parts, program, parent):
    Statement.__init__(self, parts, program, parent)
    self.type = 'literal'
  def execute(self):
    return eval(self.children[0].body)

class SOperator(Statement):
  def scope(self, is_global = False): return self.parent.scope(is_global)
  def __init__(self, parts, program, parent):
    Statement.__init__(self, parts, program, parent)
    self.type = 'operator'
    self.operator = 'unknown'
    
    if self.body == '+':
      self.operator = 'plus'
  def execute(self): return None
    
    
    

#g = Generic(['test', 'test', 0, 1])


def run(statements):
  p = Program(statements).load().run()
  #print p.scope().scope
  #pp.pprint(p)
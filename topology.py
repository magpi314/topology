#  creates something like a 'manifold' data type

ALPHA = 'abcdefghijklmnopqrstuvwxyz'

class InvalidStringError(Exception):
   def __init__(self, message = 'invalid plane model string.'):
      print(message)

class EdgeNotFoundError(Exception):
   def __init__(self, message = 'edge(s) not found in plane representation'):
      print(message)

class Manifold:
   _t_class = ''
   _chi = 0
   _string = ''
   _normal_form = ''
   paths = [] # this will be a collection of '_Path' objects

   def __init__(self, string):
      # dimension? it's always 2 right now...
      # operations: cartesian product?
      # can i represent an n dimensional manifold with an n-1 dimensional array?
      edges = []
      if not _check_string(string): raise InvalidStringError
      if len(string) > 52: raise InvalidStringError
      s = string  
      self._string = s
      for i in range(len(s)):
         edges.append(s[i])
      nodes = [None] * (len(edges) + 1)
      nodes[0] = 0
      nodes[len(edges)] = 0

      while _empty_nodes(nodes):
   
         for k in range(2):   
            # making it do this twice is not the best way...but it works!
            for i in range(len(nodes)):
               nn = nodes[i]  # this is the name of the node we're looking at
               if nn == None: continue
               try:
                  atbuttof = edges[i]
               except:
                  atbuttof = edges[0]
               try:
                  atpointof = edges[i-1]
               except:
                  atpointof = edges[len(edges)-1]
               for j in range(len(edges)):
                  edge = edges[j]
                  if edge == atbuttof or edge == _altcase(atpointof):
                     nodes[j] = nn
                  if edge == atpointof or edge == _altcase(atbuttof):
                     nodes[j + 1] = nn
         if _empty_nodes(nodes):
            nodes[nodes.index(None)] = max(x for x in nodes if x not in {None}) + 1 # look for first empty and fill it
            
      self._chi = int(2 - len(edges) / 2 + max(nodes))
   
      if self.orientable == True:
        # it's nTor or Sph
         n = int((2 - self._chi) / 2)
         if n == 1: n = ""
         self._t_class = "S" if n == 0 else str(n) + "T"
         if self._t_class == "S":
            self._normal_form = sphere()
         else:
            if n == "": n = 1
            self._normal_form = torus(n)
      else:
         # it's nProj
         n = 2 - self._chi
         if n == 1: n = ""
         self._t_class = str(n) + "P"   
         if n == "": n = 1   
         self._normal_form = proj(n)
      
      return

   def path(self, string):
      pass

   @property
   def orientable(self):
      return True if len(set(self.string)) == len(self.string) else False

   @property
   def string(self):
      return self._string

   @property
   def t_class(self):
      return self._t_class

   @property
   def chi(self):
      return self._chi

   @property
   def normal_form(self):
      return self._normal_form
      
   def __repr__(self):
      return "< i would like this to work>"

   def __add__(self, other):
      if not isinstance(other, Manifold): raise TypeError("expected <Class 'Manifold'> got {}.".format(type(other)))
      a = str(self)
      b = str(other)
      if len(a) + len(b) > 52: raise OverflowError('done because we are too menny.')
      b = _reparse(b, len(a)/2)
      typ = Manifold(a + b).t_class
      s = typ if len(typ) == 1 else typ[1]
      n = 1 if len(typ) == 1 else int(typ[0])
      if s == "S": return Manifold(sphere())
      if s == "T": return Manifold(torus(n))
      if s == "P": return Manifold(proj(n)) 
   
   __radd__ = __add__
   
   #  other valid topological operations (aside from cut/paste):
   #  [x] a [y] A <--> [x] A [y] a     doesn't do much?
   #  [x] a [y] a <--> [x] A [y] A     should i bother?
   #

   #  aA <--> null   a type of 'cancelling'
   #        perhaps this way
   #  surf.join(aa) ' looks for aa and deletes it
   
   #  surf.rewrite() ' rewrites surf, making it ALPHAical?
     
   def split(self, string):
      if string not in self.string: raise EdgeNotFoundError
      if len(string) > 1: 
         raise InvalidStringError('only on edge may be be split at a time')
      model = self.string
      if _altcase(string) in model and model.index(string) > model.index(_altcase(string)):
         string = _altcase(string)
      try:
         firstpos = model.index(string)
      except:
         firstpos = model.index(_altcase(string))
      try:
         lastpos = model[(firstpos + 1):].index(string) + firstpos + 1
      except:
         lastpos = model[(firstpos + 1):].index(_altcase(string)) + firstpos + 1
      same = model[firstpos] == model[lastpos]
      #  the letters are in positions firstpos and lastpos
      #  same is true if they're the same case, false if not
      firstrepl = string + _next_letter(model)
      if same == True:
         lastrepl = firstrepl
      else:
         lastrepl = _altcase(_next_letter(model)) + _altcase(string)
      retstring = model[0:firstpos] + firstrepl
      retstring += model[firstpos + 1:lastpos] + lastrepl
      retstring += model[lastpos + 1:len(model)]
      print(retstring)
      self.__init__(retstring)

   def join(self, string):
      #  [x] ab [y] BA <--> [x] a [y] A   one way 'splits'
      #  [x] ab [y] ab <--> [x] a [y] a   the other way 'joins'
      #
      #  surf.split(a) ' looks for a, replaces it with a[nextletter]
      #                ' and replaces altcase(a) with [NEXTLETTER]A
      #  surf.join(ab) ' looks for ab, another ab or BA,
      #                ' replaces ab with a and BA with A if applicable   
      if len(string) != 2: 
         raise InvalidStringError('only two edges may be joined')
      if string not in self.string: raise EdgeNotFoundError
      opstr = _altcase(string[0]) + _altcase(string[1])
      if self.string.count(string) + self.string.count(opstr) != 2:
         raise InvalidStringError('these edges may not be joined')
            
     
class _Path:
   def __init__(self, f, t):
      # a path is drawn from the beginning, middle, or end of one path
      # to the beginning, middle, or end of another.
      # to actually look at the plane, it might look like multiple lines.
      #
      # if you cut along the line, you'll end up with several children.
      #        a            A
      #   tail^ ^head  head^ ^tail
      pass

   
def sphere():
   return 'aA'
   
def proj(n):
   if n == 1: 
      retString = 'aa'
   else:
      retString = ''
      for i in range(n):
         retString += ALPHA[i] * 2
   return retString
   
def torus(n):
   if n == 1: 
      retString = 'abAB'
   else:
      retString = ''
      for i in range(n):
         retString += ALPHA[2 * i] + ALPHA[2 * i + 1]
         retString += ALPHA[2 * i].upper() + ALPHA[2 * i + 1].upper()
   return retString
       
def _next_letter(string):
   s = string.lower()
   return ALPHA[ALPHA.index(max(string)) + 2]

def _reparse(string, begin):
   newstring = ''
   begin = int(begin)
   for i in range(len(string)):
      oldch = string[i]
      if oldch.islower():
         newch = ALPHA[ALPHA.index(oldch) + begin]
      else:
         newch = ALPHA[ALPHA.index(oldch.lower()) + begin].upper()
      newstring += newch
   return newstring

def _empty_nodes(nodes):
   return None in nodes 

def _altcase(ch):
   # return opposite case of character l
   if ch.isupper(): 
      return ch.lower() 
   else:
      return ch.upper()

def _check_string(string):
   # check the string to see if it's a valid plane diagram
   if not string.isalpha(): return False
   scheck = string.lower()
   for i in range(len(scheck)):
      if scheck.count(scheck[i]) != 2:
         # print(str(scheck.count(scheck[i])) + ' instances of ' + scheck[i])
         return False
   return True
   
if __name__ == '__main__':
   # ask user to create the plane diagram string
   print('use single characters to label edges, capital and lower case to indicate opposing directions.')
   s = raw_input('Enter plane string: ')
   #a = Manifold(torus(1))
   #b = Manifold(torus(1))
   pm = Manifold(s)
   
   print('euler characteristic: ' + str(pm.chi))
   print('orientable: ' + str(pm.orientable))
   print('topological class: ' + pm.t_class)
   print('string: ' + pm.string)
   print('normal form: ' + pm.normal_form)
   print('next letter: ' + next_letter(pm))

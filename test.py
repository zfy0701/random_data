#############################
# Type syntax (provisional) #
#############################
### Typing judgement:
# name : type

### Classic type system:
#- class types: int, float, str, ClassA, ClassB, ...
#- classes themselves: <int>, <float>, <str>, <ClassA>, <ClassB>, ...
#- function types: int -> str, A -> B, ...
#- tuple types: (int, float), (A, B, C), ...
#               single element tuples are considered scalar and no parenthese will be added.
#               so you have "A -> B" instead of "(A) -> B".
#- list types: [int], [A], [(A, B)], ...
#- dict types: {int => str}, {A => B}

### Extended type system:
#- union types: {int | str}, {A | B | C}, ...
#- recursive types (types with components that are themselves): #1(int,1), #2(int -> 2), ...
#- open types (we don't what it is, but we do know what fields it should have): ?[a : int, b : str], ...
#- error type (type error was found with this value): !


#################################
# Inter-procedual flow-analysis #
#################################
# Given a function with a parameter 'x' and the function tries to access
# the 'z' field in this x. How would you know where 'z' is defined? PySonar
# accurately locates those fields by using inter-procedual control-flow
# analysis.

class A1:
  z = 1

class B1:
  z = A1()

class C1:
  z = B1()

o1 = C1()

def f1(x):
  return x.z   # Moving the cursor to 'z' will highlight the z inside class C1 only ...

f1(o1)         # ... because f1 tries to access the 'z' field of o1 (type C1) only

def g1(x):
  return x.z   # Moving the cursor to 'z' will highlight the z inside B1 and C1 ...

g1(g1(o1))     # ... because g1 accesses C1.z which is a B1, then g1 accesses B1.z which is A1

def h1(x):
  return x.z   # Moving the cursor to 'z' will highlight the z inside A1, B1, C1 ...

h1(h1(h1(o1))) # ... bacause h1 accesses C1.z which is a B1, then followed by B1.z, A1.z



########################
# High-order functions #
########################
# Function f2 is "mapped" to a list containing A2 and B2 objects and access
# their 'w' fields. The map function below is a high-order function which
# takes another function (f2) as an argument. PySonar will find both w's in
# A2 and B2 when asked for it in f2.

class A2:
  w = 'Boeing'

class B2:
  w = 787

def f2(y):
  return y.w  # Moving the cursor to 'w' will highlight w inside both A2 and B2

def map(f, ls):
  if (len(ls) == 0):
    return []
  else:
    return [f(ls[0])] + map(f, ls[1:])

a = [A2(), B2(), A2()]

b = map(f2, a)

print b



#####################
# curried functions #
#####################
# Move the cursor to curr, curr1, curr2, curr3 to show type hints.
# Like ML or Haskell, the arrow operator is right-associative,
# so you see "int -> int -> int" instead of "int -> (int -> int)"

def curr(x):
  return lambda y: lambda z: x + y + z

curr1 = curr(1)
curr2 = curr1(2)
curr3 = curr2(3)



#####################
# "Dependent types" #
#####################
# Because types are first-class citizen in Python, it is natural for Python
# programmers to use "dependent types", which essentially are type-space
# computations (use arbitrary computation to generate types, and then use
# them). Here, the function Foo may output different types randomly.
class A3:
  w = 'OTP'

class B3:
  w = 263950

def Foo(x):
  if (random(x) < 100):
    return A3
  else:
    return B3

Type1 = Foo(30)
obj1  = Type1()

print obj1.w  # Moving the cursor to 'w' will highlight w in both A3 and B3



###############################
# parametric types (generics) #
###############################
# PySonar handles common parametric types such as lists etc.
class A5:
  w = 1

class B5:
  w = 'cherry'

ls = [A5(), A5()]
ls[1] = B5()         # Here the type of list 'ls' is "[{A5 | B5}]" meaning "a list of A5 or B5"

print ls[0].w        # Moving cursor to 'w' will highlight both 'w's in A5 and B5



###################
# recursive types #
###################
# PySonar's recursive types are the general mu-types in type theory
# literature. PySonar uses a notation much like mu-types. For example,
# #1(1->int) means (mu x. x->int). These types can be infinite.

# Function which returns a tuple of itself
# StrangeLoop : #1() -> (1, 1)
# Here #1 is an "anchor" denoting the function type itself, the two "1"s
# inside the tuple "reference" the anchor, so that the tuple contains two
# references to the function itself. Using ths notation we can denote any
# recursive type.
def StrangeLoop():
  return (StrangeLoop, StrangeLoop)

# A tuple containing itself as an element
# tup : #1(str, str, 1)
tup = ('kitty', 'chase', 'tail')
tup[2] = tup



################################################
# open types (a la OCaml)                      #
# (unknown types with certain required fields) #
################################################
# The type of x below is displayed as ?[a : ?, b : ?], meaning that the
# parameter x must have the fields a and b, but their types are unknown.

def WhatEverWithAB(x):
  print x.a, x.b
  return 0



##########################
# dynamic field creation #
##########################
# PySonar can track down the dynamically created fields such as the 'y'
# field inside o2.
class A6:
  w = 1

o2 = A6()
o2.y = 3

print o2.w, o2.y  # move cursor to 'y' and o2.y above should be highlighted



########################
# multiple definitions #
########################
# In Python a name may have multiple locations of definitions. PySonar
# tracks down all of them.
if (x < 12):
  class A7:
    w = 1
else:
  class A7:
    w = 1

o7 = A7()     # highlights both A7 definitions above
print o7.w    # highlights both 'w' fields in A7's definitions



###############
# Bug finding #
###############

# "Undefined fields" and their consequences. This is probably the only
# perceived phenomenon when "type errors" happen in Python. This uniformity
# is a very nice property of Python.
class AC:
  f14 = 'Tomcat'

lincoln = AC()

def TopSecret(x):
  return x.f22                  # 'f22' is not defined in an instance of AC

raptor = TopSecret(lincoln)     # raptor is not defined as a consequence
icecream = raptor.missle        # icecream is not a missle
icecream.fire()                 # Can't fire icecream
raptor.gun = 'M61'              # Can't install a gun in a nonexistent aircraft



# Function not always return a value. One branched conditional returns a
# string if the condition is true, but no return value otherwise.
def F(x):
  if (x < 1):
    return 'B-2'

# G is contaminated by F so it also misses return values
def G(y):
  if (y < 2):
    return F(y + 1)             # F may not return a value, thus G.
  else:
    return 'H-bomb'

print G(5)

# No problem for H because H doesn't return values in any case
def H(x):
  y = 'What am I doing here?'
  if (x < 1):
    print 'hard data is'        # None
  else:
    print 'good to find'        # None

H(3)

# Unreachable code
def Google(hour):
  if (hour <= 10):
    return 'breakfast'
  elif (hour < 13):
    return 'lunch'
  elif (hour < 20):
    return 'dinner'
  else:
    return 'snack'
  return 'hungry'              # unreachable code

Google(random(24))



#######
# ;-) #
#######
# A popular problem control-flow analysis may run into is the halting
# problem. If calls are followed every time, there could be infinite loops
# that cause the analyzer not to terminate. PySonar deals with this by
# memorizing input types.
class Halting:
    z = 1

class Problem:
    z = Halting()

class Solved:
    z = Problem()

o3 = Solved()

def f(x):
  f(x.z) # move cursor to 'z' will highlight all three 'z' fields above and one error message

f(o3)

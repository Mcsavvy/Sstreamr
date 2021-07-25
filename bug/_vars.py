INVOKE = """
TRIGGER
========
{fn[trigger]}

CALLBACK
========
{fn[function]}

RESULT
======
{fn[result]}
"""

PARSE_SLICE_SYNTAX = """
CORRECT SYNTAX
==============
Callback[Callable]

Callback[Callable]:

Callback[...]:Args[Iterable]

Callback[...]::Kwargs[dict]

Callback[...]:Args[...]:Kwargs[...]
"""

ON_SYNTAX = """
CORRECT SYNTAX
==============
Exception, Callback[Callable]

Exception, Callback[Callable]:

Exception, Callback[...]:Args[Iterable]

Exception, Callback[...]::Kwargs[dict]

Exception, Callback[...]:Args[...]:Kwargs[...]
"""

USAGE = """
The goal is to handle errors gracefully.
For now let's just call it Bug

FEATURES
========
* Drown errors that don't matter
* Set Callbacks for different error encountered
* capture errors by their message using regular expressions

USAGE
=====
In [1]: # import the three core objects

In [2]: from bug import Bug, Expect, Bind

In [4]: # using Expect to catch Exceptions before they occur                    
                                                                                
In [5]: # Regular usage                                                         
                                                                                
In [6]: bugs = Expect([TypeError, NameError])                                   
HandledBug('...')                                                               
                                                                                
In [7]: # Then just refer to it in a with block                                 
                                                                                
In [8]: with bugs:                                                              
   ...:     # let's create an Exception on purpose                              
   ...:     raise NameError                                                     
   ...:                               
# Nothing happens!
                                                                         
In [9]: # okay, that was a little too boring, watch this...                     
                                                                                
In [10]: # we can assign functions to Exceptions                                

In [11]: bugs.on(NameError, print, 'now', 'this', 'is', 'cool!', sep=" ")       
Out[11]: bug.exceptions.Bug('...')                                              
                                                                                
In [12]: # now let's raise an Exception again                                   
                                                                                
In [13]: with bugs:                                                             
    ...:     # let's create an Exception on purpose                             
    ...:     raise NameError                                         
    ...:                                                                        
now this is cool!                                                               
                                                                                
TRIGGER
========
<class 'NameError'>
                                                                      
CALLBACK                                                                        
========                                                                        
print('now', 'this', 'is', 'cool!', sep=' ')                                    
                                                                                
RESULT                                                                          
======                                                                          
None                                                                            
                                                             
                                                                    
In [14]: 
"""

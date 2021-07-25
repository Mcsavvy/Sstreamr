# Goal

the goal is to seamlessly handle exceptions raised during runtime
exceptions should be treated as part of your programs

## Bug as an object
Bug is the main exception object

* catching exceptions programmatically
_context managers_

> with Bug({exception}) as bug:
    bug.throwIf(TypeError)
    <!-- Continues to run if not isintance({exception}, TypError) -->
> with Bug({exception}) as bug:
    bug.throwifNot(Exception)
    <!-- Continues to run if isinstance({exception}, Exception) -->
    <!-- This can be used in cases of SystemExit or KeyboardInterrupt -->
> with Bug({exception}) as bug:
    bug.on(BaseException, print, 'System Exit!')
    bug.throwIfNot(Exception)
    <!--
    If not isinstance({{exception}, Exception})
    'SystemExit!' is printed then the exception is thrown
    many callbacks can be specified
    -->

_decorators_
: the function must accept 'bug' keyword argument

> @Bug()
  def divide_100_by(number: int, bug=None) -> int:
    bug.on(BasException, print, 'wrong input!')
    bug.on(ZeroDivisionError, print, 'Cannot divide with 0')
    bug.on(TypeError, print, 'Must be an integer')
    bug.throwIfNot([TypeError, ZeroDivisionError])
    bug.call(print, 'correct input!')
    return 100 // number
> divide_100_by('not an integer')
wrong input!
Must be an integer
> divide_100_by(0)
wrong input!
Cannot divide with 0
> divide_100_by(5)
correct input!
20

* NOTE: ALL CALLBACKS WOULD BE  CALLED IN THE ORDER THEY WERE ADDED
* NOTE: ANY EXCEPTION THROWN WHILE HANDLING A CALLBACK IS RAISED
* INFO: YOU CAN ACCESS THE RETURN VALUES OF CALLBACKS BY SETTING A __key__ FOR IT
> bug.on(Exception, list, "exception", __key__='list')
<!-- after callback is invoked -->
> bug['list']
['e', 'x', 'c', 'e', 'p', 't', 'i', 'o', 'n']
> bug.call(list, 'bugfree', __key__='list__')
<!-- after callback is invoked -->
> bug['list__']
['b', 'u', 'g', 'f', 'r', 'e', 'e']


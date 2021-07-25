# from collections import defaultdict, deque
from re import S
import re
import typing
from copy import deepcopy

class Contraint:
    def __init__(self, name, types: typing.Union[type]) -> None:
        self._name = name
        self._type = types

    def __get__(self, instance, cls):
        if instance is None:
            return self
        else:
            return instance.__dict__[self._name]
    
    def __set__(self, instance, value):
        if not isinstance(value, self._type):
            raise TypeError(f'Expected {self._type} not {type(value)}')
        instance.__dict__[self._name] = value
    
    def __delete__(self, instance):
        del instance.__dict__[self._name]

'''
Creating a context variable manager the gets attributes based on the present
context

with ctx() as a:
    a.list = [a]
    with a:
        a.list.append(b)
        # list contains [a, b]
    # list contains only [a]

'''

class Nested(list):
    """
    Reentrant context manager
    """

    class CTX(dict):
        def __missing__(self, key):
            return 'not-set'

    def __init__(self, keep_last_context: bool = True) -> None:
            self._max = 200
            self._ctx_vars = set()
            super().__init__(
                [self.CTX()]
            )
            self._is_base = True

    def __getitem__(self, name):
        if isinstance(name, (int, slice)):
            return super().__getitem__(name)
        return super().__getitem__(-1)[name]

    def __setitem__(self, name, value):
        if isinstance(name, int):
            
            return super().__setitem__(name, value)
        return super().__getitem__(-1).__setitem__(name, value)

    def append(self, __object) -> None:
        if not isinstance(__object, self.CTX):
            raise RuntimeError("Cannot set context variable")
        return super().append(__object)
    def clear(self):
        raise RuntimeError("Can't clear contexts")
    def index(self, __value, __start: int, __stop: int) -> int:
        raise RuntimeError(
            "Use [<index>] to get a particular context or [<var>] to get a context variable"
        )
    def pop(self, __index: int = -1) -> object:
        if __index != -1:
            raise RuntimeError('Program attempting to skip nesting.')
        return super().pop(__index)
    def insert(*args) -> None:
        raise RuntimeError("Can't insert contexts")
    def reverse(self) -> list:
        return self[:].reverse()
    def remove(self, __value) -> None:
        raise RuntimeError("Can't remove contexts")
    def count(self, __value) -> int:
        count = 0
        for ctx in self:
            if __value in ctx:
                count += 1
        return count
    
        
    def __enter__(self):
        if self._is_base:
            self['that'] = self[-1]
            self._base = len(self) - 1
            self['this'] = self[-1]
            self._is_base = False
            print("entering base context[{}]".format(len(self)))   
            return self
        if self._max <= len(self):
            raise RuntimeError(
                "Max Context Nesting Reached"
            ) from None
        print("entering nested context[{}]".format(len(self) + 1))
        self['that'] = self[-1]       
        self.append(deepcopy(self[-1]))
        self['this'] = self[-1]
        return self

    def __exit__(self, *exc_info):
        if not hasattr(self, '_base'):
            raise RuntimeError("Trying to exit context that was not entered")
        if len(self) == self._base + 1:
            print("leaving base context[{}]".format(len(self) - self._base))
            self._is_base = True
            return
        print("leaving nested context[{}]".format(len(self)))
        self.pop()
        

        
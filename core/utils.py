from collections.abc import Iterable
from collections import OrderedDict
import os
import random
from inspect import signature
import sys
from typing import Mapping, Tuple
from math import ceil
from django.conf import settings
import stackprinter
from datetime import datetime


class Attr:
    def __init__(self, obj):
        self.obj = obj

    def __repr__(self):
        return repr(self.obj)

    def __str__(self):
        return self.__repr__()

    def __getattr__(self, name):
        if name not in self.__dict__:
            return getattr(self.obj, name, Attr(name))
        return self.__dict__[name]

    def __len__(self):
        return len(self.obj)

    def __bool__(self):
        return bool(self.obj)

    def __iter__(self):
        return iter(self.obj)

    def __call__(self, *_, **__):
        return


def position(integer: int):
    raw = str(integer)
    if integer > 3 and integer < 21:
        return raw + "th"
    elif raw.endswith("1"):
        return raw + "st"
    elif raw.endswith("2"):
        return raw + "nd"
    elif raw.endswith("3"):
        return raw + "rd"
    else:
        return raw + "th"


is_type = {
    'function': lambda x: isinstance(x, type(Attr.__call__)),
    'method': lambda x: isinstance(x, type(Attr(0).__call__))
}


def pos(integer: int):
    raw = "pos" + str(integer)
    return raw


def prange(Range: int):
    return [pos(i + 1) for i in range(Range)]


def pmap(data: Iterable):
    if not isinstance(data, Iterable):
        return {"pos1": Attr("Data cannot be parsed")}
    od = OrderedDict()
    for i in range(len(data)):
        od[pos(i + 1)] = data[i]
    return od


def _2Dmap(_2Darray):
    mapped = []
    for cols in _2Darray:
        mapped.append(pmap(cols))
    return pmap(mapped)


def _2Darray(data, shape: Tuple[int, int], spillover=True, fillempty=object, loop=True, shuffle=False):
    DATA = list(data)
    if shuffle:
        random.shuffle(DATA)
    grid = []
    r, c = shape
    # iterate through number of rows
    for row in range(r):
        # each row should be an Attr
        ROW = Attr([])
        # iterate through the number of column  supposed to be in a row
        for col in range(c):
            # pop items from the data and append to the column till it is filled
            try:
                ROW.append(DATA.pop(0))
            # data is exhausted
            except IndexError:
                # allows data to be exhausted
                if spillover:
                    # value to use to fill empty column spaces
                    if fillempty is not object:
                        # format fillempty with local variables
                        if isinstance(fillempty, str):
                            ROW.append(fillempty.format(**locals()))
                        else:
                            ROW.append(fillempty)
                    # no value set to fill empty spaces
                    else:
                        pass
                else:
                    raise IndexError(
                        f'Can\'t apply {shape} shape on data of length {len(data)}, use data of lenght {r * c} or greater'
                    )
        if ROW:
            grid.append(ROW)
    for index, row in enumerate(grid):
        row.this = index
        row.slide = index + 1
        try:
            row.next = grid[index + 1]
        except IndexError:
            if loop:
                try:
                    row.next = grid[0]
                except IndexError:
                    row.next = None
            else:
                row.next = None
        row.parent = grid
    return grid


def grid(
    data, *, height=None, width=None,
    shuffle=False, slide=0, loop=True,
    spillover=False, fillempty=None
):
    if not isinstance(data, Iterable):
        raise TypeError(
            f'grid: expected an Iterable not {type(data)}'
        )
    data = list(data)
    if isinstance(data, Mapping):
        raise TypeError(
            f'grid: not expecting a mapping'
        )
    if not any((height, width)):
        raise TypeError(
            f'grid: no height or width specified'
        )
    if all((height, width)):
        area = (height * width)
        data = data[:area]
    else:
        if height:
            width = ceil(len(data) / height)
        elif width:
            height = ceil(len(data) / width)
    grid = _2Darray(
        data, shape=(height, width),
        loop=loop, fillempty=fillempty,
        spillover=spillover, shuffle=shuffle
    )
    try:
        return grid[(slide % len(grid)) - 1] if slide else grid
    except ZeroDivisionError:
        return grid


def gridmap(data, xrows=None, ycols=None):
    grid_ = grid(data, xrows, ycols)
    return _2Dmap(grid_)


def arg_parser(arguments):
    """
    turn a single string to *args and **kwargs
    sample positional only arguments;
        'foo&&bar&&baq' => (foo, bar, baq)
    sample keyword only arguments;
        '??foo=True&&bar=False&&baq=None' => (foo=True, bar=False, baq=None) 
    sample *args and **kwargs;
        'foo&&bar??baq=True' => (foo, bar, baq=True)
    """
    arguments = arguments.split("??")
    if arguments[1:2]:
        has_kwargs = True
    else:
        has_kwargs = False
    if arguments[0:1]:
        has_args = True
    else:
        has_args = False
    if has_args:
        args = []
        for x in arguments[0].split("&&"):
            try:
                args.append(eval(x))
            except Exception:
                args.append(x)
    if has_kwargs:
        kwargs = {}
        for x in arguments[1].split("&&"):
            _ = x.split("=")
            if _[0:1] and _[1:2]:
                try:
                    kwargs[_[0]] = eval(_[1])
                except Exception:
                    kwargs[_[0]] = _[1]
    else:
        kwargs = {}
    return args, kwargs

def arg_writer(*args, **kwargs):
    """
    turn *args and **kwargs to a single string using "??"
    to seperate args from kwargs and "&& to seperate arguments
    sample positional only arguments;
        (foo, bar, baq) => 'foo&&bar&&baq'
    sample keyword only arguments;
        (foo=True, bar=False, baq=None) => '??foo=True&&bar=False&&baq=None'
    sample *args and **kwargs;
        (foo, bar, baq=True)  => 'foo&&bar??baq=True'
    """
    positional = ""
    for x in args:
        positional += f"{x!r}&&"
    if positional:
        positional = positional[:-2]
    keywords = ""
    for k, v in kwargs.items():
        keywords += f"{k}={v!r}&&"
    if keywords:
        keywords = keywords[:-2]
    return "{}??{}".format(positional, keywords)
    


def whatCallable(o):
    import typing
    if not isinstance(o, typing.Callable):
        raise TypeError('whatCallable(o) expected a callable')
    if type(o) == type:
        return 'class'
    if hasattr(o, '__qualname__'):
        # not a class
        if 'self' in signature(o).parameters:
            return 'class-method'
        if type(o).__name__ == 'function':
            return 'function'
        if type(o).__name__ == 'method':
            return 'method'
    else:
        if hasattr(o, '__init__'):
            if 'self' in signature(o.__init__).parameters:
                return 'class'
            elif hasattr(o, '__call__'):
                return 'instance'
    breakpoint()
    # need to inspect o


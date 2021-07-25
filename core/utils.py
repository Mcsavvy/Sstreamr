from collections.abc import Iterable
from collections import OrderedDict
import random
from inspect import signature


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


def _2Darray(data, c, r, spillover=True, fillempty=None, loop=True):
    reverse_data = data[::-1]
    grid = []
    for row in range(r):
        ROW = Attr([])
        for col in range(c):
            try:
                ROW.append(reverse_data.pop())
            except IndexError:
                if spillover:
                    if fillempty:
                        if isinstance(fillempty, str):
                            debug = fillempty.format(**locals())
                            ROW.append(debug)
                        else:
                            ROW.append(fillempty)
                    else:
                        if ROW:
                            grid.append(ROW)
                        return grid
        grid.append(ROW)
    for index, row in enumerate(grid):
        try:
            row.this = index
            row.slide = index + 1
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
    data, num_of_cols=None, num_of_rows=None, *,
    shuffle=False, slide=0, loop=True,
    spillover=False, fillempty=""
):
    if not isinstance(data, Iterable):
        return [[Attr("Data cannot be parsed.")]]
    data = list(data)
    if isinstance(data, dict):
        return [[Attr("Dict object not accepted.")]]
    if not any((num_of_rows, num_of_cols)):
        return [[Attr("No height or width detected.")]]
    if all((num_of_rows, num_of_cols)):
        area = (num_of_rows * num_of_cols)
        data = data[:area]
    else:
        if num_of_rows:
            num_of_cols = len(data) // num_of_rows
        elif num_of_cols:
            num_of_rows = len(data) // num_of_cols
    grid = _2Darray(
        data, num_of_cols, num_of_rows,
        loop=loop, fillempty=fillempty,
        spillover=spillover
    )
    if shuffle:
        random.shuffle(grid)
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
    for k, v in kwargs.keys():
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

    
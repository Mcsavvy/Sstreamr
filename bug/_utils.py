from inspect import signature
import typing
import re
try:
    from ._vars import *
except ImportError:
     from _vars import *
from collections import OrderedDict, namedtuple


class HandledBug(Exception):
    """
    The base exception class for all handled bugs
    """


class DrownedBug(HandledBug):
    """
    The base exception class for all drowned bugs
    """


class UnExpectedBug(Exception):
    """
    The base exception class for all unexpected errors
    """


class AnonymousError(HandledBug):
    """
    UnNamed Errors
    """


class ReRaised(Exception):
    "For exceptions that are reraised"


def _makeRepr(function, *position_arguments, **keyword_arguments):
    if not callable(function):
        return
    name = function.__name__ if hasattr(
        function,
        '__name__'
    ) else function.__class__
    args = ', '.join(f"{x!r}" for x in position_arguments) + (
        (', ' if position_arguments else '') if keyword_arguments else ''
    )
    kwargs = ', '.join(
        f"{x}={keyword_arguments[x]!r}" for x in keyword_arguments
    )
    return f"{name}({args}{kwargs})"


def _isBug(
    bug: BaseException, throw=True
) -> tuple((bool, bool)):
    is_exception = False
    is_instance = True
    if not isinstance(bug, BaseException):
        if isinstance(bug, type):
            if issubclass(bug, BaseException):
                is_exception = True
                is_instance = False
    else:
        is_exception = True
    if not is_exception and throw:
        raise TypeError(
            'bug must be an instance or subclass of BaseException.'
        ) from None
    return is_exception, is_instance


def _flatten_(
    o: typing.Union[
        Exception,
        typing.Iterable[Exception],
        typing.Callable
    ]
):
    is_bug, _ = _isBug(o, throw=False)
    if isinstance(o, str) and bool(o):
        yield o
    elif isinstance(
        o, (tuple, set, list)
    ):
        for i in o:
            yield from _flatten_(i)
    elif is_bug:
        yield o

def _compare(
    signal: typing.Union[BaseException, str],
    event: typing.Union[BaseException, str],
    matchMessage: bool = False,
    allow_str_event: bool = True
):
    sig_exc, sig_inst  = _isBug(signal, throw=False)
    ev_exc, ev_inst = _isBug(event,throw=not allow_str_event)

    def match_exc_exc(sig, ev):
        if sig_inst:
            if ev_inst:
                # check to see if they are of the same type
                same_type = isinstance(sig, ev.__class__)
                both_have_message = all(
                    getattr(e, 'args') for e in (sig, ev)
                )
                if same_type:
                    if matchMessage:
                        if both_have_message and re.search(
                            str(sig.args[0]), str(ev.args[0])
                        ):
                            return True
                    else:
                        return True
                else:
                    if matchMessage:
                        if both_have_message and re.search(
                            str(sig.args[0]), str(ev.args[0])
                        ):
                            return True
                return False
            else:
                if isinstance(sig, ev):
                    return True
                else:
                    if matchMessage:
                        return bool(re.search(
                            str(sig) or repr(sig),
                            repr(ev)
                        ))
        else:
            if ev_inst:
                if issubclass(sig, ev.__class__):
                    return True
                if matchMessage:
                    return bool(
                        re.search(
                            sig.__name__, str(ev) or repr(ev)
                        )
                    )
            else:
                return issubclass(sig, ev) or bool(
                    re.search(sig.__name__, ev.__name__)
                )
        return False

    def match_str_exc(sig, ev):
        if ev_inst:
            if str(ev):
                if re.search(sig, ev.__class__.__name__):
                    return True
                else:
                    return bool(re.search(sig, str(ev)))
            if matchMessage:
                return bool(re.search(sig, str(ev) or ev.args[0] or repr(ev)))
        else:
            return bool(re.search(sig, ev.__name__))
        return False

    def match_exc_str(sig, ev):
        return match_str_exc(ev, sig)

    def match_str_str(sig, ev):
        return bool(re.search(sig, ev))

    if ev_exc:
        if sig_exc:
            return match_exc_exc(signal, event)
        return match_str_exc(signal, event)
    else:
        if sig_exc:
            return match_exc_str(signal, event)
        return match_str_str(signal, event)


def _parseSlice(slice_: slice):
    try:
        if not isinstance(slice_, slice):
            if isinstance(slice_, typing.Callable):
                _callback, _args, _kwargs = slice_, tuple(), dict()
            else:
                raise TypeError(
                    f"Expected a callable but got [{type(slice_)}]"
                )
        else:
            if isinstance(slice_.start, typing.Callable):
                _callback = slice_.start
            elif isinstance(slice_.stop, typing.Callable):
                return slice_.stop, tuple(), dict()
            else:
                raise TypeError(
                    "slice expected a callable as "
                    f"first argument but got [{type(slice_.start)}]"
                )
            if isinstance(slice_.stop, typing.Iterable):
                _args = tuple(slice_.stop)
            elif slice_.stop is None:
                _args = tuple()
            else:
                raise TypeError(
                    "slice expected a Sequence as "
                    f"second argument but got [{type(slice_.stop)}]"
                )
            if isinstance(slice_.step, dict):
                _kwargs = slice_.step
            elif slice_.step is None:
                _kwargs = dict()
            else:
                raise TypeError(
                    "slice expected None|dict as "
                    f"last argument but got [{type(slice_.step)}]"
                )
    except TypeError as e:
        raise e from SyntaxError(PARSE_SLICE_SYNTAX)
    return _callback, _args, _kwargs


class __parseBugs__:
    def __init__(
        self,
        bugs: typing.Union[BaseException, typing.Iterable[BaseException]]
    ):
        self._bugs = OrderedDict()
        self._disperse(bugs)

    @property
    def bug(self):
        return self._compress(getattr(self, '_bugs', tuple()))

    def _disperse(self, bugz):
        collect = namedtuple(
            'Exception',
            ['ERR_NO', 'OBJECT', 'CLASS', 'MESSAGE']
        )
        for index, bug in enumerate(_flatten_(bugz)):
            if not _isBug(bug, throw=False)[0]:
                bug = AnonymousError(bug)
            if not _isBug(bug, throw=False)[1]:
                try:
                    bug = bug()
                    bug.__bug__ = bug
                except Exception as e:
                    bug = UnExpectedBug()
                    bug.__name__ = e.__name__
                    bug.__bug__ = e
            if not isinstance(getattr(bug, 'args') or None, tuple):
                bug.args = (
                    str(bug) or getattr(
                        bug, '__name__',
                        repr(bug).strip('()')
                    )
                )
            bug.message = bug.args[0]
            bug.err_no = f'{self.index}'.zfill(3)
            self._bugs[bug] = collect(
                bug.err_no,
                bug,
                bug.__bug__.__class__,
                bug.message
            )

    def _compress(self, bugs):
        return bugs




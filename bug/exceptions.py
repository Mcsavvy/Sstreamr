import typing
try:
    from ._utils import (
        ReRaised,
        _makeRepr, _isBug, _flatten_, _compare,
        _parseSlice
    )
except ImportError:
    from _utils import (
        ReRaised,
        _makeRepr, _isBug, _flatten_, _compare,
        _parseSlice
    )
from functools import wraps
from inspect import  signature
try:
    from ._vars import (
        USAGE
    )
    from .meta_classes import Nested
except ImportError:
    from _vars import (
        USAGE
    )
    from meta_classes import Nested

class Trigger:
    def __init__(self, fn, *args, key=None, signal=None, **kwds) -> None:
        if not isinstance(fn, typing.Callable):
            raise TypeError(':param "fn" must be a callable')
        self._fn = fn
        self._args = args
        self._kwargs = kwds
        self._signal = signal
        self._key = key

    def __repr__(self):
        this = lambda: None
        this.__name__ = self.__class__.__name__
        return _makeRepr(
            this,
            callback=_makeRepr(self._fn, *self._args, **self._kwargs),
            key=self._key,
            signal=self._signal,
        )

    def __eq__(self, o: object) -> bool:
        return repr(self) == repr(o)

    def precall(self, bug, matchMessage: bool = True):
        return _compare(bug, self._signal, matchMessage=matchMessage)

    def call(self, bug: BaseException, matchMessage: bool = True):
        if self.precall(bug, matchMessage):
            return {
                'key': self._key,
                'result': self._fn(*self._args, **self._kwargs),
                'signal': self._signal,
                'trigger': bug
            }


class Call:
    def __init__(self, fn, *args, key=None, **kwds) -> None:
        if not isinstance(fn, typing.Callable):
            raise TypeError(':param "fn" must be a callable')
        self._fn = fn
        self._args = args
        self._kwargs = kwds
        self._key = key

    def call(self):
        return {
            'key': self._key,
            'result': self._fn(*self._args, **self._kwargs),
        }
    
    def __repr__(self) -> str:
        this = lambda: None
        this.__name__ = self.__class__.__name__
        return _makeRepr(
            this,
            callback=_makeRepr(self._fn, *self._args, **self._kwargs),
            key=self._key,
        )

    def __eq__(self, o: object) -> bool:
        return repr(self) == repr(o)


class Bug(Nested):
    __doc__ = USAGE
    def __init__(
        self,
        bug: typing.Union[BaseException, None] = None,
        keep_last_context: bool = False
    ):
        if bug and not _isBug(bug, throw=False)[0]:
            raise TypeError(
                ':param "bug" must be an instance of BaseException'
            ) from None
        # initialize containers
        "for storing all callback values"
        super().__init__()
        "for storing triggers"
        self['triggers'] = []
        "for storing calls"
        self['calls'] = []
        "for storing drowned error"
        self['drowned'] = set()
        "for storing already selected triggers"
        if bug:
            self.drown(bug)
            self['err'] = bug

    def __call__(self, fn: typing.Union[typing.Callable, BaseException]):
        if _isBug(fn, throw=False)[0]:
            self['err'] = fn
            self.drown(fn)
            return self
        @wraps(fn)
        def inner(*args, **kwds):
            sentinel = object()
            err_raised = False
            g = fn.__globals__
            old_value = g.get('bug', sentinel)
            inner.__bug__ = self
            self.__enter__()
            try:
                par_bug = signature(fn).parameters.get('bug')
                if par_bug and par_bug.default is None:
                    kwds['bug'] = self
                    res = fn(*args, **kwds)
                else:
                    g['bug'] = self
                    res = fn(*args, **kwds)
                    this = g['bug']
            except BaseException as e:
                self['err'] = e
                err_raised = True
            finally:
                if old_value is sentinel:
                    if 'bug' in g:
                        del g['bug']
                else:
                    if 'bug' in g:
                        g['bug'] = old_value
                if err_raised:
                    if not self.__exit__(
                        type(self['err']), self['err'], self['err'].__traceback__
                    ):
                        self.reraise()
                else:
                    self.__exit__(None, None, None)
                    return res
        return inner

    def __enter__(self):
        super().__enter__()
        return self

    def __exit__(self, bug_type, bug, trace):
        # breakpoint()
        if bug.__class__ == ReRaised:
            for x in self._invokeCalls():
                pass
            self.flush()
            super().__exit__()
            return False
        if bug is not None:
            if self._capture(bug):
                for x in self._invokeTriggers(bug):
                    pass
                self.flush()
                super().__exit__()
                return True
            
            else:
                for x in self._invokeTriggers(bug):
                    pass
                self.flush()
                super().__exit__()
                return False
        else:
            for x in self._invokeCalls():
                pass
            self.flush()
            super().__exit__()
            return True

    def _capture(
        self,
        bug: typing.Iterable[typing.Union[BaseException, str]],
        matchMessage: bool = True
    ):
        caught = False
        for x in _flatten_(bug):
            catch_drowned = tuple(map(
                lambda y: _compare(x, y),
                self['drowned']
            ))
            if any(catch_drowned):
                caught = True
                break
        return caught

    def _invokeTriggers(self, bug, matchMessage: bool =True):
        _triggers = iter(self['triggers'][:])
        self.flush()
        for t in _triggers:
            result = t.call(bug, matchMessage=matchMessage)
            if result:
                self[str(result['key'])] = result['result']
                yield result

    def _invokeCalls(self):
        calls_ = iter(self['calls'][:])
        self.flush()
        for c in calls_:
            result = c.call()
            if result:
                self[str(result['key'])] = result['result']
                yield result
    
    def flush(self):
        self['calls'] = []
        self['triggers'] = []
        self['drowned'] = set()

    def willDrownException(self, bug: BaseException, matchMessage: bool = True):
        """
        Return true if error matches drowned triggers
        else false
        """
        for b in _flatten_(bug):
            for d in self['drowned']:
                if _compare(b, d, matchMessage=matchMessage):
                    return True
        return False
    
    def willTriggerCallback(self, bug: BaseException, matchMessage: bool = True):
        for b in _flatten_(bug):
            for t in self['triggers']:
                if t.precall(b,  matchMessage=matchMessage):
                    return True
        return False

    def drown(self, bug: BaseException):
        bugs = tuple(_flatten_(bug))
        # print(f'drowning {" & ".join(str(x) for x in bugs)}')
        for x in bugs:
            # _isBug(x)
            self['drowned'].add(x)
        return self.drown

    def on(
        self,
        bug: typing.Iterable[typing.Union[BaseException, str]],
        fn: typing.Callable,
        *args,
        __key__=None,
        drown=True,
        **kwds
    ):
        for b in _flatten_(bug):
            _isBug(b)
            if __key__ is None:
                if not self['triggers']:
                    __key__ = 0
                else:
                    int_keys = tuple((t._key for t in self['triggers'] if isinstance(t._key, int)))
                    if int_keys:
                        __key__ = max(int_keys) + 1
                    else:
                        __key__ = 0
            new = Trigger(
                fn,
                *args,
                key=__key__,
                signal=b,
                **kwds
            )
            for t in self['triggers']:
                if t == new:
                    # print(f'match found for {new!r} -> {t!r}')
                    break
            else:
                # print(f'no match found for {new!r}')
                self['triggers'].append(new)
        if drown:
            self.drown(bug)
        return self.on
        

    def reraise(self):
        err = self['err']
        if not _isBug(err, throw=False)[0]:
            return print('No Exception To Reraise')
        if not _isBug(err)[1]:
            try:
                err = err()
            except:
                err = Exception(err.__name__)
        raise ReRaised(repr(err)) from err


    def call(self, fn, *args, __key__=None, **kwds):
        if not __key__:
            if not self['triggers']:
                __key__ = 0
            else:
                int_keys = tuple((c._key for c in self['calls'] if isinstance(c._key, int)))
                if int_keys:
                    __key__ = max(int_keys) + 1
                else:
                    __key__ = 0
        
        new = Call(fn, *args, key=__key__, **kwds)
        for c in self['calls']:
            if c == new:
                # print(f'match found for {new!r} -> {c!r}')
                break
        else:
            # print(f'no match found for {new!r}')
            self['calls'].append(new)
        return self.call

    
    def throwIf(self, bug, matchMessage: bool = True):
        if self._capture(bug, matchMessage=matchMessage):
            for x in self._invokeTriggers(bug, matchMessage=matchMessage):
                pass
            self.reraise()
        return self.throwIf

    def throwIfNot(self, bug, matchMessage: bool = True):
        if not self._capture(bug, matchMessage=matchMessage):
            for x in self._invokeTriggers(bug, matchMessage=matchMessage):
                pass
            self.reraise()
        return self.throwIfNot


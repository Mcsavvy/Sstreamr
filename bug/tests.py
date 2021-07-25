import unittest
try:
    from exceptions import (
        Bug,
        _compare, _isBug,
        _makeRepr, _flatten_,
        _parseSlice, ReRaised,
    )
except ModuleNotFoundError:
    from .exceptions import (
        Bug,
        _compare, _isBug,
        _makeRepr, _flatten_,
        _parseSlice, ReRaised,
    )
# try:
#     from signals_and_events import EVENT, SIGNAL

class _UtilsTest(unittest.TestCase):
    def setUp(self):
        pass

    def testIsBug(self):
        self.assertFalse(_isBug('An exception', throw=False)[0])
        self.assertTrue(
            _isBug(BaseException)[0]
        )
        self.assertTrue(
            _isBug(BaseException())[0]
        )
        self.assertTrue(
            _isBug(BaseException())[1]
        )
        self.assertFalse(
            _isBug(BaseException)[1]
        )
        self.assertRaises(
            TypeError,
            _isBug,
            'BaseException'
        )

    def testMakeRepr(self):
        self.assertEqual(
            _makeRepr(print, 'Hello', 'World!', sep=" "),
            "print('Hello', 'World!', sep=' ')",
            'Bad *args, **kwargs formatting'
        )
        self.assertEqual(
            _makeRepr(print, 'Hello', 'World!'),
            "print('Hello', 'World!')",
            'Bad *args formatting'
        )
        self.assertEqual(
            _makeRepr(print, sep=":"),
            "print(sep=':')",
            'Bad **kwargs formatting'
        )

    def testParseSlice(self):
        self.assertEqual(
            _parseSlice(print),
            (print, tuple(), dict()),
            'Cannot parse Callback[Callable]'
        )
        self.assertEqual(
            _parseSlice(slice(print)),
            (print, tuple(), dict()),
            'Cannot parse Callback[Callable]:'
        )
        self.assertEqual(
            _parseSlice(slice(print, ('Hello', 'World!'))),
            (print, ('Hello', 'World!'), dict()),
            'Cannot parse Callback[...]:Args[Iterable]'
        )
        self.assertEqual(
            _parseSlice(slice(print, None, {'sep': ' '})),
            (print, tuple(), {'sep': ' '}),
            'Cannot parse Callback[...]::Kwargs[dict]'
        )
        self.assertEqual(
            _parseSlice(slice(print, ('Hello', 'World!'), {'sep': ' '})),
            (print, ('Hello', 'World!'), {'sep': ' '}),
            'Cannot parse Callback[...]:Args[...]:Kwargs[...]'
        )

    def testFlatten(self):
        self.assertEqual(
            tuple(_flatten_(Exception)),
            (Exception,),
            'Could not flatten single object'
        )
        self.assertEqual(
            tuple(_flatten_('Exception')),
            ('Exception',),
            'Could not flatten single string object'
        )
        self.assertEqual(
            tuple(_flatten_([Exception, 'ThisToo'])),
            (Exception, 'ThisToo'),
            'Could not parse str object'
        )
        self.assertEqual(
            tuple(_flatten_([Exception, 'ThisToo', 1234, dict, bool, object])),
            (Exception, 'ThisToo'),
            'Parsed :not(Exception, str)'
        )

    def testCompare(self):
        '''
        I make the assumtion that the following are true

        * the trigger is compared to the bug
        * the trigger can be a regex pat, str or another Exception
        '''

        """
        A regex trigger with match an exception or it's message

        """
        self.assertTrue(_compare('.*', Exception))
        self.assertTrue(_compare('[Me]{2}s{2}...', Exception('Message')))
        self.assertTrue(_compare('Except', Exception))
        self.assertTrue(_compare('Message', Exception('thisMessage')))
        self.assertTrue(_compare('Error', SyntaxError))

        """
        Two exceptions of different types will never match even if their
        messages matches
        """
        self.assertFalse(_compare(SyntaxError('FOO'), TypeError('FOO')))
        self.assertFalse(_compare(SyntaxError('.*'), TypeError('FOO')))
        # except you explicitly declared matchMessage=True
        self.assertTrue(_compare(SyntaxError('FOO'),
                                 TypeError('FOO'), matchMessage=True))
        self.assertTrue(_compare(SyntaxError('.*'),
                                 TypeError('FOO'), matchMessage=True))

        """
        Two exceptions would always match as long as the first
        is a subclass or instance of the second
        """
        self.assertTrue(
            _compare(TypeError('invalid type'), Exception('generic')))
        self.assertTrue(_compare(TypeError(), Exception))
        self.assertTrue(_compare(TypeError(), Exception()))
        self.assertTrue(_compare(TypeError, Exception()))
        self.assertTrue(_compare(TypeError, TypeError))
        #  except you explicitly declared matchMessage=True
        self.assertFalse(_compare(
            SyntaxError('invalid syntax at a'),
            SyntaxError('invalid syntax at b'),
            matchMessage=True
        ))
        self.assertFalse(_compare(
            SyntaxError('invalid syntax'),
            Exception('generic'),
            matchMessage=True
        ))

        # in the inheritance tree, the ancestor will never match a descendant
        self.assertTrue(_compare(Exception, BaseException))
        self.assertFalse(_compare(BaseException, Exception))

        """
        A TypeError would be raised if the second argument is not
        a subclass or instance of BaseException
        """
        self.assertRaises(TypeError, _compare, TypeError(), '.*')
        self.assertRaises(TypeError, _compare, '.*', '.*')


class BugTest(unittest.TestCase):
    def test__init__(self):
        # raise an error when not initialized with an
        # instance of BaseException
        self.assertRaises(
            TypeError,
            Bug,
            'Exception'
        )
        "new bug instance bug=Exception"
        bug = Bug(Exception)
        # a new bug instance would have empty triggers
        self.assertFalse(bug['triggers'])
        # same with  calls
        self.assertFalse(bug['calls'])
        # but the current exception is drowned
        self.assertIn(Exception, bug['drowned'])
        # most recent exception is alway the first param
        self.assertEqual(bug['err'], Exception)
        "new bug instance bug=Exception"
        bug_ = Bug(Exception)
        # drowned always contains the first param
        self.assertIn(Exception, bug_['drowned'])
        "new bug instance bug=Non"
        bug__ = Bug()
        # err does not exist
        self.assertEqual(bug__['err'], 'not-set')
        # drowned would be empty
        self.assertFalse(bug__['drowned'])

    def testWillDrownException(self):
        bug = Bug()
        '''
        promises to truthfully tell you if an exception would be drowned
        on encounter
        '''
        bug.drown(ValueError('incorrect'))
        self.assertTrue(bug.willDrownException('correct'))
        bug.drown(KeyError('key not found'))
        self.assertTrue(bug.willDrownException(KeyError))
        self.assertFalse(bug.willDrownException(KeyError('val not found')))
        self.assertFalse(bug.willDrownException(SyntaxError))

    def testReraise(self):
        bug = Bug(Exception('an error occurred'))
        self.assertRaises(ReRaised, bug.reraise)


    def testCapture(self):
        bug = Bug(Exception('CapturedException'))
        self.assertTrue(bug._capture(
            FileExistsError('CapturedException'),
            matchMessage=True
        ))

    def testContextManager(self):
        from io import StringIO
        def context_fn(exception_to_raise):
            global bug, IO
            with Bug(BaseException) as bug:
                IO = StringIO()
                bug.on(Exception, print, "An error occurred", file=IO, __key__='err1')
                bug.on(SyntaxError, print, 'type: SyntaxError', file=IO, __key__='err2', end="")
                bug.on(TypeError, print, 'type: TypeError', file=IO, __key__='err3', end="")
                bug.on(KeyError, print, "type: KeyError", file=IO, __key__='err5', end="")
                bug.call(print, 'No errors occurred', file=IO, __key__='call_1', end="")
                if exception_to_raise:
                    raise exception_to_raise
        """
        I make the following assumptions about Bug as a context manager
        """
        # all callbacks will be flushed when the context is exited
        context_fn(Exception)
        self.assertFalse(bug['triggers'])
        self.assertFalse(bug['calls'])
        # all callbacks return values would be mapped to their __key__s
        context_fn(Exception)
        self.assertIn('err1', bug['this'])
        self.assertNotIn('err2', bug['this'])
        # all callbacks are called appropriately
        context_fn(SyntaxError)
        IO.seek(0) # going to the top of the file
        self.assertEqual(
            IO.read(),
            "An error occurred\ntype: SyntaxError"
        )
        # if no error is raised, calls are calledback
        context_fn(None)
        IO.seek(0) # going to the top of the buffer
        self.assertEqual(
            IO.read(),
            "No errors occurred",
        )
    
    def testDecorator(self):
        """
        NOTE: the decorated func must accept a keyword arg 'bug'
            which is the instance of Bug cntrolling the current context

        the decorated func in fact runs in a context of bug
        """
        @Bug(BaseException)
        def decorated(exception_to_raise, bug=None):
            from io import StringIO
            global IO, err
            err = bug
            IO = StringIO()
            bug.on(Exception, print, "An error occurred", file=IO, __key__='err1')
            bug.on(SyntaxError, print, 'type: SyntaxError', file=IO, __key__='err2', end="")
            bug.on(TypeError, print, 'type: TypeError', file=IO, __key__='err3', end="")
            bug.on(KeyError, print, "type: KeyError", file=IO, __key__='err5', end="")
            bug.call(print, 'No errors occurred', file=IO, __key__='call_1', end="")
            if exception_to_raise:
                raise exception_to_raise
                """
        I make the following assumptions about Bug as a decorator
        """
        # all callbacks will be flushed when the function returns
        decorated(Exception)
        self.assertFalse(err['triggers'])
        self.assertFalse(err['calls'])
        # all callbacks return values would be mapped to their __key__s
        decorated(Exception)
        self.assertIn('err1', err[-1])
        self.assertNotIn('err2', err[-1])
        # all callbacks are called appropriately
        decorated(SyntaxError)
        IO.seek(0) # going to the top of the file
        self.assertEqual(
            IO.read(),
            "An error occurred\ntype: SyntaxError"
        )
        # if no error is raised, calls are calledback
        decorated(None)
        IO.seek(0) # going to the top of the buffer
        self.assertEqual(
            IO.read(),
            "No errors occurred",
        )

    def testThrowIf(self):
        '''
        Tests all triggers against a supplied exception
        if any trigger goes off:
            throwIf(exc): reraises Exception
            throwIfNot(exc): does nothing
        if none goes off:
            throwIf(exc): does nothing
            throwIfNot(exc): reraises Exception
        '''
        bug = Bug()
        # Add a regex/str trigger
        bug.drown(NameError)
        # NameError is triggered so reraised
        bug['err'] = NameError
        self.assertRaises(
            ReRaised,
            bug.throwIf,
            'NameError'
        )
        # NameError is triggered so nothing happens
        bug.drown(NameError)
        bug.throwIfNot(NameError)

        bug.drown(SyntaxError)  # match all exceptions
        self.assertRaises(
            ReRaised,
            bug.throwIf,
            '.*'
        )
        bug.throwIf(BaseException)


if __name__ == '__main__':
    unittest.main()

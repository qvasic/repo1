class CompareFloatSeq:
    """Compare object, takes two iterables, which contain floating-point number, and compare them.
    A numbers a considered equal, if they are equal rounded up until precision digits after
    floating point. If iterables are of different sizes - they are not equal as well."""

    def __init__( self, precision ):
        self.precision = precision

    def __call__( self, a, b ):
        if len( a ) != len( b ):
            return False

        for i, j in zip( a, b ):
            if round( i, self.precision ) != round( j, self.precision ):
                return False

        return True

def test_returns( cases ):
    """Test function returns. Takes iterable with test cases.
    Each test case is iterable of three elements:
    func to call, param to pass, and what to expect in return.
    If param is a tuple, it is expanded into separate positional parameters.
    There can be fourth optional element - function that compares actual to expected values.
    Useful in situations with complicated floating-point calculations.
    """
    failed = 0
    for c in cases:
        func, param, expected = c[0], c[1], c[2]
        compare = c[3] if len(c)>3 else None
        try:
            if type( param ) is tuple:
                actual = func( *param )
            else:
                actual = func( param )
        except Exception as exc:
            print( "{f}( {p} ) raised {a} of {c}, while was expected to return {e}".format(
                               f=func.__name__, p=param, a=exc, c=type(exc), e=expected ) )
            failed += 1
        else:
            if compare:
                as_expected = compare( actual, expected )
            else:
                as_expected = actual == expected

            if not as_expected:
                print( "{f}( {p} ) returned {a}, while {e} was expected".format(
                                   f=func.__name__, p=param, a=actual, e=expected ) )
                failed += 1

    return failed

def test_raises( cases ):
    """Test function raises. Takes iterable with test cases.
    Each test case is iterable of three elements:
    func to call, param to pass, and exception of what type should be raised.
    If param is a tuple, it is expanded into separate positional parameters.
    """
    failed = 0

    for func, param, exp_exc in cases:
        try:
            if type( param ) is tuple:
                actual = func( *param )
            else:
                actual = func( param )
        except Exception as exc:
            if type( exc ) is not exp_exc:
                print( "{f}( {p} ) raised {a} of {c}, while was expected to raise {e}".format(
                                   f=func.__name__, p=param, a=exc, c=type(exc), e=exp_exc ) )
                failed += 1
        else:
            print( "{f}( {p} ) retuned {a}, while was expected to raise {e}".format(
                               f=func.__name__, p=param, a=actual, e=exp_exc ) )
            failed += 1

    return failed

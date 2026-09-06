"""
sorts string that includes integers, based on integer value.
a normal string sort would sort "10" to be lower than "2",
but this module aims to tackle that.
Note that sort is case-insensitive

Note that there is a package on PyPI called nat_sort, which does
kinda' the same (and more) but I felt like creating this one.
This module is also fewer lines and therefore better human readable.
"""

import re

class _SupportSort:
    """
    class supports string comparison, but if strings on both of the sides of
    the comparison are found to be digits, their integer values are compared
    instead of their string values (which would be ASCII-comparison, which
    potentially has a different result)
    supporting class for key_for_natural_string_sort and natural_string_sort

    Example:
    >>> "10" > "2"
    False
    >>> _SupportSort("10") > _SupportSort("2")
    True
    """

    def __init__(self, value: str) -> None:
        self.value = value.lower()

    # TODO: for every comparison, self.value.isdigit() is checked. Might it be more
    #  efficient to check this in __init__ and store the result in an attribute
    #  yeah, I very much think so
    def _transform_to_digit_if_digits(self, other):
        # if both strings are isdigit, we want a comparison
        # between ints, not between two strings
        # such that both then have to be converted to integers
        _a = self.value
        _b = other.value
        if (_a.isdigit() and _b.isdigit()):
            _a = int(_a)
            _b = int(_b)
        return _a, _b
    
    def __lt__(self, other):
        _a, _b = self._transform_to_digit_if_digits(other)
        return _a < _b

    def __eq__(self, other):
        _a, _b = self._transform_to_digit_if_digits(other)
        return _a == _b

    def __repr__(self):
        # added in case an error occurs and a readable text is needed in a log
        output = "<{}({})>".format(type(self).__name__, repr(self.value))
        return output

# TODO: -> str suggests this function spits out a string, but it spits out
#  a list 
def key_for_natural_string_sort(s: str) -> str:
    """
    this function should be used as a key to sort strings for
    natural sort.

    natural sort:
    a normal string sort would sort a string with digits "10" to be
    lower than "2", but a natural sort would sort "10" to be higher
    than "2" like a regular human would.
    """

##    # my own function for splitting, but I doubt it's efficient
##    
##    # all the characters in the string are treated as a seperate
##    # element, to seperate the digits from the string
##    L = list(s)
##
##    if s:
##        # test 'if s' to weed out empty lists (otherwise a Key Error may occur)
##        m = L[-1].isdigit()
##
##    for i in reversed(range(1, len(L))):
##        # excluded case of i = 0, as it'll cause an of bounds
##        m, n = L[i - 1].isdigit(), m
##        # a bit ugly, but added for efficiency
##        if not m ^ n:
##            # exclusive nor. both are either string or digit,
##            # so they can be concatenated.
##            L[i - 1] += L[i]
##            del L[i]
##        # supposedly, re.split should also be able to do this.
##        # but not sure, not sure what's more efficient (but a package can handle CPython, so might be quicker)
##        # there is a 10-liner that uses re.split, but I think that was in Python 2.7

    L = re.split("([0-9]+)", s)

    return [_SupportSort(e) for e in L]

# TODO: accepts a list of strings. see how you can modify that
def natural_string_sort(LST):
    """
    a normal string sort would sort "10" to be lower than "2",
    but this function aims to remedy that.

    Argument LST is a list of strings that are to be sorted.
    returns the sorted list, i.e. does not do a list.sort()
    """
    return sorted(LST, key = key_for_natural_string_sort)

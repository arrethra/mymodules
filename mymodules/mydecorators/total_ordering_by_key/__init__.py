"""
The function total_ordering_by_key is a class decorator that implements
all the comparisons dunders for a given key.
The values in argument key must be able to support all comparison operators.
If the class already has user defined comparison dunders, they will not be
overwritten.
The dunders are __lt__, __le__, __eq__, __ne__, __ge__ and __gt__

The name is derived from decorator functools.total_ordering which implements
a somewhat similar but still different scheme. that functool function
infers the other comparison dunders based on just two comparison dunders,
and adds them to the class.
"""

import operator


compare_operators = {
    "__lt__": operator.lt,
    "__le__": operator.le,
    "__eq__": operator.eq,
    "__ne__": operator.ne,
    "__ge__": operator.ge,
    "__gt__": operator.gt,
                    }
comparison_dunder_names = tuple(compare_operators.keys())


def _assert_include(include = comparison_dunder_names):
    """
    check argument include for validity; typo's are quite easily made
    and will have consequences.
    """
    if not include == comparison_dunder_names:
        for i in include:
            if i not in comparison_dunder_names:
                raise ValueError(f"keyword argument include contained the item: '{i}\', but only"
                                 f" allows the following {comparison_dunder_names=}",)
    return include


def total_ordering_by_key_functions(key,
                                    include = comparison_dunder_names,
                                    ):
    """
    creates all the comparison functions based on given key; these 
    functions are returned into a dict. The keys of the dict are the
    strings __lt__, __le__, __eq__, __ne__, __ge__ and __gt__.
    This way, you can build additional functionatilty around the given
    comparison functions, by integrating them into into your own
    functions.

    if errors arise, troubleshooting might be difficult. To troubleshoot,
    consider a try-except clause encompassing the key, to get more detail
    about the errors.

    When two objects are compared and they are not are
    not instances of eachother, NotImplemented is returned (as normal)
    
    key:   function that accepts an instance of the class, and
            returns an object that can be comparable. For example:
            def key(obj): return [obj.attribute1, obj.attribute2]
            This argument key works the same as the key for sorted(key=key)
    include: defines all the dunders that are to be collected in the 
            returned dict. default are all dunders:
            ["__lt__", "__le__", "__eq__", "__ne__", "__ge__", "__gt__"]
            Note: including dunders_names here will not cause them
            to overwrite used-defined dunders.

    """
    _assert_include(include)
    
    def base_compare_operator(cmpr_op):
        def base_compare(self, other):
            # sorta catch all
            if ( not isinstance(self, type(other)) and
                 not isinstance(other, type(self)) ):
                return NotImplemented
                
            return cmpr_op(key(self), key(other)) # troubleshoot using try-except in key
        return base_compare
    
    return {k: base_compare_operator(v)  for k,v in compare_operators.items()
                if k in include}



def total_ordering_by_key(key=None,
                          *,
                          method_name=None,
                          include = comparison_dunder_names,
                          ):
    """
    A class decorator that implements all the comparisons dunders for a
    given  argument key (function). The values produced by the key must
    be able to support all (the included)
    operators. If the class already has some of these dunders, they
    will not be overwritten. The dunders are
    "__lt__", "__le__", "__eq__", "__ne__", "__ge__", "__gt__"

    The name is derived from decorator functools.total_ordering which implements
    a somewhat similar but still different scheme. that functool function
    infers the other comparison dunders based on just two comparison dunders,
    and adds them to the class.

    the comparison dunders are based on key. However, when two objects
    are compared and they are not are not instances of eachother,
    NotImplemented is returned (as normal)
    
    If errors arise, troubleshooting might be difficult.
    To troubleshoot, consider a try-except clause that encompasses the
    code in the key function/method, to get more detail about the
    errors. Or implement the comparison dunders yourself.
    
    all arguments are keyword arguments. Either key or methodname
    must be given; it cannot be both.
    key:   must be a function that accepts an instance of the class, and
            returns an object that can be comparable. For example:
            def key(obj): return [obj.attribute1, obj.attribute2]
            This argument key works the same as the key for sorted(key=key)
    method_name: name of the method (str) of target class that is the key.
            If the target class contains a method that acts as a key for that
            class, this argument presents a way to use it cleanly.
            This method must satisfy all conditions stipulated for
            keyword argument key. 
    include: defines all the dunders to (gently) overwrite.
            default are all dunders:
            ["__lt__", "__le__", "__eq__", "__ne__", "__ge__", "__gt__"]
            Note including dunders_names here will not cause them
             to overwrite used-defined dunders

    ## simple example
    >>> @total_ordering_by_key(key=lambda x: [x.a, x.b])
    ... class tobkClass:
    ...     def __init__(self, a, b):
    ...         self.a, self.b = a, b
    >>> Foo = tobkClass(1,2)
    >>> Bar = tobkClass(2,3)
    >>> Foo < Bar
    True

    ##  example in which the key is derived from the class attributes
    >>> @total_ordering_by_key(method_name = "sorting_key")        
    ... class tobkClass:
    ...     def __init__(self, a, b):
    ...         self.a, self.b = a, b
    ...     def sorting_key(self):
    ...         return list(self.__dict__.values())
    >>> Foo = tobkClass(1,2)
    >>> Bar = tobkClass(2,3)
    >>> Foo < Bar
    True
    """
    if key and method_name:
        raise TypeError("cannot have both key and method_name as keyword argument; "
                        "only 1 of those is allowed")
    elif not key and not method_name:
        raise TypeError("you have to specify the argument key or keyword argument method_name")
    elif not method_name and not callable(key):
        raise ValueError(f"argument {key=} must be callable, but found {type(key)}.")
    
    def _total_ordering_by_key(cls):
        _key = key or getattr(cls, method_name)

        # Check if there are already user-defined comparisons.
        # modified the following line from functools.total_ordering
        user_defined = {cp for cp in compare_operators.keys()
                            if getattr(cls, cp, None) is not getattr(object, cp, None)}
        [setattr(cls, k, f) for k, f in total_ordering_by_key_functions(_key, include).items()
                                     if k not in user_defined ]       
        return cls

    return _total_ordering_by_key





    




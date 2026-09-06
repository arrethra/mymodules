import collections.abc
import typing


class BoolFunc:
    modes_possible = [None, "or", "and", "invert", "xor" ]
    def __init__(self, function: collections.abc.Callable) -> None:
        """
        A class decorator for boolean functions (i.e. a function
        that returns a boolean). Operators can act on the functions 
        before any arguments are received. A new instance will be
        created when an operator (see below) is used on the instance(s)

        The operators:
           or-operator ( | )           mimics 'or'
           and-operator ( & )          mimics 'and'
           xor-operator ( ^ )          mimics  ^    (which is xor)
           invert-operator ( ~ )       mimics 'not' 

        Note that you cannot use the written 'and', 'or' or 'not' as 
        you would in a regular if-statements (see pitfalls below)

        The use of operators ( | & ^ ~ ) on BoolFunc will 
        result in a new instance. If a concatenating operator ( | & ^ )
        is used and the new instance is called, both (old) instances
        are called as well with the same arguments. This means that the
        underlying boolean functions are also called with the same 
        arguments. e.g. if two instances are initiated with the 
        functions foo(x:int) and bar(s:str, d:dict), concatenated with
        ( & | ^ ) and the new instance is subsequently called, it will
        end in an error. see pitfalls below.

        The invert-operator ( ~ ) will invert the outcome of
        BoolFunc, similar to how "not True" would work
        (see examples below for more).
        Note: when the invert-operator ( ~ ) acts on a boolean, this
        creates weird results; see pitfalls below


        examples:
        >>> @BoolFunc
        ... def foo():
        ...     return True
        >>> (foo | foo)()
        True

        # main example:
        >>> def isBool(b) -> bool:
        ...     return bool(b)
        >>> def isNotBool(b) -> bool:
        ...     return not bool(b)
        >>> A = BoolFunc(isBool)
        >>> N = BoolFunc(isNotBool)

        # the instances can be called, and the initiating functions
        #  are executed, respectively isBool and isNotBool
        >>> A(True), N(True)              
        (True, False)
        >>> (A | N)(True)         # example of the  or-operator working
        True
        >>> (A & A)(False)        # example of the and-operator working
        False
        >>> (A & A)(True)
        True

        # inverting a BoolFunc, i.e. when called, instances
        # will return the opposite of their normal behavior when called
        >>> (A & ~N)(True)     
        True
        >>> (A & ~N)(True)     # tilde ( ~ ) can be used to same effect
        True

        >>> ((A & ~N) & (A | N))(True)           # nesting is just fine
        True


        !!! pitfalls:  do not use the written 'and', 'or' and 'not' !!!
        >>> (N and A)(True)          # this leads to unexpected result
        True
        >>> (N & A)(True)     # for comparison
        False
        >>> (N and A) is A    # reason: the instance N is already
        ...                   # considered truthy so the 'and' will only
        ...                   # return A and execute it 
        True

        !!! pitfalls:  do not use "or" !!!
        >>> (A or N)(False)             # unexpected result
        False
        >>> (A | N)(False)              # for comparison   
        True
        >>> (A or N) is A               # reason: instance A is already
        ...                             # thruthy so N is ignored 
        True


        !!! pitfalls (continued)
        >>> try:
        ...     (not N & A)(True)                # don't use 'not'  !!!
        ... except TypeError as E: print(E)
        'bool' object is not callable

        # inverts-operator is not processed before function is called !!!
        >>> ~A(True), ~True 
        (-2, -2)
        >>> (~A)(True)             # the correct way: using parentheses
        False

        !!! pitfalls: initiating boolean functions do not accept same
        number of arguments
        >>> @BoolFunc
        ... def foo():
        ...     return True
        >>> @BoolFunc
        ... def bar(a, b, c):
        ...     return a and b and c
        >>> f = foo & bar
        >>> try:
        ...     f()
        ... except TypeError as E: print(E) 
        bar() missing 3 required positional arguments: 'a', 'b', and 'c'
        >>> f2 = foo | bar
        >>> f2()           # passes surprisingly: bar is never evaluated
        True

        """
        self. mode = None
        self.function = [function]
        return


    def __call__(self, *args, **kwargs) -> bool:
        method_name = f"_call_{self.mode}_"
        f = getattr(self, method_name,)
        return f(*args, **kwargs)

    
    def _call_None_(self, *args, **kwargs) -> bool:
        if len(self.function) > 1:
            raise Exception("self.function has length len(self.function) "
                            "but should be 1 for mode None.")
        f = self.function[0]

        # designed for easier error-handling
        try:
            output = f(*args, **kwargs)
        except Exception as E:
            E.add_note(f"  - Raised while executing function "
                       f"named '{repr(f)}' with arguments "
                       f"({args=}, {kwargs=})")
            raise E
        return output

    
    def _call_and_(self, *args, **kwargs):
        for f in self.function:
            if not f(*args, **kwargs):
                return False
        return True
        
    def __and__(self, other):
        return self._concatenate_(other, mode="and")

    def _call_or_(self, *args, **kwargs):
        for f in self.function:
            if f(*args, **kwargs):
                return True
        return False

    def __or__(self, other):
        return self._concatenate_(other, mode="or")

    def _call_invert_(self, *args, **kwargs):
        if len(self.function) > 1:
            raise Exception("ehh, this can never happen?")
        f = self.function[0]
        return not f(*args, **kwargs)

    def __invert__(self):
        cls = type(self)
        output = cls(self)
        output.mode = "invert"
        return output



    def _call_xor_(self, *args, **kwargs):
        if not len(self.function) == 2:
            raise Exception("this should not happen, {len(self.fumnction)=}")
        b0 = self.function[0](*args, **kwargs)
        b1 = self.function[1](*args, **kwargs)
        return bool(b0) ^ bool(b1) 

    def __xor__(self, other):
        return self._concatenate_(other, mode = "xor")

    def _concatenate_(self, other, mode):
        motherclass = BoolFunc
        if not isinstance(other, motherclass):
            raise TypeError(f"other is not an instance of {motherclass}, "
                            f"but instead {type(other)=} with value {other}")

        # if they are inherited from motherclass, I need to determine the
        # new class. Not sure how to go about this if they are at not the same
        # inheritance level.
        # I have implemented that the new class becomes
        # the class with the deepest inheritance (not sure if correct choice)
        if isinstance(self, type(other)):
            cls = type(self)
        elif isinstance(self, (type(self))):
            cls = type(other)
        else:
            raise TypeError(
                "the two classes are not (inherited) instances of "
                f"each other, namely {type(self)=} and {type(other)=}")

        
        if self.mode is None and other.mode is None:
            # mode == None means that no operator is applied yet,
            # so the structure can be simplified.
            output = cls(self.function[0])  # would a copy also suffice?
            output.function += other.function
        else:
            output = cls(self)
            output.function.append(other)
        output.mode = mode
        return output

    def __repr__(self, recursive = None):
        if recursive is None:
            output = f"{type(self)}[function="
        else:
            # if type(self) get s very long due to pre-pended modules,
            # this gets long very quick when applying operators such as
            # ( & ^ | )
            output = f"BoolFunc[function="
        motherclass = BoolFunc
        for f in self.function:
            if isinstance(f, motherclass):
                output += f.__repr__(True) + ", "
                continue
            else:
                output += repr(f) + ", "
        
        output = output[:-2] + f", mode={repr(self.mode)}]"
        return output
        

            
        
    

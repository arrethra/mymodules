import functools
import inspect


class ParameterError(BaseException):
    """
    The decorator from this module will set the argument names as
    attributes. To protect dunders from being overwritten, if an
    argument is given a name that starts and ends with double
    underscores, this ParameterError will be raised.
    """
    pass


def set_arguments_as_attributes(cls_or_method):
    """
    set arguments of the class or method, as attributes of the 
    instance. decorates either a class or method.
    if class, it decorates only __init__
    It will overwrite existing attributes. However, (look-a-like)
    dunders are not allowed as arguments and will raise a 
    ParameterError. This includes names such as __eq__ but also 
    look-a-likes like __some_name__.

    If the class or method asks for vargargs (eg. def foo(*args): pass)
    then these will be collected into a tuple, see relevant example
    below. If no arguments are passed onto *args, then the attribute will
    be an empty tuple. If 1 argument is given to *args, it'll also be
    encompassed in a tuple.

    example: decorate classes
    >>> @set_arguments_as_attributes
    ... class SAAAclass:
    ...     def __init__(self, a, b):
    ...         pass
    >>> A = SAAAclass(1,2)
    >>> A.a
    1

    example: decorate methods
    >>> class SAAAclass2:
    ...     @set_arguments_as_attributes
    ...     def foo(self, a, b):
    ...         pass
    >>> B = SAAAclass2()
    >>> hasattr(B, "a")
    False
    >>> B.foo(1, 2)
    >>> B.a
    1

    example: varargs are collected into tuple
    >>> @set_arguments_as_attributes
    ... class SAAAclass3:
    ...     def __init__(self, *args):
    ...         pass
    >>> B = SAAAclass3()
    >>> B.args
    ()
    >>> C = SAAAclass3(1,)
    >>> C.args
    (1,)
    >>> D = SAAAclass3(1, 2, 3)
    >>> D.args
    (1, 2, 3)
    """
    if inspect.isclass(cls_or_method):
        cls = cls_or_method
        existing_method = getattr(cls, "__init__")
    else:
        existing_method = cls_or_method

    # I name then args_saaa and kwargs_saaa because they are not common names
    
    @functools.wraps(existing_method)
    def method_wrapper(self, *args_saaa, **kwargs_saaa):
        obtained_args_kwargs = locals().copy()

        # while inspect.getfullargspec doesn't require for-loops,
        # inspect.signature is recommended by someone/something
        sig = inspect.signature(existing_method)


        # process defaults first, they can be overriden later
        arg_kwarg_dict = {name: p.default for name, p in sig.parameters.items()
                                                 if p.default != inspect.Parameter.empty}

 
        # process args; start with lining up expected arg names
        #  with obtained arg values
        kind_pos_args = [inspect.Parameter.POSITIONAL_ONLY,
                         inspect.Parameter.POSITIONAL_OR_KEYWORD]
        expected_pos_args_names = [p for p in sig.parameters
                                          if sig.parameters[p].kind in kind_pos_args]

        # first arg will be self, so gotta filter that one out. hence the [1:] slices
        number_of_pos_args = len(expected_pos_args_names[1:])
        arg_kwarg_dict.update( dict(zip(expected_pos_args_names[1:],
                                        obtained_args_kwargs["args_saaa"])) )


        # process *args, i.e. VAR_POSITIONAL, there can only be 1 such argument
        kind_vararg = [inspect.Parameter.VAR_POSITIONAL]
        vararg_name = [p for p in sig.parameters
                                          if sig.parameters[p].kind in kind_vararg]
        vararg_name = vararg_name[0] if vararg_name else None

        if vararg_name:
            # gotta remove the pos_args first
            vararg_value = obtained_args_kwargs["args_saaa"][number_of_pos_args:]
            
            arg_kwarg_dict.update({vararg_name: vararg_value})
        

        # process kwargs; this is easy
        arg_kwarg_dict.update(obtained_args_kwargs["kwargs_saaa"])
 

        for a in arg_kwarg_dict:
            if a.startswith("__") and a.endswith("__"):
                msg = (f"OverwriteProtection; the decorator does not allow argument {a}"
                       " to be named like that"
                       " as it looks like dunder (i.e. starts&ends with __) to protect"
                       " dunders from being overwritten")
                raise ParameterError(msg)
            setattr(self, a, arg_kwarg_dict[a])
        
        return existing_method(self, *args_saaa, **kwargs_saaa)
    
    if inspect.isclass(cls_or_method):
        setattr(cls, "__init__", method_wrapper)
        return cls
    else:
        return method_wrapper



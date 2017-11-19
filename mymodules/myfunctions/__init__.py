# written by arrethra https://github.com/arrethra

import sys, inspect, os

def args_taken_by(function, include_kwargs=False):
    """
    Calculates number of arguments that can be taken by input function
    and returns tuple with respectively the lower and upper limit.
    (upper limit can be float("inf").)
    
    Note that, by default, it does not count arguments which REQUIRE* a
    keyword (i.e., kwargs in bar(**kwargs)). To count these arguments,
    set the second argument 'include_kwargs' to be True.

    *positional keywords, such as y in foo(x,y=1), are counted by
    default and count towards the upper limit that is returned.
    """
    import inspect
    if not callable(function):
        error_message = "Input must be callable, but found type %s"%type(function)
        raise TypeError(error_message)

    if not isinstance(include_kwargs, bool):
        error_message = "argument include_keyword_only should be boolean, but found type %s"%exclude_keyword_only
        raise TypeError(error_message)
    
    arguments = inspect.signature(function)
    Par = arguments.parameters
    parameters = [Par[key] for key in Par]
    
    required = 0
    optional = 0

    for X in parameters:
        x = str( X.kind)
        if x == 'POSITIONAL_ONLY':
            required += 1
        elif x == 'POSITIONAL_OR_KEYWORD':
            if type(X.default) == type(inspect._empty):
                required += 1
            else:
                optional += 1
        elif x == 'VAR_POSITIONAL':
            optional = float("inf")
        elif x == 'KEYWORD_ONLY':
            if  include_kwargs:
                optional += 1
        elif x == 'VAR_KEYWORD':
            if include_kwargs:
                optional = float("inf")
            
    return (required, required + optional)


def isiterable(var):
    """Returns whether input is iterable or not."""
    try:
        iter(var)
        return True
    except TypeError:
        return False



COUNTER_dict = {}
def counter_function(start=1, step=1, elem="default", reset=False, return_keys=False):
    """
    Returns the number of times this counter has been called upon.
    Note that it will start at the number 1 by default
    (see argument start).
    
    Arguments:
    reset:       If this argument is 'True', this resets the counter
                 to 0. If this argument is either an integer or float,
                 the counter will be reset to that value. Note that
                 reset will never reset value to start.
    elem:        This function enables multiple counters to be run at
                 the same time, without interfering with each other.
                 The argument 'elem' enables this behavior.
                 All the counters are stored in a dictionary. 'elem' is
                 the keyword from which the needed counter is retreived.
                 TODO: improvement on elem-docstring needed :P
    start:       The value of the counter the first time it's called.
    step:        The step-size that is to be added to the count.
                 (This will not be remembered between subsequent calls,
                  so it must be specified each time if it should not be
                  default)
                  TODO: make it also possible that step can be a
                        function, which accepts the current value as the
                        first argument, and calculates the next counter
                        value (or should I not...?)
    return_keys: If this argument is specified to be True, the names of
                 all counters will be returned (i.e., all the names that
                 elem has been called). This will supersede all other
                 arguments, and no counter will be returned.
    """
    global COUNTER_dict

    if return_keys:
        return COUNTER_dict.keys()

    
    if isinstance(reset,bool):
        reset_to_value = 0    
    elif isinstance(reset,(int,float)):
        reset_to_value = reset
        reset = True    
    else:
        error_message ="Argument 'reset' should be boolean (if True, "+\
                       "counter will be reset to 0) or integer/float "+\
                       "(counter will be reset to that value), but "  +\
                       "was to be found of type %s."%type(reset)
        raise TypeError(error_message)

    if callable(step):
        lower_args,higher_args = args_taken_by(step)
        if not lower_args <= 1 <= higher_args:
            error_message = "Argument 'step' was found to be callable, "+\
                            "but has to accept 1 argument. However, function "+\
                            "accepted between '%s' and '%s' arguments (not "%\
                            (lower_args,higher_args)  +\
                            "including arguments that Require a keyword)."
            raise ValueError(error_message)        
    elif not isinstance(step,(int,float)):
        error_message = "Argument 'step' should be integer, float or callable, "+\
                        "but found type %s."%type(step)
        raise TypeError(error_message)
    

    if not elem in COUNTER_dict.keys():
        COUNTER_dict[elem] = start
    elif reset: 
        COUNTER_dict[elem] = reset_to_value
    else:
        if isinstance(step,(float,int)):
            COUNTER_dict[elem] += step
        if callable(step):
            COUNTER_dict[elem] = step(COUNTER_dict[elem])
            if not isinstance(COUNTER_dict[elem],(float,int)):
                error_message = "Argument 'step' was found to be function, "+\
                                "which should return either float or integer,"+\
                                " but found it returned '%s'."\
                                %type(COUNTER_dict[elem])
                raise TypeError(error_message)
    return COUNTER_dict[elem]


def do_nothing(*x):
    """Does nothing """
    pass


def isIDLE():
    """
    Finds out whether the script is run through IDLE or not.
    Does not always work for version 2.X, see link below
    https://stackoverflow.com/questions/3431498/what-code-can-i-use-to-check-if-python-is-running-in-idle
    """
    # TODO: make it work for (all) v2.x, see link above
    return "idlelib" in sys.modules


def get_location(folders_up = 0):
    """
    Returns the folder location where this function is called.
    If folders_up is specified, it will remove the last few folders.
    """
    # does this function mirror another stdlib-function...?
    # this function is also mirrored in the module importcustommodules,
    # though named 'get_parent_folder' or 'get_parent_folder_stack'
    # (the latter can go deepeer into the stack)
    if not isinstance(folders_up,int):
        error_message = "argument 'folders_up' must be integer, but found type '%s'."%type(folders_up)
        raise TypeError(error_message)
    if not folders_up >= 0:
        error_message = "argument 'folders_up' must zero or positive, but found value '%s'."%(folders_up)
        raise ValueError(error_message)

    
    originating_folder = os.path.split( inspect.stack()[1][1] )[0]
    for i in range(folders_up):
        originating_folder = os.path.split(originating_folder)[0]
    return originating_folder



        
        
            


if __name__ == "__main__":
    import unittest
    from test.test_myfunctions  import *
    unittest.main()

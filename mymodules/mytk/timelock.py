# written by arrethra https://github.com/arrethra

import functools

def timelockwrapper(master,
                    duration_of_lock=100):
    def decorator(func):
        @functools.wraps(func)
        def call(*args,**kwargs):
            locker_key = "timelock-wrapped function called '%s'."%call.__name__
            timelocker = timelock(master=master,
                                  func=func,
                                  func_args=args,
                                  func_kwargs=kwargs,                                      
                                  duration_of_lock=duration_of_lock,
                                  locker_key=locker_key)
        return call   
    return decorator

_LOCKER_DICT = {}
def timelock(  master,
                func,
                func_args="()",
                func_kwargs = "{}",
                duration_of_lock = 100,
                locker_key = "default",
                reset=False,
                return_dict = False):
    """
    This function enables a timelock to be placed upon the
    input-function ('func'). This means that after 'func' is called,
    that function cannot be called for a certain duration of time. If
    this timelock is called upon 'func' during this lock, it will be
    executed once the lock ends.

    A good example is when a certain expensive function is called upon
    many times unnecessarily, thereby chewing up good amounts of
    calculation-time. This timelock prevents that certain function
    from being called upon too many times. 
    
    Arguments:
    -master:    The master-widget, to which this function must be tied.
                # TODO: for the time being, the method master.after is
                vital to the workings of this function. However, it'd
                be a good idea if this function can work without after.
    -func:      The function that is to be called.
    -func_args: Arguments that will be entered into func. Must be
                collected into a tuple.
    -func_kwargs:
                Key-word arguments that will be entered into func. Must
                be a dictionary
                NOTE: TODO: func_args and func_kwargs cannot change between succesive calls
    -duration_of_lock:
                Duration between succesive calls of func in milliseconds.
    -locker_key:
                Enables parallel use of multiple locks running at the
                same time; without this argument present, all calls to
                this function would count toward the same lock. By
                specifying this argument, a new lock is created.
                locker_key must be specified the same to access the
                same lock. 
    -return_dict:
                If specified True, this function will return (a copy of)
                the dictionary that holds all the keys and the statusses
                of all locks.
    -reset:     If specified True, resets given locker_key and executes
                function.
                If specified the string 'all', it'll reset all
                locker_keys and do nothing else. In this case, the
                validity of the other arguments do not matter
                (e.g. argument master and func can be None)       
    """
    original_args_of_this_function = locals().copy()
    
    global _LOCKER_DICT

  
    
    if not locker_key in _LOCKER_DICT or reset:
        _LOCKER_DICT[locker_key] = 0
        if isinstance(reset,str) and reset.lower() == 'all':
            _LOCKER_DICT = {}
            return
       
    if return_dict:
        return _LOCKER_DICT.copy()

    if _LOCKER_DICT[locker_key]:
        _LOCKER_DICT[locker_key] += 1
        # this is placed here for efficiency
        return
    else:
        _LOCKER_DICT[locker_key] += 1

    if func_args=="()":
        func_args=()
    if func_kwargs == "{}":
        func_kwargs = {}
        
    # calls upon error-function
    if _assert_timelock(func,func_args,func_kwargs,duration_of_lock):
        raise _assert_timelock(func,func_args,func_kwargs,duration_of_lock)

    def bar(*x):
        global _LOCKER_DICT
        locker_copy = _LOCKER_DICT[locker_key]
        _LOCKER_DICT[locker_key] = 0
        # catches any event during the time that it was still locked
        if locker_copy>1:
            timelock(**original_args_of_this_function)

    func(*func_args,**func_kwargs)
    master.after(duration_of_lock,bar)
    
    

    
def _assert_timelock(func,func_args,func_kwargs,duration_of_lock):
    """
    Assert errors in timelock-input, and if found, returns them
    (in stead of raising).
    """
    if not callable(func):
        error_message = "Arg 'func' must be callable, but was of type %s."\
                        %type(func)
        return TypeError(error_message)

    if not isinstance(func_args, tuple):
        error_message = "Arg 'func_args' must be contained within a "\
                        +"tuple, but found type %s."%type(func_args)
        return TypeError(error_message)

    if not isinstance(func_kwargs,dict):
        error_message = "Arg 'func_kwargs' must be contained within a "\
                        +"dictionary, but found type %s."%type(func_args)
        return TypeError(error_message)
    else:
        for kwarg_key in func_kwargs.keys():
            if not isinstance(kwarg_key,str):
                error_message = "Arg 'func_kwargs' contains a key that is not string, but of type '%s'."%type(kwarg_key)
            return ValueError(error_message)   
    
    if not isinstance(duration_of_lock, int):
        error_message ="Arg 'duration_of_lock' must be integer, but found type %s."\
                       %type(duration_of_lock)
        return TypeError(error_message)
    elif duration_of_lock <0:
        error_message = "Arg 'duration_of_lock' must be zero or above, "\
                        +"but found '%s'."%duration_of_lock
        return ValueError(error_message)



if __name__ == '__main__':
    import unittest
    from test.test_timelock import *
    unittest.main()


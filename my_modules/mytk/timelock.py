# written by arrethra https://github.com/arrethra

LOCKER_DICT = {}
def timelock(  master,
                func,
                func_args="()",
                duration_of_lock = 100,
                locker_key = "default",
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
    -master:     The master-widget, to which this function must be tied.
                 # TODO: for the time being, the method master.after is
                 vital to the workings of this function. However, it'd
                 be a good idea if this function can work without after.
    -func:       The function that is to be called.
    -func_args:  Arguments that will be entered into func.
    -duration_of_lock:
                 Duration between succesive calls of func.
    -locker_key: Enables parallel use of multiple locks running at the
                 same time; without this argument present, all calls to
                 this function would count toward the same lock. By
                 specifying this argument, a new lock is created.
                 locker_key must be specified the same to access the
                 same lock. 
    -return_dict:
                 If specified True, this function will return (a copy of)
                 the dictionary that holds all the keys and the statusses
                 of all locks.
    """
    args = locals().copy()
    
    global LOCKER_DICT
    
    if return_dict:
        return LOCKER_DICT.copy() 
    
    if not locker_key in LOCKER_DICT:
        LOCKER_DICT[locker_key] = 0

    if LOCKER_DICT[locker_key]:
        LOCKER_DICT[locker_key] += 1
        # this is placed here for efficiency
        return
    else:
        LOCKER_DICT[locker_key] += 1
    
    
    
    # catches any errors due to wrong input
    if not callable(func):
        error_message = "Arg 'func' must be callable, but was of type %s."\
                        %type(func)
        raise TypeError(error_message)
    if func_args=="()":
            func_args=()
    elif not isinstance(func_args, tuple):
        error_message = "Arg 'func_args' must be contained within a "\
                        +"tuple, but found type %s"%type(func_args)
        raise TypeError(error_message)
    elif not isinstance(duration_of_lock, int):
        error_message ="Arg 'duration_of_lock' must be integer, but found type %s"\
                       %type(duration_of_lock)
        raise TypeError(error_message)
    elif duration_of_lock <=0:
        error_message = "Arg 'duration_of_lock' must be above zero, "\
                        +"but found '%s'"%duration_of_lock
        raise ValueError(error_message)

    def bar(*x):
        global LOCKER_DICT
        locker_copy = LOCKER_DICT[locker_key]
        LOCKER_DICT[locker_key] = 0
        # catches any event during the time that it was still locked
        if locker_copy>1:
            timelock(**args)

    func(*func_args)
    master.after(duration_of_lock,bar) # TODO: make this a timer and a new thread...?


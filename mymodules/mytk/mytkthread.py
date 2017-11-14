# written by arrethra https://github.com/arrethra

import threading
import functools
import copy


_FUNCTIONS_DICT = {}
def _initialize_FUNCTIONS_DICT(master):
    global _FUNCTIONS_DICT
    try:
        _FUNCTIONS_DICT[master]
    except KeyError:
        _FUNCTIONS_DICT[master] = []

    
def list_function_for_execution(master,
                                function, args=None, kwargs=None,
                                snapshot=False,
                                wait_untill_execution=False):
    """
    Lists functions to be executed by a GUI. Functions cannot have
    arguments. Use this function in combination with execute_functions.
    My main reason for writing this, is that another thread can list
    such a function, and that the GUI in his own thread can execute
    the function (maybe after a slight delay).
    (A GUI itself is not supposed to get calls from different threads,
    e.g. a tk-window cannot be destroyed from another loop, so that
    other thread has to list the destroy-method)
    
    Arguments:
    master:       You have to specify which master has to execute the
                  function.
    function:     The function that has to be listed. (Do not call upon
                  the function yet)
    args:         Any arguments that the function has to get, summed up
                  in a tuple.
    kwargs:       Any keywords the function has to get, collected in a
                  dictionary.
    snapshot:     Creates a deepcopy of both args and kwargs.
                  This prevents the argument from changing during the
                  delay it takes 'execute_functions' to call upon the
                  function and arguments. An example of such a change
                  can be a list as argument, which has been appended
                  right after the argument has been entered into this
                  function (but the function must wait untill called by
                  execute_functions.
    wait_untill_execution:
                  If specified True, the current thread will wait untill
                  that listed function has been executed.
    """
    global _FUNCTIONS_DICT   
    _initialize_FUNCTIONS_DICT(master)

    if args == None:
        args = ()
    elif not isinstance(args,tuple):
        error_message = "Argument 'args' should be a tuple, but instead found type %s."%type(function)
        raise TypeError(error_message)

    if kwargs == None:
        kwargs = {}
    elif not isinstance(kwargs,dict):
        error_message = "Argument 'kwargs' should be a dictionary, but instead found type %s."%type(function)
        raise TypeError(error_message)

    if snapshot:
        args = copy.deepcopy(args)
        kwargs = copy.deepcopy(kwargs)
        

    if not callable(function):
        error_message = "Argument 'function' should be callable, but instead found type %s."%type(function)
        raise TypeError(error_message)

    if wait_untill_execution:
        sleeper_cell = threading.Event()

        def sleeper_cell_wrapper(event):
            def sleeper_cell_decorator(func):
                @functools.wraps(func)
                def foo(*args,**kwargs):
                    try:
                        output = func(*args,**kwargs)
                    finally:
                        event.set()
                    return output
                return foo
            return sleeper_cell_decorator
        
        function = sleeper_cell_wrapper(sleeper_cell)(function)
        
    # TODO: check how many argument it has...

    _FUNCTIONS_DICT[master].append((function,args,kwargs))

    if wait_untill_execution:
        sleeper_cell.wait()
    

def execute_functions(master,timer = 0.05):
    """
    Executes functions, that were listed by list_function_for_execution.
    My main reason for writing this, is that another thread can list
    such a function, and that the GUI in his own thread can execute
    the function (maybe after a slight delay).
    (A GUI itself is not supposed to get calls from different threads)
    timer is delay in second, and determines how often is checked
    whether there are any functions to be executed.

    Note: If a function executed by the master 'freezess the master,
          this function will be frozen likewise (TODO: yes, rly?)
    """
    global _FUNCTIONS_DICT    
    _initialize_FUNCTIONS_DICT(master)

    if not isinstance(timer,(int,float)):
        error_message = "Argument timer must be either float or integer, but found type %s."%type(timer)
        raise TypeError(error_message)
    elif  timer <0.001:
        error_message = "Argument timer must be 0.001 or greater, but found value '%s'."%timer
        raise ValueError(error_message)
    
    def execute_functions_loop():
        if len(_FUNCTIONS_DICT[master]) != 0:
            func, args, kwargs = _FUNCTIONS_DICT[master][0] 
            func(*args,**kwargs) # execute function that was listed to be executed.
             
            del _FUNCTIONS_DICT[master][0]
            
            execute_functions_loop() # check if there are more functions listed to be executed
        else:
            master.after(int(timer*1000), execute_functions_loop)
    
    execute_functions_loop()




if __name__ == "__main__":
    import unittest
    from test.test_mytkthread import *
    unittest.main()        
                

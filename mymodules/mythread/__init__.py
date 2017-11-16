# written by Arrethra https://github.com/arrethra/

import threading
import time
import functools
import datetime
        

class WaitTillThreadIsOver(threading.Thread):
    """
    Creates a thread, but waits untill it's over.
    The created thread is an instance of threading.Thread
    """
    # TODO; kinda useless class, actually, ain't it...?
    def __init__(self,*args,**kwargs):
        if 'target' in kwargs:
            target = kwargs['target']
            target = self._wrap_target(target)
            kwargs['target'] = target

        self.parent = threading.current_thread()
        self.time_elapsed = 0
        super().__init__(*args,**kwargs)

        
    def start(self,):
        self._wait_event = threading.Event()
        self.time_elapsed = 0
        time_at_start = time.time()
        output = super().start()
        self._wait_event.wait() # the magic wait
        self.time_elapsed = time.time() - time_at_start
        return output


    def _wrap_target(self,target):
        def call(*args,**kwargs):
            try:
                result = target(*args,**kwargs)
            finally:
                self._wait_event.set() # breaks the magic wait
            return result
        return call




    

def _assert_lock(lock):
    """
    Checks if input is a lock/semaphore/else by checking the presence of
    the methods 'acquire' and 'release'. If failed, this function
    returns the appropiate Exception (Note, it is not raised)
    """
    try:
        if not callable(lock.acquire) or not callable(lock.release):
            error_message = "Argument 'lock'; either method(/attribute) 'acquire' and 'release' (or both) were not callable. 'lock' was of type '%s'."%type(lock)
            return TypeError(error_message)
    except AttributeError:
        error_message = "Argument 'lock' did not have either the method 'acquire' and 'release' (or both). 'lock' was of type '%s'."%type(lock)
        return TypeError(error_message)


def lockwrapper(lock):
    """
    A wrapper to encase a function with the specified lock.
    It will always release the lock, even when the function
    caused an error.
    """
    if _assert_lock(lock):
        raise _assert_lock(lock)

    def decorator(func):
        @functools.wraps(func)
        def foo(*args,**kwargs):
            lock.acquire()
            try:
                output = func(*args,**kwargs)
            finally:
                lock.release()
            return output            
        return foo
    return decorator


def timelockwrapper(delay=0.1):
    """
    If a function is expensive and called upon too many times,
    this wrapper can be used.  This wraps around the function, and when
    the function is called, it sets up a timelock (for duration 'delay')
    During that timelock, calls upon that function are ignored. When the
    timelock ends, those ignored calls trigger a last call* (resetting the
    timelock). If no calls are placed during a timelock, no such trigger
    happens.

    NOTE:   This wrapper uses threads. Therefor the wrapped function
            needs to be thread-safe.
    NOTE 2: The function will be given the following attributes, which
            should not be overwritten:
            lock, active_thread_name, args, kwargs.

    *this call will have the args/kwargs from the last ignored call.
    """
    if not isinstance(delay,(float,int)):
        error_message = "'delay' must be float or integer, but found type '%s'."%type(delay)
        raise TypeError(error_message)
    elif delay<0:
        error_message = "'delay' must be positive, but found '%s'."%delay
        raise ValueError(error_message)
    
    def decorate(func):
        @functools.wraps(func)
        def call(*args,**kwargs):
            
            try:
                call.lock += 1
            except AttributeError:
                call.lock = 0
                
            try:
                active_thread_name_copy = call.active_thread_name                
            except AttributeError:
                call.active_thread_name = False
            else:
                if isinstance(active_thread_name_copy,bool):
                    pass
                elif not call.active_thread_name == threading.current_thread().name:
                    return

            call.args = args
            call.kwargs = kwargs                         
                
            if call.lock > 0:
                return
            func(*args,**kwargs)

            def reset_lock():
                time.sleep(delay)
                lock_copy = call.lock
                call.lock = -1
                if lock_copy > 0: 
                    call(*call.args,**call.kwargs)
                else:
                    call.active_thread_name = False
                    
            thread_name = "[timelockwrapper around '{0}' ({1})]".format(call.__name__, str(datetime.datetime.now())  )
            threading.Thread( target = reset_lock,
                              daemon = True,
                              name = thread_name
                                              ).start()
            
            call.active_thread_name = thread_name
            return
        return call
    return decorate



class MyThread(threading.Thread):
    """Sets parent-thread handle as parent attribute."""
    def __init__(self,*args,**kwargs):
        self.parent = threading.current_thread()
        super().__init__(*args,**kwargs)


## Obsolete but kept due to legacy-reasons for now.
## (actually never should have been created, but ah well...)
def startDaemonicThread(*args,daemon_bool = True,**kwargs):
    T = threading.Thread(*args,**kwargs)
    T.daemon = daemon_bool
    T.start()
    return T


def get_all_thread_names():
    """
    Returns a list of all thread names, created by the module threading.
    """
    ALL = threading.enumerate()
    ALL_names = []
    for a in ALL:
        ALL_names.append(a.name)
    return ALL_names

    
def print_all_thread_names(*args,**kwargs):
    """
    Prints the names of all the current threads, 
    that are created by the module threading.
    """
    ALL = threading.enumerate()
    print("\nOpen Threads:",*args,**kwargs)
    for a in ALL:
        print("  ","d" if a.daemon else "0", a.name)
    return len(ALL)


if __name__ == "__main__":
    from test.test_mythread import *#Testmythread
    import unittest
    unittest.main()

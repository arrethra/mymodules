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

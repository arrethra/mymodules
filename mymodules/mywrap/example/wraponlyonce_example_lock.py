# written by Arrethra https://github.com/arrethra/
try:
    import importcustommodules
    importcustommodules.add_parent_folder_to_sys_path(parent=3,  override=True,
                                                      print_warnings=False)
except ModuleNotFoundError: pass

# TODO: untested

import functools
import threading
import mymodules.mywrap.wraponlyonce as woo

def lockwrapper_woo(lock):
    """
    A wrapper to encase a function with the specified lock.
    It will always release the lock, even when the function
    caused an error.
    """
    def decorator(func):
        @woo.wraponlyonce(func,"lock id = "+ str(id(lock)) ) # imprints on the id of the lock
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

mylock = threading.Semaphore()
class MyLockedClass:

    @lockwrapper_woo(mylock)
    def do_something_1(self):
        print("do something 1")

    @lockwrapper_woo(mylock)
    def do_something_2(self):
        print("do something 2")

    @lockwrapper_woo(mylock)
    def do_all(self):
        self.do_something_1()
        self.do_something_2()
        
# normally, do_all cannot execute methods do_something_1 and do_something_2
# because they are wrapped with the same lock. 
# However, wraponlyonce recognises that they are all in the same thread,
# and therefore ignores/bypasses those lockwrappers
# and thus gives do_all access to both methods

mylockedclass = MyLockedClass()
mylockedclass.do_all()

# >>> do something 1
# >>> do something 2








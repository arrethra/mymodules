import threading
import functools
import inspect
import hashlib
import collections as col
import time

def ishashable(item):
    """
    Returns True if the item can be hashed, False if cannot be hashed.
    """
    try:    hash(item)
    except: return False
    else:   return True

def unhashabletype(item):
    """
    Returns a string with the type of the item that cannot be hashed.
    Semi-usefull if unhashable type is buried within the item.
    Returns empty string if item can be hashed.
    """
    try:
        hash(item)
    except Exception as e:
        e = str(e).split("'")[1]
        return e        
    else:
        return ""       
    

def get_unique_hash_of_function(function, hashfunction = 'sha224'):
    """
    Makes a (secure) hash out of the source-code of argument.
    Thereby the hash is not dependant on either the creation of the
    function (e.g. by a factory) or by the input to that function.

    Arguments:
    function:     The function/class/method you want to hash
    hashfunction: Default uses 'sha224', but you can provide your own
                  hash_algorithm here (can be a function)

    For most functions, it imprints on (only) module-path and code-line,
    which should be entirely unique for each defined function/class/..
    """
    # optimizing a bit for speed, but also traceback
    found_A0 = False
    # if function
    try:                    A0 = function.__code__      
    except AttributeError:  pass
    else:                   found_A0 = False

    if not found_A0:# if method
        try:                    A0 = function.__func__.__code__        
        except AttributeError:  pass
        else:                   found_A0 = False

    if found_A0:
        A1 = str(A0)
        A2 = A1.split("file")[1:] # finds line at which it is defined
        A3 = "".join(A2).replace(">","")
    else:
        if inspect.isbuiltin(function):
            A3 = function.__name__+"<built-in>"
        else:
            A0 = inspect.getsourcefile(function)
            # this bit is relatively expensive
            A1 = inspect.getsourcelines(function)
            A2 = A1[0] 
            A3 = A0 +" at line "+str(A1[1]) +"\n" +"".join(A2)        
        
    A4 = bytes(A3.encode())
    # low collision posibility
    if isinstance(hashfunction,str):        
        A5 = hashlib.new(hashfunction)        
        A5.update(A4)            
    else:
        A5 = hashfunction(A4)
    if isinstance(A5,(str,bytes,int)):
        return A5
    output = A5.hexdigest()
    return output


_wrap_being_used = {}
def wraponlyonce(function,wrapper):
    """
    It makes sure that if 'wrapper' is wrapped around 'function' twice,
    the wrapper is only executed once (the outer wrapper)
    It works by checking whether the 'wrapper' has been called before.
    This argument does not have to be a function, but can also be a
    unique hashable. It is strongly advised to use the latter option if
    wrapper is based on a wrapper factory. This is because the key will
    depend on the name of the wrapper. Therefore, all wrappers created
    by the wrapper_factory will be treated as one and the same wrapper.

    NOTE:   If there are multiple wrappers with the same function name
            (possibly due to different wrapper-factories) the argument
            use_function_hash prevents one from cancelling eachother.
            However, looking up that hash is quite slow (1-10ms).
            use_function_hash only works if argument wrapper is callable    
       
    Assumption is that wrapper would execute function under normal
    circumstances.

    This wrapper is used as follows:
    (functions do_something and create_hash must be of your own design)  

    def wrapper(func):
        @wraponlyonce(func,wrapper)
        @functools.wraps(func)
        def call(*args,**kwargs):
            return do_something(func,*args,**kwargs)
        return call

    Or in a wrapper_factory as
    
    def wrapper_factory(*f_args,**f_kwargs):
        unique_name = create_hash(wrapper_factory,*f_args,**f_kwargs) 
        def wrapper(func):
            @wraponlyonce(func,unique_name)
            @functools.wraps(func)
            def call(*args,**kwargs):
                return do_something(func,*args,**kwargs) 
            return call
        return wrapper
    """
    global _wrap_being_used
    if not callable(wrapper) and not ishashable(wrapper): 
            error_message = "Argument wrapper should either be callable or "+\
                            "hashable, but contained an unhashable type '%s'."\
                            %unhashabletype(wrapper)
            raise TypeError(error_message)



    # preparation for making 'thiskey'
    if callable(wrapper):
        thiswrappername = "<%s> "%wrapper.__name__ + " with hash=" + \
                               str(get_unique_hash_of_function(wrapper))
    else:
        thiswrappername = wrapper

    
    def dec(call):
        @functools.wraps(call)
        def call_(*args,**kwargs):
            global _wrap_being_used            
            
            # capture thread-name to ensure thread-safety
            # TODO: thread-safety untested
            thisthreadname = threading.current_thread().name
            thiskey = (thiswrappername,thisthreadname)

            try:
                _wrap_being_used[thiskey]
            except KeyError:
                _wrap_being_used[thiskey] = False

            if _wrap_being_used[thiskey]:
                return function(*args,**kwargs)
            else:
                _wrap_being_used[thiskey] = True
                try:
                    output = call(*args,**kwargs)
                finally:
                    _wrap_being_used[thiskey] = False
                return output
        return call_
    return dec
            
            
            

if __name__ == "__main__":
    import unittest
    from test.test_wraponlyonce import *
    unittest.main()

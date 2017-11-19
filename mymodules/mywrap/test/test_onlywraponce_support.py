# written by Arrethra https://github.com/arrethra/

# support for module test_onlywraponce

try:
    import importcustommodules
    importcustommodules.add_parent_folder_to_sys_path(parent=3,  override=True,
                                                      print_warnings=False)
except ModuleNotFoundError: pass

import mymodules.mywrap.onlywraponce as owo
import functools


# blatant copies from test_onlywraponce :P
# but I wanted to see what happens if they're moved outside of the running module
CONTROL_LIST = []
def add_to_control_list(item):
    global CONTROL_LIST
    CONTROL_LIST.append(item)
def reset_control_list():
    global CONTROL_LIST
    CONTROL_LIST = []

def wrapper_factory_support(item,wrapper_name='wrapper'):
    def wrapper(func):
        @owo.onlywraponce(func,wrapper if wrapper_name=='wrapper' else wrapper_name)
        @functools.wraps(func)
        def call(*args,**kwargs):
            add_to_control_list(item)            
            output = func(*args,**kwargs)
            add_to_control_list(item)
            return output
        return call
    return wrapper

# this foo functions is used for testing purposes in test_onlywraponce
@wrapper_factory_support("a")
def foo():
    pass

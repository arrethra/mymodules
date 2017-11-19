# written by Arrethra https://github.com/arrethra/
try:
    import importcustommodules
    importcustommodules.add_parent_folder_to_sys_path(parent=3,  override=True,
                                                      print_warnings=False)
except ModuleNotFoundError: pass

import unittest
import mymodules.mywrap.onlywraponce as owo
import functools
import mymodules.mywrap.test.test_onlywraponce_support as towos

CONTROL_LIST = []
def add_to_control_list(item):
    global CONTROL_LIST
    CONTROL_LIST.append(item)
def reset_control_list():
    global CONTROL_LIST
    CONTROL_LIST = []
    
def wrapper_factory(item,wrapper_name='wrapper'):
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

def wrapper(func):
    @owo.onlywraponce(func,wrapper)
    @functools.wraps(func)
    def call(*args,**kwargs):
        add_to_control_list("wrapper")            
        output = func(*args,**kwargs)
        add_to_control_list("wrapper")
        return output
    return call

def dec(func):
    @owo.onlywraponce(func,dec,use_function_hash=False )
    @functools.wraps(func)
    def call(*args,**kwargs):
        add_to_control_list("dec")            
        output = func(*args,**kwargs)
        add_to_control_list("dec")
        return output
    return call

def wrapper_factory1(item):
    def dec(func):
        @owo.onlywraponce(func,dec,
                          use_function_hash=False )
        @functools.wraps(func)
        def call(*args,**kwargs):
            add_to_control_list(item)            
            output = func(*args,**kwargs)
            add_to_control_list(item)
            return output
        return call
    return dec


class Test_onlywraponce(unittest.TestCase):
    def setUp(self):
        self.assertTrue(CONTROL_LIST==[])
    
    def test_owo(self):
        @wrapper_factory("a")
        @wrapper_factory("a")
        def foo():
            pass
        foo()
        self.assertTrue(CONTROL_LIST == ["a","a"])

    def test_owo_factory1(self):
        # these wrappers will not hinder eachother
        @wrapper_factory("a","a")
        @wrapper_factory("b","b")
        def foo():
            pass
        foo()
        self.assertTrue(CONTROL_LIST == ["a","b","b","a"])

    def test_owo_factory2(self):
        # these wrappers WILL hinder eachother
        @wrapper_factory("a","a")
        @wrapper_factory("b","a")
        def foo():
            pass
        foo()
        self.assertTrue(CONTROL_LIST == ["a","a"])
        
    def test_owo_nested1(self):
        # these are wraps nested, and do cancel eachother
        @wrapper_factory("a")
        def foo():
            add_to_control_list("foo")
            bar()
            add_to_control_list("foo")
        @wrapper_factory("b")   
        def bar():
            add_to_control_list("bar")
        foo()
        self.assertTrue(CONTROL_LIST == ["a","foo","bar","foo","a"])
        
    def test_owo_nested1(self):
        # these are wraps nested, and do cancel eachother
        @wrapper_factory("a","a")
        def foo():
            add_to_control_list("foo")
            bar()
            add_to_control_list("foo")
        @wrapper_factory("b","b")   
        def bar():
            add_to_control_list("bar")
        foo()
        self.assertTrue(CONTROL_LIST == ["a","foo","b","bar","b","foo","a"])

    def test_owo_wrappers_with_same_name(self):
        # wrappers (after creation) have 
        @wrapper_factory("a")
        @wrapper
        def foo():
            pass
        foo()
        self.assertTrue(CONTROL_LIST == ["a","wrapper","wrapper","a"])

    def test_owo_use_function_hash_2(self):
        # example of where it can go wrong
        # both have use_function_hash=False

        # these are clearly two different wrappers, but
        # to the computer the names of their created wrappers is the same
        # and because no hash is used, they cancel each other falsely
        @wrapper_factory1("a")
        @dec
        def foo():
            pass
        foo()
        self.assertTrue(CONTROL_LIST == ["a","a"])

    def test_owo_from_antoher_module(self):
        # test if working from between modules still works
        myfoo = towos.foo
        def foo():
            pass
        mywrappedfoo = towos.wrapper_factory_support("b")(myfoo)
        mywrappedfoo()
        self.assertTrue(towos.CONTROL_LIST == ["b","b"])
        towos.reset_control_list()

    # TODO: test for thread-safety?? (how??)

    def tearDown(self):
        reset_control_list()
##        print(3*"\n")
        


if __name__ == "__main__":
    unittest.main()

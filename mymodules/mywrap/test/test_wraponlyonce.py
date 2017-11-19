# written by Arrethra https://github.com/arrethra/
try:
    import importcustommodules
    importcustommodules.add_parent_folder_to_sys_path(parent=3,  override=True,
                                                      print_warnings=False)
except ModuleNotFoundError: pass

import unittest
import mymodules.mywrap.wraponlyonce as woo
import functools
import mymodules.mywrap.test.test_wraponlyonce_support as twoos

CONTROL_LIST = []
def add_to_control_list(item):
    global CONTROL_LIST
    CONTROL_LIST.append(item)
def reset_control_list():
    global CONTROL_LIST
    CONTROL_LIST = []
    
def wrapper_factory(item,wrapper_name='wrapper'):
    def wrapper(func):
        @woo.wraponlyonce(func,wrapper if wrapper_name=='wrapper' else wrapper_name)
        @functools.wraps(func)
        def call(*args,**kwargs):
            add_to_control_list(item)            
            output = func(*args,**kwargs)
            add_to_control_list(item)
            return output
        return call
    return wrapper

def wrapper(func):
    @woo.wraponlyonce(func,wrapper)
    @functools.wraps(func)
    def call(*args,**kwargs):
        add_to_control_list("wrapper")            
        output = func(*args,**kwargs)
        add_to_control_list("wrapper")
        return output
    return call



class Test_wraponlyonce(unittest.TestCase):
    def setUp(self):
        self.assertTrue(CONTROL_LIST==[])
    
    def test_woo(self):
        @wrapper_factory("a")
        @wrapper_factory("a")
        def foo():
            pass
        foo()
        self.assertTrue(CONTROL_LIST == ["a","a"])

    def test_woo_factory1(self):
        # these wrappers will not hinder eachother
        @wrapper_factory("a","a")
        @wrapper_factory("b","b")
        def foo():
            pass
        foo()
        self.assertTrue(CONTROL_LIST == ["a","b","b","a"])

    def test_woo_factory2(self):
        # these wrappers WILL hinder eachother
        @wrapper_factory("a","a")
        @wrapper_factory("b","a")
        def foo():
            pass
        foo()
        self.assertTrue(CONTROL_LIST == ["a","a"])
        
    def test_woo_nested1(self):
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
        
    def test_woo_nested1(self):
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

    def test_woo_wrappers_with_same_name(self):
        # wrappers (after creation) have same function-name. However, because 
        @wrapper_factory("a")
        @wrapper
        def foo():
            pass
        foo()
        self.assertTrue(CONTROL_LIST == ["a","wrapper","wrapper","a"])


    def test_woo_from_another_module(self):
        # test if working from between modules still works
        myfoo = twoos.foo
        def foo():
            pass
        mywrappedfoo = twoos.wrapper_factory_support("b")(myfoo)
        mywrappedfoo()
        self.assertTrue(twoos.CONTROL_LIST == ["b","b"])
        twoos.reset_control_list()

    # TODO: test for thread-safety?? (how??)

    def test_get_unique_hash_for_function(self):
        def custom_function():
            pass
        class CustomClass:
            def custommethod(self):
                pass
        MyCustomClass = CustomClass()
        list_test_functions = [custom_function,
                               hash, #builtin
                               CustomClass,
                               CustomClass.custommethod,
                               MyCustomClass.custommethod ]
        hash1 = []
        hash2 = []
        for test_function in list_test_functions:            
            hash1.append( woo.get_unique_hash_of_function(test_function) )
            hash2.append( woo.get_unique_hash_of_function(test_function) )
            self.assertTrue( hash1 == hash2 )
        self.assertTrue(hash1[-2] == hash1[-1]) # methods are the same, regardless whether the class is initiated or not
        
        

    def tearDown(self):
        reset_control_list()
##        print(3*"\n")
        


if __name__ == "__main__":
    unittest.main()

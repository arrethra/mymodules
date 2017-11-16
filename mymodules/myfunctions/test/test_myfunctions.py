# written by Arrethra https://github.com/arrethra/

try:
    import importcustommodules
    importcustommodules.add_parent_folder_to_sys_path(parent=3, override=True,   
                                         print_warnings = False)
except ModuleNotFoundError: pass

import sys,inspect,os
import unittest
import mymodules.myfunctions as myf

current_folder = os.path.realpath(os.path.abspath(os.path.split(
                                 inspect.getfile( inspect.currentframe() ))[0]))
parent_folder = os.path.split(current_folder)[0]


class TestArgsTakenByFunction(unittest.TestCase):    
    
    def test(self):
        # **kwargs are not counted
        def f():    pass
        self.assertTrue(myf.args_taken_by(f) == (0,0))
        
        def g(*x):  pass
        self.assertTrue(myf.args_taken_by(g) == (0,float("inf")))
        
        def h(x,*y):pass
        self.assertTrue(myf.args_taken_by(h) == (1,float("inf")))
        
        def i(x=1,*y): pass
        self.assertTrue(myf.args_taken_by(i) == (0,float("inf")))
        
        def j(**kwargs): pass
        self.assertTrue(myf.args_taken_by(j) == (0,0))
        
        def k(x,y=1,*args,z=2,**kwargs): pass
        self.assertTrue(myf.args_taken_by(k) == (1,float("inf")))
        
        def l(x,y=1,z=2): pass
        self.assertTrue(myf.args_taken_by(l) == (1,3))
        
        def m(x,y,**kwargs): pass
        self.assertTrue(myf.args_taken_by(m) == (2,2))

        def n(x,y=1,**kwargs):pass        
        self.assertTrue(myf.args_taken_by(n) == (1,2))


    def test_include_keyword(self):
        # counts **kwargs now too
        def f():    pass
        self.assertTrue(myf.args_taken_by(f,True) == (0,0))
        
        def g(*x):  pass
        self.assertTrue(myf.args_taken_by(g,True) == (0,float("inf")))
        
        def h(x,*y):pass
        self.assertTrue(myf.args_taken_by(h,True) == (1,float("inf")))
        
        def i(x=1,*y): pass
        self.assertTrue(myf.args_taken_by(i,True) == (0,float("inf")))
        
        def j(**kwargs): pass
        self.assertTrue(myf.args_taken_by(j,True) == (0,float("inf")))
        
        def k(x,y=1,*args,z=2,**kwargs): pass
        self.assertTrue(myf.args_taken_by(k,True) == (1,float("inf")))
        
        def l(x,y=1,z=2): pass
        self.assertTrue(myf.args_taken_by(l,True) == (1,3))
        
        def m(x,y,**kwargs): pass
        self.assertTrue(myf.args_taken_by(m,True) == (2,float("inf")))

        def n(x,y=1,**kwargs):pass        
        self.assertTrue(myf.args_taken_by(n,True) == (1,float("inf")))
        
        
        
        
        
class TestIsIterable(unittest.TestCase):

    def test(self):
        self.assertTrue(myf.isiterable( [1,2,3] ))
        self.assertTrue(myf.isiterable( (1,2,3) ))
        self.assertFalse(myf.isiterable( 1      ))
        self.assertTrue(myf.isiterable( "aa"   ))
        self.assertTrue(myf.isiterable( a for a in [1,2,3]   ))
        



class TestCounterFunction(unittest.TestCase):

    def assert_default_function(self,*args,**kwargs):
        self.assertTrue(myf.counter_function(*args,**kwargs) == 1)
        for n in range(10):
           self.assertTrue(myf.counter_function(*args,**kwargs) == n+2)
           
    def assert_reset(self,x,**kwargs):
        myf.counter_function(reset=x,**kwargs)
        for n in range(10):
           self.assertTrue(myf.counter_function(**kwargs) == n+1+x)

    def assert_step(self,x,**kwargs):
        import math
        
        myf.counter_function(reset=True,**kwargs)
        
        for n in range(10):        
           self.assertTrue( math.isclose(myf.counter_function(step=x,**kwargs) , (n+1)*x,abs_tol=1e-5))
    
    def test_default_function(self):
        self.assert_default_function()
           
    def test_default_reset(self):
        #check if reset works (resetted through tearDown)
        self.assert_default_function()

    def test_elem(self):
        self.assert_default_function(elem=1)
        self.assert_default_function()

    def test_reset(self):
        self.assert_reset(-1)
        self.assert_reset(-0.5)

    def test_step(self):
        self.assert_step(2)       
        self.assert_step(2.1)
        self.assert_step(-1)



    def tearDown(self):
        myf.counter_function(reset=True)
        for key in myf.counter_function(return_keys=True):
            myf.counter_function(elem=key, reset=True)


class TestGetLocation(unittest.TestCase):
    def test_get_location(self):
        self.assertTrue( myf.get_location() == current_folder )
        self.assertTrue( myf.get_location(folders_up=1) == parent_folder )
        


if __name__ == "__main__":
    unittest.main()

    

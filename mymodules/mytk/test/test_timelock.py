# written by Arrethra https://github.com/arrethra/
try:
    import importcustommodules
    importcustommodules.add_parent_folder_to_sys_path(parent=3,  override=True,
                                                      print_warnings=False)
except ModuleNotFoundError: pass

import unittest
import tkinter as tk
import time
import mymodules.mytk.timelock as tmlck
import mymodules.mytk.mytkfunctions as mytkf

TEST_DURATION = 0.335 # seconds
delay = 10 #ms
lock_delay = 60 # ms


class TestTimeLock(unittest.TestCase):

    def setUp(self):
        self.assertTrue( TEST_DURATION*1000 >= lock_delay*5) # else the test might be flawed
        self.assertTrue(lock_delay >= delay) # else the test might be flawed
        
    def test_timelock_basic(self,hook=None):        
        self.FOO = 0
        def foo():
            self.FOO += 1

        self.master = mytkf.MakeInvisibleMaster()
##        tk.Label(self.master,text="this window is opened for test_timelock_basic").pack() 
        self.master.update()
        
        if hook:
            hook(self)

        def foo_timelock():
            tmlck.timelock(self.master,
                           foo,
                           duration_of_lock=lock_delay)
            self.master.after(delay,foo_timelock)
        foo_timelock()
        
        # insurance that test will end
        self.master.after(int(TEST_DURATION * 1000+1), self.master.destroy)       



        self.master.mainloop()
        self.assertTrue( abs(self.FOO - TEST_DURATION*1000/lock_delay)  <= 1   )
        delattr(self,'FOO')
        

    def test_timelock_execute_after_waitperiod(self,hook=None):
        
        self.FOO = 0
        def foo():
            self.FOO += 1
        
        self.master = mytkf.MakeInvisibleMaster() 
        self.master.update()
        
        if hook:
            hook(self)


        def foo_timelock():
            tmlck.timelock(self.master, foo, duration_of_lock=lock_delay)
            
        foo_timelock()
        self.master.after(delay,foo_timelock())
        self.assertTrue(self.FOO == 1)
        self.master.after(lock_delay*3,self.master.destroy)

        self.master.mainloop()
        
        self.assertTrue(self.FOO == 2)        
        delattr(self,'FOO')
    
        

    def test_timelock_locker_key(self):
        # test if two timelocks can run simultaneously, as long as locker_key is different
        def hook(self):
            self.BAR = 0
            def bar():
                self.BAR += 1
            def bar_timelock():
                tmlck.timelock(self.master,
                               bar,
                               duration_of_lock=lock_delay,
                               locker_key = "a" )
                self.master.after(delay,bar_timelock)
            bar_timelock()
       
        self.test_timelock_basic(hook=hook)
        
        self.assertTrue( abs(self.BAR - TEST_DURATION*1000/lock_delay)  <= 1  )   
        delattr(self,'BAR')



    # TODO: test wrapper factory
    

    def tearDown(self):
        tmlck.timelock(None,
                           None,
                           reset='all')
        if hasattr(self,'master'):
            try:
                self.master.destroy()
            except: pass
            finally:
                delattr(self,'master')

       


if __name__ == "__main__":
    unittest.main()

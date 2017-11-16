# written by Arrethra https://github.com/arrethra/
try:
    import importcustommodules
    importcustommodules.add_parent_folder_to_sys_path(parent=3,  override=True,
                                          print_warnings = False)
except ModuleNotFoundError: pass

import mymodules.mytk.mytkfunctions as mytkf
import mymodules.mytk.mytkthread as mytkth
import unittest
import tkinter as tk
import threading
import time

ERROR = 0.04
SECONDS = 0.3


class TestMyTKthread(unittest.TestCase):


    def test_execute_functions(self):

        self.FOO = []
        self.BAZ = []
        self.FOOZ = []
        def foo(fuz):            
            self.FOO += [fuz]
        def bar(z=3):
            self.FOO += z
        def break_mainloop(master):
            master.destroy()
        def baz(lst):
            self.BAZ += lst
        def fooz(lst):
            self.FOOZ += lst

        def foobar(seconds=0.1):
            time.sleep(seconds)
            mytkth.list_function_for_execution(self.master, foo, ("x",))
            time.sleep(seconds)
            mytkth.list_function_for_execution(self.master, foo, ("y",))
            mytkth.list_function_for_execution(self.master, foo, ("z",))

            BAZ_lst = ['cheese']
            mytkth.list_function_for_execution(self.master,  baz, (BAZ_lst,))
            BAZ_lst.append('egg')

            FOOZ_lst = ['cheese']
            mytkth.list_function_for_execution(self.master,  fooz, (FOOZ_lst,), snapshot=True)
            FOOZ_lst.append('egg')
            

            
            time.sleep(seconds)
            mytkth.list_function_for_execution(self.master, bar, kwargs={"z":'a'})
            time.sleep(seconds)

            # real reason this module was written:
            # .destroy can only be called from it's own thread and not from this thread
            mytkth.list_function_for_execution(self.master, self.master.destroy)
            
        self.master = tk.Tk()
        self.master.update()
        mytkth.execute_functions(self.master)

        T = threading.Thread(target=foobar)
        T.daemon = True
        T.start()
        
        self.master.mainloop()

        # checks if functions 'foo' have been executed in correct order
        self.assertTrue( self.FOO==['x','y','z',"a"] )
        delattr(self,'FOO')

        # asserts that the function baz has been changed
        self.assertFalse(self.BAZ == ['cheese'] ) # might fail once in a blue moon. run again to check again
        delattr(self,"BAZ")

        # checks if the snapshot argument works
        self.assertTrue(self.FOOZ == ['cheese'] )
        delattr(self,'FOOZ')
        
        self.assertFalse(mytkf.is_root_present()) # should not fail, unless error
        
        # TODO: also test that it can service two masters at once (preferably in different threads)


    def test_execute_functions__wait_untill_execution(self):
        """
        Test argument wait_untill_execution of
        list_function_for_execution, which works in conjunction with
        execute_functions.
        """        
        def foo(seconds):
            start_time = time.time()
            
            mytkth.list_function_for_execution(self.master, time.sleep,args=(seconds,), wait_untill_execution=True)

            elapsed_time = time.time() - start_time
            self.assertTrue(abs(elapsed_time - SECONDS)< (ERROR+TIMER))
            
            mytkth.list_function_for_execution(self.master, self.master.destroy)

        
        self.master = mytkf.MakeInvisibleMaster()
        tk.Label(self.master,text="test_execute_functions_wait_untill_execution").pack()
        TIMER = 0.01
        mytkth.execute_functions(self.master,timer=TIMER)

        T = threading.Thread(target=foo,args=(SECONDS,))
        T.daemon = True
        T.start()

        self.master.after(int((SECONDS+TIMER)*2000),self.master.destroy) # insurance that test is not halted...
        self.master.mainloop()

        
    def setUp(self):
        self.assertFalse(mytkf.is_root_present()) # if this line fails, error might be somewhere else

    def tearDown(self):
        if hasattr(self,'master'):
            try:
                self.master.destroy()
            except: pass
            finally:
                delattr(self,'master')
                

if __name__ == "__main__":
    unittest.main()

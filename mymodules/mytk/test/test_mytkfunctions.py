# written by Arrethra https://github.com/arrethra/
try:
    import importcustommodules
    importcustommodules.add_parent_folder_to_sys_path(parent=3, override=True,
                                          print_warnings = False)
except ModuleNotFoundError: pass

import mymodules.mytk.mytkfunctions as mytkf
import unittest
import tkinter as tk
from tkinter import messagebox as tkm
import time

ERROR = 0.04
SECONDS = 0.3


class TestMyTKFunctions(unittest.TestCase):
    def test_is_root_present(self):
        self.master =  mytkf.MakeInvisibleMaster()#tk.Tk() 
        self.assertTrue(mytkf.is_root_present())
        self.master.destroy()
        self.assertFalse(mytkf.is_root_present())
        
        

    def test_MakeInvisibleMaster(self):
        self.master = mytkf.MakeInvisibleMaster()
        self.assertTrue(mytkf.is_root_present())
        self.master.destroy()

    def test_Wrapper_MakeInvisibleMaster(self):
        # depends on validity of is_root_present()
        # Creates a popup message twice, so I can imagine it if you'd want to disable this test...
        
        askyesno_wrapped = mytkf.InvisibleMasterWrapper(tkm.askyesno)
        askyesno_wrapped("PRESS ENTER TO CONTINUE","Just give me an answer, so this test can continue.\n"+
                         "PS, no other tk-window should be visible.")
        self.assertFalse(mytkf.is_root_present())

        self.master = tk.Tk()
        askyesno_wrapped("PRESS ENTER TO CONTINUE","Just give me an answer, so this test can continue.\n"+
                         "PS, a tk-window should be visible")
        self.assertTrue(mytkf.is_root_present())

    def test_is_root_alive(self):
        self.master =  mytkf.MakeInvisibleMaster()
        self.assertTrue( mytkf.is_root_alive(self.master) )
        self.masterTOP = tk.Toplevel(self.master)
        self.assertTrue( mytkf.is_root_alive(self.masterTOP) )
        self.masterTOP.destroy()
        self.assertFalse( mytkf.is_root_alive(self.masterTOP) )
        self.master.destroy()
        self.assertFalse( mytkf.is_root_alive(self.master) )

    def test_get_parent(self):
        self.master =  mytkf.MakeInvisibleMaster()
        widget = tk.Toplevel(self.master)
        self.assertTrue(self.master ==  mytkf.get_parent(widget))
        self.master2 = mytkf.MakeInvisibleMaster()
        widget2 = tk.Toplevel(self.master2)
        self.assertTrue(self.master2 ==  mytkf.get_parent(widget2))
        self.assertTrue(self.master ==  mytkf.get_parent(widget))        
        self.assertTrue(self.master == mytkf.get_parent(self.master) )
        self.master2.destroy()
        delattr(self,'master2')

    def test_get_root(self):
        self.master = mytkf.MakeInvisibleMaster()
        toplevels  = [tk.Toplevel(self.master)]
        for i in range(0,3):
            toplevels += [tk.Toplevel(toplevels[-1])]
        root = mytkf.get_root(toplevels[-1])
        self.assertTrue(self.master == root )
        self.assertTrue(self.master == mytkf.get_root(self.master) )
        
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

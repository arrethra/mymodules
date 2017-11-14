# written by Arrethra https://github.com/arrethra/
try:
    import importcustommodules
    importcustommodules.add_parent_folder_to_sys_path(parent=3,
                                          print_warnings = __name__=="__main__")
except ModuleNotFoundError: pass

import my_modules.mytk.mytkfunctions as mytkf
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

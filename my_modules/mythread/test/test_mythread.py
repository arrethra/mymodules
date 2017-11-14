# written by Arrethra https://github.com/arrethra/
try:
    import importcustommodules
    importcustommodules.add_parent_folder_to_sys_path(parent=3,
                                          print_warnings = __name__=="__main__")
except ModuleNotFoundError: pass

## TODO: old import-statement, remove
##import sys,os,inspect
##current_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]))
##parent_folder = os.path.split(current_folder)[0]
##if parent_folder not in sys.path:
##    sys.path.insert(0, parent_folder)
##    
##del current_folder, parent_folder, sys,os,inspect

import unittest
import time
import threading
import my_modules.mythread as myth

SECONDS = 0.5

global_time_list = []
def add_global_time_list():
    global global_time_list
    global_time_list += [time.time()]

def reset_global_time_list(add=True):
    global global_time_list
    global_time_list = []
    if add:
        add_global_time_list()

def calculate_global_elapsed_time(elem = -1):
    global global_time_list
    return global_time_list[elem] - global_time_list[0]



class Testmythread(unittest.TestCase):
    def test_WaitTillThreadIsOver(self):

        start_time = time.time()
        A = myth.WaitTillThreadIsOver(target=time.sleep,args=(SECONDS,))
        A.start()
        elapsed_time = time.time() - start_time

        self.assertTrue(abs(elapsed_time - SECONDS) <0.03 )

    def test_lockwrapper(self):
        test_lock = threading.Semaphore()
        reset_global_time_list()

        @myth.lockwrapper(test_lock)
        def foo():
            time.sleep(SECONDS)
            add_global_time_list()



        add_global_time_list()
        threading.Thread(target=foo).start()
        foo()
        elapsed_time = calculate_global_elapsed_time()

        self.assertTrue( abs(elapsed_time - 2*SECONDS) < 0.03)
        reset_global_time_list(add=False)

    def test_lockwrapper_error_handling(self):
        with self.assertRaises(TypeError):
            @myth.lockwrapper("a")
            def foo():
                pass

        with self.assertRaises(TypeError):
            @myth.lockwrapper(reset_global_time_list)
            def bar():
                pass




if __name__ == "__main__":
    unittest.main()

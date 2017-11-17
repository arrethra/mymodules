# written by Arrethra https://github.com/arrethra/
try:
    import importcustommodules
    importcustommodules.add_parent_folder_to_sys_path(parent=3,  override=True,
                                                      print_warnings=False)
except ModuleNotFoundError: pass

import unittest
import time
import threading
import mymodules.mythread as myth

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
            
    def test_timelockwrapper(self):
        self.FOO = 0
        
        @myth.timelockwrapper(SECONDS)
        def foo():
            self.FOO += 1

        foo()
        foo()
        self.assertTrue(self.FOO == 1)
        time.sleep(SECONDS*1.1)
        self.assertTrue(self.FOO == 2)




if __name__ == "__main__":
    unittest.main()

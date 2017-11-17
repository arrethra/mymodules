# written by arrethra https://github.com/arrethra

import tkinter as tk
import functools


def set_minimum_size(master, fix_max=False, fix_min=True):
    """
    Sets current size of a window 'master' to minimum size.
    If argument fix_max is True, the current size of window
    is the maximum size.
    """
    master.update()
    geom = master.geometry().split("+")[0].split("x")
    size = tuple(map(int,geom))
    if fix_min:
        master.minsize(*size)
    if fix_max:
        master.maxsize(*size)

        
def is_root_present():
    """
    Returns a boolean on whether there is a tk-window active or not.
    
    This method is based on the fact that tk.IntVar cannot work
    without a root/master present somewhere.
    """
    try:
        Ii = tk.IntVar()
        Ii.set(0)
        Ii.trace("w",lambda*x:x)                
    except:
        output = False                
    else:
        output = True
            
    return output

def is_root_alive(root):
    """
    Checks if root is alive, and returns it's state.
    If destroyed, it returns False.
    """
    try:
        answer = root.state()            
    except Exception as e:
        # I guess all exceptions mean that the window is not live..
        return False 
##        e = str(e).lower()        
##        if e.endswith('application has been destroyed'):
##            return False
##        else:
##            raise        
    else:
        return answer
        


class MakeInvisibleMaster(tk.Tk):
    """
    Creates an invisible master. Can serve well as a master for pop-up
    messages, such as those from tkinter.messagebox.
    Do remember to destroy master afterwards.
    """
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.wm_overrideredirect(1)
        self.attributes("-alpha",0)


def InvisibleMasterWrapper(func):
    """
    Wrapper around a function that creates an invisible master,
    if no master is to be present.
    Master is detroyed instantly, after function has executed.
    Suitable to be wrapped around functions such as pop-ups from
    tkinter.messagebox.
    """
    @functools.wraps(func)
    def decorator(*args,**kwargs):
        root_bool = is_root_present()
        if not root_bool:
            InvisMas = MakeInvisibleMaster()
        try:
            output = func(*args,**kwargs)
        finally:
            if not root_bool:
                InvisMas.destroy()
        return output
    return decorator


if __name__ == "__main__":
    import unittest
    from test.test_mytkfunctions import *
    unittest.main()

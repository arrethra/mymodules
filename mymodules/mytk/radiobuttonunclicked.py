# written by arrethra https://github.com/arrethra

import tkinter as tk
from tkinter import ttk

# couples self.variable to self.variable_memory
_MEMORY_VARIABLE_LIST = []
def _create_or_match_memory_variable(var):
    """
    Matches the correct memory_variable between classes
    or creates a StringVar for it
    """
    global _MEMORY_VARIABLE_LIST
    var_list =  [a[0] for a in _MEMORY_VARIABLE_LIST]
    if var in var_list:
        i = var_list.index(var)
        return _MEMORY_VARIABLE_LIST[i][1]
    else:
        memory_var = tk.StringVar()
        _MEMORY_VARIABLE_LIST.append([var,memory_var])
        return memory_var
        
        

# TODO: seems to sometimes glitch, but not sure
class RadiobuttonUnclicked(tk.Radiobutton):
    """
    Acts exactly as a radiobutton, except that it can be unclicked.
    This means that when clicked upon a radiobutton while it was already
    was selected, it now will be unselected.
    When the radiobutton is unclicked, it's value will become
    unclicked_value.
    
    NOTE:  If there is a radiobutton linked to unclick_value, that
           button will be selected instead.

    NOTE2: When putting a trace on the 'variable, unclicking causes an
           extra event to be sparked, before it is set to unclick_value.
    """
    
    def __init__(self, master=None, unclick_value = 0, cnf={}, **kw ):
        """
        Construct a radiobutton widget with the parent MASTER.

        Valid resource names: activebackground, activeforeground, anchor,
        background, bd, bg, bitmap, borderwidth, command, cursor,
        disabledforeground, fg, font, foreground, height,
        highlightbackground, highlightcolor, highlightthickness, image,
        indicatoron, justify, padx, pady, relief, selectcolor, selectimage,
        state, takefocus, text, textvariable, underline, value, variable,
        width, wraplength.

        extra argument:
        unclick_value: when a radiobutton is unselected,
                       the variable becomes this value
        """
        # TODO: automaticaly inherit docstring from parent, but add the last few lines...
                  
        self.kw = kw
        if 'command' in kw:
            self.command = kw['command']
            kw['command'] = lambda*x:(self.unclick(),self.command(*x))
        else:
            kw['command'] = self.unclick
        
        if 'unclick_value' in kw:
            self.unclick_value = kw['unclick_value']
            del kw['unclick_value']
        else:
            self.unclick_value = unclick_value
            
        # sorry, I don't know how to corrrectly obtain variable
        # from the Radiobutton-class directly..
        if 'variable' in kw:
            self.variable = kw['variable']            
        else:            
            self.variable = tk.StringVar()
            kw['variable'] = self.variable
            self.variable.set(unclick_value)
        
        self.variable_memory = _create_or_match_memory_variable(self.variable)
        self.variable_memory.set( self.variable.get() )

        super().__init__(master,cnf,**kw)
        

    def unclick(self):
        """
        This method is responsible for unclicking the radiobutton.
        This method is automatically added to the 'command' option,
        and is executed everytime the button is clicked upon.
        """
        if self.variable.get() == self.variable_memory.get():            
            self.variable.set( self.unclick_value )
##            self['value'] = self.unclick_value
        self.variable_memory.set( self.variable.get() )
        return self.variable.get()


    def config(self,cnf=None, **kw):
        __doc__ = super().config.__doc__
        if 'command' in kw:
            self.command = kw['command']
            kw['command'] = lambda*x: (self.unclick(),
                                       self.command(*x))
        if 'unclick_value' in kw:
            self.unclick_value = kw['unclick_value']
            del kw['unclick_value']
        if 'variable' in kw:
            self.variable = kw['variable']
            self.variable_memory = _create_or_match_memory_variable(self.variable)
            self.variable_memory.set( self.variable.get() )
        super().config(cnf,**kw)

    def configure(self,cnf=None,**kw):
        __doc__ = super().config.__doc__
        self.config(cnf=None,**kw)




if __name__ == "__main__":
    # example
    class r: pass
    R = r()

    def foo(*x):
        print(R.var.get())

    
    root = tk.Tk()

    R.var = tk.StringVar()
    R.var.set(0)
    R.var.trace('w',foo)


    nr_of_buttons = 5
    for i in range(1,nr_of_buttons+1):
        setattr(R,"R"+str(i), RadiobuttonUnclicked(root,text=str(i),variable=R.var, value = i)  )
        getattr(R,"R"+str(i)).pack()

    root.mainloop()

        
        

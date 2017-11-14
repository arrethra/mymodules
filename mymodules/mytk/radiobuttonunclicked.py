# written by arrethra https://github.com/arrethra

import tkinter as tk
from tkinter import ttk


class RadiobuttonUnclicked(tk.Radiobutton):
    """
    Acts exactly as a radiobutton, except that it can be unclicked.
    This means that when clicked upon a radiobutton while it was already
    was selected, it now will be unselected.
    When the radiobutton is unclicked, it's value will become
    unclicked_value. NOTE: if there is a radiobutton linked to that
    specific value, that button will be selected instead.

    NOTE2: when putting a trace on the 'variable, unclickign might
    cause an extra event to be sparked, before it is set to 0.
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
            kw['command'] = lambda*x:(self.unclick(),self.command())
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

        
        self.variable_memory = self.variable.get()

        super().__init__(master,cnf,**kw)
        

    def unclick(self):
        """
        This method is responsible for unclicking the radiobutton.
        This method is automatically added to the 'command' option,
        and is executed everytime the button is clicked upon.
        """
        if self.variable.get() == self.variable_memory:            
            self.variable.set( self.unclick_value )
        else:
            self.variable.set( self['value'] )
        self.variable_memory = self.variable.get()
        return self.variable.get()


    def config(self,cnf=None, **kw):
        __doc__ = super().config.__doc__
        if 'command' in kw:
            self.command = kw['command']
            kw['command'] = lambda*x: (self.unclick(),
                                       self.command())
        if 'unclick_value' in kw:
            self.unclick_value = kw['unclick_value']
            del kw['unclick_value']
        if 'variable' in kw:
            self.variable = kw['variable']
        super().config(cnf,**kw)

    def configure(self,cnf=None,**kw):
        __doc__ = super().config.__doc__
        self.config(cnf=None,**kw)




if __name__ == "__main__":
    ## example
    root = tk.Tk()

    R_var = tk.StringVar()
    R_var.set(0)
    R_var.trace("w",lambda*x:foo("=="))

    def foo(*args):
        print("A",R_var.get(),*args)

    R1 = RadiobuttonUnclicked(root,text='1',variable=R_var, value = 1, command= foo)
    R1.pack()
    R2 = RadiobuttonUnclicked(root,text='2',variable=R_var, value = 2, command= foo)
    R2.pack()

    root.mainloop()

        
        

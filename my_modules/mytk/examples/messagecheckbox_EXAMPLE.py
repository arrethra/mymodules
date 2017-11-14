import tkinter as tk
from tkinter import ttk

import sys,os,inspect
current_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]))
parent_folder = os.path.split(current_folder)[0]
if parent_folder not in sys.path:
    sys.path.insert(0, parent_folder)    
del current_folder, parent_folder, sys,os,inspect

from messagecheckbox import MessageCheckBox, ShowMessageCheckBox

root = tk.Tk()

I = tk.IntVar()
I.set(0)
I.trace("w",lambda*x:print("this one has been toggled"))

counter =0

stringssss = [("a","b","c","d","e"),
              ("1","2","3","4"),
              ("!","@","#")]+110*[("P","G")]

def foo(title=None):
    global counter
    countercopy = counter
    counter += 1

    def bar(countercopy):
        def f():
            print("%s:"%countercopy, A)
        return f
    f = bar(countercopy)
    
    A = ShowMessageCheckBox(
                        master = root,
                        title= title if title else "PREFS "+str(countercopy),
                        message = 20*"+",
                        disabled = I.get(),
                        checkbutton_var = I,
                        checkbutton_text = "Do not show this message again",
                        strings= stringssss[countercopy]
                        )
    f()


B = ttk.Button(root, text = "create", command = foo)
B.pack()

for i in range(1):
    root.after(600*i,foo)


print("HOI")
root.mainloop()
print("mainloop ended")

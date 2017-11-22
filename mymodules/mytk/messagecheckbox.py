# written by arrethra https://github.com/arrethra

import tkinter as tk
from tkinter import ttk
import os.path
import threading
import time




CENTER_POSITION = (0,0)

# TODO: if no message is entered, title might not be shown, because window is not large enough
def create_transparent_icon(path = "temporary"):
    """
    Creates a transparent icon-file and returns the path to the file.   
    if path is specified, the transparent icon will be
    created/overwritten at given location. Otherwise, the transparent
    icon will be created in a temporary file.
    """
    #source: http://stackoverflow.com/questions/550050/removing-the-tk-icon-on-a-tkinter-window
    import tempfile
    
    ICON = (b'\x00\x00\x01\x00\x01\x00\x10\x10\x00\x00\x01\x00\x08\x00h\x05\x00\x00'
            b'\x16\x00\x00\x00(\x00\x00\x00\x10\x00\x00\x00 \x00\x00\x00\x01\x00'
            b'\x08\x00\x00\x00\x00\x00@\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x01\x00\x00\x00\x01') + b'\x10'*1282 + b'\xff'*64
       
    if path == "temporary":
        _, ICON_PATH = tempfile.mkstemp()
    else:
        if not os.path.exists(path):
            error_message = "Argument path is not a valid path. (It was '%s'.)"%path
            raise ValueError(error_message)
        ICON_PATH = path
        
    with open(ICON_PATH, 'wb') as icon_file:
        icon_file.write(ICON)
    return ICON_PATH


def reposition_center():
    import random
    global CENTER_POSITION
    
    step = 50
    nr_of_steps = 2
    original_pos = CENTER_POSITION
    x,y = _add_tuples(CENTER_POSITION, (step,step))
 
    def out_of_bounds(*X):
        return any(abs(x) > nr_of_steps * step for x in X)

    if out_of_bounds(x,y):
        x = x - 2 * nr_of_steps* step - step
        y = y - 2 * nr_of_steps* step         
        while out_of_bounds(x,y):
            x,y = _add_tuples((x,y), (step,step))
            if out_of_bounds(x) and out_of_bounds(y):
                x,y = (nr_of_steps* step , -nr_of_steps* step)
    
    CENTER_POSITION = (x,y)
    
    random_pos = (random.randint(0,int(step/5)),random.randint(0,int(step/5)))    
    return _add_tuples(original_pos, random_pos)


def _add_tuples(*args):
    A = len(args[0])
    if not all(len(a)==A for a in args):
        error_message = "Expected all arguments to be of same length, but instead found respective lengths %s"%[len(a) for a in args]
        raise ValueError(error_message)
    output = (0,)*A
    for arg in args:
        output = [a + output[i] for i,a in enumerate(arg)]
    output = tuple(output)
    return output
    
        
class DefaultValues:
    """
    Contains default values for MessageBox and MessageCheckBox.
    """
    master = None
    message = ""
    wrap_length = "off"
    title = None
    checkbutton_var = "BooleanVar(False)"
    checkbutton_text = ""
    strings = "(OK,)"
    default = "strings[-1]"    
    default_disabled = "strings[-1]"
    disabled = False
    icon = "transparent"
    timer = "off"
    close_upon_function = "disabled"
    close_upon_function_timer = 0.1

DEFAULT = DefaultValues()

_GRID_OPTIONS ={}

WINDOWS_OPEN = [] # TODO: right now, this moldule can't serve two masters I think, so each window in this list needs to be linked with that master....


class MessageBox():
    def __init__(self,  master        = DEFAULT.master,
                        message       = DEFAULT.message,
                        title         = DEFAULT.title,
                        wrap_length   = DEFAULT.wrap_length,
                        strings       = DEFAULT.strings,
                        default       = DEFAULT.default,
                        default_disabled = DEFAULT.default_disabled,
                        disabled      = DEFAULT.disabled,
                        icon          = DEFAULT.icon,
                        timer         = DEFAULT.timer,
                        close_upon_function = DEFAULT.close_upon_function ):
        """
        This class enables a challenge box to be popped up, with
        customized title, message(/question) and buttons. Use the method
        'show' to reveal the challenge box. The answer will be based on
        the text of the button.v(see argument strings)
        
        Arguments (all optional):
        master:         The master can be specified through this
                        argument. Specify it to be the string 'own' if
                        it should be a stand-alone box, not tied to any
                        master present.
        message:        The message that will be displayed, upon which
                        the user must base his choice.
        wrap_length:    Lines in the message will begin a new line after
                        this many characters in a line. wrap_length can
                        disabled by input of 0 or less, or the string
                        "off".
        title:          The title of the challenge box.
        strings:        This argument defines the text on the buttons
                        and the number of buttons displayed. This
                        argument is a tuple that contains strings; the
                        number of strings is the number of buttons, and
                        the order of the strings will be the order of
                        the buttons (left to right). The returned answer
                        (first element of returned tuple from method
                        show) will be one of the strings contained
                        within this argument (and of course based on the
                        button that is chosen by the user).
                        Duplicates are not allowed.
        default:        Default answer that is returned if
                        messagebox was exited (by red X topright corner).
        default_disabled:
                        Default value that is returned, if disabled.
                        Also determines which button is highlighted when
                        the messagebox is popped up. This
                        furthermore means that if pressed "Return",
                        this answer will be selected. Default is the last
                        element from the argument strings.
        disabled:       If this argument is specified to be true, this
                        will disable the pop-up from appearing when the
                        method show is called. The answer will become
                        the argument default_disabled.
        timer:          If above zero, the message will be destroyed in
                        the number of seconds entered. The answer
                        returned will be 'default_disabled'. This button
                        will also contain the timer counting down.
                        Timer will be disabled by a value of 0 or less,
                        or the string 'off'.
        icon:           Determines the icon of the pop-up. The possible
                        values are the following:
                        -"transparent": icon will be set to transparent.
                        -"default": nothing is enforced (i.e. icon will
                                    either have default tkinter icon, or
                                    obtains icon from parent if
                                    configured that way)
                        -filepath to a valid icon-file. See method
                            tk.Toplevel.iconbitmap for more information.
        close_upon_function:
                        This should be a function that returns False as
                        long as the messagebox should be alive. When the
                        function changes to True, the mesagebox should
                        be closed. This function is called at intervals.
                        These intervals are by default 0.1s, but can be
                        changed by giving function an attribute 'timer'
                        (seconds)
                        
        

        Attributes: 
        TOP:             Handle of the window. If no master was present,
                         this is the handle of the root. If a master was
                         present, this will be the handle of a
                         Toplevel-window.
        label:           Handle of the label, that holds the message.
        button_*string*: Handle of a button, with text string. Example,
                         if there are two buttons, 'yes' and 'no', then
                         the attributes would be called button_yes and
                         button_no.

        *argument*:      Each argument has their own attribute, that is
                         called the same.
        Notes on attributes:
                         -handles are only created when calling
                          the method show. Upon closing the
                          messagecheckbox, these attributes are deleted
                          as well. This means that they are only live
                          during the method 'show'. Note that there is a
                          method hook, that is performed before the
                          mainloop is entered. These attributes will be
                          accessable via that method.
                         -when changing arguments, any default values
                          from other attributes (such as the default
                          of default_disabled strings) will not be
                          changed accordingly. 
                          
        """
        self._all_arguments = locals().copy()
        del self._all_arguments["self"]

        self.active = False

        
        self.master = master
        self.strings = strings
        self.default = default
        self._returned_button = self.default

        self.default_disabled = default_disabled


        self.title = title
        self.message = message
        
        self.wrap_length = wrap_length
        self.disabled = disabled
        self.icon = icon
        self.timer = timer

        self.close_upon_function = close_upon_function
     
        self._wrap_message(message, wrap_length)
        self._check_argument_attributes()
        
        


    @property
    def strings(self):
        return self._strings
    @strings.setter
    def strings(self,val):        
        if val == DEFAULT.strings:
            val = ("OK",)
        if self._assert_strings(val):
            raise self._assert_strings(val)
        self._strings = val
        
    @property
    def default(self):
        return self._default
    @default.setter
    def default(self,val):        
        if val == DEFAULT.default:
            val = self.strings[-1]
        if self._assert_default(val):
            raise self._assert_default(val)
        self._default = val

    @property
    def default_disabled(self):
        return self._default_disabled
    @default_disabled.setter
    def default_disabled(self,val):        
        if val == DEFAULT.default_disabled:
            val = self.strings[-1]
        if self._assert_default_disabled(val):
            raise self._assert_default_disabled(val)
        self._default_disabled = val

    @property
    def wrap_length(self):
        return self._wrap_length
    @wrap_length.setter
    def wrap_length(self,val):
        if not isinstance(val,(int,str)):
            error_message = "wrap_length should be integer or the string"\
                            +"'off', but found type %s"%type(val)
            raise TypeError(error_message)
        if isinstance(val,str) and val.lower() != "off":
            error_message = "wrap_length was found to be string, but should be"\
                            "the string 'off'; instead found '%s'"%val
            raise ValueError(error_message)
        
        self._wrap_length = val
        if hasattr(self,"_wrapped_message"):
            # putting it under this statement makes startup more efficient
            self._wrap_message(self.message, self._wrap_length)
            
    @property
    def message(self):
        return self._message
    @message.setter
    def message(self,val):        
        if not isinstance(val,str):
            error_message = "'message' was not a string, but of type %s"\
                            %type(val)
            raise ValueError(error_message)
        self._message = val
        if hasattr(self,"_wrapped_message"):
            # putting it under this statement makes startup more efficient
            self._wrap_message(self.message, self.wrap_length)            

    @property
    def timer(self):
        return self._timer
    @timer.setter
    def timer(self,val):        
        if self._assert_timer(val):
            raise self._assert_timer(val)
        self._timer = val

    @property
    def master(self):
        return self._master
    @master.setter
    def master(self,val):        
        if self._assert_master(val):
            raise self._assert_master(val)
        self._master = val

    @property
    def icon(self):
        return self._icon
    @icon.setter
    def icon(self,val):        
        if self._assert_icon(val):
            raise self._assert_icon(val)
        self._icon = val
        
    @property
    def close_upon_function(self):
        return self._close_upon_function
    @close_upon_function.setter
    def close_upon_function(self,val):        
        if self._assert_close_upon_function(val):
            raise self._assert_close_upon_function(val)
        self._close_upon_function = val
        
    @property
    def close_upon_function_timer(self):
        return self._close_upon_function_timer
    @close_upon_function_timer.setter
    def close_upon_function_timer(self,val):        
        if self._assert_close_upon_function_timer(val):
            raise self._assert_close_upon_function_timer(val)
        self._close_upon_function_timer = val
        

    def show(self):
        """
        This method will show the messagecheckbox. The return of this
        method will be a tuple containing the answer and the state of
        the checkbox.
        """
        if self.disabled:            
            return self._disabled()
        
        self._returned_button = self.default
        
        global WINDOWS_OPEN
        # cannot change attributes while current messagecheckbox is still active
        # thus, a new instance must be created (not ideal though...)
        if self in WINDOWS_OPEN:
            return MessageCheckBox(**self._all_arguments).show()        
        WINDOWS_OPEN += [self]

        if self.is_root_present():
            self.TOP = tk.Toplevel(self.master)             
        else:
            self.TOP = tk.Tk()

        self.active = True
            
        if isinstance(self.title,str):
            self.TOP.title(self.title)
        self.TOP.withdraw()
        self.TOP.protocol('WM_DELETE_WINDOW', self._destroy)
        self.TOP.bind_all("<Escape>",self._destroy)
        
        self.set_icon(self.icon)
       
        self._create_message()
        self._create_buttons(*self.strings)
        
        if isinstance(self,MessageCheckBox):
            self._create_checkbutton(text = self.checkbutton_text,
                                     checkbutton_var = self.checkbutton_var)
        for x in range(len(self.strings)):
            self.TOP.grid_columnconfigure(x,weight=1)        

        self.TOP.update()        
        self.TOP.deiconify()
        self._center_message()        
        self._focus_and_lift()
        self.TOP.grab_set()


        self.hook()
        if self.close_upon_function != DEFAULT.close_upon_function:
            self.set_close_upon_function()
        self._set_timer()
        
        self.TOP.mainloop()

        return self._return_show()

    def _return_show(self):
        return self._returned_button
    
    def hook(self):
        """
        A hook that is called upon by method show, before it enters
        the mainloop.
        
        When inherited and overidden, it enables extra functions/actions
        to be carried out before entering mainloop (which would make it
        impossible to perform functions/actions on the messagecheckbox
        before an answer has been given).
        """
        pass


    def _disabled(self):
        """
        The method show will call upon this method, if the variable
        disabled is True.
        """
        self._returned_button = self.default_disabled
        return self._return_show()
    
    def _destroy(self,*x):
        """
        Destroys the messagecheckbox, quits the mainloop.
        Arguments *x do not do anything.
        """
        if self.active:
            self.active = False
            
            
            self.TOP.grab_release()
            self.TOP.destroy()
            self.TOP.quit()
            self._stop_after()
            global WINDOWS_OPEN
            WINDOWS_OPEN.remove(self)
            if WINDOWS_OPEN:
                WINDOWS_OPEN[-1].TOP.grab_set()
                WINDOWS_OPEN[-1]._focus_and_lift()
            self._cleanup()

                
    def _cleanup(self):
        """Deletes the attributes of the handles, that are no longer used."""
        attributes_to_be_deleted = ["TOP",
                                    '_is_root_present_bool',
                                    "_focus_on_button_with_string",
                                    "_timer_handle"]
        for attr in attributes_to_be_deleted:
            if hasattr(self,attr):
                delattr(self,attr)

        for s in self.strings:
            delattr(self,"button_"+s)


    def _stop_after(self):
        """
        The timer and close_upon_function use the method after.
        If such a function/method is scheduled, when the message_box
        quits, this gives off an error. Running this method deschudeles
        those methods.
        """        
        if hasattr(self,"_timer_handle"):
            try:
                self.TOP.after_cancel(self._timer_handle)
            except: pass

        if hasattr(self,"_loop_upon_function_handle"):
            try:
                self.TOP.after_cancel(self._loop_upon_function_handle)
            except: pass
        

    def _find_master(self):
        if self.master and not isinstance(self.master,str):
            master = self.master
        else:
            master_name = self.TOP.winfo_parent()
            master = self.TOP._nametowidget(master_name)
        return master


    def set_icon(self, icon):
        self.icon = icon        

        if self.icon.lower() == "transparent":
            self.TOP.iconbitmap(create_transparent_icon())
        elif self.icon.lower() == "default":
            pass
        elif isinstance(icon,str) and os.path.exists(icon):
            self.TOP.iconbitmap(icon)


    def _wrap_message(self, message, wrap_length):
        if isinstance(wrap_length,int):
            if wrap_length > 0:
                pass
            else:
                self._wrapped_message = message
                return
        elif isinstance(wrap_length, str) and wrap_length.lower() == "off":
            self._wrapped_message = message
            return
            
        
        message_broken = message.split("\n")
        wrapped_message = []
        for m in message_broken:
            wrapped_message.append(m)
            while len(wrapped_message[-1])>wrap_length:
                index = wrapped_message[-1][0:wrap_length].rfind(" ")
                if index==-1: index = wrap_length            
                new_line = wrapped_message[-1][index:]
                wrapped_message[-1] = wrapped_message[-1][0:index]
                wrapped_message.append(new_line.lstrip())
        if wrapped_message[-1] == len(wrapped_message[-1])*" ":
            wrapped_message = wrapped_message[:-1]
        
        self._wrapped_message = "\n".join(wrapped_message)

        
        

    def _create_message(self):
        self.label = tk.Label(self.TOP,text= self._wrapped_message)
        self.label.grid(row=0,column=0,pady=10,padx=10
                          ,columnspan=len(self.strings),
                          sticky='nswe',**_GRID_OPTIONS)

       
    def _create_buttons(self,*strings):
        for i,s in enumerate(strings):
            def callback(s):
                def f(*x):
                    self._returned_button = s                    
                    self._destroy()
                    
                return f
            b = ttk.Button(self.TOP, text=s, command= callback(s))
            
            pad_x = 2*[5]
            if i == 0:            pad_x[0] += 5
            if i == len(strings): pad_x[1] += 5
            
            b.grid(column=i, row=1,
                   padx=pad_x, pady=[7,10])           
            
            b.bind("<Return>",callback(s))
            if s == self.default_disabled:
                self._focus_on_button(b, s)
            setattr(self, "button_"+s, b)           
            b.bind("<Left>", lambda*x:self._focus_on_new_button(-1))
            b.bind("<Right>",lambda*x:self._focus_on_new_button(1))
            


    def _focus_on_button(self, button_handle, button_string):
        button_handle.focus_set()
        self._focus_on_button_with_string = button_string
        

    def _focus_on_new_button(self,direction = 1):
        if not direction in [1,-1]:
            error_message = "Argument direction must be either 1 (right) or -1 (left), but found '%s'."%direction
            raise ValueError(error_message)
        old_index = self.strings.index(self._focus_on_button_with_string)
        new_index = old_index + direction
        if new_index < 0:
            new_index = len(self.strings)-1
        elif new_index>=len(self.strings):
            new_index = 0

        new_string = self.strings[new_index]
        new_button_handle = getattr(self,"button_"+new_string)

        self._focus_on_button(new_button_handle, new_string)
        
            
        

    def _set_timer(self):
        if isinstance(self.timer,int) and self.timer <=0:
            return
        if isinstance(self.timer,str) and self.timer.lower() == "off":
            return
        
        Button_handle = getattr(self,"button_"+self.default_disabled)
        self._time_left = self.timer

        def update_timer(Button_handle):

            if isinstance(self._time_left,str):
                if self._time_left == 'off':
                    # set text to normal
                    Button_handle.configure(text = self.default_disabled)
                    return
                else:
                    Exception # this should never happen
            else:
                self._time_left += -1
                _time_left = self._time_left
            
            m,s=divmod(max(_time_left,0),60)
            h,m=divmod(m,60)
            if _time_left >= 3600:
                time_string = "%sh"%h
            elif _time_left >= 60:
                time_string = "%sm"%m
            else:
                time_string = "%s"%s
                
            Button_handle.configure(text = self.default_disabled+" ({})".format(time_string) )
            if _time_left>0:
                def foo():
                    return update_timer(Button_handle)
                self._timer_handle = Button_handle.after(1000, foo)
            else:
                def bar():
                    self._returned_button = self.default_disabled
                    self._destroy()
                self._timer_handle = self.TOP.after(100, bar)

                   
        update_timer(Button_handle)
         

    def reset_timer(self,reset_to="default"):
        """
        If timer has been enabled, this function resets that timer.
        If the argument is a possitive integer, timer will be reset to this
        value.
        If it has a value of 0, messagebox will close down immediately.
        Enter 'default' to reset the timer to original value.
        Enter 'off' to shut down the timer.
        """
        if not hasattr(self,'_time_left') and reset_to != 0:
            return    
               
        if self._assert_reset_timer(reset_to):
            raise self._assert_reset_timer(reset_to)

        if reset_to == 0:
            self._returned_button = self.default_disabled
            self._destroy()
        if reset_to == "default":
            self._time_left = self.timer          
        else:
            self._time_left = reset_to


    def set_close_upon_function(self, timer = DEFAULT.close_upon_function_timer ):
        """
        This method closes the messagebox at the change of a particular
        function. When this function returns True instead of False, the
        messagebox is closed.

        
        Arguments:
        timer:       Determines at which interval that function should
                     be checked. Note that this should be a background
                     process and does not need to cost a lot of
                     calculating power. This is by default 0.1s, but can
                     be overrided by giving the 'close_upon_function'
                     a timer attribute.
        """
        if not hasattr(self,'close_upon_function_timer') or timer != DEFAULT.close_upon_function_timer:            
            self.close_upon_function_timer = timer
            
        if self.close_upon_function == DEFAULT.close_upon_function:
            return # well, if default, this function should be disabled
        
        if self._assert_set_close_upon_function(self.close_upon_function,timer):
            raise self._assert_set_close_upon_function(self.close_upon_function,timer)        
        
        def loop_that_checks_upon_function():
            if hasattr(self.close_upon_function, "timer"):
                if self._assert_close_upon_function_timer_attr(self.close_upon_function.timer):
                    raise self._assert_close_upon_function_timer_attr(self.close_upon_function.timer)                
                self.close_upon_function_timer = max(self.close_upon_function.timer,0.001)

            if not hasattr(self,"TOP") or self not in WINDOWS_OPEN:
                pass # _destroy method has apparently already run 
            elif self.close_upon_function():
                self._destroy()           
            else:
                time_delay = int(self.close_upon_function_timer*1000)
                self._loop_upon_function_handle =  self.TOP.after(int(self.close_upon_function_timer*1000), loop_that_checks_upon_function)


        self._loop_upon_function_handle = self.TOP.after(int(self.close_upon_function_timer*1000), loop_that_checks_upon_function)

                    




        
    def is_root_present(self):
        """
        Returns a boolean on whether there is a tk-window active or not.
        
        This method is based on the fact that tk.IntVar cannot work
        without a root/master present somewhere."""

        if hasattr(self,'_is_root_present_bool'):
            return self._is_root_present_bool
        
        if isinstance(self.master,str):
            if self.master.lower() == 'own':
                output = False
            else:
                raise self._assert_master(self.master)
        elif self.master:
            output = True
        else:
            try:
                Ii = tk.IntVar()
                Ii.set(0)
                Ii.trace("w",lambda*x:x)                
            except:
                output = False                
            else:
                output = True
                
            try:    del Ii
            except: pass
        self._is_root_present_bool = output
        return output
    

    def _center_message(self):
        """
        Centers the message on the screen, or over the master
        (if the master is specified).
        
        This method also makes sure that multiple
        messagecheckbox'es will not be stacked exactly on top
        of each other.
        """
        
        screen_size, window_pos, window_size = self._get_relevant_geometries()

        if self.is_root_present():
            master_pos, master_size  = self._get_window_geo(self._find_master())        
            screen_size, window_pos, window_size = self._get_relevant_geometries()

            pos_rel_to_master =    tuple(int((a-window_size[i])/2) for i,a in enumerate(master_size))
            new_pos = _add_tuples(pos_rel_to_master, master_pos)
        else:            
            new_pos = tuple([int((screen_size[i]-a)/2-35) for i,a in enumerate(window_size)])
        new_pos = _add_tuples(new_pos,reposition_center())
        new_pos = (new_pos[0] if new_pos[0]>0 else 0, new_pos[1] if new_pos[1]>0 else 0)
        def f():
            self.TOP.geometry("+%s+%s"%new_pos)
            self.TOP.minsize(*window_size)
            self.TOP.maxsize(*window_size)            
        f()
        self.TOP.after(100, f)


    def _get_relevant_geometries(self):
        screen_size = (self.TOP.winfo_screenwidth(), self.TOP.winfo_screenheight())              
        window_geo, window_size = self._get_window_geo(self.TOP)
        return screen_size,window_geo,window_size

    def _get_window_geo(self,window):
        window_geo = window.wm_geometry()
        window_size = tuple(map(int, window_geo.split("+")[0].split("x")))
        window_pos = tuple(map(int,window_geo.split("+")[-2:]))
        return window_pos, window_size        




    def _focus_and_lift(self):
        self.TOP.lift()
        self.TOP.focus()


        




    def _check_argument_attributes(self):
        """
        All arguments are supposed to be stashed in a attribute with
        the same name. This method checks if that's true. If not, it'll
        print (not raise) the error.
        """
        for arg in self._all_arguments:
            if not hasattr(self,arg):
                error_message = "This class misses an attribute that"+\
                                "stores the argument '%s'."%arg
                print(error_message)


    def _assert_master(self,master):
        if not master:
            return None
        if isinstance(master,str):
            specified = ['own']
            if master.lower() not in specified:
                error_message = "Argument master was found to be a string, but should be equal to '%s'"%("', '".join(specified))
                return ValueError(error_message)
            # TODO what's the test to check if something is a good master?


    def _assert_strings(self,strings):
        if not isinstance(strings,tuple):
            error_message = "Argument 'strings' should be tuple, but found "+\
                            "type %s"%type(strings)
            return TypeError(error_message)
        if not len(strings):
            error_message = "Argument 'strings' should have at least 1 "+\
                            "element, but found empty tuple."
            return ValueError(error_message)
        for i,s in enumerate(strings):
            if not isinstance(s,str):
                error_message = "Argument strings should be a tuple"+\
                                "containing strings. However, element %s"+\
                                "contained type %s"%(i, type(strings[i]))
                return TypeError(error_message)

        s_previous = []
        for s in strings:
            if s in s_previous:
                error_message = "Argument strings should not contain duplicates; '%s'."%(s)
                return ValueError(error_message)
            s_previous += [s]
            
            


    def _assert_default(self, default):
        if not isinstance(default, str):
            error_message = "Argument 'default' should be string, but found"+\
                            "type %s"%type(default)
            return TypeError(error_message)

    def _assert_default_disabled(self, default_disabled):
        if not isinstance(default_disabled, str):
            error_message = "Argument 'default_disabled' should be string,"+\
                            " but found type %s"%type(default_disabled)
            return TypeError(error_message)

    def _assert_icon(self,icon):

        if isinstance(icon,(str,bytes)):
            if icon in ["default","transparent"]:
                pass            
            elif not os.path.exists(icon):
                error_message = "Argument icon was of type %s, so should be path to icon, but %s was an invalid path."%(type(icon),"'%s'"%icon if isinstance(icon,str) else "")
                return ValueError(error_message)
        else:
            error_message = "Argument icon was of invalid type %s."%(type(icon))
            return ValueError(error_message)

    def _assert_timer(self,timer):
        if isinstance(timer,int):
            return
        if isinstance(timer,str):
            if not timer.lower() == "off":
                error_message = "Argument 'timer' was a string, but instead of value 'off', it was '%s'. 'timer' can also be a positive integer."%timer
                return ValueError(error_message)
        else:
            error_message = "Argument 'timer' was not of type int or string, but rather of type %s"%type(timer)
            return TypeError(error_message)

    def _assert_set_close_upon_function(self,function,timer):
        if self._assert_close_upon_function(function):
            return self._assert_close_upon_function(function)
        
        if self._assert_close_upon_function_timer(timer):
            return self._assert_close_upon_function_timer(timer)
        

    def _assert_close_upon_function(self,function):
        if function == DEFAULT.close_upon_function:
            return
        elif not callable(function):
            error_message = "Argument function should be callable, but instead found type %s."%type(function)
            return TypeError(error_message)
        
    def _assert_close_upon_function_timer(self,timer):
        if not isinstance(timer,(int,float)):
            error_message = "Argument timer for 'close_upon_function' should be either int or float, but found type %s."%type(timer)
            return TypeError(error_message)
        elif not timer > 0 :
            error_message = "Argument timer for 'close_upon_function' should be positive, but found a value of '%s'."%timer            
            return ValueError(error_message)
        
    def _assert_close_upon_function_timer_attr(self,timer):
        if not isinstance(timer,(int,float)):
            error_message = "Attribute 'timer' of the 'close_upon_function' should be either int or float, but found type %s."%type(timer)
            return TypeError(error_message)
        elif not timer > 0 :
            error_message = "Attribute 'timer' of the 'close_upon_function' should be positive, but found a value of '%s'."%timer            
            return ValueError(error_message)
        
        
    def _assert_reset_timer(self,reset_to):
        if isinstance(reset_to,int):            
            if reset_to >= 0:
                return
            elif reset_to < 0:
                error_message = "Argument reset_to cannot be negative, but found value '%s'."%reset_to
                return ValueError(error_message)
        elif isinstance(reset_to,str):
            if reset_to not in ['default','off']:
                error_message = "Argument reset_to must be either positive integer or the string 'default'/'off', but found '%s'."%reset_to
                return ValueError(error_message)            
        else:
            error_message = "Argument reset_to must be either positive integer or the string 'default'/'off', but found type '%s'."%type(reset_to)
            return TypeError(error_message)
            








class MessageCheckBox(MessageBox):
    def __init__(self,  master        = DEFAULT.master,
                        message       = DEFAULT.message,
                        wrap_length   = DEFAULT.wrap_length,
                        title         = DEFAULT.title,
                        checkbutton_var = DEFAULT.checkbutton_var,
                        checkbutton_text = DEFAULT.checkbutton_text,
                        strings       = DEFAULT.strings,
                        default       = DEFAULT.default,
                        default_disabled = DEFAULT.default_disabled,
                        disabled      = DEFAULT.disabled,
                        icon          = DEFAULT.icon,
                        timer         = DEFAULT.timer,
                        close_upon_function = DEFAULT.close_upon_function
                 ):
        """
        This class enables a challenge box to be popped up, with
        customized title, message(/question), buttons and a checkbox.
        Use the method 'show' to reveal the challenge box. This method
        also returns the answer and the state of the checkbutton
        (contained in a tuple). The answer will be based on the text
        of the button. (see argument strings)
        
        Arguments (all optional):
        master:         The master can be specified through this
                        argument. Specify it to be the string 'own' if
                        it should be a stand-alone box, not tied to any
                        master present.
        message:        The message that will be displayed, upon which
                        the user must base his choice.
        title:          The title of the challenge box.
        checkbutton_var:
                        This is the variable linked to the state of the
                        check button. This argument must be either a
                        StringVar, IntVar or BooleanVar from the module
                        tkinter. Note that you can link this variable to
                        a function whenever the value changes, using the
                        method trace.
        checkbutton_text:
                        The text that will be displayed next to the
                        checkbutton.
        strings:        This argument defines the text on the buttons
                        and the number of buttons displayed. This
                        argument is a tuple that contains strings; the
                        number of strings is the number of buttons, and
                        the order of the strings will be the order of
                        the buttons (left to right). The returned answer
                        (first element of returned tuple from method
                        show) will be one of the strings contained
                        within this argument (and of course based on the
                        button that is chosen by the user).
                        Duplicates are not allowed.
        default:        Default answer that is returned if
                        messagecheckbox was closed.
        default_disabled:
                        Default value that is returned, if disabled.
                        Also determines which button is highlighted when
                        the messagecheckbox is popped up. This
                        furthermore means that if pressed "Return",
                        this answer will be selected. Default is the last
                        element from the argument strings.
        disabled:       If this argument is specified to be true, this
                        will disable the pop-up from appearing when the
                        method show is called. The answer will become
                        the argument default_disabled.
        timer:          If above zero, the message will be destroyed in
                        the number of seconds entered. The answer
                        returned will be 'default_disabled'. This button
                        will also contain the timer counting down.
                        Timer will be disabled by a value of 0 or less,
                        or the string 'off'.
        icon:           Determines the icon of the pop-up. The possible
                        values are the following:
                        -"transparent": icon will be set to transparent.
                        -"default": nothing is enforced (i.e. icon will
                                    either have default tkinter icon, or
                                    obtains icon from parent if
                                    configured that way)
                        -filepath to a valid icon-file. See method
                            tk.Toplevel.iconbitmap for more information.
        close_upon_function:
                        This should be a function that returns False as
                        long as the messagebox should be alive. When the
                        function changes to True, the mesagebox should
                        be closed. This function is called at intervals.
                        These intervals are by default 0.1s, but can be
                        changed by giving function an attribute 'timer'
                        (seconds)     

        Attributes: 
        TOP:             Handle of the window. If no master was present,
                         this is the handle of the root. If a master was
                         present, this will be the handle of a
                         Toplevel-window.
        label:           Handle of the label, that shows the message.
        button_*string*: Handle of a button, with text string. Example,
                         if there are two buttons, 'yes' and 'no', then
                         the attributes would be called button_yes and
                         button_no.
        checkbutton:     Handle of the checkbutton.

        *argument*:      Each argument has their own attribute, that is
                         called the same.
        Notes on attributes:
                         -handles are only created when calling
                          the method show. Upon closing the
                          messagecheckbox, these attributes are deleted
                          as well. This means that they are only live
                          during the method 'show'. Note that there is a
                          method hook, that is performed before the
                          mainloop is entered. These attributes will be
                          accessable via that method.                           
                         -when changing arguments, any default values
                          from other attributes (such as the default
                          of default_disabled strings) will not be
                          changed accordingly.                           
        """
        self._all_arguments = locals().copy()
        # TODO: make a list argument_to_be_deleted, and then use a for-loop
        del self._all_arguments["self"]
        del self._all_arguments["checkbutton_var"]
        del self._all_arguments["checkbutton_text"]
        del self._all_arguments["__class__"]
        super().__init__(**self._all_arguments)

        self._all_arguments = locals().copy()
        del self._all_arguments["self"]
        
        self.checkbutton_var = checkbutton_var       
        if self._assert_checkbutton_var(checkbutton_var):
            raise self._assert_checkbutton_var(checkbutton_var)
        self.checkbutton_text = checkbutton_text
        
        self._check_argument_attributes()
        
        





    def _cleanup(self):
        """Deletes the attributes of the handles, that are no longer used."""
        super()._cleanup()
        delattr(self,"checkbutton")
        
        


    def _return_show(self):
        return self._returned_button, self.checkbutton_var.get()

    def _disabled(self):
        """The method show will call upon this method, if disabled is True."""
        self._returned_button = self.default_disabled
        return self._return_show()

    def _create_checkbutton(self, text = "",
                            checkbutton_var = DEFAULT.checkbutton_var):
        
        if checkbutton_var == DEFAULT.checkbutton_var:
            checkbutton_var  = tk.BooleanVar()
            checkbutton_var.set(False)  
        self.checkbutton_var = checkbutton_var
        
        self.checkbutton = ttk.Checkbutton(self.TOP,
                                           variable = checkbutton_var,
                                           text = text)
        self.checkbutton.grid(row=2, column=0, pady=(0,7), padx=10,
                              columnspan=len(self.strings),sticky="w")
        
        




    def state_checkbutton(self):
        """
        Returns a Boolean to describe the state of the check button
        (i.e. checked or not).
        """
        return True if self.checkbutton.state() else False



        

     

    def _assert_checkbutton_var(self, checkbutton_var):
        ALLOWED_TYPES =(tk.IntVar,tk.StringVar,tk.BooleanVar)
        if checkbutton_var == DEFAULT.checkbutton_var:
            return
        if not isinstance(checkbutton_var,ALLOWED_TYPES):
            error_message = "argument 'checkbutton_var' should be of type(s)"+\
                            "%s but found type %s"\
                            %(ALLOWED_TYPES, type(checkbutton_var))
            return TypeError(error_message)



def ShowMessageBox( master      = DEFAULT.master,
                    message     = DEFAULT.message,
                    wrap_length = DEFAULT.wrap_length,
                    disabled    = DEFAULT.disabled,
                    title       = DEFAULT.title,
                    strings     = DEFAULT.strings,
                    default     = DEFAULT.default,
                    default_disabled = DEFAULT.default_disabled,
                    icon        = DEFAULT.icon,
                    timer       = DEFAULT.timer):
    """
    This function pops up a challenge box with customized title,
    message(/question) and buttons. The function returns the answer.
    The answer is based on the text of the button that is chosen
    (see argument strings)
    
    Arguments (all optional):
    master:         The master can be specified through this
                    argument. Specify it to be the string 'own' if
                    it should be a stand-alone box, not tied to any
                    master present.
    message:        The message that will be displayed, upon which
                    the user must base his choice.
    title:          The title of the challenge box.    
    strings:        This argument defines the text on the buttons
                    and the number of buttons displayed. This
                    argument is a tuple that contains strings; the
                    number of strings is the number of buttons, and
                    the order of the strings will be the order of
                    the buttons (left to right). The returned answer
                    (first element of returned tuple) will be one of
                    the strings contained within this argument
                    (and of course based on the button that is
                    chosen by the user).
    default:        Default answer that is returned if
                    messagebox was exited (by red X topright corner).
    default_disabled:
                    Default value that is returned, if disabled.
                    Also determines which button is highlighted when
                    the messagebox is popped up. This
                    furthermore means that if pressed "Return",
                    this answer will be selected. Default is the last
                    element from the argument strings.
    disabled:       If this argument is specified to be true, this
                    will disable the pop-up from appearing. The
                    answer will become the argument default_disabled.
    timer:          If above zero, the message will be destroyed in
                    the number of seconds entered. The answer
                    returned will be 'default_disabled'. This button
                    will also contain the timer counting down.
                    Timer will be disabled by a value of 0 or less,
                    or the string 'off'.
    icon:           Determines the icon of the pop-up. The possible
                    values are the following:
                    -"transparent": icon will be set to transparent.
                    -"default": nothing is enforced (i.e. icon will
                                either have default tkinter icon, or
                                obtains icon from parent if
                                configured that way)
                    -filepath to a valid icon-file. See method
                        tk.Toplevel.iconbitmap for more information.
    """
    args = locals().copy()
    _messagebox = MessageBox(   **args)
    output = _messagebox.show()
    del _messagebox    
    
    return output












def ShowMessageCheckBox(master = DEFAULT.master,
                        message = DEFAULT.message,
                        wrap_length = DEFAULT.wrap_length,
                        disabled = DEFAULT.disabled,
                        title = DEFAULT.title,
                        checkbutton_var = DEFAULT.checkbutton_var,
                        checkbutton_text = DEFAULT.checkbutton_text,
                        strings = DEFAULT.strings,
                        default = DEFAULT.default,                        
                        default_disabled = DEFAULT.default_disabled,
                        icon = DEFAULT.icon,
                        timer         = DEFAULT.timer):
    """
    This function pops up a challenge box with customized title,
    message(/question) and buttons. The function returns a tuple
    with the answer and the state of the checkbutton (boolean).
    The answer is based on the text of the button that is chosen
    (see argument strings)
    
    Arguments (all optional):
    master:         The master can be specified through this
                    argument. Specify it to be the string 'own' if
                    it should be a stand-alone box, not tied to any
                    master present.
    message:        The message that will be displayed, upon which
                    the user must base his choice.
    title:          The title of the challenge box.
    checkbutton_var:
                    This is the variable linked to the state of the
                    check button. This argument must be either a
                    StringVar, IntVar or BooleanVar from the module
                    tkinter. Note that you can link this variable to
                    a function whenever the value changes, using the
                    method trace.
    checkbutton_text:
                    The text that will be displayed next to the
                    checkbutton.
    strings:        This argument defines the text on the buttons
                    and the number of buttons displayed. This
                    argument is a tuple that contains strings; the
                    number of strings is the number of buttons, and
                    the order of the strings will be the order of
                    the buttons (left to right). The returned answer
                    (first element of returned tuple) will be one of
                    the strings contained within this argument
                    (and of course based on the button that is
                    chosen by the user).
    default:        Default answer that is returned if
                    messagecheckbox was closed.
    default_disabled:
                    Default value that is returned, if disabled.
                    Also determines which button is highlighted when
                    the messagecheckbox is popped up. This
                    furthermore means that if pressed "Return",
                    this answer will be selected. Default is the last
                    element from the argument strings.
    disabled:       If this argument is specified to be true, this
                    will disable the pop-up from appearing. The
                    answer will become the argument default_disabled.
    timer:          If above zero, the message will be destroyed in
                    the number of seconds entered. The answer
                    returned will be 'default_disabled'. This button
                    will also contain the timer counting down.
                    Timer will be disabled by a value of 0 orless,
                    or the string 'off'.
    icon:           Determines the icon of the pop-up. The possible
                    values are the following:
                    -"transparent": icon will be set to transparent.
                    -"default": nothing is enforced (i.e. icon will
                                either have default tkinter icon, or
                                obtains icon from parent if
                                configured that way)
                    -filepath to a valid icon-file. See method
                        tk.Toplevel.iconbitmap for more information.
    """
    args = locals().copy()
    _messagecheckbox = MessageCheckBox(   **args)
    output = _messagecheckbox.show()
    del _messagecheckbox
    
    
    return output
    


def quityesnocheck(master = DEFAULT.master,                   
                   disabled = False,
                   title = "Quit Program",
                   checkbutton_text = "Do not show this again",
                   function = "master.destroy",
                   checkbutton_var = DEFAULT.checkbutton_var,                   
                   ):
    """
    Pops up a challenge box, whether the user really wishes to exit the
    program or not. The challenge box also has a checkbox, in which
    users can specify they no longer wish to see the challenge box.
    (Although this last part has to be constructed manually, see below)

    Returns a tuple with the answer and whether the checkbutton was
    checked or not (boolean). Example:  ("yes", True)
    
    Arguments: 
    -master:       Parent-window for this function.
                   Specify it to be the string 'own' if
                   it should be a stand-alone box, not tied to any
                   master present.
    -disabled:     If set to True, the pop-up message will not appear
                   but the answer "yes" is automatically generated
                   and the argument 'function' will be executed.    
    -title:        Title of the messagecheckbox. 
    -function:     function that will executed if clicked 'yes'.
    -checkbutton_var:
                   IntVar/StringVar/BooleanVar that will be coupled to
                   the checkbox.  

    The structure with the "do not show this again"-checkbutton has to
    be constructed manually. Suggestion: save a Boolean to a file as a
    preference (with default False) and feed it to the argument
    disabled. When the second argument of the returned tuple (i.e.,
    the state of the check button) returns True, change the saved
    preference accordingly. This way, it will be fed back to the
    argument disabled, and the challenge box will not be shown again.
    """
    if not isinstance(master,(type(None),tk.Tk,tk.Toplevel)):
        error_message = "Argument master received unknown value of type %s."\
                                            %(type(master))
        raise TypeError(error_message)
    if function == "master.destroy":
        if not master:
            error_message = "No master has been specified, so the default of "+\
                            "function 'master.destroy' cannot be created. "+\
                            "Specify either argument master or function."
                            
            raise ValueError(error_message)
        function = master.destroy
    else:
        if not callable(function):
            error_message = "Argument function was not callable, but of type '%s'."%type(function)
            raise TypeError(error_message)        
    
    message = " Do you wish to close the program?" 
    strings = ("yes","no") 
    
    A = MessageCheckBox(master = master,
                        message = message,
                        title = title,
                        checkbutton_var = checkbutton_var,
                        checkbutton_text = checkbutton_text,
                        strings = strings,
                        disabled = disabled,
                        default_disabled = "yes")
    
    answer = A.show()    
    if answer[0] == strings[0]:
        function()
    return answer
        

if __name__ == "__main__":
    #TODO: write this into a test-case......

    A = ShowMessageCheckBox(message = "The timer will quit this messsage by itself.",
                            strings=("OK","Cancel"),timer=5)
    
    B = quityesnocheck(function=lambda*x:print("exited")) 
    
    C = MessageBox(title="title",message = "shuts down timer before it can end",timer=4)
    def foo():
        time.sleep(2)
        C.reset_timer('off')
    threading.Thread(target=foo).start()
    C.show()

    bar_val = 0
    def bar():
        global bar_val
        bar.timer = 2
        bar_val += 1
        if bar_val > 3:
            return True

    D = MessageBox(title="t",message="this will close itself if close_upon_function works",close_upon_function=bar)
    D.show()

    

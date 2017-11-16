"""
This module offers easy functions to edit the searchspace in which
modules can be found.
Any modules causing a potential conflict with other (installed) modules
are collected in variable 'CONFLICT_MODULES'.
"""
CONFLICT_MODULES = []
ALL_ADDED_FOLDERS = []

import os, sys, inspect
import functools

version = [sys.version_info[i] for i in range(3)]



def capture_printed_text(func,*args,**kwargs):
    """
    Captures text from printed statements within func.
    TODO: untested for python 2.x
    Not thread-safe, as it temporarily binds stdout to a new output.
    Therefor, any print statement running concurrently in another thread
    are directed to this function instead of the screen.
    
    These functions are straight from stackoverflow
    (with some dressing up around them)
    # https://stackoverflow.com/questions/16571150/how-to-capture-stdout-output-from-a-python-function-call
    """
    def capture_printed_text_v3_4(func,*args,**kwargs):
        import io
        from contextlib import redirect_stdout
        f = io.StringIO()
        with redirect_stdout(f):
            func(*args,**kwargs)
        return f.getvalue()
    
    def capture_printed_text_other_versions(func,*args,**kwargs):
        """
        TODO: NEVER TESTED for v2.x (only have python 3.6)
        """
        try:                from cStringIO import StringIO
        except ImportError: from io        import StringIO
        import sys

        class Capturing(list):
            def __enter__(self):
                self._stdout = sys.stdout
                sys.stdout = self._stringio = StringIO()
                return self
            def __exit__(self, *args):
                self.extend(self._stringio.getvalue().splitlines())
                del self._stringio    # free up some memory
                sys.stdout = self._stdout
                
        with Capturing() as output:
            func(*args,**kwargs)
        return "\n".join(output)
  
        
    if version >= [3,4]:
        return capture_printed_text_v3_4(func,*args,**kwargs)
    else:
        return capture_printed_text_other_versions(func,*args,**kwargs)




def get_all_installed_modules():
    """
    Gets all installed modules, and returns them in a list.
    # TODO: Change this function that it not uses stdout anymore,
            because it can cause stupid unexpected errors
    """
    out = capture_printed_text(help,'modules')
    out = out[71:-137]
    out = sorted([o for o in out.replace("\n"," ").split(" ") if o])
    return out


    
target_folders = []


_current_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]))
_filename = os.path.join(_current_folder,"import_custom_module_dir_paths.txt")

try:
    with open(_filename,'r') as input_file:
        for line in input_file:
            target_folders.append(line.replace("\n",""))
except FileNotFoundError:
    # well, could be that you didn't
    # bother to write the file....
    pass 


def add_folder_to_sys_path(folders, print_warnings=False, override = False):
    """
    Adds a folder to sys.path. This enables modules to be imported
    from that specific folder. These 'new modules' can be imported
    from the entire workspace, not just the module that calls this
    function.
    TODO: Works for in python 3.x, but is untested for python 2.x+

    Arguments:
    folders:          Folder(s) that are to be added to sys.path.
                      This must be the path to a folder, which contains
                      the modules you want to be able to import.
                      This can also be a list of multiple paths.
    print_warnings:   Modules that can be imported from folders,
                      might conflict with existing modules.
                      Specifying this argument 
                      If this argument is specified to be non-default,
                      these warnings will be returned as a string.
                      If argument is specified True, these warnings will
                      also be printed out to the screen.
                      Note2: setting this argument not thread-safe
                             regarding print-statements.
                             See function 'capture_printed_text'
    override:         Whether the 'imported modules' will override any
                      existing modules or not. 
    """
    global ALL_ADDED_FOLDERS
    if isinstance(folders, (str,bytes)):
        folders = [folders]
        
    if not isinstance(override,int):
        error_message = "Argument 'override' should be bool or integer, but found type '%s'."%type(override)
        raise TypeError(error_message)
        
    if print_warnings:    
        _original_modules_list = get_all_installed_modules()
        double_modules = []


        
    # is executed when module is called,
    # i.e. adds the module_paths to sys_path
    for target_folder in folders:
        if not os.path.isdir(target_folder):
            error_message = "Specified path is not a directory. Specified path was '%s'."%target_folder
            raise FileNotFoundError(error_message)
                
        if target_folder.lower() not in [syspath.lower() for syspath in sys.path]:
            if override:                 
                sys.path.insert(1, target_folder)                
            else:
                sys.path.append(target_folder)



            ALL_ADDED_FOLDERS.append(target_folder)
            
            if print_warnings: 
                
                imported_modules = [os.path.join(target_folder,a) for a in  os.listdir(target_folder) if not a.startswith("__pycache__")] 
                # weed out any folders/files that cannot possibly be a module
                for imp_mod in imported_modules.copy():
                    if os.path.isdir(imp_mod):
                        # weed out any directories that cannot pose as modules
                        if not "__init__.py" in os.listdir(imp_mod):
                            imported_modules.remove(imp_mod)
                    elif os.path.isfile(imp_mod):
                        # weerd any files that are not pythonic
                        if not '.py' in os.path.split(imp_mod)[1][-4:]:
                            imported_modules.remove(imp_mod)                    
                        if os.path.split(imp_mod)[1] == "__init__.py":
                            imported_modules.remove(imp_mod)


                # check if any imported modules double an existing module
                for module_path in imported_modules:
                    module_name = os.path.basename(module_path)
                    if module_name in _original_modules_list:
                        double_modules.append(module_path)
                    elif module_name.endswith(".py") and\
                         module_name[0:-3] in _original_modules_list:
                        double_modules.append(module_path)


                # if more paths are added, new modules might conflict
                # with modules from previous paths. This catches those.
                module_names = [os.path.split(a)[1] for a in imported_modules]
                _original_modules_list += [a[:-3] if a.endswith('.py') else a for a in module_names]

    error_message = ""
    if print_warnings and double_modules:
        # TODO: include a trace-stack
        error_message = ("WARNING from module '%s': \n"%__name__+
                         "The following modules could cause conflicts with "+
                         "existing modules if imported, because modules with the same name already exist. "+
                         "The modules that probably cause conflicts are:\n"+
                         "\n".join(double_modules),)[0]
        
        global CONFLICT_MODULES
        CONFLICT_MODULES += double_modules
        if isinstance(print_warnings,bool):
            print(error_message) # TODO: how to give a proper warning
    if print_warnings != False:
        return error_message

def _assert_parent(parent):
    if not isinstance(parent,int):
        error_message = "argument 'parent' must be integer, but found type '%s'."%type(parent)
        return TypeError(error_message)
    if not parent >= 0:
        error_message = "argument 'parent' must zero or positive, but found value '%s'."%(parent)
        return ValueError(error_message)
    

def get_parent_folder_stack(parent=1, stack=1):
    """
    Returns the location of the parent folder from where a 'certain
    function' was called. This 'certain function' is determined by argument
    'stack' and looks back in the stack 
    
    Arguments:
    parent:     Determines whether you are looking for the location of
                itself (0), its parent's folder (1), it's grandparent's
                folder (2) and so fort.
    stack:      Checks how far you like to go on the stack of functions.
                Default is the location from which you are calling
    """
    if _assert_parent(parent):
        raise _assert_parent(parent)

    originating_folder = os.path.split( inspect.stack()[stack][1] )[0]
    for i in range(parent):
        originating_folder = os.path.split(originating_folder)[0]
    return originating_folder


def get_parent_folder(parent=1):
    """
    Returns the location of the parent folder from where this function
    was called.
    
    Arguments:
    parent:     Determines whether you are looking for the location of
                itself (0), its parent's folder (1), it's grandparent's
                folder (2) and so fort.
    """
    # TODO: does this function mirror another stdlib-function...?
    if _assert_parent(parent):
        raise _assert_parent(parent)

    return get_parent_folder_stack(parent,stack=2)

def add_parent_folder_to_sys_path(parent, print_warnings=True, override = False):
    """
    Adds the parent folder to sys.path. This enables modules to be
    imported from that specific folder. These 'new modules' can be
    imported from the entire workspace, not just the module that calls
    this function.
    TODO: Works for in python 3.x, but is untested for python 2.x

    Arguments:
    parent:           Determines whether you are looking for the
                      location of itself (0), its parent's folder (1),
                      it's grandparent's folder (2) and so fort.
    print_warnings:   Modules that can be imported from folders,
                      might conflict with existing modules.
                      Specifying this argument 
                      If this argument is specified to be non-default,
                      these warnings will be returned as a string.
                      If argument is specified True, these warnings will
                      also be printed out to the screen.
                      Note: must be version 2.x or 3.4+.
                      Note2: setting this argument not thread-safe
                             regarding print-statements.
                             See function 'capture_printed_text'
    override:         Whether the 'imported modules' will override any
                      existing modules or not. 
    """
    if _assert_parent(parent):
        raise _assert_parent(parent)

    parent_folder = get_parent_folder_stack(parent, stack=2)
 
    add_folder_to_sys_path(parent_folder, print_warnings=print_warnings, override=override)


if __name__ == "__main__":    
    add_folder_to_sys_path(target_folders,
                           print_warnings = ( __name__=="__main__"
                                             and (version>=[3,4] or version<[3])
                                             )
                           )

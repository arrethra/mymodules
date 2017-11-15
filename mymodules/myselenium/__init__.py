# written by Arrethra https://github.com/arrethra/

try:
    import mymodules.preferences as preferences # < https://github.com/arrethra/preferences >
except:
    # this script is supposed to work without preferences, although that one isn't fully tested...
    imported_prefs = False 
else:
    imported_prefs = True
    default_values = {"path_to_profile":"[enter default path_to_profile]",  ## https://stackoverflow.com/questions/37358546/python-selenium-how-to-load-the-browsers-datacookies-or-bookmarks
                      "path_to_adblocker":"[enter_path_to_adblocker]",
                      "path_to_chromedriver":"?"}
    P = preferences.Preferences(defaults = default_values,
                                filename="my_selenium - personal paths.txt")


PATH_TO_ADBLOCKER = "specify path to adblocker here, if you cannot import preferences"
    

import threading
import os, sys, inspect
import os.path as osp
from tkinter import messagebox
import time
import tkinter as tk
from tkinter import filedialog
from copy import copy

class MakeInvisibleMaster(tk.Tk):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.wm_overrideredirect(1)
        self.attributes("-alpha",0)

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.keys import Keys
except ModuleNotFoundError:
    A = MakeInvisibleMaster()
    messagebox.showinfo("selenium not found",
                    "For this module to run correctly, selenium must be able to be imported.\n"+\
                    "See one of the following websites for information on how to install selenium:\n"+\
                    "http://stackoverflow.com/questions/17540971/how-to-use-selenium-with-python\n"+\
                    "http://www.marinamele.com/selenium-tutorial-web-scraping-with-selenium-and-python\n"+\
                    "(no guarantees implied that it'll work, or that they're thrustworty sites.\n"+\
                    "use at own risk.)")
    A.destroy()
    quit()


download_chromedriver_link = "https://sites.google.com/a/chromium.org/chromedriver/downloads"
download_adblockers_link   = "http://chrome-extension-downloader.com/"


# TODO: change to more suitable style
current_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]))


# setting default download-directory

default_download_directory = "[enter default download directory]" # otherwise it'll get stored in the preferences-file, but it'll needs to be initiated the first time
def ask_for_default_download_directory():
    global default_download_directory
    if imported_prefs:
        P.set_default_values(default_download_directory = default_download_directory)
        default_download_directory = P.default_download_directory
    if not os.path.exists(default_download_directory):
        default_download_directory = False    
        if imported_prefs:
            A = MakeInvisibleMaster()
            if "yes" == messagebox.askquestion(   "Set default Download directory",
                                                  "Please set your default download directory. \n"+\
                                                  "This path will be saved for future times.\n\n"+\
                                                  "Hint: I'll keep asking the next time you start up,\n"+\
                                                  "if you don't set the default directory...."):
                folder_answer = filedialog.askdirectory(initialdir=current_folder)

                if osp.exists(folder_answer):
                    default_download_directory = folder_answer
                    P.default_download_directory = default_download_directory
            A.destroy()
ask_for_default_download_directory()





def askstrings(title, message,strings):
    import tkinter.dialog as tkd
    d = tkd.Dialog(None, {'title': title,
                          'text': message
                          ,
                          'bitmap': "question",
                          'default': 0,
                          'strings': strings})
    return strings[d.num]

def askyesnodownload(title,message):
    return askstrings(title,message,("Yes","Yes, download","No"))




#starts  chrome, but with preferences that I like.
def start_Chrome(use_saved_profile = False, adblocker = False):
    """
    Starts Chrome with certain preferences that I like, and also
    with the option to use a saved profile (option not tested, iirc)
    or to use adblockers.
    """
    options = webdriver.ChromeOptions()


    if use_saved_profile:
        path_to_profile = "[Enter default path to profile here]"    
        if imported_prefs:
            path_to_profile = P.path_to_profile
        if not os.path.isabs(path_to_profile):
            A = MakeInvisibleMaster()
            if "yes" == messagebox.askquestion("Locate profile",
                                               "Do you wish to locate your profile,"+\
                                               "\nor do you wish to continue without"+\
                                               "\nyour default profile?" +\
                                               "" if not imported_prefs else \
                                               "\n(You only have to locate this once,"+\
                                               "\nthereafter the location will get stored.)"):
                path_to_profile = filedialog.askdirectory(initialdir=current_folder)
                if imported_prefs and os.path.isabs(P.path_to_profile):
                    P.path_to_profile = path_to_profile
            else:
                use_saved_profile = False
            A.destroy()
        

        
    if use_saved_profile:
        options.add_argument("user-data-dir=" + path_to_profile) ## TODO: does it work????
    else:
        prefs_dict = {  "net.network_prediction_options":False, #didn't work, iirc
                        "safebrowsing.enabled":True,
                        "enable_do_not_track":True, #sends a Do_Not_Track-thingy
                        "download.prompt_for_download":True,
                        "download.directory_upgrade": True                                     
                        }
        if default_download_directory:
            temp = { "download.default_directory" : default_download_directory}
            prefs_dict.update(temp)
            del temp
        options.add_experimental_option("prefs",prefs_dict)     
    if adblocker:
        path_to_adblocker = PATH_TO_ADBLOCKER # if preferences can be imported, that will take over the ride
        
        options = add_adblocker_to_profile(options,path_to_adblocker)

    options.add_argument("start-maximized") #makes sure the screen starts maximalized


    def locate_webdriver(options):
        if imported_prefs and osp.exists(P.path_to_chromedriver):
            path_to_webdriver = P.path_to_chromedriver
        else:  
            msgbx(imported_prefs)
            A = MakeInvisibleMaster()
            opening_file = filedialog.askopenfile()
            if opening_file == None:
                return locate_webdriver(options)
            path_to_webdriver = opening_file.name 
            A.destroy()
            if not osp.exists(path_to_webdriver):
                return locate_webdriver(options)
            if imported_prefs:
                P.path_to_chromedriver = path_to_webdriver
        try:
            driver = webdriver.Chrome(executable_path = path_to_webdriver,
                                      chrome_options=options)
        except OSError:
            print("Some error went down with Chrome-driver, probably not found. "+\
                  "The path to chromedriver was '%s'."%path_to_webdriver)
            raise

        return driver


    def msgbx(imported_prefs):
        import sys
        python_folder = sys.exec_prefix
        python_scripts_folder = os.path.join(python_folder,"Scripts")
        
        A = MakeInvisibleMaster()
        a = tk.messagebox.askokcancel("Missing: Chromedriver",
                    "To start up google Chrome with python selenium, \n"+\
                    "you need to locate the chromedriver.exe . \n\n"+\
                    "Do you wish to proceed and locate this Chromedriver? \n\n"+\
                    (("Fortunately, you'll only needs to do this once, as I'll\n"+\
                    "be able to save that location.\n") if imported_prefs else \
                    ("Unfortunately, I can't save the location for future times,\n"+\
                    "so you'll need to locate that file again and again.\n"))+\
                    "\nIt is recommended to move Chromedriver into the python folder:"+\
                    "\n"+ python_scripts_folder + \
                    "\n\nFor further information on Chromedriver, you might like to take a look at \n"+\
                    download_chromedriver_link + " \n"+\
                    "(no garuantess about thrustworthiness and so forth)\n"+\
                    "or use FireFox or IE .")
        if not a:
            A.destroy()
            quit()
        else:
            A.destroy()

    chromedriver_is_easily_found = True
    try:
        driver = webdriver.Chrome(chrome_options=options)            
    except Exception as e:
        e = str(e)
        if not "Message: 'chromedriver' executable needs to be in PATH.".lower() in e.lower():
            raise
        chromedriver_is_easily_found = False
        
    if not chromedriver_is_easily_found:
        driver = locate_webdriver(options)
    
        
        
    
    # if an adblocker is installed, this loads up an extra "first run" page, which I'd like to close
    time.sleep(0.5)
    if len(driver.window_handles) > 1:
        driver.switch_to_window( driver.window_handles[-1])
        driver.close()
        driver.switch_to_window( driver.window_handles[0])

    
    return driver




def add_adblocker_to_profile(profile_options, path_to_adblocker="no path"):    

    add_blocker_ask_question = ("Specify location of adblockers",
                                 ("Please specify the directory where the files "+
                                  "for the adblockers are stored.\n"+
                                  "This path will be saved for future times.\n\n"+
                                  "By clicking on \"Yes, dowload\" you can choose to download the extensions from the site*\n"+
                                  "'%s'\n"%download_adblockers_link+
                                  "Make sure that these are '.crx'-extensions\n\n"+
                                  "Hint: because adblocker is set to be included at every start, "+
                                  "I'll keep asking for their location, the next time you start up, "+
                                  "if you don't set the default directory....\n\n"+
                                  "*No guarantees that those site(s) and/or extensions are safe, ofcourse"
                                 ) 
                                )

    if imported_prefs:
        path_to_adblocker = P.path_to_adblocker
    if not osp.exists(path_to_adblocker):
        
        A = MakeInvisibleMaster()
        A_answer = askyesnodownload(*add_blocker_ask_question)
        A.destroy()
        if A_answer == "Yes, download":
            threading.Thread(target = lambda*x:(time.sleep(1),update_adblockers()) ).start()                
        if A_answer == "Yes" or A_answer == "Yes, download" :
            A = MakeInvisibleMaster()
            path_to_adblocker = filedialog.askdirectory(initialdir=current_folder)
            A.destroy()
            if path_to_adblocker != "" and imported_prefs:
                P.path_to_adblocker = path_to_adblocker
        elif A_answer.lower() == "no":
            return profile_options        

    if not osp.exists(path_to_adblocker):
        return add_adblocker_to_profile(profile_options, path_to_adblocker="no path")
            
                
    filenames = [a.lower() for a in os.listdir(path_to_adblocker)  if osp.isfile(osp.join(path_to_adblocker, a)) and a.endswith(".crx")]
    for specific_name in ["adblock-plus","adblock"]:  
        adblockers = sorted([a for a in filenames if a.startswith(specific_name)]) # hopefully sorts to version
        if adblockers:
            profile_options.add_extension( osp.join(path_to_adblocker,adblockers[-1]) )
            break
    else:
            A = MakeInvisibleMaster()
            a = messagebox.askquestion("No Adblockers found",
                                        ("No adblockers found in specified folder. \n"+
                                         "Do you wish to try again to try again (YES) "+
                                         "or proceed without adblockers (NO).")
                                       )
            A.destroy()
            
            if a in ["yes","ok","OK"]:
                P.reset_to_default("path_to_adblocker")
                profile_options = add_adblocker_to_profile(profile_options, path_to_adblocker="no path")
            

            
                      
    return profile_options
        
            


def open_new_tab(driver):
    """
    Opens a new tab in the browser and returns handle of new tab.
    However, you have to switch to the tab manually, for example with
    driver.switch_to_window(driver.window_handles[-1])
    NOTE: This works on the window that is VISUALLY active, not on the
          window that is actually active according to selenium (i.e. the
          window that is active set by method switch_to_window)
    """
    #check_if_new_window_opened=len(driver.window_handles)

    old_driver_handles = copy(driver.window_handles)
    len_old_driver_handles = len(old_driver_handles)
    
    driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + 't')#opens a new tab
    if len_old_driver_handles==len(driver.window_handles):   #control+T does not always work with the chromeDriver, so this check has to be implemented (and the command below sup'dly only works with chrome...
        driver.execute_script("window.open('');")
    
    current_window_handles = driver.window_handles
    
    for i,a in enumerate(current_window_handles):
        if i >= len_old_driver_handles or a != old_driver_handles[i]:
            return a

def open_new_tab_and_switch(driver):
    """
    Opens a new tab in the browser, switches to it and returns
    handle of new tab.
    NOTE: This works on the window that is VISUALLY active, not on the
          window that is actually active according to selenium (i.e. the
          window that is active set by method switch_to_window)
    """
    output = open_new_tab(driver)
    driver.switch_to_window(output)
    return output

          

    
    
        

def natural_typing(driver_element, string,time_delay=0.2):
    """
    types in the text, but with small delays, to mimic actual typing.
    THIS FUNCTION HASN'T BEEN TESTED YET.
    Suggestion; at random mistype a letter; then correct them.
    args:
    time_delay: average time delay between keys.
    """
    from selenium import webdriver
    import time
    import random
    for letter in string:
        driver_element.send_keys(letter)
        time.sleep(time_delay/2+time_delay*random.random())
        

def close_window(driver):
    """Closes current window, and activates the window to its right."""
    from selenium import webdriver
    current_window_index = driver.window_handles.index(driver.current_window_handle)
    driver.close()
    try:
        new_window_index = min(current_window_index,len(driver.window_handles)-1)
        driver.switch_to_window(driver.window_handles[new_window_index])
    except: pass #(dunno which exception to except, so I'll except them all... :(   )


def is_Chrome_open(driver):
    """
    Returns Boolean whether Crhome is open or not.
    Can also return a string with an error message, if status is
    undetermined (see message for more information).
    Note: If that message is 'CannotSendRequest', Chrome is probably
          live, but handling another request.
    """
    from http.client import CannotSendRequest # This is (assumably) the error, that happens if I request windows_handles while busy
    from selenium import webdriver    

    try:        
        browsername = driver.capabilities["browserName"].lower()
    except AttributeError:
        return False

    try:
        if not driver.window_handles:
            return False
    except CannotSendRequest:
        # The webdriver is probably handling another request, so
        # my guess is that it is live
        return "CannotSendRequest"
    except Exception as e:
        E = str(e)
        Elower = E.lower()

        if "CannotSendRequest".lower() in Elower:
            # The webdriver is probably handling another request, so
            # my guess is that it is live
            return "CannotSendRequest"
        
        possible_errors = ["chrome not reachable",
                           "no such session",
                           "An existing connection was forcibly closed by the remote host",
                           "No connection could be made because the target machine actively refused it",
                           "no such window",
                           "target window already closed"]

        # checks for possible errors that surely indicate that webdriver is closed
        for p_e in possible_errors:
            if p_e.lower() in Elower:
                return False
        
        # When returning E, this means that the status is undetermined
        # See message E for more information.
        return E
    else:
        output = True if browsername == "chrome" else "Found not Chrome, but instance of %s."%browsername
        return output


def open_site(URL, driver=None,**kwargs):
    """
    Opens given URL. If no driver is specified, it will start up Chrome.
    Else, it'll open the site in a new tab of the specified driver.
    """
    if not is_Chrome_open(driver):
        driver = start_Chrome(**kwargs)        
    else:
        driver.switch_to_window(open_new_tab(driver))
    driver.get(URL)
    return driver

def update_chromedriver(driver = None,**kwargs):
    driver = open_site(download_chromedriver_link,driver,**kwargs)
    return driver

def update_adblockers(driver = None,**kwargs):
    driver = open_site(download_adblockers_link,driver,**kwargs)
    SEARCH_BOX = driver.find_element_by_xpath("/html/body/div[2]/div/div/div[2]/div[2]/form/div[1]/input")
    adblock_plus_site = "https://chrome.google.com/webstore/detail/adblock-plus/cfhdojbkjhnklbpkdaibdccddilifddb"
    SEARCH_BOX.send_keys(adblock_plus_site)
##    open_new_tab_and_switch(driver)
##    driver.get("https://chrome.google.com/webstore/search/adblock")
    
    return driver


import threading
   
    

_CloseDriverAfterBrowserHasClosed_counter = 0

class CloseDriverAfterBrowserHasClosed:
    """
    Starts a loop in which is checked if the browser has closed. 
    If the browser is closed, it will exit that driver entirely, by 
    calling on the method exit_browser.
    (Usually, when the browser is closed manually, a background process
     of selenium will keep running. This class makes sure to exit that 
     background process at the appropiate time)

    Works only on Chrome, for the time being.

    Arguments:
    driver:   The driver that drives the browser. For now, it only
              supports Chrome. (Although you could supply your own
              method is_browser_open )
    lock:     Selenenium is not thread safe. Therefor, the option is 
              given to specify a lock/semaphore. Not needed if thread is 
              specified False.
    thread:   Option to start the loop in a thread. Default is False.
              Note that selenium is not thread-safe and thus care has to
              be taken with this option. If you are planning to use
              selenium after this class has been called, either locks
              have to be used, or some other precautions (such as
              inheriting this class, and then disable the method
              is_browser_open during your usage of selenium.
    freq:     The frequency in Hertz at which the loop will check on the
              status of the browser. Default is 1 Hz.
    start_loop:
              If True (default), the loop is started instantly.
              If False, the loop needs to be initiated via the method
              'start'.
    All arguments (except start_loop) are accessible at attributes
    of the same name.
    """
    def __init__(self, driver,
                       lock = None,
                       thread = False,
                       freq = 1,
                       start_loop = True):

        self.driver = driver
        self.lock = lock
        self.thread = thread
        self.freq = freq

        self._interrupt_called = False
        self._pause_bool = False
        self._sleeping_beauty = threading.Event()
        

        if start_loop:
            self.start()
	

    
    def start(self, thread="self.thread"):
        """
        Starts the loop that checks on the status of the driver.
        Is automatically called when the class is started, unless
        specified otherwise. This loop can be started in a thread.
        Calls upon the method exit_browser if the browser is closed.
        """
        if self._pause_bool:
            return self.resume()

        if thread == "self.thread":
            thread = self.thread
            
        if thread:
            ## TODO: replace counter with counter_function if possible
            global _CloseDriverAfterBrowserHasClosed_counter
            thread_name = "CloseDriverAfterBrowserHasClosed [%s]"%_CloseDriverAfterBrowserHasClosed_counter
            _CloseDriverAfterBrowserHasClosed_counter += 1

            T =  threading.Thread(target = self._start, name = thread_name)
	    
            T.start()
        else:
            self._start()
        

    def _start(self):
        """
        The method that instantiates the loop, 
        called upon by the method start.
        """   
            
        while True:            
            self._sleeping_beauty.wait(1/self.freq)
            if self._pause_bool:
                self._sleeping_beauty.wait()
            if self._interrupt_called:
                self._interrupt_called = False
                return
            if not self.is_browser_open():                
                break

        self.exit_driver()
        

    def is_browser_open(self):
        """
        Called to check whether Chrome is open or not.
        """
        self._set_lock()
        try:
            output = is_Chrome_open(self.driver)     
            # Make sure the browser is really closed. This protects against 
            # flukes that close the browser at unwanted times.
            if not output: 
                time.sleep(0.5)
                output = is_Chrome_open(self.driver)   
        except: 
            raise
        finally: # always released
            self._release_lock()
        return output



    def interrupt(self):
        """
        Stops the loop manually and will not call upon the method 
        exit_browser.
        Calling this method only makes sense if the loop is threaded.
        """
        self._interrupt_called = True
        self._sleeping_beauty.set

        ## If a lock is set by self.is_chrome_open(), then the 
        ## below statement waits untill that lock is over.
        self._set_lock()
        self._release_lock()


    def exit_driver(self):
        """
        Exits the driver entirely. 
        Automatically called at the end of every loop.
        """        
        self._set_lock()
        try:
            self.driver.quit()
        except:
            raise
        finally: # always release the lock
            self._release_lock()


    def pause(self):
        """ 
        Pauses the loop. 
        Can be resumed by calling the method resume() or start().        
        Calling this method only makes sense if the loop is threaded.
        """
        self._pause_bool = True

        ## If a lock is set by self.is_chrome_open(), then the below statement waits untill that lock is over.
        self._set_lock()
        self._release_lock()


    def resume(self):
        """ 
        Resumes the loop, if paused by method pause().        
        Calling this method only makes sense if the loop is threaded.
        """
        if self._pause_bool:
            self._pause_bool = False
            self._sleeping_beauty.set()      


    def _set_lock(self):
        if self.lock:
            self.lock.acquire()

    def _release_lock(self):
        if self.lock:
            self.lock.release()
            

    @property
    def lock(self):
        return self._lock
    @lock.setter
    def lock(self,lock):
        if self._assert_lock(lock):
            raise self._assert_lock(lock)
        self._lock = lock

    @property
    def freq(self):
        return self._freq
    @freq.setter
    def freq(self,freq):
        if self._assert_freq(freq):
            raise self._assert_freq(freq)
        self._freq = freq


    def _assert_lock(self,lock):
        if not lock:
            return
        try:
            if not callable(lock.acquire) or not callable(lock.release):
                error_message = "Argument 'lock'; either attribute 'acquire' and 'release' (or both) were not callable. Found 'lock' was of type '%s'."%type(lock)
                return TypeError(error_message)
        except AttributeError:
            error_message = "Argument 'lock' did not have either the method 'acquire' and 'release' (or both). Found 'lock' was of type '%s'."%type(lock)
            return TypeError(error_message)

        
##        if not isinstance(lock,self._lock_type):
##            error_message = "Argument 'lock' needs to be of type threading.Lock or, but was found to be of type '%s'."%type(lock)
##            return TypeError(error_message)


    def _assert_freq(self,freq):
        if not isinstance(freq,(int,float)):
            error_message = "Argument 'freq' needs to be an integer or float, but was found to be of type '%s'."%type(freq)
            return TypeError(error_message)
        if not freq >= 0:
            error_message = "Argument 'freq' needs to be positive, but was found to be '%s'."%(freq)
            return ValueError(error_message)


        



if __name__ == "__main__":
    
    driver = update_chromedriver(adblocker=True)
    driver.switch_to_window(open_new_tab(driver))
    close_window(driver)

    A = CloseDriverAfterBrowserHasClosed(driver)
    print("Browser exited")
   


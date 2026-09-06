import unittest
import propertyfactory as pf

class Test_propertyfactory(unittest.TestCase):

    # the doc has an example case in the doc. gotta make sure it works
    def test_propertyfactory_lock_attr_from_doc(self):
        class MyLockedClass:
            y = pf.propertyfactory_lock_attr("y")   
            def __init__(self,y):
                self._private_lock_for_y = True
                # although locked, y can still be set, because y
                # has not been set yet
                self.y = y
        D = MyLockedClass(10)
        
        try:
            D.y = 12        # exception is caught
            raise ValueError("previous line should raise exception")
        except AttributeError as Ex:
            if not Ex.args[0].startswith("Locked"):
                raise       # not gonna happen

            
    # test most basic cases
    def test_propertyfactory_lock_attr(self):
        
        class MyLockedClass:
            y = pf.propertyfactory_lock_attr("y","_lock_y")
            x = pf.propertyfactory_lock_attr("x","_lock_y")
            
            def __init__(self, y):
                self._lock_y = True

                # although locked, y can still be set,
                # because y has not been set yet
                self.y = y

        D = MyLockedClass(10)

        # test if it throws the expected exception
        try:
            D.y = 12
            raise ValueError("# if ValueError is raised, you know the supposed "
                             "AttributeError has not been raised")
        except AttributeError as Ex:
            self.assertTrue( Ex.args[0].lower().startswith("Locked".lower()) )

        D.x = 9
        self.check_if_attribute_x_is_actually_locked( D )

        # test if unlocking works
        D._lock_y = False
        D.y = 20

        # test if deleting the variable works. As it no longer exists, it
        # can be set again while being locked
        D._lock_y = True
        del D.y
        D.y = 11

        # test whether the get-function works
        if D.x:
            pass
        
        
    def test_propertyfactory_lock_attr_format_name_lock(self):
        class foo():
            x = pf.propertyfactory_lock_attr("x","_custom_lock_for_{}")
        D = foo()
        D.x = 2
        D._custom_lock_for_x = True
        
        self.check_if_attribute_x_is_actually_locked( D )
        
        
    
    def test_propertyfactory_lock_attr_default_name_lock(self):
        class foo():
            x = pf.propertyfactory_lock_attr("x")

        D = foo()

        D._private_lock_for_x = True
        D.x = 9
        
        self.check_if_attribute_x_is_actually_locked( D )


    # test lock_default = True
    def test_propertyfactory_lock_attr_self_locking(self):
        class foo():
            x = pf.propertyfactory_lock_attr("x", lock_default = True)

        D = foo()
        D.x = 9
        
        self.check_if_attribute_x_is_actually_locked( D )


    # test lock_default = False
    def test_propertyfactory_lock_attr_self_locking_false(self):
        class foo():
            x = pf.propertyfactory_lock_attr("x", lock_default = False)

        D = foo()
        D.x = 9
        D.x = -12


    # test if two attributes do not intermingle whith each other
    # partially tested in test_propertyfactory_lock_attr, but in those cases
    # the name_lock was not default
    def test_propertyfactory_lock_attr_two_cases(self):
        class foo():
            x = pf.propertyfactory_lock_attr("x")
            y = pf.propertyfactory_lock_attr("y")

        D = foo()

        D.x = 1
        D.y = 2

        D._private_lock_for_x = True

    # name mangling
    def test_propertyfactory_lock_attr_double_underscore(self):
        class foo():
            __x = pf.propertyfactory_lock_attr("__x",
                                               lock_default = "pindakaas")
            def __init__(self):
                self.__x = 9

                try:
                    self.__x = -12
                    raise ValueError("it should throw a specific Error. "
                                     "If not, this behavior is faulty") 
                except AttributeError as Ex:
                    # lower() is just to make sure the comparison isn't fowled
                    # up by some misuse of capitals.
                    if not Ex.args[0].lower().startswith("Locked".lower()) :
                        raise

                self.__x
                
        # test all code within __init__, because due to the name mangling, it's hard(er) to test the code
        # outside the class     
        D = foo()

        
        

        

    # to prevent code from repeating, it is written in here
    def check_if_attribute_x_is_actually_locked(self, obj):
        try:
            obj.x = -12
            raise ValueError("it should throw a specific Error. "
                             "If not, this behavior is faulty") 
        except AttributeError as Ex:
            # lower() is just to make sure the comparison isn't fowled up
            # by some misuse of capitals.
            self.assertTrue( Ex.args[0].lower().startswith("Locked".lower()) )
        

if __name__ == "__main__":
    unittest.main()

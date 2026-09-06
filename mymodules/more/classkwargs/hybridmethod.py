# TODO: write a test for this...?
# TODO: instancemethod doesn't inherit doc that is set for the classmethod.
#       maybe write it in such a way that it automatically does
#       https://stackoverflow.com/questions/5931386/explicitly-set-docstring-of-a-method
# TODO: help sees the classmethod as an instance method. can this be changed? ask original author?

class hybridmethod:
    """
    descriptor.
    if decorated, method can act like a class method and instance
    method, depending on how it is called.
    source: https://stackoverflow.com/questions/28237955/
    
    example:
    class Foo():
        @hybridmethod
        def bar(cls):
            print("class")
        @bar.instancemethod
        def bar(self):
            print("instance")
            
    Foo.bar()
    Foo().bar()
    """
    
    def __init__(self, fclass, finstance=None, doc=None):
        self.fclass = fclass
        self.finstance = finstance
        self.__doc__ = doc or fclass.__doc__
        # support use on abstract base classes
        self.__isabstractmethod__ = bool(
            getattr(fclass, '__isabstractmethod__', False)
        )

    def classmethod(self, fclass):
        return type(self)(fclass, self.finstance, None)

    def instancemethod(self, finstance):
        return type(self)(self.fclass, finstance, self.__doc__)

    def __get__(self, instance, cls):
        if instance is None or self.finstance is None:
              # either bound to the class, or no instance method available
            return self.fclass.__get__(cls, None)
        return self.finstance.__get__(instance, cls)

    
def isclass( cls_or_self ):
    """
    Tests if it is a class or not. Returns Boolean.
    Used to differentiate between class method and instance method.
    # TODO: inspect.isclass works just fine, I imagine...
    """
    if isinstance(cls_or_self, type):
        return True
    else:
        return False


if __name__ == "__main__":
    # TODO: this is a test, move it to a test
    class Foo():
        @hybridmethod
        def bar(cls):
            print("class")
            return "class"
        @bar.instancemethod
        def bar(self):
            print("instance")
            return "instance"
        
    Foo.bar()
    Foo().bar()

    

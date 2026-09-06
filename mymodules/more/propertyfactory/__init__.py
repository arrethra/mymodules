"""
The class property is very usefull to adjust attributes into method-like
bahavior. However, using property can be a bit cumbersome, especially if
a lot of attributes need to have the same property-behavior. In such
cases, a propertyfactory can save a ot of code duplication. This module
offers an example and a specific use (i.e. making attributes read only
by locking them), but also serves as inspiration to make other
propertyfactories.

Note: I think the term factory is correct, but I'm not 100% sure.
"""


# TODO: property is a class. therefor, there might be some opertunity
# to inherit the class, which will mean greater flexibility.
# use help(property) to find out if they use methods setter, getter 
# and deleter, such that they can be easily overridden

# TODO: adjust examples in doc such that doctest can be run

def propertyfactory_example(name_attr,
                    doc = None):
    """
    Example of a propertyfactory, to showcase it is possible to make
    this. Stores the value of the attribute into another attribute, but
    starting with an underscore.
    Note that original name_attr should not contain an underscore as
    well; otherwise a second underscore will be added and
    python might start name mangling (not sure actually how much this
    matters?)

    Example of how to use it:
    class MyClass:
        y = propertyfactory_example("y") 
    """
    # The value of attribute name_attr has to be stored into a secondary
    # attribute. For convenience, this attribute is made private.
    _name_attr = "_" + name_attr
    def g(obj):
        return getattr(obj, _name_attr)
    def s(obj, value):
        print("propertyfactory_example has been executed for attribute '{}'"
              "".format(name_attr))
        setattr(obj, _name_attr, value)
    def d(obj):
        delattr(obj, _name_attr)
    return property(g, s, d, doc = doc)


def propertyfactory_lock_attr(name_attr,
                              name_lock = "_private_lock_for_{}",
                              lock_default = None):
    """
    A propertyfactory that can set an attribute 'name_attr' to be
    locked (i.e. read only), by setting its locking attribute
    'name_lock' to True. By default, you yourself must set the lock.
    See below how to actually initialize such an attribute

    name_attr:    name of the attribute, must be a string. This name
                  should mirror main attribute as a proper
                  coding practice. Note that this
                  propertyfactory does not initialze the main attribute,
                  just decorate it. However, the decorator will eventually
                  create a shadow attribute, whose name will be based upon
                  name_attr by prefixing "_private_attribute_for_".
                  The names cannot match, otherwise if you would set
                  the main attribute, it will cause a recursive loop.
    name_lock:    name for the lock attribute, must be string. If curly
                  brackets are present, those curly brackets will be
                  replaced with name_attr with str.format
    lock_default: if this argument is not default (None), the lock will be
                  set to this value. 
                            
    usage:                                    #        this is how
    class MyLockedClass:                      #        the main attribute
        y = propertyfactory_lock_attr("y")    # <====  should be defined.
        def __init__(self,y):
            self._private_lock_for_y = True
            # although locked, y can still be set, because y
            # has not been set yet
            self.y = y
    D = MyLockedClass(10)
    try:
        D.y = 12        # exception is caught
        raise ValueError()
    except AttributeError as Ex:
        if not Ex.args[0].startswith("Locked"):
            raise       # not gonna happen
    """

    # test if input is valid
    args = {"name_attr": name_attr,
            "name_lock": name_lock}    
    
    for arg_s in args.keys():
        # test if it is a valid type 
        if not isinstance(args[arg_s], str):
            _e = ("For argument '{}', the value must be a string, but found "
                  "type '{}' with value '{}'"
                  .format(arg_s, type(args[arg_s]), args[arg_s])  )
            raise ValueError(_e)

    
    # this will be the name of attributes that help to store the value of the
    # actual attribute. the attribute is made private. 
    _name_attr = "_private_storage_for_" + name_attr
    

    # for name_lock, if curly brackets are present, format accordingly
    # to insert name_attr
    if all(c in name_lock for c in "{}"):
        name_lock = name_lock.format(name_attr)

    def g(obj):
        return getattr(obj, _name_attr)
    
    def s(obj, value):
        if (hasattr(obj, _name_attr) # cant lock attr if it hasnt been set yet
               and getattr(obj, name_lock, None) ):   
            _e = ("Locked: for class {} with attribute '{}', it was tried to "
                  "change the value to {}, but the value has been locked by "
                  "the attribute {} (whose value is {})."
                  "".format(obj, name_attr, value,
                            name_lock, getattr(obj, name_lock)) )
            raise AttributeError(_e)

        if lock_default is not None and not hasattr(obj, name_lock):
            setattr(obj, name_lock, lock_default)
        setattr(obj, _name_attr, value)
        
    def d(obj):
        delattr(obj, _name_attr)

    lock_default_text = ""
    if lock_default is not None:
        lock_default_text = f"""
        The lock will be created once the attribute is initialized (set),"
        "and will default to '{lock_default}'."""
    doc = f"""
        Attribute '{name_attr}' can be locked (i.e. read only) by
        setting its locking attribute '{name_lock}' to True.
        It is not locked if the lock-attribute is not initialized.
        Attribute can always be initilized, regardless of lock. {lock_default_text}
        
        
        The lock was created with propertyfactory_lock_attr.
        """
    return property(g, s, d, doc)




if __name__ == "__main__":
    pass

    class foo():
        x = propertyfactory_lock_attr("x",
                                           lock_default = "pindakaas")
        def __init__(self):
            pass

    D = foo()
    
    help(foo)


    
    
##    class MyLockedClass:
##        y = propertyfactory_lock_attr("y","_lock_y")
##        def __init__(self,y):
##            self._lock_y = True
##
##            # although locked, y can still be set, because y has not been set yet
##            self.y = y  
##
##    D = MyLockedClass(10)
##
##    try:
##        D.y = 12
##    except AttributeError as Ex:
##        if not Ex.args[0].lower().startswith("Locked".lower()):
##            raise
##
##    D._lock_y = False
##    D.y = 20
##
####    help(D)

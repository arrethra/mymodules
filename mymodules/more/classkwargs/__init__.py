# maybe just a vanity project. I guess there are better
# checkers, and better docstring generators

import inspect
import textwrap
import collections
import typing
from classkwargs import myerrors
from classkwargs import hybridmethod
from classkwargs import simpleformat

DEFAULT_KEYTEXT = "to_be_set_by_method_set_docstring"
DEFAULT_allow_outside_kwargs = False
DEFAULT_text_indent_length = 8
DEFAULT_max_line_length = 72
DEFAULT_assert_available_kwargs = True
DEFAULT_total_indent = 0
DEFAULT_start_text = ""
DEFAULT_end_text = ""

# TODO: make decorator for setting doc_string for a function
# TODO: also assert the kwargs in that decorator? and args?
#       and what about *args? make a special key that allows *args?
#       > let typeguard or beartype handle those

# TODO: rename KwargsHandler and module name, especially if you're making
#       a decorator out of it, but can't think of a good name...
#       > KwargChecker?

# TODO: add typing annotations. in this module, but also any underlying modules
#       and process them with beartype or mypy or something.
#       if so, demolish a lot of the type checking...

# TODO: the term {to_be_set_by_method_set_docstring}, will it still work
#       when it's divided over a few lines? don't think so; 
#       the \n-character will be in the way

# TODO: rename execute_kwargs to assert kwargs ?

# TODO: rename set_docstring to generate_docstring ?

# TODO: I read somehwere that for windows, \r\n are line breaks, not \n
#       this will influence _text_wrap and _text_wrap_kwarg

# TODO: _text_wrap and text_wrap_kwarg share some of the same code. 
#       I know that I had difficulty adjusting _text_wrap_kwarg,
#       and therefor created _text_wrap, but see if code from one
#       function can be reused into the other

# TODO: set_docstring calls _set_docstring, using all the arguments. 
#       just use *args and **kwargs. if necesary, leech them of locals()
#       and if you need to change some variable to default, update either
#       the locals or locals.copy()

# TODO: make docstring on module lvl?


def isstr(x):
    """ tests isinstance(x, str), returns boolean"""
    return isinstance(x,str)


def works_for_isinstance(x):
    """
    test if something will work for isinstance. This test is performed
    here, for the fail fast-ethos. Also, if it fails, A relevant TypeError
    will be raised.
    """
    try:
        isinstance(1, x)
    except TypeError:
        return False
    else:
        return True
    

class KwargsHandler():
    """
    Example class, how kwargs could be handled.
    The kwargs are automaticaly collected into this docstring.

    This class was created to make it easier to create doc for kwargs:
    sometimes it is sometimes difficult to keep a clean docstring
    when changes are made. However, creating a dictionary
    'available_kwargs' makes it easier to keep track of the docstring
    for each kwarg as they are defined in the same dict.
    
    available_kwargs:  available_kwargs is a dictionary of dictionaries.
              Each key from available_kwargs must be a string,
              representing an available kwarg. kwargs entered via
              **kwargs are evaluated through this available_kwarg.
              each kwarg-dictionary (i.e. sub-dictionary) can only have
              the following keys. These sub-keys will be relevant to it's
              specific kwarg.

              doc:  string that documents that kwarg into docstring of
                    this class. The docstring of the class must contain
                    the KEYTEXT (see set_docstring) in curly brackets; 
                    at this position will the generated docstring be placed.
              func:  if defined, this function is to be executed for
                    that kwarg with the kwarg-value as input for the
                    function. Will also be executed if a default is
                    given.
              default:  default value for that kwarg. If defined, this
                    will trigger 'func'.
              asserttype:  if defined, an error will be raised if that
                    kwarg is not of that type, i.e. it will evaluate
                    isinstance(kwarg, asserttype).
              assert:  function to perform additional checks on that
                    kwarg if needed. Must be a function, with the kwarg
                    as input. Somewhat redundantas assertions can be
                    included to 'func'. Note that the output of the
                    assert-function is not evaluted. If you wish to
                    raise Errors based on input, you have to do it
                    yourself.
    allow_outside_kwargs:  Normally, only kwargs can be given that are
              among the available kwargs; otherwise it will throw an
              error. If this is set to True, no such error will be
              given.
              Boolean. Default: False.
    **kwargs:  these **kwargs are tested against available_kwargs. If
              allow_outside_kwargs = False, then these **kwargs have to
              be present in available_kwargs. Are stored in attribute
              kwargs, but default values get added in there too.
              original input for **kwargs is stored in attribute _kwargs

    Note: some of it's methods are hybrid methods; they can act like both
          class methods and instance methods; it depends on how they are
          called. Example, both would give the same result:
            from copy import copy
            av_kw = {"foo": {"default":1}}
            S1 = KwargsHandler.set_docstring(av_kw, copy(KwargsHandler))
            S2 = KwargsHandler(av_kw).set_docstring()

    And this is where the code will generate the docstring based upon
    available_kwargs:
    ==>
    {to_be_set_by_method_set_docstring}

    -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    Example of a dictonary that can be given to available_kwargs:
    A = {
        "foo": {
                "func":lambda x: print("foo does something with",x),
                "doc":"does something with foo",},
        "bar": {
                "func":lambda x: print("baz does something with",x),
                "doc":"does something with bar",},
        "foobar": {
                "doc":"does something else"+200*"=",
                "default":"-",
                "asserttype":str,},
        "fb":   {"func":len,}
        }
    -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    """
    # TODO: explain which attributes are available to public, such as 
    #       self.available_kwargs, self.kwargs and other relevant attributes
    #       (such as the attribute that is to be written for the
    #       TODO in the genereated docstring

    # TODO: add arg assert_available_kwargs to __init__

    def __init__(self,
                    # TODO: oops, do not uses dicts as default values
                    # https://docs.python.org/3/faq/programming.html#why-are-default-values-shared-between-objects
                 available_kwargs = {},
                 allow_outside_kwargs = DEFAULT_allow_outside_kwargs,
                 **kwargs,):
	
        self.allow_outside_kwargs = allow_outside_kwargs
        self._kwargs = {} # make a copy. TODO: use dict.copy()
        self._kwargs.update(kwargs) # preserves original input
        self.kwargs = {}  # make a copy. TODO: use dict.copy()
        self.kwargs.update(kwargs) # new kwargs might be added if they have a default.
        self.set_available_kwargs(available_kwargs = available_kwargs)
        self.set_docstring(self.available_kwargs,
                           self,
                           assert_available_kwargs = False,
                           start_text = "The following kwargs can be used:\n\n")
        self.execute_kwargs(allow_outside_kwargs = self.allow_outside_kwargs)


    def set_kwargs(self, **kwargs):
        """
        updates the kwargs of this instance of this class
        """
        self._kwargs.update(kwargs)
        self.kwargs.update(kwargs)
        
                    # TODO: oops, do not uses dicts as default values
                    # https://docs.python.org/3/faq/programming.html#why-are-default-values-shared-between-objects
    def set_available_kwargs(self, available_kwargs = {},
                                   assert_available_kwargs =
                                          DEFAULT_assert_available_kwargs):
        """
        available_kwargs: is a dictionary of dictionaries. each key must
              be an string, representing an available kwarg (a kwarg
              in **kwarg from __init__). This key defines a
              kwarg-dictionary in which the possible keywords can be
              the following:
              doc:  string that documents that kwarg into docstring of
                    this class. The docstring of the class must contain
                    the DEFAULT_KEYTEXT in curly brackets; at this position
                    will the generated docstring be placed.
              func:  if defined, this function is to be executed for
                    that kwarg with the kwarg-value as input for the
                    function. Will also be executed if a default is
                    given.
              default:  default value for that kwarg. If defined, this
                    will trigger 'func'.
              asserttype:  if defined, an error will be raised if that
                    kwarg is not of that type, i.e. it will evaluate
                    isinstance(kwarg, asserttype).
              assert:  function to perform additional checks on that
                    kwarg if needed. Must be a function, with the kwarg
                    as input. Somewhat redundantas assertions can be
                    included to 'func'. Note that the output of the
                    assert-function is not evaluted. If you wish to
                    raise Errors based on input, you have to do it
                    yourself.
        assert_available_kwargs:  If True, asserts if available_kwargs
              has been formatted properly.
              default = __debug__
        """

        if not isinstance(available_kwargs, dict):
            _e = ("available_kwargs is not a dict, but rather type '{}' "
                  "with value {}."
                  "".format(type(available_kwargs),
                            repr(available_kwargs))
                  )
            raise TypeError(_e)
              
        
        # from python 3.7, all dicts are ordered dicts. no guarantees before 3.7
        # about ordering. built-in dicts (>=3.7) are supposedly more efficient
        
        if not hasattr(self,"available_kwargs"): 
            self.available_kwargs = {}
        

        # current method intiates the dictionary according to python-version
        # available kwargs are actually set in this method
        # as that method can easier be overridden.
        
        
        self._assert_available_kwargs(available_kwargs)  
        self.available_kwargs.update(available_kwargs)


    # defined outside a method, such that it can be accesed by class methods
    # and is not defined multiple times, if the method would be called
    # multiple times
    #
    # The dictionary below defines all possible keywords that a
    # kwarg_dictionary can be given. The 'check'-values of the dictionary
    # below are a function that will assert checks on the validity of
    # the associated value in the kwarg-dictionary. If such a check is
    # failed, it will raise an error with 'errormsg'. The errormsg will be
    # formatted when the error is raised.
    #
    _kwarg_dict_possibilities = {
        "doc":  {"check": isstr,
                 "errormsg":("For available_kwarg '{kwarg}' the "
                             "'doc'-keyword "
                             "should be a string but found {vtype}.") },
        "func": {"check":callable,
                 "errormsg":("For available_kwarg '{kwarg}' the 'func' "
                             "should be callable but found type {vtype}.")},
        "default":None,
        "asserttype":{
                 "check": works_for_isinstance,
		# TODO" test if this is raised well, and if error_message is raised
                 "errormsg":("For available_kwarg '{kwarg}' the "
                             "'asserttype'-keyword should be class, tuple "  
                             "of "
                             "classes or a union but found type {vtype} "
                             "(for the purpose of isinstance).")},

        "assert":{"check":callable, 
                  "errormsg":("For available_kwarg '{kwarg}' the "
                              "'assert'-keyword "
                              "should be callable but found type {vtype}.")},
                                          }
    
    @hybridmethod.hybridmethod
    def execute_kwargs(cls,
                       # TODO: oops, do not uses dicts as default values
                       # https://docs.python.org/3/faq/programming.html#why-are-default-values-shared-between-objects
                       available_kwargs = {},
                       allow_outside_kwargs = DEFAULT_allow_outside_kwargs,
                       assert_available_kwargs = __debug__,
                       **kwargs):
        """
        For all kwargs (**kwargs), executes the 'default', 'func',
        'asserttype' and 'assert' from available_kwargs. See doc from
        main class for more info on those 4 keywords.

        Is a hybrid method; can be used as class method or as instance
        method

        if used as an instance method, argument available_kwargs and
        **kwargs  will be updated to the available_kwargs and **kwargs
        that were already present in the instance. All will then be
        executed.

        returns **kwargs. if default values are present in
        available_kwargs, those kwargs will be added and set to default.
        """
        if assert_available_kwargs:
            cls._assert_available_kwargs(cls, available_kwargs)
        return cls._execute_kwargs(cls,
                           available_kwargs = available_kwargs,
                           allow_outside_kwargs = allow_outside_kwargs,
                           **kwargs)
        
    @execute_kwargs.instancemethod
    def execute_kwargs(self, 
                    # TODO: oops, do not uses dicts as default values
                    # https://docs.python.org/3/faq/programming.html#why-are-default-values-shared-between-objects
                       available_kwargs = {},
                       allow_outside_kwargs = DEFAULT_allow_outside_kwargs,
                       assert_available_kwargs = __debug__,
                       **kwargs):
        
        if available_kwargs:
            self.set_available_kwargs(available_kwargs,
                                      assert_available_kwargs =
                                                        assert_available_kwargs)
        if kwargs:
            self._kwargs.update(kwargs) # preserves input in case of defaults
            self.kwargs.update(kwargs)

        return self._execute_kwargs(available_kwargs = available_kwargs,
                             allow_outside_kwargs = allow_outside_kwargs,
                             **kwargs) 
    
    def _execute_kwargs(self_or_cls,
                    # TODO: oops, do not uses dicts as default values
                    # https://docs.python.org/3/faq/programming.html#why-are-default-values-shared-between-objects
                        available_kwargs = {},
                        allow_outside_kwargs = DEFAULT_allow_outside_kwargs,
                        **kwargs):
        """
        For all kwargs (**kwargs), executes the 'default', 'func',
        'asserttype' and 'assert' from available_kwargs. See doc from
        main class for more info on those 4 keywords.
        """
        # is a normal class, but a classmethod (from this class) might also
        # call on this method, which does have implications

        # asuming available_kwargs has already been checked
        # whether it is properly formatted or not
        
        _available_kwargs = {}
        _kwargs = {}
	

        if hybridmethod.isclass( self_or_cls ): # TODO: use inspect.isclass()
            # TODO: the argument available_kwargs and kwargs from argument
            #       need to be updated anyway, also only if not isclass
            #       and well, incorporate into test...
            # it is cls
            _available_kwargs.update(available_kwargs)
            _kwargs.update(kwargs)
        else:
            # then it is self
            _available_kwargs.update(self_or_cls.available_kwargs)
            _kwargs.update(self_or_cls.kwargs)
            

            
        # check if any kwargs are given that are not supposed to be in there.
        if not allow_outside_kwargs:
            wrong_kwargs = _kwargs.keys() - _available_kwargs.keys()
            if wrong_kwargs:
                _e = ("{} was given wrong kwargs, namely '{}' while "
                    "only the following available_kwargs are allowed: '{}'. To "
                    "allow kwargs that are not defined in available_kwargs, see"
                    " keyword allow_outside_kwargs"
                    "".format(self_or_cls,
                              "', '".join(wrong_kwargs),
                              "', '".join(_available_kwargs.keys()) ))
                raise TypeError(_e)
        
        # start checking for asserttype, assert and func
        for kwrg in _available_kwargs:
            if not kwrg in _kwargs and "default" in _available_kwargs[kwrg]:
                _kwargs[kwrg] = _available_kwargs[kwrg]["default"]
            if "asserttype" in _available_kwargs[kwrg]:
                if (kwrg in _kwargs and
                    not isinstance(_kwargs[kwrg],
                                  _available_kwargs[kwrg]["asserttype"])):
                    asserttypes = _available_kwargs[kwrg]["asserttype"]
                    asserttypes = myerrors.extract_class_strings(asserttypes)
                    _e = ("For kwarg {}, expected type {} "
                       "but found value {} with type {}.".format(
                        kwrg, asserttypes,
                        repr(_kwargs[kwrg]),
                        type(_kwargs[kwrg]))  )
                    raise TypeError(_e)
            if "assert" in _available_kwargs[kwrg] and kwrg in _kwargs:
                _available_kwargs[kwrg]["assert"](_kwargs[kwrg])
            if kwrg in _kwargs:
                if "func" in _available_kwargs[kwrg]:
                    if _available_kwargs[kwrg]["func"]: 
                        _available_kwargs[kwrg]["func"](_kwargs[kwrg])

        if not hybridmethod.isclass(self_or_cls):
            self_or_cls.kwargs.update(_kwargs)
        return _kwargs
                    

    @hybridmethod.hybridmethod
    def set_docstring(cls,
                      available_kwargs ,
                      obj = None,
                      text_indent_length = DEFAULT_text_indent_length,
                      total_indent = DEFAULT_total_indent,
                      max_line_length = DEFAULT_max_line_length,
                      start_text = DEFAULT_start_text,
                      end_text = DEFAULT_end_text,
                      assert_available_kwargs = DEFAULT_assert_available_kwargs,
                      keytext = DEFAULT_KEYTEXT,
                      ):
        """
        hybrid method. can be called as class method or as instance
        method. Updates __doc__ for given class, function or method.
        obj.__doc__ must have the keytext as a placeholder for the
        generated docstring. After modifying obj.__doc__,
        Returns the generated docstring, not the whole obj.__doc__
        
        Code in this method can only executed the first time per keytext,
        as the keytext is replaced. Multiple passes over different keytext
        can be accomplished if obj.__doc__ contains those different
        keytexts.
        
        available_kwargs:  must be a dict. content of this dict shapes
                the string that will update doc. See doc on this class
                for more specifics how available_kwargs should be
                formatted.
                default = {}
        obj:    must be a function, class or method, of which the
                docstring will be updated.  If default (None), it
                will not modify the doc, but only return the string.
                if docstring is absent from obj (such as None or ""),
                docstring will be set to the generated docstring.
                Note, if obj was an instance, the class will not have
                a docstring.
                default = None
        text_indent_length: after each new keyword, determines the
                number of spaces of indent before the text starts,
                with respect to the beginning of the kwarg.
                if the keyword is longer than the indent, the first line
                is not affected.
                default = 8
        total_indent: indent overall. text_indent_length is affected
                accordingly.
                default 0
        max_line_length:  determines the maximum line length, before
                beginning a new line.
        start_text:  text to be shown at the beginning of the generated
                string.
                default = ""
        end_text:  text to be shown at the end of the generated string.
                default = ""
        assert_available_kwargs:  If True, asserts if available_kwargs
                has been formatted properly.
                default = True
        keytext:  obj.__doc__ must contain keytext in curly brackets.
                This keytext will be replaced by the generated docstring.
                if obj.__doc__ is not set (i.e. None) or empty, it will
                be replaced with generated docstring, keytext will be
                disregarded.
                Must be string.
                default is   to_be_set_by_method_set_docstring
        """
        
        return cls._set_docstring(cls,
                           available_kwargs,
                           obj = obj,
                           text_indent_length = text_indent_length,
                           total_indent = total_indent, 
                           max_line_length = max_line_length,
                           start_text = start_text,
                           end_text = end_text,
                           assert_available_kwargs = assert_available_kwargs,
                           keytext = keytext 
                           )
    
	# TODO: add an opt_out that self.available_kwargs in not added to 
        #        generated docstring, only those from the input.
    @set_docstring.instancemethod
    def set_docstring(self,
                    # TODO: oops, do not uses dicts as default values
                    # https://docs.python.org/3/faq/programming.html#why-are-default-values-shared-between-objects
                      available_kwargs = {},
                      obj = None,
                      text_indent_length = DEFAULT_text_indent_length,
                      total_indent = DEFAULT_total_indent,
                      max_line_length = DEFAULT_max_line_length,
                      start_text = DEFAULT_start_text,
                      end_text = DEFAULT_end_text,
                      assert_available_kwargs = DEFAULT_assert_available_kwargs,
                      keytext = DEFAULT_KEYTEXT,
                      ):
        """
        This is the instance method. See docstring of the classmethod.
        (not sure how to get it to here. don't want to copy-paste,
        because then I have to synchronize manually)
        """
        if available_kwargs:
            self.set_available_kwargs(available_kwargs,
                                      assert_available_kwargs =
                                          assert_available_kwargs)
                  
        return self._set_docstring(
                           self.available_kwargs,
                           obj = obj,
                           text_indent_length = text_indent_length,
                           total_indent = total_indent,
                           max_line_length = max_line_length,
                           start_text = start_text,
                           end_text = end_text,
                           assert_available_kwargs = False, # they were already
                                        # asserted in self.set_available_kwargs,
                                        # no need to do it twice
                           keytext = keytext,
                           )

            
    def _set_docstring(self_or_cls,
                       available_kwargs,
                       obj = None,
                       text_indent_length = DEFAULT_text_indent_length,
                       total_indent = DEFAULT_total_indent,
                       max_line_length = DEFAULT_max_line_length, 
                       start_text = DEFAULT_start_text,
                       end_text = DEFAULT_end_text,
                       assert_available_kwargs = DEFAULT_assert_available_kwargs,
                       keytext = DEFAULT_KEYTEXT, 
                       ):

        if assert_available_kwargs:
            # calling upon a method of this class, is tricky, since a call from
            # a methodclass tho that method is different than if you'd call that
            # method from an instance method
            if hybridmethod.isclass(self_or_cls): # = cls, or class method
                self_or_cls._assert_available_kwargs(self_or_cls,
                                                     available_kwargs)
            
        # simple check
        if not isinstance(available_kwargs, dict):
            _e = ("Method set_docstring expected a dict "
                  "for 'available_kwargs'"
                  " but found '{}'.".format(type(available_kwargs)))
            raise TypeError(_e)
        
        if not isinstance(start_text, str):
            myerrors.TypeErrorWithMessage("start_text", str, start_text)
        if not isinstance(end_text, str):
            myerrors.TypeErrorWithMessage("start_text", str, end_text)

        _doc_addition =  self_or_cls._text_wrap(start_text,
                                                 width = max_line_length,
                                                 total_indent = total_indent )
        after_kwrg = ":  "



        # create the docstring (but just string fow now)
        for kwrg in available_kwargs:
            _text_start = (  kwrg
                           + after_kwrg
                           +  " " * max(text_indent_length
                                        - len(kwrg) - len(after_kwrg), 0)
                          )
            _text = _text_start
            if isinstance(available_kwargs[kwrg], str):
                _text += available_kwargs[kwrg]
            elif isinstance(available_kwargs[kwrg], dict):
                tx = ""
                if "doc" in available_kwargs[kwrg]:
                    tx += available_kwargs[kwrg]["doc"]
                    if tx and tx[-1] != ".":
                        tx += "."
                    
                if "asserttype" in available_kwargs[kwrg]:
                    if tx: # i.e. if "doc" in kwargs[kwrg]:
                        tx += "\n"
                    s = myerrors.extract_class_strings(
                                        available_kwargs[kwrg]["asserttype"]
                                                      )
                    tx += "Argument must be of type {}.".format(s)
                if "default" in available_kwargs[kwrg]:
                    if tx and not "\n" in tx:
                        tx += "\n"
                    if tx and tx[-1] != " " and tx[-1] != "\n":
                        tx += " "
                    tx += ("Default value is "
                              + str(available_kwargs[kwrg]["default"])
                              + "." )
                        # TODO: these text like "Default is " and
                        #  "docstring not defined, sorry.", put them in a class
                        #  attribute, such that they can be overwritten as
                        #  people want their own style of doc.
                        #  even the after_kwarg ":  " thingy should be added to 
                        #  the attribute.
                _text += tx
            if _text == _text_start:
                _text += "docstring not defined, sorry."

            _doc_addition += self_or_cls._text_wrap_kwarg(_text,
                                    width = max_line_length,
                                    text_indent_length = text_indent_length,
                                    total_indent = total_indent)
            
        # the very last \n doesn't have to be shown
        
        if _doc_addition and _doc_addition[-1] == "\n":
            _doc_addition = _doc_addition[0:-1]

        _doc_addition += self_or_cls._text_wrap(end_text,
                                               width = max_line_length,
                                               total_indent = total_indent )

        if obj:
            if obj.__doc__:
                kwargs_for_simpleformat = {keytext: _doc_addition}
                if inspect.ismethod(obj):
                    # https://stackoverflow.com/questions/5931386/
                    #               explicitly-set-docstring-of-a-method
                    obj.__func__.__doc__ = simpleformat.simpleformat(
                                                   obj.__func__.__doc__,
                                                   **kwargs_for_simpleformat )
                else:
                    obj.__doc__ = simpleformat.simpleformat(obj.__doc__,
                                                   **kwargs_for_simpleformat )
            else: 
                obj.__doc__ = _doc_addition
                        
        return _doc_addition

    @staticmethod
    def _text_wrap(text,
                   width = DEFAULT_max_line_length,
                   total_indent = DEFAULT_total_indent):
        """
        static method.
        text_wrap for formatting text into docstring.
        used by set_docstring. I had to create my own, as
        textwrap.wrap doesn't like new line breaks (see kwarg
        replace_whitespace for textwrapper.wrap for more explanation)
        """
        _text = ""
        for t in text.split("\n"):
            _text += "\n".join(textwrap.wrap(t,
                                             width = width,
                                             initial_indent =
                                                 indent_length(total_indent),
                                             subsequent_indent = 
                                                 indent_length(total_indent)
                                            ))
            _text += "\n"
        if _text and _text[-1] == "\n":
            _text = _text[0:-1]
        return _text
            
    

    @staticmethod
    def _text_wrap_kwarg( text,
                    width = DEFAULT_max_line_length,
                    text_indent_length = DEFAULT_text_indent_length,
                    total_indent = DEFAULT_total_indent):
        """
        static method.
        text_wrap for formatting kwargs into docstring.
        used by set_docstring. I had to create my own, as
        textwrap.wrap doesn't like new line breaks (see kwarg
        replace_whitespace for textwrapper.wrap for more explanation)
        """
        _text = ""
        initial_indent = total_indent
        for i, t in enumerate(text.split("\n")):
            if i == 1:  # textwrap doesn't expect lines to be broken
                        # by \n midsentence
               initial_indent += text_indent_length 
            _text += "\n".join(textwrap.wrap(t,
                                             width = width,
                                             initial_indent =
                                                 indent_length(initial_indent),
                                             subsequent_indent = 
                                                 indent_length(text_indent_length
                                                               + total_indent)
                                                               ))
            _text +=  "\n"
        return _text

# TODO: oops, do not uses dicts as default values
# https://docs.python.org/3/faq/programming.html#why-are-default-values-shared-between-objects
    def _assert_available_kwargs(self_or_cls, available_kwargs = {}):
        """Asserts whether  dictionary for available kwargs is correct. """
        # is a normal class, but a classmethod (from this class) might also
        # call on this method, which does have implications
        
        if not isinstance(available_kwargs, dict):
            raise myerrors.TypeErrorWithMessage("available_kwargs",
                                          dict,
                                          available_kwargs)


        
        # test if available_kwargs is indeed a dict
        _available_kwargs = {}
        if not hybridmethod.isclass( self_or_cls ):
            if not isinstance(self_or_cls.available_kwargs, dict):
                raise myerrors.TypeErrorWithMessage("available_kwargs", dict,
                              self_or_cls.available_kwargs)
            _available_kwargs.update(self_or_cls.available_kwargs)
        if available_kwargs:
            if not isinstance(available_kwargs, dict):
                raise myerrors.TypeErrorWithMessage("available_kwargs", dict,
                              available_kwargs)
            _available_kwargs.update(available_kwargs)
        
        for kwrg in _available_kwargs:
            if not isinstance(kwrg, str):
                _e = ("In available_kwargs, a kwarg was "
                    "required to be a string, but kwarg was found"
                    " to be '{}' of type {}.".format(kwrg, type(kwrg)))
                raise TypeError(_e)
            
            if not isinstance(_available_kwargs[kwrg], dict):
                _e = ("For keyword '{}' the value should be a dict "
                      "(within a dict), but found type {} with value {}."
                      "").format(kwrg,
                                 type(_available_kwargs[kwrg]),
                                 repr(_available_kwargs[kwrg]))
                raise TypeError(_e)
                 
            for kwarg_ky in _available_kwargs[kwrg]:
                if not isinstance(kwarg_ky, str):
                    _e = ("For available kwargs, a kwarg dictionary with "
                        "key '{}' needed to be a string with specific "
                        "keywords. type '{}' was found but choices were"
                        " '{}'.".format(kwrg, type(kwarg_ky,),
                                         self_or_cls._kwarg_dict_possibilities))
                    raise TypeError(_e)
                if not kwarg_ky in self_or_cls._kwarg_dict_possibilities:
                    possibles = "', '".join(self_or_cls._kwarg_dict_possibilities.keys())
                    _e = ("For available kwargs, a kwarg dictionary with key '{}'"
                        " needed to have specific keywords. '{}' was found but "
                        "choices were '{}'.".format(kwrg,
                                                   kwarg_ky,
                                                   possibles )
                                            )
                    raise ValueError(_e)
                if self_or_cls._kwarg_dict_possibilities[kwarg_ky]:
                    if not self_or_cls._kwarg_dict_possibilities[kwarg_ky]["check"](_available_kwargs[kwrg][kwarg_ky]):
                        _e = self_or_cls._kwarg_dict_possibilities[kwarg_ky]["errormsg"].format( kwarg = kwrg,
                                                                vtype = type(_available_kwargs[kwrg][kwarg_ky]))
                        raise TypeError(_e)
        return

                    
    def __str__(self):
        a_k = list(self.available_kwargs.keys())
        name = type(self).__name__

        output = f"<class '{name}({a_k})'>"
        return output
    

    def __repr__(self):
        location = super().__repr__()
        location = location.split(" ")[-1].rstrip(">")
        name = type(self).__name__

        a_k = repr(list(self.available_kwargs.keys()))
        kwargs = repr(list(self.kwargs.keys()))
        
        output = (f"<class '{name}(available_kwargs={a_k}, "
                  f"kwargs={kwargs})' at location {location}>" )
        return output


    def __eq__(self, other):
        attributes = ["_kwargs", "kwargs", "available_kwargs"]
        for a in attributes:
            if not hasattr(other, a):
                return False
        
        return all(getattr(self, a) == getattr(other, a) for a in attributes)


def indent_length(i):
    """
    Returns number of spaces specified by i.
    """
    return i*" "


                
if __name__ == "__main__" and True:
    pass

##    A = {
##            "foo": {
##                    "func":lambda x:setattr(self,"foo",x),
##                    "doc":"does something with foo",},
##            "bar": {
##                    "func":lambda x:setattr(self,"bar",x),
##                    "doc":"does something with bar",},
##            "foobar": {
##                    "doc":"does something else"+200*"=",
##                    "default":"-",
##                    "asserttype":str,},
##            "fb":   {"func":len,}
##            }
##    
##    B = KwargsHandler(A)
##    print(type(B), type(KwargsHandler))






##        # maybe after __main__ == __name__
##        
##        # used to add these keywords to docstring of class
##        # I wanted to let this also set the docstring of this method, but app
##        # apparently, method.__doc__ can't be modified somehow
##        self._keywords_for_set_available_kwargs = {
##            "doc":   {"doc":
##                          "string that documents that kwarg into docstring of "
##                          "this Class.",},
##            "func":  {"doc":
##                          "if defined, this function is to be executed for that"
##                          " kwarg with the kwarg-value as input for the "
##                          "function. "
##                          "Will also be executed if a default is given.",},
##            "default": {"doc":
##                          "default value for that kwarg. If defined, this will "
##                          "trigger 'func'.",},
##            "asserttype": {"doc":
##                           "if defined, an error will be raised "
##                           "if that kwarg is "
##                           "not of that type, i.e. isinstance(kwarg, "
##                           "asserttype)",
##                           },
##            "assert":  {"doc":
##                            "function to perform additional checks "
##                            "on that kwarg if needed. Must be a function, "
##                            "with the kwarg as input. Somewhat redundant "
##                            " as assertions can be included to"
##                            " 'func'."}        
##                                                    }
##                      
##        Z = self.set_docstring(self._keywords_for_set_available_kwargs,
##                                          text_indent_length = 6,
##                                          max_line_length = 58)
##        print(Z)

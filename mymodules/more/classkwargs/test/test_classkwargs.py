import unittest
import classkwargs as ck
import copy



ORIGINAL_DOC = ck.KwargsHandler.__doc__


# used in method test_docstring, but found it more usefull to state this
# variable before anything was declared, such that indentation required
# after a class-statement or method-statement is less of an issue 
control_docstring =  "\n".join([
    "",
    "some text followed by the keytext:",
    "",
    "The following arguments can be used:",
    "foo:    does something with foo.",
    "bar:    does something with bar.",
    "foobarrrrrr:  does something else---------------------------------------",
    "        ----------------------------------------------------------------",
    "        ----------------------------------------------------------------",
    "        ---------------------------------.",
    "        Argument must be of type 'str', 'int',",
    "        '__main__.Test_classkwargs.test_docstring.<locals>.MyFoo'.",
    "        Default value is -.",
    "foobazzzzzz:  does something else---------------------------------------",
    "        ----------------------------------------------------------------",
    "        ----------------------------------------------------------------",
    "        ---------------------------------.",
    "        Default value is -.",
    "fb:     docstring not defined, sorry.",
    "",
    ])


class Test_classkwargs(unittest.TestCase):
    def setUp(self ):
        """
        some test calls on
        ck.KwargsHandler.set_docstring(kw, ck.KwargsHandler)
        but this alters the docstring of the class
        and has to be reset
        """
        ck.KwargsHandler.__doc__ = ORIGINAL_DOC
    
        
        
    def test_docstring(self):
        class MyFoo():
            """
            some text followed by the keytext:

            The following arguments can be used:
            {to_be_set_by_method_set_docstring}
            """
            def __repr__(self):
                return "MyFoo_repr()"
            def __str__(self):
                return "MyFoo_str()"

        myfoo = MyFoo()

        kw = {
                "foo": {
                        "func":lambda x:setattr(self,"foo",x),
                        "doc":"does something with foo",},
                "bar": {
                        "func":lambda x:setattr(self,"bar",x),
                        "doc":"does something with bar",},
                "foobarrrrrr": {
                        "doc":"does something else"+200*"-",
                        "default":"-",
                        "asserttype":(str,int,MyFoo,)},
                "foobazzzzzz": {
                        "doc":"does something else"+200*"-",
                        "default":"-"},
                "fb":   {"func":lambda x:print("what will be printed:", x),}
                }

        # decorator for other functions, in the making
        S0 = ck.KwargsHandler().set_docstring(kw, myfoo)
        
        self.assertEqual(myfoo.__doc__,
                         control_docstring,
                         msg = " If module_name changes, this'll probably fail."
                               " If python 3.7 or lower, this will probably"
                               " fail, as dicts only preserved order in "
                               "subsequent releases"  
                         )
        
        
        # test if kw has no doc-keywords. what happens then?
        # default and asserttype will generate docstring, but what
        # if none of those are present as well??
        kw_ds = {
                "foo": {},
                "bar": {},
                }
        S = ck.KwargsHandler().set_docstring(kw_ds, )
        control_string = "\n".join([
                            "foo:    docstring not defined, sorry.",
                            "bar:    docstring not defined, sorry.",
                                    ])
        self.assertEqual(S, control_string)

        # if only default is present, no doc or asserttypes.
        kw_ds_2 = {
                  "foo": {"default":1},
                  "bar": {"default":1},
                   }
        S2 = ck.KwargsHandler().set_docstring(kw_ds_2, )
        control_string2 = "\n".join([
                            "foo:    Default value is 1.",
                            "bar:    Default value is 1.",
                                    ])
        self.assertEqual(S2, control_string2)

        # for empty dict (empty input), it won't generate any output
        # (well, an empty string)
        S3 = ck.KwargsHandler().set_docstring({}, )
        self.assertEqual(S3, "")


    def test_docstring2(self):
        # what if it doesn't alter docstring, but I just want it to
        # return the string
        kw = {"foo":{"doc":"whatever"},
              "bar":{"doc":"does something",
                     "default":1},
              }
        
        S = ck.KwargsHandler().set_docstring(kw,)

        control_string = "\n".join([
              "foo:    whatever.",
              "bar:    does something.",
              "        Default value is 1.",
                          ])
        
        self.assertEqual( S,
                          control_string)

        # test if \n are respected in docstring
        kw_ds2 = {"foo": {"doc":"text \n more text"}}
        S2 = ck.KwargsHandler().set_docstring(kw_ds2,)
        
        control_string2 = "\n".join([
            "foo:    text", # it strips traling spaces, apparently
            "         more text.",
                             ])
        self.assertEqual(S2, control_string2)


    def test_docstring_on_functions(self):
        # while docstring accepts classes, it must also accept functions
        
        def foo():
            """
            some text followed by the keytext:

            The following kwargs can be used:
            {to_be_set_by_method_set_docstring}
            """
            pass

        control_string = "\n".join([
            "",
            "some text followed by the keytext:",
            "",
            "The following kwargs can be used:",
            "bar:    docstring not defined, sorry.",
            "foobar:  docstring not defined, sorry.",
            "",
                                    ])

        kw_f = {"bar": {},
                "foobar": {}}
        S_f = ck.KwargsHandler().set_docstring(kw_f, foo)
 
        self.assertEqual(foo.__doc__,
                         control_string)

    def test_docstring_errorhandling(self):
        # whether it can spot bad input, when piped through docstring

        kw_er0 = {1111111:1}
        with self.assertRaises(TypeError):
            ck.KwargsHandler.set_docstring(kw_er0)

        kw_er1 = "a"
        with self.assertRaises(TypeError):
            ck.KwargsHandler.set_docstring(kw_er1)
        
        
    def test_docstring__adding_aditional_available_kwargs(self):
        
        kw_aaak0_1 = {"foo":{},
                      "bar": {},
                      }
        kw_aaak0_2 = {"deer": {},
                       "kamp":{},
                       }
        A = ck.KwargsHandler(kw_aaak0_1)
        S = A.set_docstring(kw_aaak0_2)

        kw_aaak0_totaal = {}
        kw_aaak0_totaal.update(kw_aaak0_1)
        kw_aaak0_totaal.update(kw_aaak0_2)

        for k in kw_aaak0_totaal:
            if not k in S:
                raise OSError("I don't know which error to raise,"
                                " but doesn't really matter, does it?")


    def test_docstring__obj_has_no_or_wrong_keyword(self):
        # keytext is not in docstring, so an error is raised
        class Saz():
            """
            some docstring
            {wrong keyword}
            """
            pass

        kw = {"fwoo": {} }        
        with self.assertRaises(KeyError):
            ck.KwargsHandler.set_docstring(kw, Saz())

        #       just to check it's still present and docstring
        #       of class hasn't been modified
        ck.KwargsHandler.set_docstring(kw, Saz(), keytext="wrong keyword")


        # if docstring is entirely absent, it will be overwritten
        class Gaz():
            pass
        G = Gaz()
        ck.KwargsHandler.set_docstring(kw, G)
        self.assertTrue( isinstance(G.__doc__, str))
        self.assertTrue(len(G.__doc__) > 0 )
        

        # if docstring is empty string, the truthiness of the empty string
        # means it'll be overwritten
        class Maz():
            """"""
            pass
        M = Maz()
        ck.KwargsHandler.set_docstring(kw, M)
        self.assertTrue(len(M.__doc__) > 0 )


        # test strange characters as keywords
        class Kaz():
            """  {_} {+} {-} {*} """
            pass

        key_K = "bzbzbz"
        kw_K = {key_K : {}}
        K = Kaz()

        chars = ["_","+","-","*"]
        for s in chars:
            ck.KwargsHandler.set_docstring(kw_K, K, keytext=s)
        Ks = K.__doc__.split(key_K)
        self.assertEqual(len(chars), len(Ks)-1,
                        msg = "not all characters from {} "
                        "are supported as keytext.".format(chars))
        
        
    def test_docstring_if_it_can_handle_methods(self):
        kw_Q = {"fgoo": {}}
        class Qaz():
            def stupid_method(self):
                """
                some description about a stupid method
                {argument}
                """
                pass
        
        S = ck.KwargsHandler.set_docstring(kw_Q, Qaz.stupid_method,
                                           keytext = "argument")
        control_string = "\n".join([
            "",
            "some description about a stupid method",
            "fgoo:   docstring not defined, sorry.",
            "",
                                    ])
        self.assertEqual(Qaz.stupid_method.__doc__,
                         control_string)
        


    def test_self_assertion(self):
        # whether it can spot bad input
        kw_minus1 = "aaaaBBBcccDDD"
        with self.assertRaises(TypeError):
            ck.KwargsHandler(kw_minus1)

        # test for case of methodclass
        with self.assertRaises(TypeError):
            ck.KwargsHandler.execute_kwargs(kw_minus1)
        
        
        class MyFoo():
            """
            some text followed by the keytext:
            
            {to_be_set_by_method_set_docstring}
            """
            pass

        myfoo = MyFoo()
        
        kw0 = 1
        with self.assertRaises(TypeError):
            ck.KwargsHandler(kw0)
        
        kw1 = {1:1}
        with self.assertRaises(TypeError):
            ck.KwargsHandler(kw1, )

        # keywords per kwarg should be carefully crafted
        kw2 = {  "bar": {"funcyyyyyy":lambda x:setattr(self,"bar",x),
                        "doc":"does something with bar",},             }
        with self.assertRaises(ValueError):
            ck.KwargsHandler(kw2,)

        # check errorhandling: should be a dict of dicts    
        kw3 = {"bar": 1}
        with self.assertRaises(TypeError):
            ck.KwargsHandler(kw3,  )

        # check errorhandling: doc should be a string
        kw4 = {"bar": {"doc":1}}
        with self.assertRaises(TypeError):
            ck.KwargsHandler(kw4, )

        # check errorhandling: func should be callable
        kw5 = {"bar": {"func":1}}
        with self.assertRaises(TypeError):
            ck.KwargsHandler(kw5,)

        # check errorhandling: 'assert' should be callable
        kw6 = {"bar": {"assert":1}}
        with self.assertRaises(TypeError):
            ck.KwargsHandler(kw6, )

        # check errorhandling: 'asserttype' should be a class or something
        kw7 = {"bar": {"asserttype":1}}
        with self.assertRaises(TypeError):
            ck.KwargsHandler(kw7,)

        
    def test_allow_outside_kwargs(self):
        kw_aok = {"bar": {
                          "doc":"does something"}
                  }
        # outside kwargs are allowed, so fine
        A = ck.KwargsHandler(available_kwargs = kw_aok,
                             allow_outside_kwargs = True,
                             foo = 2,
                             barrrr = 3)

        with self.assertRaises(TypeError):
            A = ck.KwargsHandler(available_kwargs = kw_aok,
                                 allow_outside_kwargs = False,
                                 foo = 2,
                                 barrrr = 3)

        kw_aok_1 = {"bar": {"default": 5},
                    "foo": {},
                    "foobar": {},
                    }

        A = ck.KwargsHandler(available_kwargs = kw_aok_1,
                             allow_outside_kwargs = True,
                             foo = 2,
                             bar = 3,
                             foorbar = {})
        
        pass

    def test_set_kwargs(self):
        
        A = ck.KwargsHandler(foo = 1,
                             bar = 2,
                             allow_outside_kwargs = True)
        self.assertEqual( A.kwargs  ,
                          {"foo": 1, "bar": 2}
                          )
        A.set_kwargs(papa = 4)
        self.assertEqual( A.kwargs,
                          {"foo": 1, "bar": 2, "papa": 4}
                          )


    def test__execute_kwargs_normal_method_not_methodclass(self):
        # check if asserttype works
        kw_ek = {
                "foo": {
                        "doc":"does something else",
                        "default":"-",
                        "asserttype":(str,int,)},
                }
        # first check if nothing is wrong with input of kw_ek
        A = ck.KwargsHandler(kw_ek, )
        with self.assertRaises(TypeError):
            A = ck.KwargsHandler(kw_ek, foo = {})


        # check if assert works
        def FooTrue(x):
            return True
        def BarRaise(x):
            if not isinstance(x, int):
                raise OSError("test")
        
        kw_ek2 = {"foo": {"assert": FooTrue},
                  "bar": {"assert": BarRaise},
                 }
        # first check if nothing is wrong with input of kw_ek2
        A = ck.KwargsHandler(kw_ek2, )
        A = ck.KwargsHandler(kw_ek2, foo = {})
        with self.assertRaises(OSError):
            A = ck.KwargsHandler(kw_ek2, bar = {})

        # test if execute_kwargs updates available_kwargs
        kw_ek3_1 = {"barpapa":{}}
        kw_ek3_2 = {"barmama":{}}

        kw_ek3_totaal = copy.copy(kw_ek3_1)
        kw_ek3_totaal.update(kw_ek3_2)
        A = ck.KwargsHandler(kw_ek3_1, )
        A.execute_kwargs(available_kwargs = kw_ek3_2)
        self.assertEqual(A.available_kwargs,
                         kw_ek3_totaal)

        # test if execute_kwargs updates kwargs
        A = ck.KwargsHandler(kw_ek3_1, barpapa = 3)
        A.execute_kwargs(kw_ek3_2, barmama = 4)
        self.assertEqual(A.kwargs,
                         {"barpapa":3, "barmama":4}
                         )
                          

    def test_if_input_for_kwargs_is_preserved(self):
        kw_ = {"foo": {"default":1},
               "bar": {}}
        A = ck.KwargsHandler(kw_, bar = 3)
        # default values are not stored in _kwargs
        self.assertEqual(A._kwargs, {"bar":3})
        # but default values do get updated into kwargs
        self.assertEqual,A.kwargs,  {"bar":3, "foo":1}



    def test_execute_kwargs_the_hybridclass(self):
        # hybrid class acts as both a instance method and class method,
        # depending on how you call it
        # https://stackoverflow.com/questions/28237955/
        
        def foo(x):
            pass

        # check basic instance of methodclass
        kw_ektm0 = {"foomama": {"asserttype": int}}
        ck.KwargsHandler.execute_kwargs(kw_ektm0, )
        ck.KwargsHandler.execute_kwargs(kw_ektm0, foomama = 1)
        with self.assertRaises(TypeError):
            ck.KwargsHandler.execute_kwargs(kw_ektm0, foomama = "a")
                    
        kw_ektm1_1 = {"foopapa": {"asserttype": int,
                                  "func": foo,
                                  "assert": foo }}
        kw_ektm1_2 = {"foogran": {"asserttype": str}}
        A = ck.KwargsHandler(kw_ektm1_1)
        A.execute_kwargs(kw_ektm1_2, foopapa = 1,
                                     foogran = "g")
        
        

    def test_repr(self):
        kw_r = {"foo": {}}
        A = ck.KwargsHandler(kw_r, foo = {})
        repr(A)
        str(A)


    def test___eq__(self):
        kw_eq1 = {"foo": {},
                  "bar": {"default": 3} }
                  
        A1 = ck.KwargsHandler(kw_eq1)
        A2 = ck.KwargsHandler(kw_eq1)

        self.assertEqual(A1, A2)
        self.assertFalse(A1 is A2) # is checks for id(x), and not for __eq__

        A2.set_kwargs(foo = 1)
        self.assertFalse(A1 == A2)
        
        
    def test_available_kwargs_func(self):
        foocount_storage = []
        def FooCount(x):
            """ if executed, it can be tested"""
            foocount_storage.append(x)
            
        kw_f = {"foo": {"func": FooCount},
                 }
        # first check if nothing is wrong with input of kw_ek2
        A = ck.KwargsHandler(kw_f, )
        A = ck.KwargsHandler(kw_f, foo = {"baby":1})
        # test if FooCount has been performed
        self.assertEqual( foocount_storage, [{"baby":1}] )

    def test_available_kwargs_default(self):

        # check if it possible to set a default
        kw_akd0 = {"foo": {"default": 1}}
        A = ck.KwargsHandler(kw_akd0,)
        self.assertEqual(A.kwargs,
                         {"foo":1})
        # able to change it via execute_kwargs
        A.execute_kwargs(foo = 2)
        self.assertEqual(A.kwargs,
                         {"foo":2})
        # and via classmethod?
        D = ck.KwargsHandler.execute_kwargs(kw_akd0,)
        self.assertEqual(D,
                         {"foo":1})
        D = ck.KwargsHandler.execute_kwargs(kw_akd0, foo=2)
        self.assertEqual(D,
                         {"foo":2})

        # check if I give default of wrong asserttype, is will raise
        kw_akd1 = {"foo": {"default": 1,
                          "asserttype": str },
                   }
        
        with self.assertRaises(TypeError):
            A = ck.KwargsHandler(kw_akd1,)
            

    def test_code_in_docstring_about_hybrid_classes(self):
        av_kw = {"foo": {"default":1}} #dict(foo=dict(default=1))

        # docstring of KwargsHandler will be altered, so save the original
        original_docstring = ck.KwargsHandler.__doc__
        
        A1 = copy.copy(ck.KwargsHandler)(av_kw)
        A2 = copy.copy(ck.KwargsHandler)
        
        # docstring has already been altered; this is just to see if
        # they get the same output
        docstring1 = A1.set_docstring(
                           start_text = "The following kwargs can be used:\n\n")

        # this alters docstring of the class, not the instance.
        # setUp restores doc to original value every time
        docstring2 = ck.KwargsHandler.set_docstring(av_kw, A2,
                           start_text = "The following kwargs can be used:\n\n")

        self.assertEqual(docstring1, docstring2)
        self.assertEqual(A1.__doc__, A2.__doc__)

        self.assertNotEqual(A2.__doc__, original_docstring)
                                
    def test_multiple_passes_of_docstring(self):
        class Haz():
            """
            does something
            
            positional arguments:
            {positional_arguments}

            optional arguments:
            {optional_arguments}

            keyword arguments:
            {keyword *arguments}
            """
            pass

        kw_pos_arg = {"foo_pos": {},
                      "bar_pos": {},}

        kw_opt_arg = {"opt_arg": {},}

        kw_kw      = {"foo_kw": {},
                      "bar_kw": {}, }

        S1 = ck.KwargsHandler.set_docstring(kw_pos_arg, Haz,
                                            keytext = "positional_arguments")
        S2 = ck.KwargsHandler.set_docstring(kw_opt_arg, Haz,
                                            keytext = "optional_arguments")
        S3 = ck.KwargsHandler.set_docstring(kw_kw, Haz,
                                            keytext = "keyword *arguments")
        control_string =  "\n".join([
            "",
            "does something",
            "",
            "positional arguments:",
            "foo_pos:  docstring not defined, sorry.",
            "bar_pos:  docstring not defined, sorry.",
            "",
            "optional arguments:",
            "opt_arg:  docstring not defined, sorry.",
            "",
            "keyword arguments:",
            "foo_kw:  docstring not defined, sorry.",
            "bar_kw:  docstring not defined, sorry.",
            "",
                          ])
        self.assertEqual(Haz.__doc__,
                         control_string)

    def test_multiple_passes_of_docstring_nested(self):
        class Faz():
            """
            do your best Faz
            {first argument}
            {keywords for arg1}
            {arguments resumed}
            {some text}
            
            
            """
            pass
        
        kw_1 = {"bar" : {"doc":  "this is a dictionary. "
                                           "Each key in the dictionary has "
                                           "options, as stated below:"
                                           "",
                                   "default":{},
                                   "asserttype":dict}}
        kw_2 = {"foo" : {"doc": "does something else",
                         "asserttype": (list, tuple)},}

        kw_1rst_arg = {"bar_key1": {"doc": "This is the first option",
                                    "default": 1},
                       "bar_key2": {"doc": "second option",
                                    "asserttype": int,
                                    "default": -7, }
                       }
        
        
        
        S0 = ck.KwargsHandler.set_docstring(kw_1,  Faz, keytext="first argument",)
        S1 = ck.KwargsHandler.set_docstring(kw_1rst_arg, Faz,
                                            keytext="keywords for arg1",
                                            total_indent = 9
                                       )
        S2 = ck.KwargsHandler.set_docstring(kw_2,  Faz,
                                            keytext="arguments resumed",)
        S2 = ck.KwargsHandler.set_docstring({},  Faz,
                                            keytext="some text",
                                            start_text = "And this is the end."
                                            + 80*"+")

        # TODO finish

        



if __name__ == "__main__":

    unittest.main()

    

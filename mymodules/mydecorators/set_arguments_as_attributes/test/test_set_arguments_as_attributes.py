import doctest
import unittest
import inspect
import set_arguments_as_attributes as saaa



class Test_set_arguments_as_attributes_class(unittest.TestCase):
    
    def test_args(self):
        @saaa.set_arguments_as_attributes
        class MyClass:
            def __init__(self, a, b):
                self.init_executed = True
                return
        
        A = MyClass(1, 2)
        self.assertEqual(A.a, 1)
        self.assertEqual(A.b, 2)
        self.assertTrue(A.init_executed)
        return

    def test_args_that_are_also_keywords(self):
        @saaa.set_arguments_as_attributes
        class MyClass:
            def __init__(self, a="A", b="B"):
                self.init_executed = True
                return
        
        A = MyClass(1, 2)
        self.assertEqual(A.a, 1)
        self.assertEqual(A.b, 2)
        self.assertTrue(A.init_executed)

        A = MyClass()
        self.assertEqual(A.a, "A")
        self.assertEqual(A.b, "B")
        self.assertTrue(A.init_executed)
        return

    
    def test_args_that_are_also_keywords2(self):
        # little bit different
        @saaa.set_arguments_as_attributes
        class MyClass:
            def __init__(self, a, b="B"):
                self.init_executed = True
                return
        
        A = MyClass(1, 2)
        self.assertEqual(A.a, 1)
        self.assertEqual(A.b, 2)
        self.assertTrue(A.init_executed)

        A = MyClass(1)
        self.assertEqual(A.a, 1)
        self.assertEqual(A.b, "B")
        self.assertTrue(A.init_executed)
        return
    

    def test_varargs(self):
        @saaa.set_arguments_as_attributes
        class MyClass:
            def __init__(self, *only_vargargs):
                self.init_executed = True
                return
            
        A = MyClass(1, 22)
        self.assertEqual(A.only_vargargs, (1, 22)) 
        self.assertTrue(A.init_executed)

        B = MyClass("one arg")
        self.assertEqual(B.only_vargargs, ("one arg",) ) 
        self.assertTrue(B.init_executed) 

        C = MyClass(tuple(["tuple of args", "2nd element of tuple"]))
        self.assertEqual(C.only_vargargs, ((tuple(["tuple of args", "2nd element of tuple"])),) ) 
        self.assertTrue(C.init_executed)

        D = MyClass()
        self.assertEqual(D.only_vargargs, () ) 
        self.assertTrue(D.init_executed)
        return
    

    def test_args_and_varargs(self):
        @saaa.set_arguments_as_attributes
        class MyClass:
            def __init__(self, a, b, *more):
                self.init_executed = True
                return
            
        A = MyClass(1, 2, ("a", "b"))
        self.assertEqual(A.a, 1)
        self.assertEqual(A.b, 2)
        self.assertEqual(A.more, (("a", "b"),) )
        self.assertTrue(A.init_executed)

        B = MyClass(11, 2)
        self.assertEqual(B.a, 11)
        self.assertEqual(B.b, 2)
        self.assertTrue(hasattr(B, "more"))
        self.assertEqual(B.more, () )

        C = MyClass(1, 21, 23)
        self.assertEqual(C.more, (23,))

        D = MyClass( "[", "]", "{", "}")
        self.assertEqual(D.more, ("{", "}") )
        
        return

    
    def test_args_and_varargs2(self):
        # different number of arguments
        @saaa.set_arguments_as_attributes
        class MyClass:
            def __init__(self, a, *more):
                self.init_executed = True
                return
            
        A = MyClass(1, ("aa", "b"))
        self.assertEqual(A.a, 1)
        self.assertEqual(A.more, (("aa", "b"),) ) 
        self.assertTrue(A.init_executed)

        B = MyClass(1, ("aa", "b"), "cc")
        self.assertEqual(B.a, 1)
        self.assertEqual(B.more, (("aa", "b"), "cc"))
        self.assertTrue(B.init_executed)
        return

    def test_args_and_varargs3(self):
        # with 
        @saaa.set_arguments_as_attributes
        class MyClass:
            def __init__(self, a, b="default value", *more):
                self.init_executed = True
                return
            
        A = MyClass(12, 13)
        self.assertEqual(A.a, 12)
        self.assertEqual(A.b, 13)
        self.assertEqual(A.more, ())

        B = MyClass(23, 34, "z")
        self.assertEqual(B.a, 23)
        self.assertEqual(B.b, 34)
        self.assertEqual(B.more, ("z",))

            
        C = MyClass("A1", "B1", "zz", "zzz")
        self.assertEqual(C.a, "A1")
        self.assertEqual(C.b, "B1")
        self.assertEqual(C.more, ("zz", "zzz"))

        D = MyClass("A11", )
        self.assertEqual(D.a, "A11")
        self.assertEqual(D.b, "default value")
        self.assertEqual(D.more, ())        
        return

    

    def test_kwargs(self):
        # b is keyworld-only 
        @saaa.set_arguments_as_attributes
        class MyClass:
            def __init__(self, a, *more, b=3):
                self.init_executed = True
                return
            
        A = MyClass(1, b=3)
        self.assertEqual(A.a, 1)
        self.assertEqual(A.b, 3)
        self.assertTrue(A.init_executed)
        return

    def test_kwargs2(self):
        # bit different, use of **kwargs
        @saaa.set_arguments_as_attributes
        class MyClass:
            def __init__(self, a, *more, **kwargs):
                self.init_executed = True
                return
            
        A = MyClass(1, b=3)
        self.assertEqual(A.a, 1)
        self.assertEqual(A.b, 3)
        self.assertTrue(A.init_executed)
        return

    def test_kwargs3(self):
        # bit different, use of kwargs with default and **kwargs
        @saaa.set_arguments_as_attributes
        class MyClass:
            def __init__(self, a, *more, b=3, **kwargs):
                self.init_executed = True
                return
            
        A = MyClass(1, b=3)
        self.assertEqual(A.a, 1)
        self.assertEqual(A.b, 3)
        self.assertTrue(A.init_executed)

        B = MyClass(1, 2, 4, 5, 6)
        self.assertEqual(B.a, 1)
        self.assertEqual(B.b, 3)
        self.assertEqual(B.more, (2, 4, 5, 6) )

        C = MyClass(1, 2, 4, 5, 6, b = 6, c = 7)
        self.assertEqual(C.a, 1)
        self.assertEqual(C.b, 6)
        self.assertEqual(C.c, 7)
        self.assertEqual(C.more, (2, 4, 5, 6) )
        return
    

    
    def test_when_init_is_not_user_defined(self):
        # pretty useless test, but can't hurt
        @saaa.set_arguments_as_attributes
        class MyClass:
            pass
        Z = MyClass()


    def test_decorating_twice(self):
        # it shouldn't happen that both the class and it's __init__
        # are decorated, but lets check what happens
        @saaa.set_arguments_as_attributes
        class MyClass:
            @saaa.set_arguments_as_attributes
            def __init__(self, a, b):
                pass
            
        A = MyClass(1, 2)
        self.assertEqual(A.a, 1)
        # just testing if not more keys got passed into A
        # as a result of double decorating
        self.assertTrue(list(A.__dict__.keys()), ["a", "b"] )

        # this is fine, it is not double decorating.
        # because decorating the class only decorates __init__
        @saaa.set_arguments_as_attributes
        class MyClass:
            def __init__(self, a, b):
                pass
            @saaa.set_arguments_as_attributes
            def foo(self, a, b):
                pass

    def test_decorating_class_methods(self):

        class MyClass:
            @classmethod
            @saaa.set_arguments_as_attributes
            def foo(cls, a, b):
                pass
        MyClass.foo(4, 5)
        self.assertEqual(MyClass.a, 4)


        with self.assertRaises(Exception):
            # well, this gives an error
            class MyClass:
                @saaa.set_arguments_as_attributes
                @classmethod # wrong way around, apparently
                def foo(cls, a, b):
                    pass
            MyClass.foo(6, 7)


    def test_overwrite_protection(self):
        # arguments names that look like dunders cannot be written
        @saaa.set_arguments_as_attributes
        class MyClass:
            def __init__(self, __eq__):
                self.init_executed = True
                return
        with self.assertRaises(saaa.ParameterError):
            A = MyClass(1)
        return

    def test_overwriting(self):
        # test if values are overwritten
        @saaa.set_arguments_as_attributes
        class MyClass:
            a = "c"
            def __init__(self, a):
                self.init_executed = True
                return
            
        A = MyClass(1,)
        self.assertEqual(A.a, 1)
        self.assertTrue(A.init_executed)
        return 

    def test_overwriting_keyword(self):
        # test if values are overwritten
        @saaa.set_arguments_as_attributes
        class MyClass:
            a = "c"
            def __init__(self, b, **kwargs):
                self.init_executed = True
                return
            
        A = MyClass(1, **{"a": 1})
        self.assertEqual(A.a, 1)
        self.assertTrue(A.init_executed)
        return

    def test_annotations(self):
        # dunno if they are preserved. But they should'nt cause trouble
        @saaa.set_arguments_as_attributes
        class MyClass:
            a = "c"
            def __init__(self, a:str, b: int,):
                self.init_executed = True
                return
            
        A = MyClass("c", 3)
        self.assertEqual(A.a, "c")
        self.assertTrue(A.init_executed)

        return



class Test_set_arguments_as_attributes_method(unittest.TestCase):
    
    def test_args(self):
        class MyClass:
            @saaa.set_arguments_as_attributes
            def foo(self, a: int, b: int):
                self.init_executed = True

        
        A = MyClass()
        A.foo(1, 2)
        self.assertEqual(A.a, 1)
        self.assertEqual(A.b, 2)
        self.assertTrue(A.init_executed)



        return

    
    




# because I like to include example code in the docstring, it's best to
# go ahead and test that sample code. (It would suck if such an example code
# had any errors in it.) The code below runs doctest as a unittest
# https://realpython.com/python-doctest/#running-doctest-tests-with-unittest-and-pytest
# https://stackoverflow.com/questions/5681330/using-doctests-from-within-unittests
def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(saaa))
    return tests
    
if __name__ == "__main__":    
    unittest.main()




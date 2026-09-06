import doctest
import unittest
import total_ordering_by_key as tobk


def sorting_key(self):
    return [self.a, self.b]


class MyClass:
    def __init__(self,a,b):
        self.a = a
        self.b = b
        return
    

class Test_total_ordering_by_key(unittest.TestCase):
    
    def test(self):
        # test basic functionality
        @tobk.total_ordering_by_key(key = sorting_key)
        class MyClass1(MyClass):
            pass
        
        Foo = MyClass1(1,2)
        Bar = MyClass1(2,3)
        
        self.assertTrue(Foo < Bar)
        self.assertTrue(Foo <= Bar)
        self.assertFalse(Foo == Bar)
        self.assertFalse(Foo > Bar)
        self.assertFalse(Foo >= Bar)

        Foo2 = MyClass1(3,2)
        Bar2 = MyClass1(2,3)
        
        self.assertFalse(Foo2 < Bar2)
        self.assertFalse(Foo2 <= Bar2)
        self.assertFalse(Foo2 == Bar2)
        self.assertTrue(Foo2 > Bar2)
        self.assertTrue(Foo2 >= Bar2)

        Foo3 = MyClass1("a","b")
        Bar3 = MyClass1("c","d")

        self.assertTrue(Foo3 < Bar3)
        self.assertTrue(Foo3 <= Bar3)
        self.assertFalse(Foo3 == Bar3)
        self.assertFalse(Foo3 > Bar3)
        self.assertFalse(Foo3 >= Bar3)
        return


    def test_original_comparions_are_not_overwritten(self):
        @tobk.total_ordering_by_key(key = sorting_key)
        class MyClass2(MyClass):
            def __eq__(self, other):
                self.check = "checking"
                other.check = "checking"
                # for testing purposes
                return True
            
        Foo = MyClass2(1,2)
        Bar = MyClass2(2,3)

        self.assertFalse(hasattr(Foo, "check"))
        # normally, Foo == Bar should be False. However, if __eq__ is overwritten
        # by the new __eq__, this becomes True
        self.assertTrue(Foo == Bar)
        # if __eq__ was indeed performed, attribute check should be set
        self.assertTrue(hasattr(Foo, "check"))         

        # let's test the others because we can
        self.assertTrue(Foo < Bar)
        self.assertTrue(Foo <= Bar)
        self.assertFalse(Foo > Bar)
        self.assertFalse(Foo >= Bar)
        return
    
##    def test_unsual_comparisons(self):
##        @tobk.total_ordering_by_key(key = sorting_key)
##        class MyClass3(MyClass):
##            pass
##            
##        Foo = MyClass3(1,2)
##        Bar = MyClass3(2,3)
##
##        delattr(Bar, "a")
##        Foo == Bar
##        return

        
    def test_change_in_sorting_key(self):
        # might be a bug somewhere; I'm always using the same key
        # so don't know if it is cached somewhere, and replaced
        @tobk.total_ordering_by_key(key = lambda x: [-x.a, -x.b])
        class MyClass4(MyClass):
            pass
            
        Foo = MyClass4(1,2)
        Bar = MyClass4(2,3)

        self.assertFalse(Foo < Bar)
        self.assertFalse(Foo <= Bar)
        self.assertFalse(Foo == Bar)
        self.assertTrue(Foo > Bar)
        self.assertTrue(Foo >= Bar)
        return

    def test_excluding_some_dunders(self):
        @tobk.total_ordering_by_key(key = sorting_key,
                                    include = ["__lt__", "__gt__"],
                                    )
        class MyClass5(MyClass):
            pass
            
        Foo = MyClass5(1,2)
        Bar = MyClass5(2,3)

        # >= is not implemented
        with self.assertRaises(TypeError):
            Foo >= Bar
    # this should be implemented
        self.assertFalse(Foo > Bar)

    def test_direct_calling_total_ordering_by_key_functions(self):
        # instead of decorating, total_ordering_by_key_functions
        # can be called to create the dunder methods yourself
        # and maybe embellisching them with do_something
        class MyClass6(MyClass):
            def __lt__(self, other):
                # example that other thing can be done/checked
                def do_something(): pass 
                funcs = tobk.total_ordering_by_key_functions(sorting_key)
                return funcs["__lt__"](self, other)

        Foo = MyClass6(1,2)
        Bar = MyClass6(2,3)

        self.assertTrue( Foo < Bar)

        

    def test_calling_decorator_after_class_initiation(self):
        # this ensures the 
        class MyClass7(MyClass):
            def sorting_key(self):
                return [self.a, self.b]
        tobk.total_ordering_by_key(key = MyClass7.sorting_key)(MyClass7)
        
        Foo = MyClass7(1,2)
        Bar = MyClass7(2,3)

        self.assertTrue(Foo < Bar)

        # this ensures the method can be dynamic(?)
        class MyClass8(MyClass):
            def sorting_key(self):
                return list(self.__dict__.values())
        tobk.total_ordering_by_key(key = MyClass8.sorting_key)(MyClass8)
        
        Foo = MyClass8(1,2)
        Bar = MyClass8(2,3)

        self.assertTrue(Foo < Bar)



    def test_total_ordering_by_key_with_method(self):
        @tobk.total_ordering_by_key(method_name = "sorting_key")
        class MyClass9(MyClass):
            def sorting_key(self):
                return [self.a, self.b]

        Foo = MyClass9(1,2)
        Bar = MyClass9(2,3)

        self.assertTrue(Foo < Bar)

    def test_cases_with_semi_hidden_use_of_eq(self):
        @tobk.total_ordering_by_key(key = sorting_key)
        class MyClass10(MyClass):
            pass
        
        Foo = MyClass10(1,2)
        Bar = MyClass10(2,3)

        A = [1, 2, 3, Foo]
        B = [1, 2, 3, 4]

        # the code \a in b\ uses eq to test it
        self.assertFalse("a" in A)
        self.assertTrue(Foo in A)
        self.assertFalse(Foo in B)
        

    def test_ne(self):
        @tobk.total_ordering_by_key(key = sorting_key)
        class MyClass11(MyClass):
            pass

        @tobk.total_ordering_by_key(key = sorting_key)
        class MyClass12(MyClass):
            pass
        
        Foo = MyClass11(1,2)
        Bar = MyClass11(2,3)
        FooBar = MyClass12(3,3)

        # basically test if any errors arise
        self.assertTrue(Foo != Bar)
        self.assertTrue(Foo != 1)
        self.assertTrue(Foo != FooBar)
        return
    

    def test_invalid_input(self):
        # cannot have both keywords
        with self.assertRaises(TypeError):
            @tobk.total_ordering_by_key(key = sorting_key,
                                        method_name = "sorting_key")
            class MyClass14(MyClass):
                def sorting_key(self):
                    return [self.a, self.b]

    def test_invalid_input2(self):
        # include is invalid
        with self.assertRaises(ValueError):
            @tobk.total_ordering_by_key(key = sorting_key,
                                        include = ["blad"])
            class MyClass15(MyClass):
                def sorting_key(self):
                    return [self.a, self.b]
        
    def test_invalid_input3(self):
        # at least 1 keyword for tobk
        with self.assertRaises(TypeError):
            @tobk.total_ordering_by_key()
            class MyClass16(MyClass):
                def sorting_key(self):
                    return [self.a, self.b]

    def test_equivalance_argument_key_for_sorted(self):
        # sorting_key should work as key for both tobk
        # and sorted(key=sorted_key)
        @tobk.total_ordering_by_key(key = sorting_key)
        class MyClass17(MyClass):
            pass

        A = [
            MyClass17(1, 2),
            MyClass17(2, 3),
            MyClass17(-1, 3),
            MyClass17(1,-1),
             ]

        B = A.copy()
        self.assertEqual(A, B)
        A.sort()
        self.assertFalse(A == B)
        B.sort(key = sorting_key)
        self.assertEqual(A, B)
        

# because I like to include example code in the docstring, it's best to
# go ahead and test it. The code below runs doctest as a unittest
# https://realpython.com/python-doctest/#running-doctest-tests-with-unittest-and-pytest
# https://stackoverflow.com/questions/5681330/using-doctests-from-within-unittests
def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(tobk))
    return tests
    
if __name__ == "__main__":    
    unittest.main()




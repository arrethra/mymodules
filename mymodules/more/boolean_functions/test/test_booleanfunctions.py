import copy
import doctest
import unittest

import boolean_functions.booleanfunctions as bf

def isTrue(*x):
    return True

def isFalse(*x):
    return False

def isInput(b):
    return b

def isNotInput(b):
    return not b

# I am using self.assertIs(A(), True) to test when A is called,
# it will produce True. I could use self.assertTrue, but it only
# tests truthiness. Therefor assertTrue(C) will succeed, as the
# class C is 'truthy', while we might have wanted to test C()
# instead of C, resulting in a hidden error in the unittest
 
class Test_BooleanFunction(unittest.TestCase):
    def test_call(self):

        self.assertIs(bf.BoolFunc(isTrue)(), True)
        self.assertIs(bf.BoolFunc(isFalse)(), False)
        
        self.assertIs(bf.BoolFunc(isInput)(True), True)
        self.assertIs(bf.BoolFunc(isInput)(False), False)


    def test_and(self):
        T = bf.BoolFunc(isTrue)
        F = bf.BoolFunc(isFalse)
        C1 = T & F
        self.assertIs(C1(), False)
        C2 = T & T
        self.assertNotEqual(repr(T), repr(C2))
        self.assertEqual(repr(T), repr(copy.copy(T)))
        # this last test is to see if the test before that
        # was meaningfull. if (for example) a location is added in the repr,
        # repr(T) would always mismatch repr(C2)

        # with input
        A = bf.BoolFunc(isInput)
        B = bf.BoolFunc(isNotInput)

        C = A&A
        self.assertIs(C(True), True)
        self.assertIs(C(False), False)

        C2 = A&B
        self.assertIs(C2(True), False)
        self.assertIs(C2(False), False)

    def test_or(self):
        T = bf.BoolFunc(isTrue)
        F = bf.BoolFunc(isFalse)

        C = T|T
        self.assertIs(C(), True)

        C2 = T|F
        self.assertIs(C2(), True)

        C3 = F|F
        self.assertIs(C3(), False)

    def test_nested(self):
        T = bf.BoolFunc(isTrue)
        F = bf.BoolFunc(isFalse)
        
        A = bf.BoolFunc(isInput)
        B = bf.BoolFunc(isNotInput)
        
        C = (A|B)&(T|F)

        self.assertIs(C(True), True)
        self.assertIs(C(False), True) # B will return True

        C2 = (A|B)&(F|F)
        self.assertIs(C2(True), False)
        
        
        C3 = ((A|B|A)&(T&T)&A)
        self.assertIs(C3(False), False)
        self.assertIs(C3(True), True)

    def test_concatenate(self):
        T = bf.BoolFunc(isTrue)
        with self.assertRaises(TypeError):
            T | 1


    def test_neg(self):
        T = bf.BoolFunc(isTrue)
        F = bf.BoolFunc(isFalse)
        
        C = T&~F
        self.assertIs(C(), True)
        self.assertIs((~C)(), False)

        C2 = T | ~F

    def test_invert(self):
        T = bf.BoolFunc(isTrue)
        F = bf.BoolFunc(isFalse)
        
        
        
        C = T&~F
        self.assertIs(C(), True)
        self.assertIs((~C)(), False)

    def test_xor(self):
        T = bf.BoolFunc(isTrue)
        F = bf.BoolFunc(isFalse)

        self.assertIs((T^T)(), False)
        self.assertIs((T^F)(), True)
        self.assertIs((F^T)(), True)
        self.assertIs((F^F)(), False)

        
    def test_decorator(self):
        @bf.BoolFunc
        def foo(a):
            return a

        @bf.BoolFunc
        def bar(a):
            return a

        F1 = foo | bar
        self.assertEqual(F1(True), True)

        F2 = foo & bar
        self.assertEqual(F2(True), True)

    def test_non_bool_returns(self):
        # up till now, all BoolFunc's outputted a bool. but what if
        # they return something else, how will the ( | ) and ( & ) hold up?
        @bf.BoolFunc
        def A(a):
            return a

        @bf.BoolFunc
        def N(n):
            return not n
        
        F = A | N
        self.assertEqual(F("b"), True)
        self.assertEqual(F({}), True)

        F = A & N
        self.assertIs(F("b"), False)
        self.assertIs(F({}), False)

        F = (~A) & N
        self.assertIs(F("b"), False)
        self.assertIs(F({}), True)

    def test__erro_handling(self):
        @bf.BoolFunc
        def foo():
            return True
        
        @bf.BoolFunc
        def bar(a):
            return bool(a)

        F = foo | bar
        with self.assertRaises(TypeError):
            F("b")

    def test_repr(self):
        lm = lambda *x: True
        L = bf.BoolFunc(lm)
        
        @bf.BoolFunc
        def Fls(*a):
            z = 3
            return False

        repr(L | Fls)  # not sure if tested propperly....
##        print
##        print(repr(L|Fls|L))

    def test_inheritance(self):
        class C(bf.BoolFunc):
            z = 3

        @C
        def T():
            return True

        @C
        def F():
            return False

        new_cls = (T | F )
        self.assertTrue(isinstance(new_cls, C), msg=f"{type(new_cls)}")
        self.assertIs(new_cls(), True)
        

        

        
        

def run_doctest(module):
    doctest.testmod(module, optionflags=doctest.FAIL_FAST) #
    module_name = str(module).split()[1]
    print(f"ran doctest on module={module_name}")

if __name__ == "__main__":
    run_doctest(bf)
    unittest.main()

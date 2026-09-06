import unittest
import doctest

import naturalstringsort.natural_string_sort as nss
from naturalstringsort.natural_string_sort import natural_string_sort, _SupportSort


class TestNaturalStringSort(unittest.TestCase):
    def test_natural_string_sort(self):
        A = ["",
             "5sometext",
             "123sometext",
             "_dfg12",
             "_Ffg12",
             "a",
             "sometext2bla",
             "sometext10bla",
             ]

        S = reversed(A)
        L = natural_string_sort(S)

        self.assertEqual(L, A)


class Test_SupportSort(unittest.TestCase):
    def test_repr(self):
        # __repr__
        A = _SupportSort("a")
        z = repr(A)
        self.assertEqual(z, "<_SupportSort('a')>")

    def test_comparisons(self):
        # test the __lt__ and __eq__
        # not tested exhaustively all the cases
        A = _SupportSort("a")
        A2 = _SupportSort("a")
        B = _SupportSort("b")
        C1 = _SupportSort("2")
        C2 = _SupportSort("10")

        self.assertTrue(A < B)
        self.assertFalse(A == B)
        self.assertTrue(A == A2)

        
def run_doctest(module):
    doctest.testmod(module, optionflags=doctest.FAIL_FAST) #
    module_name = str(module).split()[1]
    print(f"ran doctest on module={module_name}")

if __name__ == "__main__":
    run_doctest(nss)
    unittest.main()


    

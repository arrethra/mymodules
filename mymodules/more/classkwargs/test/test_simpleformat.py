import unittest
from classkwargs.simpleformat import simpleformat 


class Test_simpleformat(unittest.TestCase):
    
    def test_simpleformat_kwargs(self):
        strng_simple = "Give my best to {person}."
        S = simpleformat( strng_simple, person = "Roger")
        self.assertEqual(S, "Give my best to Roger.")

        # example_from_docstring
        strng = "A = {'age' = {value},}"
        S = simpleformat( strng, value = 17)
        S_control =  "A = {'age' = 17,}"
        self.assertEqual(S, S_control)

        with self.assertRaises(KeyError):
            S2 = simpleformat(strng, wrong_keyword = 17)
        

    def test_simpleformat_args(self):
        # test automatic numbering
        strng = "bla {}"
        S = simpleformat( strng, 4)
        self.assertEqual(S, "bla 4")

        strng = "bla {} {}"
        S = simpleformat( strng, 5, 6)
        self.assertEqual(S, "bla 5 6")

        # test manual numbering
        strng = "bla {0}"
        S = simpleformat( strng, 7)
        self.assertEqual(S, "bla 7")

        strng = "gah {0} {1}"
        S = simpleformat( strng, 8, 9)
        self.assertEqual(S, "gah 8 9")

        # test: cannot switch from automatic field 
        #       numbering to manual field specification
        strng = "dah {} {0}"
        with self.assertRaises(ValueError):
            S = simpleformat( strng, 10, 11)

        strng = "bah {0} {}"
        with self.assertRaises(ValueError):
            S = simpleformat( strng, 12, 13)

        # test too many arguments
        strng = "mah {} {}"
        with self.assertRaises(TypeError):
            S = simpleformat(strng, "A", "B", "C")
        
        strng = "lah {0} {1}"
        with self.assertRaises(TypeError):
            S = simpleformat(strng, "D", "E", "F")

        strng = "pah {0} {2}"
        with self.assertRaises(TypeError):
            S = simpleformat(strng, "G", "H", "I")
 
        
    def test_simpleformat_with_both_args_and_kwargs(self):
        strng     = "{name} is {} years old"
        S_control =  "Steve is 18 years old"
        S = simpleformat(strng, 18, name = "Steve")
        self.assertEqual(S, S_control)

        strng = "{subject} is {0} years old"
        S_control   = "Carl is 19 years old"
        S = simpleformat(strng, 19, subject = "Carl")
        self.assertEqual(S, S_control)

        # test that it leaves the {} unaltered
        strng = "{} {id}"
        S_control = "{} 123"
        S = simpleformat(strng, id = 123)
        self.assertEqual(S, S_control)

        # test that you can have a doubled up {{ in there
        # and/or unbalanced without its counterpart }
        strng = "{{password}"
        S_control = "{2580"
        S = simpleformat(strng, password = 2580)
        self.assertEqual(S, S_control)

        strng = "{ {_pass}"
        S_control = "{ pswrd"
        S = simpleformat(strng, _pass = "pswrd")
        self.assertEqual(S, S_control)

        strng = "{tree} }"
        S_control = "oak }"
        S = simpleformat(strng, tree = "oak")
        self.assertEqual(S, S_control)


    def test_simpleformat_z_keywords_wrong_format(self):
        # keyword cant_start_with_digit
        strng = "{1rst building} is on {street}"
        kw = {"1rst building": "HQ",
              "street": "main street"}
        with self.assertRaises(KeyError):
            S = simpleformat(strng, **kw)

        # keyword cant be empty string
        strng = "{} "
        kw = {"": "flat"}
        with self.assertRaises(KeyError):
            S = simpleformat(strng, **kw)
            
    


if __name__ == "__main__":
    unittest.main()

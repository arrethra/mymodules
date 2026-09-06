import unittest
import typing
from classkwargs import myerrors


errormessage_for_comparing_lines = (
    "the strings should be equal but are not. The string are actual output "
    "vs control-string, types on different lines"
                                   )

class Test_myerrors(unittest.TestCase):
    
    def test_extract_class_strings(self):
        self.assertEqual( myerrors.extract_class_strings(str),
                         "'str'",      )
        
        self.assertEqual(myerrors.extract_class_strings((str,int)) ,
                         "'str', 'int'" , )

    def test_extract_class_strings_with_union(self):
        A = typing.Union[int,str,list,tuple]
        self.assertEqual( myerrors.extract_class_strings( A),
                          "'int', 'str', 'list', 'tuple'" )
        


    def test_TypeErrorWithMessage(self):
    
        E = myerrors.TypeErrorWithMessage("blaat",(bool,int),"doh")

        control_string = ("For argument 'blaat', the type must be 'bool', 'int',"
                      " but found 'str' with value 'doh'.")
        self.assertEqual( E.args[0],
                          control_string, )
        


    def test_ValueErrorWithMessage1(self):
    
        E = myerrors.ValueErrorWithMessage("blaat",-9,"positive")

        
        control_string = ( "The argument 'blaat' has a value of -9, but the value "
                           "doesn't satisfy the folowing condition: positive." )
        
        self.assertEqual( E.args[0],
                          control_string, )

    def test_ValueErrorWithMessage2(self):
        class Foo():
            def __init__(self,value):
                self.value = value
            def __gt__(self,other):
                return self.value > other.value
            def __eq__(self,other):
                if not instance(self, type(other)) or isinstance(other, type(self)):
                    return False
                else:
                    return self.value == other.value
            def __str__(self):
                return "Foo({})".format(self.value)
            def __repr__(self):
                return "Foo({})".format(repr(self.value))        
    
        E = myerrors.ValueErrorWithMessage("blaat",Foo('1'), "greater than Foo('0')")

        control_string = ( "The argument 'blaat' has a value of Foo('1'), but the "
                           "value doesn't satisfy the folowing condition: greater "
                           "than Foo('0')." )
        self.assertEqual( E.args[0],
                          control_string, )








if __name__ == "__main__":
    unittest.main()

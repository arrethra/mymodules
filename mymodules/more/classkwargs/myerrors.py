import typing
                   
def TypeErrorWithMessage(argument_name,
                      forced_types,
                      argument_value,):
    """
    This class aims to make it easier to create error messages with clear text,
    without the need to type the text everytime itself.
    """

    argument_value_type = type(argument_value)
    argument_value_type = extract_class_strings(argument_value_type)

    forced_types = extract_class_strings(forced_types)
    
    if not isinstance(argument_name,str):
        _e = (f"For class TypeErrorWithMessage, argument_name must be "
              f"a string but found type {argument_value_type} with value "
              "{agument_name}."
            )
        raise TypeError(_e) # irony, but hopefully you'll learn

    _base_string_for_errormsg = (
          "For argument '{argument_name}', the type must be {forced_types}, "
          "but found {argument_value_type} with value {argument_value}."
                                      )
    _e = _base_string_for_errormsg.format(argument_name = argument_name,
                                               forced_types = forced_types,
                                               argument_value_type =
                                                        argument_value_type,
                                               argument_value =
                                                        repr(argument_value),
                                               )
    return TypeError(_e)


def ValueErrorWithMessage(argument_name,
                       argument_value,
                       argument_condition,):
    """
    This class aims to make it easier to create error messages with clear
    text, without the need to type the text everytime itself.
    Note that the argument "argument condition" must be string that
    explains the conditions the value must satisfy.
    """
    if not isinstance(argument_name,str):
        argument_value_type = type(argument_value)
        argument_value_type = extract_class_strings(argument_value_type)
        _e = ( "For class ValueErrorWithMessage, the first argument must be "
              f"a string but found {argument_value_type}."
            )
        raise TypeError(_e) # irony, but hopefully you'll learn


    _base_string_for_errormsg = (
              "The argument '{argument_name}' has a value of {argument_value}, "
              "but the value doesn't satisfy the folowing condition: "
              "{argument_condition}."
                                        )
    _e = _base_string_for_errormsg.format(
                                argument_name = argument_name,
                                argument_value = repr(argument_value),
                                argument_condition = argument_condition,
                                               )
    return ValueError(_e)
        



def extract_class_strings(types):
    """
    When you perform str(str), the result <class 'str'> isn't very
    attractive. This function extracts the class and returns 'str'.
    Argument can be a single type, or an iterable of types.
    """

    try:
        iter(types)
    except TypeError:
        T = (types,)
    else:
        T = types

    pattern_type = ("<class", ">")
    
    pattern_union = ("typing.Union[","]")

        
    output = ""
    for t in T:            
        s = str(t)

        for pattern in [pattern_type,
                        pattern_union]:
            sw, ew = pattern
            if s.startswith(sw) and s.endswith(ew):
                s = s[len(sw):-len(ew)]
                if pattern == pattern_union:
                    # they are without quotation marks
                    s = s.split(", ")
                    s = "', '".join(s)
                    s = f"'{s}'"
        
        output = ",".join([output,s])
        
    return output[1:].strip()



if __name__ == "__main__":
    
    pass

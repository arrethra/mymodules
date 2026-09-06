# TODO add type annotations

def simpleformat(text: str, *args, **kwargs) -> str:
    """
    This function aims to mimic the most basic function of str.format.
    However, where str.format doesn't really allow curly brackets in
    the main text (apart from the replacement fields), this function
    doesn't care about extra curly brackets, nor do they have to
    doubled up.
    Raises a KeyError if a keyword or optional argument has been entered,
    but not been found in the text (this differs from str.format)

    The text on which this function is called can contain literal text or
    replacement fields delimited by braces {}. Each replacement field
    contains either the numeric index of a positional argument, or the
    name of a keyword argument. Returns a copy of the string where each
    replacement field is replaced with the string value of the
    corresponding argument.
    (copied and modified from
     https://docs.python.org/3.13/library/stdtypes.html#str.format )
    
    Example:
    simpleformat can handle the following example,
    where as str.format would raise an error.

    >>> strng = "A = {'age' = {value},}"
    >>> simpleformat( strng, value = 17)
    "A = {'age = 17,}"              

    this can be helpfull for docstring that contains examples with dicts,
    but also contains replacement fields. str.format would likely error
    on the curly brackets of the dicts.
    """
    if not isinstance(text, str):
        E = TypeError("For text expcted str, but got {} with value {}."
                      "".format(type(text), repr(text)))
        raise E

    for kw in kwargs:
        if kw == "":
            _e = ("keyword cannot be empty string, to avoid confusement"
                  "with automatic fields (i.e. {} )")
            raise KeyError(_e)
        if kw[0].isdigit():
            _e = ("keyword {} started with a digit, but "
                  "keywords cannot start with digits, to avoid "
                  "confusement with manual fields (i.e. {{0}}, etc)."
                  "".format( repr(kw) ))
            raise KeyError(_e)
        kw_br = "{" + kw + "}"
        if kw_br in text:
            text = text.replace(kw_br, str(kwargs[kw]))
        else:
            # this differs from str.format, AFAIK, as str.format doesn't raise
            # an error if a keyword hasn't been found in the text
            _e = ("for kwargs, key '{}' could not be found "
                   "in text. Note keyword has to be in curly brackets"
                  "".format(kw) )
            raise KeyError( _e )
        
    manual_field_count, automatic_field_count = 0, 0 
    for i, arg in enumerate(args):
        rf_i = "{" + str(i) + "}"

        if rf_i in text:
            text = text.replace(rf_i, str(arg), 1)
            manual_field_count += 1
        elif "{}" in text:
            text = text.replace("{}", str(arg), 1)
            automatic_field_count += 1               
        else:
            # this differs from str.format, AFAIK, as str.format doesn't raise
            # an error if an argument too many has been found
            if manual_field_count:
                rf_looks_like = rf_i
            else:
                rf_looks_like = "{}"
            _e = ("for optional argument number {}, no associating "
                  "curly brackets could be found that looked like {}."
                   "".format(i+1, rf_looks_like ) )
            raise TypeError( _e )
        
        if all([manual_field_count,
                automatic_field_count]):
            _e = ("cannot switch between manual fields numbering "
                   "(such as {0} ) and  automatic fields (that are {} ).")
            raise ValueError(_e )
        
    return text


if __name__ == "__main__":
    
    pass
##    help(simpleformat)

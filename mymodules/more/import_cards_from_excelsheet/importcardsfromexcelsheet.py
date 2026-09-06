import os, inspect
import os.path as osp
import dataclasses
import pandas # pip install pandas, and all dependacies as more errors occur


# supposedly failsafe method across mulptiple platforms to find folder,
# according to some user on stackexchange
currentpath = _current_folder = os.path.realpath(os.path.abspath(
                  os.path.split(inspect.getfile( inspect.currentframe() ))[0])) 
                                          
file = osp.join(currentpath,"AE_all_cards_(Core-New_Age)_which_effects.xlsx")
file = osp.join( "for_testing.ods")


@dataclasses.dataclass
class Defaults:
    # a list is a mutuable object. when using a list as default value
    # for a function, the same object is shared between all calls of
    # that function
    # https://docs.python.org/3/faq/programming.html#why-are-default-values-shared-between-objects
    # https://docs.python.org/3.13/library/dataclasses.html#mutable-default-values
    use_columns: list = dataclasses.field(default_factory=list)




class LoadSheet():
    """
    Load a sheet and turn the rows into dictionaries in attribute
    array_dict. Keys of each dictionary are taken from the top row.
    Supports `xls`, `xlsx`, `xlsm`, `xlsb`, `odf`, `ods` and `odt`
    file extensions. See help(pandas.read_excel) for more info.

    file: must be path to a file
    use_columns:  limit to these columns only. starts count at column 0
                  (i.e. the most left column) 
                  Default value ([]) ensures that all columns are used
    check_validity: Boolean. Does a few basic checks on the validity
                   of the data. May print data that requires manual
                   checking. (TODO: automate checking)

    Example:
    input_sheet:
    Name   Cost   Type
    Peter  7      card
    Paula  3      dice
    
    output at LoadSheet(input_sheet).array_dict
    [
    {'Name':'Peter', 'Cost':7, 'Type':'card'},
    {'Name':'Paula', 'Cost':3, 'Type':'dice'},
    ]
    """
    def __init__(self, file,
                 use_columns = Defaults().use_columns,
                 check_validity = False):

##        self.file=file
##        self.use_columns=use_columns
##        self.check_validity=check_validity
        
        self.load_file(file, use_columns)
        self.sort_sheet_into_dictionary()
        if check_validity:
            self.assert_validity()


    def load_file(self,file,
                  use_columns = Defaults().use_columns):
        """Loads excel file and stores it in self.result_file """
        if not osp.isfile(file):
            raise OSError(f"File does not exist: {file}")
        
        kwargs = {}
        if use_columns:
            kwargs["usecols"] = use_columns
        self.result_file = pandas.read_excel(file,
                                             header = None,
                                             **kwargs).transpose()
        return self.result_file


    def sort_sheet_into_dictionary(self):
        # sort sheet into list, with each card as a dictionary
        self.array_dict = []
        self.card_keys = list(self.result_file[0])
        
        for i,column in enumerate(self.result_file):
            if i > 0:
                card = {}
                for j, value in enumerate(self.result_file[column]):
                    if isinstance(value, str):
                        value = value.strip() # remove leading and trailing spaces 
                    card[self.card_keys[j]] = value
                self.array_dict.append(card)
        return self.array_dict


    def assert_validity(self):
        # TODO: check if all keys are formatted as expected
        
        # for manual check (TODO: automate)
        # check if there haven't been typo's in the sheet
        # TODO better variable name; 'attribute' in name is kinda wonky
        self.check_for_typos_in_these_attributes={
               "Type":[],
               "Game":[],          }

        # for certain columns, such as cost, input should be of certain type (int)
        # and not a str (by typo)
        self.check_if_attribute_is_type = [
              ["Cost",int,[]],     ]
        
        # Above are hardcoded keys; are they present in the sheet?
        for kywrd in list(self.check_for_typos_in_these_attributes.keys()) + [
                                a[0] for a in self.check_if_attribute_is_type]:
            if kywrd not in self.card_keys:
                print("WARNING, following keyword not found in Sheet, while you"
                      " are testing for it. This will give a KeyError:",kywrd)


        # check for typos. Otherwise, certain cards could not be recognized when 
        # you filter for that specific word.
        # This is not case sensitive (TODO: should it?)
        for card in self.array_dict:
            for ky in self.check_for_typos_in_these_attributes:
                if not card[ky].lower() in self.check_for_typos_in_these_attributes[ky]:
                    self.check_for_typos_in_these_attributes[ky].append(card[ky].lower())

        # TODO: put this in hard code or something, for less manual work.   
        print("The following keywords should not have doubled types, due to typo's. "
              "Check them\n carefully for typo's. They are in alphabetical order:")
        for ky in self.check_for_typos_in_these_attributes:
            for i,strng in enumerate(self.check_for_typos_in_these_attributes[ky]):
                if strng.startswith("the "):
                    self.check_for_typos_in_these_attributes[ky][i] = strng[4:]+", the"
        for ky in sorted(list(self.check_for_typos_in_these_attributes.keys())):
            print(ky, *sorted(self.check_for_typos_in_these_attributes[ky]), sep="\n  ")


        # certain values need to be of a certain type; this checks for that
        for card in self.array_dict:            
            for ky,tp,lst in self.check_if_attribute_is_type:
                if not isinstance(card[ky], tp):
                    lst.append(card["Name"])
        
        _e=""
        for ky, tp, lst in self.check_if_attribute_is_type:
            if lst != []:
                _e+=("For attribute '{0}', the type should be {1} but it wasn't"
                     " for the following cards: {2}.  ".format(ky,tp,lst))
        if _e:
            raise ValueError(_e)
        
        # print all cards for extra testing
        for i, card in enumerate(self.array_dict):
            if i > 10:
                print("There are more cards ({} in total), "
                      "but not showing all.".format(len(self.array_dict)-1))
                break
            print(i, card)
            
            

    

if __name__ == "__main__":
    array_dict = LoadSheet(file,
##                           use_columns = [0,1,2],
                           check_validity = False ).array_dict
    print(*array_dict, sep = '\n')

# for future, if you wish to filter/replace this char, you'll need this variable
aether_character = "Æ"

### sort sheet into list
##array=[]
##for column in (result_file):
##    array.append([])
##    for i,value in enumerate(result_file[column]):
##        if not i in ignore_columns:
##            array[-1].append(value)







    
        
# how to read in excel files and ods-files    (for pandas install another module)
# https://stackoverflow.com/questions/17834995/how-to-convert-opendocument-spreadsheets-to-a-pandas-dataframe

# written by Arrethra https://github.com/arrethra/
try:
    import importcustommodules
    importcustommodules.add_parent_folder_to_sys_path(parent=3,  override=True,
                                                      print_warnings=False)
except ModuleNotFoundError: pass


import functools
import mymodules.mywrap.wraponlyonce as woo

def wrapper_to_get_entire_database(func):
    @woo.wraponlyonce(func,wrapper_to_get_entire_database)
    @functools.wraps(func)
    def call(*args,**kwargs):
        print("wrapper gets entire database")
        output = func(*args,**kwargs)
        return output
    return call

class ManipulateDatabase:
    @wrapper_to_get_entire_database
    def add_data_to_database(self,data):
        print("method: adding to database:",data)

    @wrapper_to_get_entire_database
    def delete_data_from_database(self,data):
        print("method: delete from database:",data)

    @wrapper_to_get_entire_database
    def swap_data_in_database(self,data):
        print("method: swap data in database:",data)
        self.delete_data_from_database(data)
        self.add_data_to_database([a.upper() for a in data])
        

data = ["a","b"]

DataBaseClass = ManipulateDatabase()
DataBaseClass.swap_data_in_database(data)

# wrapper will only be executed once
# >>> wrapper gets entire database
# >>> method: swap data in database: ["a","b"]
# >>> method: delete from database: ["a","b"]
# >>> method: adding to database: ["A","B"]






        

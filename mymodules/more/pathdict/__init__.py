"""
The Class PathDict is a nested dictionary structure that holds the
structure of every subfolder of path. PathDict inherited from dict,
and stores every subfolder as keys in it's dictionary. The values
paired to the keys are PathDict's of the underlying subfolders,
going recurisively down.
"""    

import os
from os import path as osp
import copy


def get_folders(path):
    dirs_and_files = os.listdir(path)
    dirs = []
    for p in dirs_and_files:
        full_path = osp.join(path,p)
        
        if osp.isdir(full_path):
            dirs.append(p)
    return dirs


def get_files(path):
    dirs_and_files = os.listdir(path)
    files = []
    for p in dirs_and_files:
        full_path = osp.join(path,p)
        
        if osp.isfile(full_path):
            files.append(p)
    return files


def get_files_and_folders(path):
    dirs_and_files = os.listdir(path)
    dirs = []
    files = []
    for p in dirs_and_files:
        full_path = osp.join(path,p)
        
        if osp.isdir(full_path):
            dirs.append(p)
        if osp.isfile(full_path):
            files.append(p)
            
    return files, dirs


class PathDict(dict):
    """
    A nested dictionary structure that holds the structure of every subfolder
    of path. PathDict inherited from dict, and stores every subfolder as keys
    in it's dictionary. The values paired to the keys are PathDict's of the
    underlying subfolders, going recurisively down.

    methods:
    fullpath
    getsubfolders
    getchildren
    getfiles
    """
    
    def __init__(self, path, ): 
        if not osp.isdir(path):
            _e = f"'{path}' is not a valid path. "
            raise ValueError(_e)

        self.path = path

        files, dirs = get_files_and_folders(path)

        for d in dirs:
            newpath = osp.join(path, d)
            pd = PathDict(newpath,) 
            self[d] = pd
        return None

    def fullpath(self,):
        """return the full path of the current PathDict"""
        return self.path

    def getsubfolders(self, fullpath = False):
        """
        Get the names (strings) of the subfolders, collected in a list. 
        If fullpath is specified to True, the entire path for each 
        subfolder is given.
        """
        if fullpath:
            return [child.fullpath() for child in self.getchildren()]       
        else:
            return [a for a in self.keys()]

    def getchildren(self):
        """
        Get the PathDict's of the subfolders of current path, collected in
        a list. The children are basically the dict.values() of the 
        PathDict.
        """
        return [d for d in self.values() if d]

    def getfiles(self):
        """
        gets the files of the current path. These files are in the same path
        as the subfolders listed as keys in this PathDict (dictionary).
        """
        return get_files(self.path)

            

if __name__ == "__main__":
    # TODO: write a unittest
    path = os.getcwd()
    Z = PathDict(path)
    print(Z,)
    print()
    
    print("Z.fullpath()= ",Z.fullpath())
    print()
    
    print(Z.getsubfolders(True))
    print()
    
    D = Z.getchildren()
    
    print(D[1].getsubfolders())

    

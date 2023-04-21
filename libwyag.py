import argparse
import collections
import configparser
import hashlib
from math import ceil
import os
import re
import sys
import zlib


argparser = argparse.ArgumentParser(description="The stupidest content tracker")
argsubparsers = argparser.add_subparsers(title="Commands", dest="command")
argsubparsers.required = True

def main(argv=sys.argv[1:]):
    args = argparser.parse_args(argv)

    # if   args.command == "add"         : cmd_add(args)
    # elif args.command == "cat-file"    : cmd_cat_file(args)
    # elif args.command == "checkout"    : cmd_checkout(args)
    # elif args.command == "commit"      : cmd_commit(args)
    # elif args.command == "hash-object" : cmd_hash_object(args)
    # elif args.command == "init"        : cmd_init(args)
    if args.command == "init"        : cmd_init(args)
    # elif args.command == "log"         : cmd_log(args)
    # elif args.command == "ls-files"    : cmd_ls_files(args)
    # elif args.command == "ls-tree"     : cmd_ls_tree(args)
    # elif args.command == "merge"       : cmd_merge(args)
    # elif args.command == "rebase"      : cmd_rebase(args)
    # elif args.command == "rev-parse"   : cmd_rev_parse(args)
    # elif args.command == "rm"          : cmd_rm(args)
    # elif args.command == "show-ref"    : cmd_show_ref(args)
    # elif args.command == "tag"         : cmd_tag(args)

#initializes the instance variables worktree, gitdir, and conf based on the path to the repository, and checks that the repository is valid and supported.
class GitRepository(object):
    """A git repository"""

    worktree = None
    gitdir = None
    conf = None
    # The path argument is the path to the top-level directory of the repository. 
    # The force argument is a boolean flag that indicates whether to force the creation of a new Git repository or not.
    def __init__(self, path, force=False): #isCreated
        self.worktree = path
        self.gitdir = os.path.join(path, ".git")
        # sets the gitdir instance variable to the path to the .git directory inside worktree.

        ## it checks if the gitdir directory exists
        if not (force or os.path.isdir(self.gitdir)): # not force and not os.path.isdir(self.gitdir)
            raise Exception("Not a Git repository %s" % path)


        self.conf = configparser.ConfigParser()     
        cf = repo_file(self, "config")  #it reads the configuration file in .git/config using the configparser

        if  cf and os.path.exists(cf):
            self.conf.read([cf])                    
        elif not force:
            raise Exception("Configuration file missing")       # If it does not exist and force is not set to True
        
        if not force:
            vers = int(self.conf.get("core", "repositoryformatversion"))
            if vers != 0:
                raise Exception("Unsupported respositoryformatversion %s" % vers)       #it checks the repository format version by reading the repositoryformatversion value from the core section of the configuration file.
    
#In a Git repository, there are many files and directories that need to be tracked and managed.
#general path building function: these utility function help with these tasks by computing the appropriate paths and creating any necessary directory structures.
def repo_path(repo, *path):
    """Compute path under repo's gitdir."""
    return os.path.join(repo.gitdir, *path)

    #repo is a GitRepository object, path is a absolute path to the specified file, mkdir argument which determines whether missing directories should be created
def repo_file(repo, *path, mkdir = False):
    #This computes the path to the parent directory of the file we want to create, and creates it if necessary using mkdir if specified. 
    if repo_dir(repo, *path[:-1], mkdir=mkdir):
        return repo_path(repo, *path)
        # repo_path computes the absolute path to the file we want to create, and returns it.
        # If repo_dir returns a path, meaning the directory was either already present or successfully created

def repo_dir(repo, *path, mkdir=False):
    """Same as repo_path, but mkdir *path if absent if mkdir"""

    #computes the absolute path to the directory we want to create
    path = repo_path(repo, *path)

    #Checks if the path already exists, and if so, whether it is a directory. 
    #If it is, the function returns the path. Otherwise, it raises an exception indicating that the path does not point to a directory.
    if os.path.exists(path):
        if (os.path.isdir(path)):
            return path
        else:
            raise Exception("Not a directory %s" % path)

    if mkdir:
        os.makedirs(path)       #If mkdir is True, the function creates the directory using os.makedirs, which creates any missing parent directories
        return path
    else:
        return None

# The function creates a new Git repository at a specified path
def repo_create(path):
    """Create a new repository at path"""

    #This creates a new GitRepository object with the specified path and sets the bare flag to True. 
    #A bare repository is a Git repository that does not have a working directory.
    repo = GitRepository(path, True)

    #check whether the directory specified by the path exists
    if os.path.exists(repo.worktree):
        if not os.path.isdir(repo.worktree):
            raise Exception ("%s is not a directory!" % path)
        if os.listdir(repo.worktree):
            raise Exception ("%s is not empty" % path)
    else:
        os.makedirs(repo.worktree)      #If it does not exist, the directory is created using os.makedirs.
    
    assert(repo_dir(repo, "branches", mkdir = True))
    assert(repo_dir(repo, "object", mkdir = True))
    assert(repo_dir(repo, "refs", "tags", mkdir = True))
    assert(repo_dir(repo, "branches", "heads", mkdir = True))

    #creates a new file called description in the .git directory of the repository, and writes the specified string to it.
    with open(repo_file(repo, "description"), "w") as f:
        f.write("Unnamed repository; edit this file 'description' to name the repository.\n")
    
    with open(repo_file(repo, "HEAD"), "w") as f:
        f.write("ref: refs/heads/master\n")
    
    with open(repo_file(repo, "config"), "w") as f:
        #The repo_default_config function returns a ConfigParser object that represents the default configuration.
        #writes the default configuration for a Git repository to the config file
        config = repo_default_config()
        config.write(f)
    
    return repo

# create configuration file: it’s a INI-like file with a single section ([core]) and three fields
def repo_default_config():
    ret = configparser.ConfigParser()

    ret.add_section("core")
    ret.set("core", "repositoryformatversion", "0") #the version of the gitdir format. 0 means the initial format, 1 the same with extensions.
    ret.set("core", "filemode", "false")            #disable tracking of file mode changes in the work tree
    ret.set("core", "bare", "false")                #indicates that this repository has a worktree.

    return ret
    
argsp = argsubparsers.add_parser("init", help = "Intialize a new, empty repository.")
argsp.add_argument("path", metavar = "directory", nargs = "?", default = ".", help="Where to create the repository.")

def cmd_init(args):
    repo_create(args.path)

#The argsp object defines the arguments for the init command, and the cmd_init function is called when the init command is executed.

#Path specifies the starting directory for the search (default is the current directory).
#Required, which specifies whether an exception should be raised if a Git repository is not found 
def repo_find(path=".", required=True):
    path = os.path.realpath(path)   #sets path to the real path of the starting directory,

    #This checks if the .git directory exists in the current path. If it does, it returns a new GitRepository object with path as its worktree.
    if os.path.isdir(os.path.join(path, ".git")):
        return GitRepository(path)

    #If the .git directory is not found in path, this line sets parent to the real path of the parent directory of path.
    parent = os.path.realpath(os.path.join(path, ".."))

    #If parent is the same as path, then path must be the root directory
    if parent == path:
        if required:
            raise Exception("No git directory.")
        else:
            return None

    return repo_find(parent, required)


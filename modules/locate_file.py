import os

def find(file_name, start_dir) -> str:
    """ Searches for file named 'file_name' starting in directory 'dir'.
        Will search current directory and all directories under current directory for file.

        Does not follow symbolic links.

        @Return:
            Absolute path to file -> If file exists
            None -> If file does not exist. 
    """
    for root, dirs, files in os.walk(start_dir):
        for file in files:
            if file == file_name:
                return root + '\\' + file 


def find_dir(dir_name, start_dir) -> str:
    """ Searches for dir named 'dir_name' starting in directory 'dir'.
        Will search current directory and all directories under current directory for file.

        Does not follow symbolic links.

        @Return:
            Absolute path to dir -> If dir exists
            None -> If dir does not exist. 
    """
    for root, dirs, files in os.walk(start_dir):
        for dir in dirs:
            if dir == dir_name:
                return root + '\\' + dir 

def get_path_from_cache(file_name, path_cache_file):
    
    try:    
        open(path_cache_file, mode='r')
    except FileNotFoundError: 
        path_cache_file = find(path_cache_file, os.getcwd())

    if path_cache_file == None: 
        raise FileNotFoundError("Unable to locate 'path_cache_file'")

    #for line in open(path_cache_file).readlines():
    with open(path_cache_file, mode='r') as f:
        lines = f.readlines()
        for line in lines:
            name, path = line.split(';')
            if name == file_name:
                return path.lstrip(), path_cache_file

def check_cache_or_find(file_name, start_dir, path_cache_file) -> str:
    """ 
        Does the same thing as find(), but first checks a "paths" text file which contains a cached path string.
        If the cached string is the correct path, it uses that.

        If not, it finds the correct path, updates the cache, and returns the path.
    """
    file_path, path_cache_file = get_path_from_cache(file_name, path_cache_file)
    try: 
        open(file_path, mode='r')
    except FileNotFoundError:
        file_path = find(file_name, start_dir)   
        open(path_cache_file, mode='w').write(file_name + '; ' + file_path)            

    return file_path

if __name__ == '__main__':
    print(find_dir('modules', start_dir=os.getcwd()))
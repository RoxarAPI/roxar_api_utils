import os

def get_file_name_parts(fullname):
    """Get parts of a complete file name
    Args:
        fullname (str):  Folder and file name
    Returns:
        folder (str): Folder name
        filename (str): File name, including suffix
        fileroot (str): File root, without suffix
        suffix (str): File suffix
    """
    folder, filename = os.path.split(fullname)

    ix = filename.rfind(r'.')

    if filename.startswith('.'):
        fileroot = filename
        suffix = ''
    elif filename.endswith('.'):
        fileroot = filename[0:ix]
        suffix = ''
    elif ix >= 0:
        fileroot = filename[0:ix]
        suffix = filename[ix+1:]
    else:
        fileroot = filename
        suffix = ''

    return (folder, filename, fileroot, suffix)

from datetime import datetime
import os

def write_file_header(filep, comment_start='#', name=None, length=50):
    """Write header to text files.
    Args:
        filep: File pointer for opened output text file
        comment_start: Characters used to denote the start of a comment
        name: Optional string with text description of data set (default None)
        length (int): Number of dashes in header lines
    """

    today = datetime.now()
    user = os.getlogin()

    print(comment_start, length*('-'), file=filep)
    if name is not None:
        print(comment_start, name, file=filep)

    print(comment_start, today.strftime("%d. %b %Y %H:%M:%S"), 'by user', user, file=filep)
    print(comment_start, length*('-'), '\n', file=filep)

    return None

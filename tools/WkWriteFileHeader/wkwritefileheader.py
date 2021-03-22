
from pathlib import Path

def myFunc():
    print("my func")
    val = input("Enter your value: ") 
    print(val) 

def file_prepender(target_file, text):
    with open(target_file, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        #f.write(text.rstrip('\r\n') + '\n' + content)
        f.write(text + "\n" + content)
        f.close()

def get_file_list(dir, filter_ext="*", verbose=False):

    """Get a directory and return the list of all the files in it with the specified extension"""
    file_list = []

    for path in Path(dir).rglob("*." + filter_ext):
        file_list.append(path)

    if verbose:
        print(f"Directory: {dir}")
        for path in file_list:
            print(f"File: {path}")

    return file_list
    
def prepend_text_to_file(dir, filter_ext, text_file):
    print(f"Text file: {text_file}")
    file_list = get_file_list(dir, filter_ext, True)

    print(f"Directory: {dir}")

    prepend_text = ""
    text_file_opened = open(text_file,mode="r")
    if not Path(text_file).exists():
        print("Input text file NOT valid...")
        return
        
    text_file_content = text_file_opened.read()
    print(f"text_file_content: {text_file_content}")
    text_file_opened.close()

    for path in file_list:
        print(f"Prepending text for file: {path} ")
        file_prepender(path, text_file_content)



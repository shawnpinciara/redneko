# import module
import shutil
import sys

try:
    shutil.copyfile(sys.argv[1], '/run/media/shawn/CIRCUITPY/code.py')
    print("Uploaded!")
except Exception as error:
    print("An exception occurred:", error) 
# copy the contents of the demo.py file to  a new file called demo1.py


#python3 copy_to.py
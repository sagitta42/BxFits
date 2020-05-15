from generator import *

def massive(userfile):
    print '#######'
    print 'Reading settings file'
    print '#######'
    f = open(userfile)
    lines = f.readlines()
    userinput = [l.rstrip() for l in lines if not '#' in l]
    print userinput
    print '~~~~~'
    setup_gen(userinput)

if len(sys.argv) == 1:    
    print generator.__doc__
    print 'Syntax: python massive.py config_file.txt'
    print 'Config file example: BxFits/set_test.txt'
    print
else:
    massive(sys.argv[1])    

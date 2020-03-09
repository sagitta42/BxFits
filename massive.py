from generator import *

def massive(userfile):
    print '~~~~~'
    print 'Reading settings file'
    print '~~~~~'
    f = open(userfile)
    lines = f.readlines()
    userinput = [l.rstrip() for l in lines]
    print userinput
    print '~~~~~'
    setup_gen(userinput)

massive(sys.argv[1])    

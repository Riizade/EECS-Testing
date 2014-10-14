import os
import commands
import sys
import getopt
import exceptions


def num(s):
    try:
        return int(s)
    except exceptions.ValueError:
        return float(s)


def divider():
    return "----------------------------------------------------------"


def main(argv):
    executable_name = ""
    arguments_list = ""
    diff = 0
    n = -1
    mode = -1
    suffix = ""

    print("\nThis is a test suite for EECS 280 and EECS 281 built by Adam Johnson.\n")

    try:
        opts, args = getopt.getopt(argv[1:], "he:a:dt:g:r:on:",
                                   ["help", "exe=", "args=", "diff", "test=", "gen=", "rm=", "out", "num="])

    #if invalid command line arguments were given
    except getopt.GetoptError:
        usage()
        print("Error: Invalid command line input.")
        sys.exit(2)

    #handle command line arguments
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-e", "--exe"):
            executable_name = arg
        elif opt in ("-a", "--args"):
            arguments_list = arg
            arguments_list.strip('\"')
        elif opt in ("-d", "--diff"):
            diff = 1
        elif opt in ("-n", "--num"):
            n = num(arg)
        elif opt in ("-t", "--test"):
            mode = 0
            suffix = arg
        elif opt in ("-g", "--gen"):
            mode = 1
            suffix = arg
        elif opt in ("-r", "--rm"):
            mode = 2
            suffix = arg
        elif opt in ("-o", "--out"):
            mode = 3

    #decide which mode to use
    if mode == 0:
        run_tests(executable_name, arguments_list, diff, suffix, n)
        sys.exit()
    elif mode == 1:
        rename(executable_name, arguments_list, suffix)
        sys.exit()
    elif mode == 2:
        remove(suffix)
        sys.exit()
    elif mode == 3:
        run_simple(executable_name, arguments_list, n)
        sys.exit()
    else:
        usage()
        print("Error: No valid mode specified.")
        sys.exit(2)


def usage():
    print("-----Help-----")
    print("This script requires that: ")
    print("\tYou are on a Linux machine running Python 3")
    print("\tAll of your test cases are named \"test-*.txt\" and do not contain a \'_\' in their filename")
    print("\tAll of your program files are contained in the same directory as this script")
    print("\tYour program can be built using \"make -r -R\"")
    print("")
    print("The commands are as follows:")
    print("\t-h, --help:\t\tPrints this help text.")
    print("\t-e, --exe [arg]:\tSpecifies the name of your program executable.")
    print("\t-a, --args \"[arg]\":\tSpecifies all of your program's command line arguments.")
    print("\t-d, --diff:\t\tSpecifies to print the diff output if a testcase did not pass.")
    print("\t-n, --num [arg]:\tSpecifies the number of lines to output.")
    print("\t-g, --gen [arg]:\tSpecifies to generate test-*_[arg].txt using current program output.")
    print("\t-t, --test [arg]:\tSpecifies to test against test-*_[arg].txt outputs.")
    print("\t-r, --rm [arg]:\t\tSpecifies to remove test-*_[arg].txt files.")
    print("\t-o, --out:\t\tSpecifies to run all tests and print their output.")
    print("Only one of (-g,-t,-r,-o) may be specified at a time.")
    print("")
    print("A valid example of generating test-*_old.txt files:")
    print("\tpython ./test.py -g old -e exchange -a \"-v -m -t\"")
    print("A valid example of regression testing against test-*_old.txt files:")
    print("\tpython ./test.py -t old -e exchange -a \"-v -m -t\" -d")


def build(executable_name):
    #build the binary
    print("Building the executable:")
    print('make -r -R')
    out = commands.getoutput('make -r -R')
    print(out)
    print('')
    #if an error occurs during building
    if "Error" in out:
        print('Error: Build was not successful.\n')
        sys.exit(3)
    else:
        print('Build successful.')


def clean():
        #clean up after itself
        print('Removing executable and objects:')
        print('make clean')
        os.system('make clean')


def rename(executable_name, arguments_list, suffix):
    build(executable_name)

    filenames = os.listdir('./')
    filenames.sort()

    print('Generating \"test-*_' + suffix + '.txt files...\"')
    for filename in filenames:
        #for each test case
        if filename[0:5] == "test-" and not '_' in filename:
            #if a solution exists
            #run the program
            os.system('./' + executable_name + ' ' + arguments_list + ' < ' + filename + ' > ' + filename[:-4] + '_' + suffix + '.txt')


def remove(suffix):
    print('Removing _' + suffix + '.txt files:')
    filenames = os.listdir('./')
    filenames.sort()
    for filename in filenames:
        if '_' + suffix + '.txt' in filename:
            print('rm ' + filename)
            os.system('rm ' + filename)
    print('')


def run_simple(executable_name, arguments_list, numlines):

    build(executable_name)

    filenames = os.listdir('./')
    filenames.sort()

    print("Running ./" + executable_name + " " + arguments_list + "...")

    for filename in filenames:
        #for each test case
        if filename[0:5] == "test-" and not '_' in filename:
            print(divider())
            print("Output for " + filename + ":")
            out = commands.getoutput('./' + executable_name + ' ' + arguments_list + ' < ' + filename)
            if numlines == -1:
                print(out)
            else:
                outlines = out.split("\n")
                for i in range(len(outlines)):
                    if i > numlines:
                        break
                    print(outlines[i])

    print(divider())
    clean()


def run_tests(executable_name, arguments_list, diff, suffix, numlines):

    build(executable_name)

    #create structures
    tests_passed = []
    tests_failed = []
    tests_no_sln = []

    filenames = os.listdir('./')
    filenames.sort()

    print("Testing ./" + executable_name + " " + arguments_list + "...")

    print('Comparing output...')
    for filename in filenames:
        #for each test case
        if filename[0:5] == "test-" and not '_' in filename:
            #if a solution exists
            if os.path.isfile("./" + filename[:-4] + '_' + suffix + '.txt'):
                #run the program
                os.system('./' + executable_name + ' ' + arguments_list + ' < ' + filename + ' > ' + filename[:-4] + '_tmp.txt')
                #diff the output
                out = commands.getoutput('diff ' + filename[:-4] + '_tmp.txt ' + filename[:-4] + '_' + suffix + '.txt')
                if out == '':
                    tests_passed.append(filename)
                else:
                    tests_failed.append((filename, out))
            else:
                #alert user that no solution exists
                tests_no_sln.append(filename)

    print('\nTests Passed:')
    if len(tests_passed) != 0:
        tests_passed.sort()
        for test in tests_passed:
            print(test)
    else:
        print('None')

    print('\nTests with no _' + suffix + '.txt:')
    if len(tests_no_sln) != 0:
        tests_no_sln.sort()
        for test in tests_no_sln:
            print(test)
    else:
        print('None')

    print('\nTests Failed:')
    if len(tests_failed) != 0:
        tests_failed.sort()
        for test in tests_failed:
            print(test[0])
            if (diff == 1):
                print(divider())
                if (numlines == -1):
                    print(test[1])
                else:
                    outlines = test[1].split("\n")
                    for i in range(len(outlines)):
                        if (i > numlines):
                            break
                        print(outlines[i])
            if (diff == 1):
                print(divider())
    else:
        print('None')
    print('')

    remove('tmp')

    clean()

if __name__ == "__main__":
    main(sys.argv)

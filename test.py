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


def main(argv=sys.argv):
    # argument variables
    buildmode = ""
    executable_name = ""
    arguments_list = ""
    diff = 0
    n = -1
    outmode = ""
    suffix = ""

    print("\nThis is a test suite for EECS classes at University of Michigan built by Adam Johnson.\n")

    try:
        opts, args = getopt.getopt(argv[1:], "he:b:a:ds:o:n:",
                                   ["help", "exe=", "build=", "args=", "diff", "suffix=", "out=", "num="])

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
        elif opt in ("-b", "--build"):
            buildmode = arg
        elif opt in ("-a", "--args"):
            arguments_list = arg
            arguments_list.strip('\"')
        elif opt in ("-d", "--diff"):
            diff = 1
        elif opt in ("-n", "--num"):
            n = num(arg)
        elif opt in ("-s", "--suffix"):
            suffix = arg
        elif opt in ("-o", "--out"):
            outmode = arg

    # decide which output mode to use
    if outmode == "test":
        outputs = run_tests(executable_name, arguments_list, buildmode)
        compare_outputs(outputs, suffix, diff)
        sys.exit()
    elif outmode == "gen":
        outputs = run_tests(executable_name, arguments_list, buildmode)
        generate_files(outputs, suffix)
        sys.exit()
    elif outmode == "rm":
        remove(suffix)
        sys.exit()
    elif outmode == "print":
        outputs = run_tests(executable_name, arguments_list, buildmode)
        print_outputs(outputs, n)
        sys.exit()
    else:
        usage()
        print("Error: No valid output mode specified.")
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
    print("\t-n, --num [arg]:\tSpecifies the number of lines to output for each test case.")
    print("\t-a, --args \"[arg]\":\tSpecifies all of your program's command line arguments.")
    print("\t-e, --exe [arg]:\tSpecifies the name of your program executable if using a single executable build mode.")
    print("\tBuild Modes")
    print("\t-b, --build [arg]:\tSpecifies the build and execution mode.")
    print("\t\t\"text\":\tOne executable already built, each test case is a text file read to stdin.")
    print("\t\t\"make\":\tEach test case is a cpp file with its own make target.")
    print("\tOutput Modes")
    print("\t-s, --suffix [arg]:\t\tSpecifies the suffix to be used in the output mode.")
    print("\t-d, --diff:\t\tSpecifies to print the diff output if a testcase did not pass, when using \"test\" mode.")
    print("\t-o, --out [arg]:\t\tSpecifies an output mode.")
    print("\t\t\"gen\":\tGenerates test-*_[suffix] using current program output.")
    print("\t\t\"test\":\tTests current output against test-*_[suffix].txt outputs.")
    print("\t\t\"rm\":\tRemoves test-*_[suffix].txt files.")
    print("\t\t\"print\":\tPrints current program output for each test to console.")
    print("")
    print("A valid example of generating test-*_old.txt files:")
    print("\tpython ./test.py -b text -o gen -s old -e exchange -a \"-v -m -t\"")
    print("A valid example of regression testing against test-*_old.txt files:")
    print("\tpython ./test.py -b text -o test -s old -e exchange -a \"-v -m -t\" -d")


# runs the command ("make "+make_target)
def build(make_target):
    #build the binary
    print("Building the executable:")
    print('make '+make_target)
    out = commands.getoutput('make '+make_target)
    print(out)
    print('')
    #if an error occurs during building
    if "Error" in out:
        print('Error: Build was not successful.\n')
        sys.exit(3)
    else:
        print('Build successful.')


# runs make clean
def clean():
    #clean up after itself
    print('Cleaning up:')
    print('make clean')
    os.system('make clean')


def generate_files(outputs, suffix):
    for testname, output in outputs.items():
        filename = rm_ext(testname)+"_"+suffix+".txt"
        f = open(filename, 'w')
        f.write(output)
        f.close()


# deletes test outputs with the correct suffix
def remove(suffix):
    print('Removing _' + suffix + '.txt files:')
    filenames = os.listdir('./')
    filenames.sort()
    for filename in filenames:
        if '_' + suffix + '.txt' in filename:
            print('rm ' + filename)
            os.system('rm ' + filename)
    print('')


# returns a list of the filenames of the testcases
def get_testcases():
    filenames = os.listdir('./')
    testnames = []
    for filename in filenames:
        if filename[0:5] == "test-" and not '_' in filename:
            testnames.append(filename)

    testnames.sort()
    return testnames


# returns a version of the string filename with the file extension truncated
def rm_ext(filename):
    return os.path.splitext(filename)[0]


# returns a list of files that have outputs with the correct suffix for a test case
def get_outputfiles(suffix):
    files = []
    for test in get_testcases():
        if os.path.isfile("./" + rm_ext(test) + '_' + suffix + '.txt'):
            files.append("./" + rm_ext(test) + '_' + suffix + '.txt')

    files.sort()
    return files


# returns a dictionary where keys are test names and values are the outputs of those tests
def run_tests(executable_name, arguments_list, buildmode):
    # decide which build mode to use
    if buildmode == "text":
        return run_tests_text(executable_name, arguments_list)
    elif buildmode == "make":
        return run_tests_make(arguments_list)
    else:
        usage()
        print("Error: No valid build mode specified.")
        sys.exit(2)


# returns a dictionary where keys are test names and values are the outputs of those tests
def run_tests_text(executable_name, arguments_list):
    build("")

    tests = get_testcases()
    outputs = {}

    print("Running ./" + executable_name + " " + arguments_list + "...")

    for test in tests:
        out = commands.getoutput('./' + executable_name + ' ' + arguments_list + ' < ' + test)
        outputs[test] = out

    clean()

    return outputs


# returns a dictionary where keys are test names and values are the outputs of those tests
def run_tests_make(arguments_list):
    outputs = {}

    # get test cases
    for testname in get_testcases():
        # if it's a .cpp file
        if os.path.isfile("./" + rm_ext(testname) + '.cpp'):
            # build the make target
            build(rm_ext(testname))
            # run the executable
            out = commands.getoutput('./' + rm_ext(testname) + ' ' + arguments_list)
            outputs[rm_ext(testname)] = out

    clean()

    return outputs


# prints test outputs
# optionally limits the number of lines per test output
def print_outputs(outputs, n):
    for testname, output in outputs.items():
        print(divider())
        print("Output for " + testname + ":")
        print(shorten_output(output, n))

    print(divider())


# if the output string has lines > numlines, it will be truncated to be only numlines lines
def shorten_output(output, numlines):
    # if there's no limit
    if numlines == -1:
        return output
    else:
        outlines = out.split("\n")
        return "\n".join(outlines[:numlines])


def compare_outputs(outputs, suffix, diff):

    # create data structures
    tests_passed = []
    tests_failed = []
    tests_no_sln = []

    generate_files(outputs, "tmp")

    print('Comparing output...')
    for test, output in outputs.items():
        if os.path.isfile(test+"_"+suffix+".txt"):
            # diff the output
            out = commands.getoutput('diff ' + test + '_tmp.txt ' + test + '_' + suffix + '.txt')
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
            # print name
            print(test[0])
            # print diff
            if diff == 1:
                print(divider())
                print(shorten_output(test[1], n))
    else:
        print('None')
    print('')

    remove('tmp')

    clean()


if __name__ == "__main__":
    main()

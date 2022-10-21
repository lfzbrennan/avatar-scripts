import os
import sys
import javalang


def read_file(fileloc):
    with open(fileloc, "r+") as file1:
        data = (file1.readlines())
        return data

def write_file(data, fileloc):
    file1 = open(fileloc, "w")
    file1.writelines(data)

def augment_buggy_code_by_variable_name(argv):
    if (not os.path.exists(argv[0])):
        sys.stderr.write("Found no file in " + argv[0] + "\n")
        sys.stderr.flush()
        sys.exit(0)

    if len(argv) != 2:
        print("you need to provide java file and buggy line as input. For example, python javaparser.py './sample_java_code.java' 20")

    fileloc = argv[0]
    buggyline = int(argv[1]) - 1

    source_code = read_file(fileloc)

    source_code = ''.join(source_code)

    # print(source_code)
    # print("*"*50)
    #
    # source_code = '''public class SimplexSolver extends AbstractLinearOptimizer{
    # 	private Integer getPivotRow(final int col, final SimplexTableau tableau) {
    # 		double minRatio = Double.MAX_VALUE;
    # 		Integer minRatioPos = null;
    # 		return minRatioPos;
    # 	}
    # }'''

    buggy_method = find_method(source_code, buggyline)

    tree = javalang.parse.parse(source_code)
    method_tree = tree.filter(javalang.tree.MethodDeclaration)
    varible_list = []

    for path, node in method_tree:
        if node.name == buggy_method['name']:
            body = node.body
            for item in body:
                if isinstance(item, javalang.tree.LocalVariableDeclaration):
                    tmp = {}
                    tmp['name'] = item.declarators[0].name
                    tmp['type'] = item.type.name
                    varible_list.append(tmp)
    # print("*" * 50)

    tokens = javalang.tokenizer.tokenize(source_code)

    modified_variable_list = []

    buggy_code = {}

    for token in tokens:
        if isinstance(token, javalang.tokenizer.Identifier):
            for obj in varible_list:
                if obj['name'] == token.value:
                    obj['line'] = token.position.line
                    modified_variable_list.append(obj)

                    if token.position.line == buggyline:
                        buggy_code = obj
                    break
        # print("*" * 50)

    # print(modified_variable_list)

    # modified with all the variables in the vulnerable line

    count = 0

    splitted_source_code = source_code.split('\n')

    code = splitted_source_code[buggyline]
    print('Found buggy code', code)
    print("*" * 50)

    if 'name' not in buggy_code:
        print('not able to perform data augmentation')

        return

    old_variable = buggy_code['name']

    for variable in modified_variable_list:
        if old_variable == variable['name']:
            continue
        code = code.replace(old_variable, variable['name'])
        splitted_source_code[buggyline] = code
        new_code = '\n'.join(splitted_source_code)

        write_file(new_code, fileloc)

        old_variable = variable['name']

        count += 1

def find_method(source_code, buggyline):
    # source_code = '''public class SimplexSolver extends AbstractLinearOptimizer{
    # 	private Integer getPivotRow(final int col, final SimplexTableau tableau) {
    # 		double minRatio = Double.MAX_VALUE;
    # 		Integer minRatioPos = null;
    # 		return minRatioPos;
    # 	}
    # 	private Integer getRow(final int col, final SimplexTableau tableau){
    # 	    double check_var = 0;
    # 	    return 0;
    # 	}
    # }'''


    tree = javalang.parse.parse(source_code)
    method_tree = tree.filter(javalang.tree.MethodDeclaration)
    method_names = []

    for path, node in method_tree:
        method_names.append(node.name)

    tokens = javalang.tokenizer.tokenize(source_code)
    method_list = []

    global_diff = 10000

    for token in tokens:
        if isinstance(token, javalang.tokenizer.Identifier):
            for method_name in method_names:
                if method_name == token.value:
                    obj = {}
                    obj['name'] = method_name
                    obj['line'] = token.position.line
                    if buggyline > obj['line']:
                        method_list.append(obj)

    method = {}
    for obj in method_list:
        diff = buggyline - obj['line']
        if diff<global_diff:
            global_diff = diff
            method = obj
    print("Buggy Method", method['name'])

    return method



if __name__ == "__main__":
    augment_buggy_code_by_variable_name(sys.argv[1:])
    # find_method()

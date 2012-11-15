import re
import subprocess
import ntpath

class ClangCompiler:
    """
    ClangCompiler wrapper from github.com/MorganBorman/cs140gide/ (did not use partial gcc implementation)
    Compiles projects and parses compiler errors.
    """

    stderr = ""
    stdout = ""

    def compile(self, files, executable):
        args = ["clang++", "-g", "-Wall"]
        args.extend(files)
        args.extend(["-o", executable])

        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.stdout, self.stderr = p.communicate()
    
    @staticmethod
    def is_id_line(line):
        '''Takes a line and checks to see if it is a clang error message'''
        if len(re.findall(".*:[0-9]+:[0-9]+: (fatal error|error|warning):.*", line)) == 1:
            return True
        return False

    @staticmethod
    def parse_id_line(line):
        '''Parses a clang line and returns a dict containing the appropriate info'''
        #Todo: this will fail if the filename contains ":"
        def path_leaf(path):
            head, tail = ntpath.split(path)
            return tail or ntpath.basename(head)

        elements = line.split(":",4)
        retval = {}
        retval['filename'] = path_leaf(elements[0])
        retval['line_no'] = int(elements[1])
        retval['char_no'] = int(elements[2])
        retval['error_type'] = elements[3].strip()
        retval['error_msg'] = elements[4].strip()
        return retval

    def errors(self):
        output = self.stderr
        lines = output.split("\n")
        sections = []
        for i, line in enumerate(lines):
            if self.is_id_line(line):
                sections.append(i)
        errors = []
        for i, line_pos in enumerate(sections):
            temp = self.parse_id_line(lines[line_pos])
            if i + 1 < len(sections):
                temp['full_msg'] = "\n".join(lines[line_pos:sections[i + 1]])
            else:
                temp['full_msg'] = "\n".join(lines[line_pos:])
            errors.append(temp)
        return errors
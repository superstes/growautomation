from pathlib import Path
from re import search as regex_search


def _file():
    subdir_count = 1
    current_path = Path(__file__).parent.absolute()
    ga_root_path = '/'.join(str(current_path).split('/')[:-subdir_count])
    secret_file_path = '/core/secret/random.key'
    return "%s%s" % (ga_root_path, secret_file_path)


def get():
    with open(_file(), 'r') as _:
        line_list = _.readlines()

        for line in line_list:
            if not regex_search('^#', line):
                return line.strip()


def put(key):
    with open(_file(), 'w') as _:
        line_list = _.readlines()
        write_list = []

        for line in line_list:
            if regex_search('^#', line):
                write_list.append(line)

        write_list.append(key)

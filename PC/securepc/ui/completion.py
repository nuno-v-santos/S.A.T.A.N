import os
import re
import readline

from typing import List
from pubsub import pub


_COMMANDS = ['add', 'remove', 'status', 'unpair', 'exit']
_RE_SPACE = re.compile('.*\s+$', re.M)

class _Completer(object):
    def __init__(self, file_list: List[str] = []):
        self._file_list = file_list
        pub.subscribe(self._update_file_list, "file_list_changed")

    def _update_file_list(self, file_list):
        self._file_list = file_list

    def _listdir(self, root: str) -> List[str]:
        """
        List the contents of a directory.

        :param root: the directory to list
        :return: a list containing the directory's contents.
                 Subdirectories will have an appended path
                 separator.
        """
        contents = []
        for name in os.listdir(root):
            path = os.path.join(root, name)
            if os.path.isdir(path):
                name += os.sep
            contents.append(name)
        return contents

    def _complete_path(self, path=None):
        "Perform completion of filesystem path."
        if not path:
            return self._listdir('.')
        dirname, rest = os.path.split(path)
        tmp = dirname if dirname else '.'
        res = [os.path.join(dirname, p)
               for p in self._listdir(tmp) if p.startswith(rest)]
        # more than one match, or single match which does not exist (typo)
        if len(res) > 1 or not os.path.exists(path):
            return res
        # resolved to a single directory, so return list of files below it
        if os.path.isdir(path):
            return [os.path.join(path, p) for p in self._listdir(path)]
        # exact file match terminates this completion
        return [path + ' ']

    def complete_add(self, args):
        "Completions for the 'add' command."
        if not args:
            return self._complete_path('.')
        # treat the last arg as a path and complete it
        return self._complete_path(args[-1])

    def complete_remove(self, args):
        "Completions for the 'remove' command."
        return self.complete_add(args)

    def complete(self, text, state):
        """
        Generic readline completion entry point.
        """
        buffer = readline.get_line_buffer()
        line = readline.get_line_buffer().split()
        # show all commands
        if not line:
            return [c + ' ' for c in _COMMANDS][state]
        # account for last argument ending in a space
        if _RE_SPACE.match(buffer):
            line.append('')
        # resolve command to the implementation function
        cmd = line[0].strip()
        if cmd in _COMMANDS:
            impl = getattr(self, 'complete_{}'.format(cmd))
            args = line[1:]
            if args:
                return (impl(args) + [None])[state]
            return [cmd + ' '][state]
        results = [c + ' ' for c in _COMMANDS if c.startswith(cmd)] + [None]
        return results[state]

_comp = _Completer()

def init_completion():
    # we want to treat '/' as part of a word, so override the delimiters
    readline.set_completer_delims(' \t\n;')
    readline.parse_and_bind("tab: complete")
    readline.set_completer(_comp.complete)

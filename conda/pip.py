"""
Functions related to core conda functionality that relates to pip
"""
from __future__ import absolute_import, print_function

import os
import re
import sys
from os.path import isdir, isfile, join

from conda.compat import itervalues
from conda.install import linked_data
from conda.misc import rel_path



def get_site_packages_dir(installed_pkgs):
    for info in itervalues(installed_pkgs):
        if info['name'] == 'python':
            if sys.platform == 'win32':
                stdlib_dir = 'Lib'
            else:
                py_ver = info['version'][:3]
                stdlib_dir = 'lib/python%s' % py_ver
            return join(stdlib_dir, 'site-packages')
    return None


def get_egg_info_files(sp_dir):
    for fn in os.listdir(sp_dir):
        if not fn.endswith(('.egg', '.egg-info')):
            continue
        path = join(sp_dir, fn)
        if isfile(path):
            yield path
        elif isdir(path):
            path2 = join(path, 'PKG-INFO')
            if isfile(path2):
                yield path2


pat = re.compile(r'(\w+):\s*(\S+)', re.I)
def read_egg_info(path):
    info = {}
    for line in open(path):
        line = line.strip()
        m = pat.match(line)
        if m:
            info[m.group(1).lower()] = m.group(2)
        try:
            return '%(name)s-%(version)s-<egg.info>' % info
        except KeyError:
            pass
    return None


def pip_installed(prefix):
    installed_pkgs = linked_data(prefix)
    sp_dir = get_site_packages_dir(installed_pkgs)
    if sp_dir is None:
        return

    conda_files = set()
    for info in itervalues(installed_pkgs):
        conda_files.update(info.get('files', []))
    print(len(conda_files))

    res = set()
    for path in get_egg_info_files(join(prefix, sp_dir)):
        f = rel_path(prefix, path)
        if f not in conda_files:
            #print(f)
            dist = read_egg_info(path)
            if dist:
                res.add(dist)
    return res


if __name__ == '__main__':
    print(pip_installed(sys.prefix))

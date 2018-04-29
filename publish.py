#!/usr/bin/python

# push slides for a talk to cern gitlab
#
# TODO: document use case
# TODO: error handling
# TODO: more proper usage of python (e.g. git module instad of check_output)
# TODO: sanity checking if called from right directory and status of repo
# TODO: python3 compatibility
# WISH: symlinking and submodule handling for main repo

import os
import sys
import json
from subprocess import check_output
import subprocess

WorldPublic = True
TrivialName = os.path.basename(os.getcwd())


def my_run(*args, **kwargs):
    from subprocess import run
    out = run(*args,
              check=True,
              stdout=subprocess.PIPE,
              stderr=subprocess.PIPE,
              **kwargs
              )
    return out


def current_branch_name():
    """current_branch_name

    Returns:
        string:   name of the current branch
    """
    try:
        import git
    except ImportError:
        out = check_output(['git', 'branch'])
        for b in out.split('\n'):
            if b.startswith('* '):
                return b.replace("* ", "")
    else:
        myrepo = git.repo.base.Repo(path=".")
        return myrepo.active_branch.name


def create_repo():
    """ create_repo
    Creates a repository on the CERN gitlab server. The repository name will be
    the current directory's name.

    Returns:
        dictionary (json decoded) server response
    """
    if WorldPublic:
        out = my_run(["curl",
                      "--header", "PRIVATE-TOKEN: "+os.environ["GITLABTOKEN"],
                      "-X", "POST",
                      "https://gitlab.cern.ch/api/v4/projects?name="+TrivialName+"&visibility=public"
                      ])
        try:
            my_run(["mv", "LICENSE.pub.md", "LICENSE.md"])
            my_run(["rm", "LICENSE.int.md"])
        except subprocess.CalledProcessError:
            import os
            if os.path.isfile("LICENSE.md"):
                print("could not replace LICENSE.md by LICENSE.int.md. Assume this has already been done.")
            else:
                raise
    else:
        out = my_run(["curl",
                      "--header", "PRIVATE-TOKEN: "+os.environ["GITLABTOKEN"],
                      "-X", "POST",
                      "https://gitlab.cern.ch/api/v4/projects?name="+TrivialName+"&visibility=private"
                      ])
        # these fail upon try-again due to failure

        try:
            my_run(["mv", "LICENSE.int.md", "LICENSE.md"])
            my_run(["rm", "LICENSE.pub.md"])
        except subprocess.CalledProcessError:
            import os
            if os.path.isfile("LICENSE.md"):
                print("could not replace LICENSE.md by LICENSE.int.md. Assume this has already been done.")
            else:
                raise
        print("TODO share with LHCb")

    print('stderr was {}'.format(out.stderr))
    repo_conf = json.loads(out.stdout.decode())
    try:
        repo_conf["name"]
    except:
        # likely repo already exists (try-again? name collision?)
        print("Could not create remote repository.")
        print("Server response is:")
        print(json.dumps(
            repo_conf,
            sort_keys=True,
            indent=2,
            separators=(',', ': ')
            ))

        sys.exit(1)
    return repo_conf


repo_conf = create_repo()

check_output(["git", "rm", "logo.png"])

# json call like this not ready for python3

try:
    import re
    # check_output(["git","remote","add",TrivialName,re.sub("7999","8443",re.sub('ssh://git','https://:',repo_conf["ssh_url_to_repo"]))])
    check_output(["git", "remote", "add",
                  "gitlab",
                  re.sub("7999", "8443", re.sub('ssh://git', 'https://:', repo_conf["ssh_url_to_repo"]))
                  ])
except:
    print("couldn't add remote")
    print(json.dumps(repo_conf, sort_keys=True, indent=2, separators=(',', ': ')))

# check_output(["git","subtree","split","--prefix="+os.path.basename(DirName),"-b",BranchName])
try:
    pushout = check_output(["git", "push", "--set-upstream", "gitlab", "{}:master".format(current_branch_name())])
except:
    # pushout unknown ...
    print("push did ", pushout)

try:
    qrgen = check_output(["qrencode", "-o", "QR.png", repo_conf['web_url']])
except:
    print("QR code generation did ", qrgen)
try:
    convert = check_output(["convert", "QR.png", "-flatten", "QR2.png"])
except:
    print("alpha channel removal did ", convert)

with open("./header.tex", "a") as header:
    header.write('\\newcommand{{\gitlablink}}{{\myhref{{{realurl}}}{{{escapedurl}}}}}\n'.format(realurl=repo_conf['web_url'],escapedurl=repo_conf['web_url'].replace("_",r'\_')))

# publication script
# Copyright (C) 2017  Paul Seyfert <pseyfert@cern.ch>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

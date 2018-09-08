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
import re
import sys
import json
from subprocess import check_output
import subprocess

WorldPublic = True
TrivialName = os.path.basename(os.getcwd())
print("repo will basically be named {}".format(TrivialName))
Token = os.environ["GITLABTOKEN"]


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
        for b in out.decode().split('\n')[:-1]:
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
    import os
    if WorldPublic:
        visibility = "public"
    else:
        visibility = "private"
    out = my_run(["curl",
                  "--header", "PRIVATE-TOKEN: {}".format(Token),
                  "-X", "POST",
                  "https://gitlab.cern.ch/api/v4/projects?name={name}&visibility={visibility}".format(visibility=visibility, name=TrivialName)
                  ])
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
        my_run(["curl",
                "--header", "PRIVATE-TOKEN: {}".format(Token),
                "-X", "POST",
                "https://gitlab.cern.ch/api/v4/projects/{}/share?group_id=120&group_access=20".format(repo_conf["id"])
                ])
        print("TODO share with LHCb")

    if WorldPublic:
        try:
            my_run(["git", "rm", "LICENSE.md"])
            my_run(["git", "mv", "LICENSE.pub.md", "LICENSE.md"])
            my_run(["git", "rm", "LICENSE.int.md"])
        except subprocess.CalledProcessError:
            if os.path.isfile("LICENSE.md"):
                print("could not replace LICENSE.md by LICENSE.int.md. Assume this has already been done.")
            else:
                raise
    else:
        try:
            my_run(["git", "rm", "LICENSE.md"])
            my_run(["git", "mv", "LICENSE.int.md", "LICENSE.md"])
            my_run(["git", "rm", "LICENSE.pub.md"])
        except subprocess.CalledProcessError:
            if os.path.isfile("LICENSE.md"):
                print("could not replace LICENSE.md by LICENSE.int.md. Assume this has already been done.")
            else:
                raise

    if os.path.isfile("logo.png"):
        check_output(["git", "rm", "logo.png"])

    with open("./header.tex", "a") as header:
        header.write('\\newcommand{{\gitlablink}}{{\myhref{{{realurl}}}{{{escapedurl}}}}}\n'.format(realurl=repo_conf['web_url'], escapedurl=repo_conf['web_url'].replace("_", r'\_')))

    return repo_conf


def add_remote(desired_push_url):
    try:
        check_output(["git", "remote", "add",
                      "gitlab",
                      desired_push_url
                      ])
    except:
        print("couldn't add remote")
        remote_lines = check_output(['git', 'remote', '-v']).decode().split('\n')[:-1]
        for remote_line in remote_lines:
            if remote_line.endswith(' (push)'):
                current_remote = remote_line.replace(" (push)", "").split("\t")
                if current_remote[0] == 'gitlab':
                    if current_remote[1] == desired_push_url:
                        print("because it already exists with the right url")
                        pass
                    else:
                        print('remote gitlab already exists with "wrong" url')
                        print('wanted {}\n got {}'.format(desired_push_url, current_remote[1]))
                        print(json.dumps(repo_conf, sort_keys=True, indent=2, separators=(',', ': ')))
                        raise


def push():
    try:
        pushout = check_output(["git", "push", "--set-upstream", "gitlab", "{}:master".format(current_branch_name())])
    except:
        # pushout unknown ...
        try:
            print("push did ", pushout)
        except:
            print("push failed")
            print("command was: git push --set-upstream gitlab {}:master".format(current_branch_name()))
            print("origin is set up and stuff, just fix the push error")
            print("maybe authenticate")


def qrgen():
    try:
        qrgen_output = check_output(["qrencode", "-o", "QR.png", repo_conf['web_url']])
    except:
        print("QR code generation did ", qrgen_output)
    try:
        convert = check_output(["convert", "QR.png", "-flatten", "QR2.png"])
    except:
        print("alpha channel removal did ", convert)

    check_output(["git", "add", "QR.png", "QR2.png"])


repo_conf = create_repo()
desired_push_url = re.sub("7999", "8443", re.sub('ssh://git', 'https://:', repo_conf["ssh_url_to_repo"]))
add_remote(desired_push_url)
qrgen()
push()


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

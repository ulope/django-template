import os
from random import choice
from time import sleep
from fabric.api import task, local
from fabric.context_managers import cd, settings, hide
from fabric.decorators import runs_once, roles
from fabric.operations import run, sudo
from fabric.state import env

env.use_ssh_config = True
env.roledefs = {
    'live': ('<INSERT HOST NAME>', ),
}

PATHS = {
    'live': {
        'process_name': "{{ project_name }}",
        'virtualenv_root': "/var/lib/virtualenvs/{{ project_name }}",
        'pip': "{0[virtualenv_root]}/bin/pip",
        'python': "{0[virtualenv_root]}/bin/python",
        'project_root': "/usr/local/pythonapps/{{ project_name }}",
        'manage.py': "{0[project_root]}/manage.py",
        'secret_key': "{0[project_root]}/secret.key",
        'user': "www-data",
        'group': "www-data",
        'logfile': "/var/log/pythonapps/{{ project_name }}.log"
    }
}


@task(default=True)
@roles("live")
def live(upgrade=False):
    """Deploy to the live server"""
    prepare()
    deploy(upgrade)
    postpare()


def deploy(upgrade=False):
    paths = get_paths()
    if upgrade:
        upgrade = "--upgrade"
    else:
        upgrade = ""
    with cd(paths['project_root']):
        run("git pull")
        try:
            run("supervisorctl stop {0[process_name]}".format(paths))
            run("{0[pip]} install {1} -r reqs/default.txt".format(paths, upgrade))
            run("{0[pip]} install {1} -r reqs/live.txt".format(paths, upgrade))

            if not os.path.exists(paths['secret_key']):
                run(
                    """echo '{0}' > {1}""".format(
                        ''.join([choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for _ in range(50)]),
                        paths['secret_key']
                    )
                )

            run("{0[python]} {0[manage.py]} syncdb".format(paths))
            run("{0[python]} {0[manage.py]} migrate".format(paths))
            run("{0[python]} {0[manage.py]} collectstatic --noinput --link".format(paths))
            run("chown -R {0[user]}:{0[group]} {0[logfile]}".format(paths))
        finally:
            # make sure were running again
            run("supervisorctl start {0[process_name]}".format(paths))


@runs_once
def prepare():
    local("git push")


def postpare():
    pass


def get_paths():
    role = next(role for role, hosts in env.roledefs.items() if env.host_string in hosts)
    return {
        k: v.format(PATHS[role]) for k, v in PATHS[role].items()
    }

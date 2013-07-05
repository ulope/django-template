from copy import copy
from random import choice
from fabric.api import task, local
from fabric.context_managers import cd
from fabric.contrib import files
from fabric.decorators import runs_once, roles
from fabric.operations import run
from fabric.state import env

env.use_ssh_config = True
env.roledefs = {
    'live': ('<INSERT HOST NAME>', ),
}

PATHS = {
    'live': {
        'name': "{{ project_name }}",
        'process_name': "{0[name]}",
        'dir_name': "{0[name]}",
        'virtualenv_root': "/var/lib/virtualenvs/{0[dir_name]}",
        'pip': "{0[virtualenv_root]}/bin/pip",
        'python': "{0[virtualenv_root]}/bin/python",
        'supervisorctl': "supervisorctl",
        'project_base': "/usr/local/pythonapps",
        'project_root': "{0[project_base]}/{0[dir_name]}",
        'manage.py': "{0[project_root]}/manage.py",
        'secret_key': "{0[project_root]}/secret.key",
        'logfile': "/var/log/pythonapps/{0[name]}.log",
        'user': 'www-data',
        'group': 'www-data',
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
    config = get_config()
    if upgrade:
        upgrade = "--upgrade"
    else:
        upgrade = ""
    with cd(config['project_base']):
        try:
            run("{0[supervisorctl]} stop {0[process_name]}".format(config))
            with cd(config['project_root']):
                run("git pull")
                run("{0[pip]} install {1} -r reqs/default.txt".format(config, upgrade))
                run("{0[pip]} install {1} -r reqs/live.txt".format(config, upgrade))

                if not files.exists(config['secret_key']):
                    run("""echo '{0}' > {1[secret_key]}""".format(generate_secret_key(), config))

                run("{0[python]} {0[manage.py]} syncdb".format(config))
                run("{0[python]} {0[manage.py]} migrate".format(config))
                run("{0[python]} {0[manage.py]} collectstatic --noinput --link".format(config))
                run("chown -R {0[user]}:{0[group]} {0[logfile]}".format(config))
        finally:
            # make sure were running again
            run("{0[supervisorctl]} start {0[process_name]}".format(config))


@runs_once
def prepare():
    local("git push")


def postpare():
    pass


def generate_secret_key():
    return ''.join([choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for _ in range(50)])


def get_config(role=None):
    """Expand format strings in PATHS definition. Repeatedly evaluate formats until fix-point is reached."""
    if not role:
        role = next(role for role, hosts in env.roledefs.items() if env.host_string in hosts)
    changed = True
    while changed:
        changed = False
        new_paths = copy(PATHS[role])
        for k, v in PATHS[role].items():
            try:
                new_v = v.format(PATHS[role])
                if v != new_v:
                    changed = True
                    new_paths[k] = new_v
            except AttributeError:
                # v doesn't have a .format() method
                pass
        if changed:
            PATHS[role] = new_paths

    return PATHS[role]

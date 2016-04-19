# -*- coding: utf-8 -*-
from fabric.api import env, roles, run, cd, local

ADDITIONAL_DATABASES = ('raw_statistics', )
PROJECT_DIR = ''

env.roledefs = {
    'lin-kmclient-stat': [
        '',
    ],
}


def local_migrate_databases():
    local('../bin/manage migrate')
    for database in ADDITIONAL_DATABASES:
        local('../bin/manage migrate --database={0}'.format(database))


def deploy_production():
    local('fab update_project')
    local('fab migrate_databases')
    local('fab collect_static')
    local('fab restart_project')


@roles('lin-kmclient-stat')
def update_project():
    with cd(PROJECT_DIR):
        run('git pull')


@roles('lin-kmclient-stat')
def restart_project():
    run('supervisorctl restart kmclient-statistics:gunicorn')
    run('supervisorctl restart kmclient-statistics:celery')
    run('kill -HUP `cat ~/www/gunicorn-api.pid`')


@roles('lin-kmclient-stat')
def collect_static():
    with cd(PROJECT_DIR):
        run('echo "yes" | bin/manage collectstatic')


@roles('lin-kmclient-stat')
def migrate_databases():
    with cd(PROJECT_DIR):
        run('bin/manage migrate')
        for database in ADDITIONAL_DATABASES:
            run('bin/manage migrate --database={0}'.format(database))


@roles('lin-kmclient-stat')
def install_requirements(update=False):
    with cd(PROJECT_DIR):
        if update:
            run('bin/pip install -U -r requirements.txt')
        else:
            run('bin/pip install -r requirements.txt')


@roles('lin-kmclient-stat')
def uninstall_requirements(packages=None):
    if packages:
        with cd(PROJECT_DIR):
            run('bin/pip uninstall -y %s' % packages)
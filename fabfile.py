from fabric.api import sudo, prompt, run, local, cd
from fabric.decorators import runs_once, hosts, task
from fabric.colors import green

@task
def ci():
    """Commit localy using mercurial"""
    comment = prompt('Commit comment: ', default='another commit from fabric')
    local('hg ci -m "%s"' % comment)
    push()

@runs_once
def push():
    print(green('pushing...'))
    local('hg push')

@task
@hosts('rif@avocadosoft.ro:22011')
def deploy():
    'Deploy the app to the target environment'
    print(green('deploying...'))
    push()
    for app in ('mcsa',):
        with cd('/home/www-data/web2py/applications/' + app):
            run('hg pul -uv')
    with cd('/home/www-data/web2py/applications/demo'):
        run('hg pul --rebase -uv')

@task
@hosts('rif@avocadosoft.ro:22011')
def reload():
    print(green('reloading...'))
    'fires an uwsgi graceful reload'
    sudo('service uwsgi-python reload')

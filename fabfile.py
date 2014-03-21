"""
Magento Fab File

This file will take care of setting your magento project up and deploying it to
your beta and production servers.

To view how to use any of these tasks, run fab -d COMMAND
"""
from __future__ import with_statement
import os
import time
import datetime
from fabric.api import *
from fabric.contrib.project import rsync_project
from fabric.contrib.console import confirm
from fabric.contrib.files import exists

# setup our variables
sshuser = 'ubuntu'  # the user you use to ssh into your server
domain = '.domain.com'  # the domain of your app/website
web_root = '/var/www/domain.com'  # the web root of your website
web_folder = web_root + '/web'  # the document root of your website
releases_folder = web_root + '/releases'  # this folder serves as a backup folder to quickly roll back to a previous release incase of emergency
shared_folder = web_root + '/shared'  # this is a folder which contains all the files and folders thats not in your source versioning
repo_folder = web_root + '/repo'  # we checkout our repo to this folder and from here rsync to our release folder
media_folder = shared_folder + '/media'  # youre media folder or mount
#env.key_filename = '/path/to/key/file.pem'  # keyfile incase you use one - if you use a public key simply comment this
git_repo = 'git@github.com:WinstonN/magento_fabric_deploy.git'  # git repo url
notice_prefix = '=> DEPLOY NOTICE ::'  # deploy notice prefix
ts = time.time()
stamp = datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d-%H%M')
keep = '5'  # number of backups / releases to keep in your releases folder
permissions_user = 'www-data'  # web server user
permissions_group = 'users'  # web server group

# define our host and infrastructure roles
env.roledefs = {
    'dev': [sshuser + '@' + domain],
    #'stage': ['host1', 'host2'], #TODO Add Stage environment
    #'qa': ['host1', 'host2'], #TODO Add QA environment
    #'prod': [
    #    sshuser + '@hostname' + domain,
    #    sshuser + '@hostname' + domain,
    #    sshuser + '@hostname' + domain,
    #    sshuser + '@hostname' + domain
    #],
    # individual web nodes
    #'web01': [sshuser + '@web01' + domain],
    #'web02': [sshuser + '@web02' + domain],
    #'web03': [sshuser + '@web03' + domain],
    #'web04': [sshuser + '@web04' + domain],
    #'web05': [sshuser + '@web05' + domain],
}

# default role will be dev
env.roles = ['dev']

def report():
    """
    # report
    # report makes the roles give feedback with their kernels
    """
    run('uname -a')


def check():
    """
    # check
    # this method check if the web root is sane
    """
    run('ls -lah ' + web_root)


def migrate():
    """
    # migrate
    # this method migrates the current setup over to our folder structure
    """

    setup()
    with settings(warn_only=True):
        with hide('stdout', 'stderr', 'warnings'):
            # move media out of the original web folder into our shared folder
            print '%s move media to shared folder' % notice_prefix
            if run("test -d %s" % web_folder + '/media').failed:
                print '%s %s/media does not exist' % (notice_prefix, web_folder)
            else:
                run('sudo mv ' + web_folder + '/media ' + shared_folder)

            # move var out of the original web folder into our shared folder
            print '%s move var to shared folder' % notice_prefix
            if run("test -d %s" % web_folder + '/var').failed:
                print '%s %s/var does not exist' % (notice_prefix, web_folder)
            else:
                run('sudo mv ' + web_folder + '/var ' + shared_folder)

            # remove web folder as we will create a symlink for it
            print '%s check if our web directory exists' % notice_prefix
            if run("test -d %s" % web_folder).failed:
                print '%s %s does not exist' % (notice_prefix, web_folder)
            else:
                print '%s %s does exist..deleting' % (notice_prefix, web_folder)
                run('sudo rm -rf ' + web_folder)


def setup():
    """
    # setup
    # this method check if the web root is sane, if not, it creates some folders we will need
    """
    with settings(warn_only=True):
        with hide('stdout', 'stderr', 'warnings'):
            # check if exist and create releases folder
            print '%s check if our releases folder exists' % notice_prefix
            if run("test -d %s" % releases_folder).failed:
                print '%s %s does not exist..creating' % (notice_prefix, releases_folder)
                run('sudo mkdir ' + releases_folder)
            else:
                print '%s %s does exist' % (notice_prefix, releases_folder)

            # check if exist and create releases folder
            print '%s check if our shared folder exists' % notice_prefix
            if run("test -d %s" % shared_folder).failed:
                print '%s %s does not exist..creating' % (notice_prefix, shared_folder)
                run('sudo mkdir ' + shared_folder)
            else:
                print '%s %s does exist' % (notice_prefix, releases_folder)



def deploy(branch='master', tag=''):
    """
    # deploy
    # deploy a branch (for now) to an environment
    """
    with settings(warn_only=True):
        with hide('stdout', 'stderr', 'warnings'):
            print '%s check if our repo directory exists' % notice_prefix
            if run("test -d %s" % repo_folder).failed:
                print '%s %s does not exist..cloning' % (notice_prefix, repo_folder)
                run("sudo -E git clone " + git_repo + " %s" % repo_folder)
    with cd(repo_folder):
        print '%s %s exists..deploying' % (notice_prefix, repo_folder)
        print '%s current directory %s' % (notice_prefix, run('pwd'))
        run('sudo -E git fetch')
        run('sudo -E git pull -f origin ' + branch)

    print '%s exporting repo into release with timestamp...' % notice_prefix
    run('sudo rsync -rlpgoD --delete --exclude=\'.git\' ' + repo_folder + '/ ' + releases_folder + '/' + stamp + ' -SXl')
    print '%s rysnc done!' % notice_prefix

    symlink()
    set_permissions()
    link_to_web()
    prune_releases()

    print '%s deploy done' % notice_prefix



def rollback(number):
    """
    # roll back to a previous deploy
    # 1 = last, possibly broken deploy; 2 = last good deploy; 3,4,5 = older deploys where 5 is the oldest
    """
    # remove web folder and get ready to link to latest archive
    run('sudo rm -rf ' + web_folder)
    with cd(releases_folder):
        run('sudo ln -s ' + releases_folder + '/$(files=( * ) n=${#files[@]}; echo ${files[n-' + number + ']})' + ' ' + web_folder)



def prune_releases():
    """
    # prune some releases in our releases folder
    # we keep only the last 5 releases
    """
    with settings(warn_only=True):
        with hide('stdout', 'stderr', 'warnings'):
            print '%s removing everything but the last %s releases archives' % (notice_prefix, keep)
            run('( cd ' + releases_folder + '; sudo rm -r $( ls -t  |  tail -n +' + str(int(float(keep) + 1)) + ' ) )')


def symlink():
    """
    # create symlinks to media, var etc
    """
    print '%s linking to shared files and folders' % notice_prefix
    # symlink media
    with settings(warn_only=True):
            with hide('stdout', 'stderr', 'warnings'):
                print '%s check if our media directory exists within web' % notice_prefix
                if run("test -d %s" % releases_folder + '/' + stamp + '/media').failed:
                    print '%s %s/%s/media not found' % (notice_prefix, releases_folder, stamp)
                    run('sudo ln -sf ' + media_folder + ' ' + releases_folder + '/' + stamp + '/media')
                else:
                    print '%s %s/%s/media exist..deleting' % (notice_prefix, releases_folder, stamp)
                    run('sudo rm -rf ' + releases_folder + '/' + stamp + '/media')
                    run('sudo ln -sf ' + media_folder + ' ' + releases_folder + '/' + stamp + '/media')

                print '%s check if our var directory exists within web' % notice_prefix
                if run("test -d %s" % releases_folder + '/' + stamp + '/var').failed:
                    print '%s %s/%s/var not found' % (notice_prefix, releases_folder, stamp)
                    run('sudo ln -sf ' + shared_folder + '/var ' + releases_folder + '/' + stamp + '/var')
                else:
                    print '%s %s/%s/var exist..deleting' % (notice_prefix, releases_folder, stamp)
                    run('sudo rm -rf ' + releases_folder + '/' + stamp + '/var')
                    run('sudo ln -sf ' + shared_folder + '/var ' + releases_folder + '/' + stamp + '/var')


def set_permissions():
    """
    # set permissions
    """
    print '%s set permissions' % notice_prefix
    run('sudo chown -R www-data:root ' + releases_folder + '/' + stamp)
    run('sudo chmod -R 775 ' + releases_folder + '/' + stamp)


def link_to_web():
    """
    # create symlink to web which is our document root, defined at the webserver level
    """
    print 'linking to web'
    with settings(warn_only=True):
            with hide('stdout', 'stderr', 'warnings'):
                print '%s check if our web directory exists' % notice_prefix
                if run("test -d %s" % web_folder).failed:
                    print '%s %s not found' % (notice_prefix, web_folder)
                    print '%s linking to web folder' % notice_prefix
                    run('sudo ln -s ' + releases_folder + '/' + stamp + ' ' + web_folder)
                else:
                    run('sudo rm ' + web_folder)
                    run('sudo ln -s ' + releases_folder + '/' + stamp + ' ' + web_folder)


def list_remote():
    """
    # list git remotes
    """
    print '%s list git remotes' % notice_prefix
    with cd(repo_folder):
        run('sudo git remote -v')


def add_remote(remote_name, remote_url):
    """
    # add a git remote
    """
    print '%s add git remote' % notice_prefix
    with cd(repo_folder):
        run('sudo git remote add ' + remote_name + ' ' + remote_url)


def show_databases(host, username, password):
    """
    # show mysql databases
    """
    run("echo 'show databases;' | mysql -u" + username + ' -p' + password + ' -h ' + host)


def create_database(host, username, password, database_name):
    """
    # create a mysql database
    """
    run("echo 'create database '" + database_name + " | mysql -u" + username + ' -p' + password + ' -h ' + host)


def import_database_archive(host, username, password, database_name, archive_path):
    """
    # import a sql.gz archive into an existing database
    """
    with cd(web_root):
        run('gunzip < ' + archive_path + ' | mysql -u' + username + ' -p' + password + ' ' + database_name)


Magento Python Fabric Deploy Script
===================================
This is a fabric deploy script with extra functions that allow anyone deploy a Magento site

Description
-----------
This fabric deploy script has the ability to

1. Add git remotes to a repo
2. Check if a web directory is sane for deployment
3. Create MYSQL databases
4. Deploy a git repository to a) single host b) group of hosts (roles)
5. Import a gz database archive into a MYSQL database
6. Create  symlink to your web foolder which points to your latest release
7. List the remotes on a git repo
8. Migrate a web folder to the expected structure
9. Prune releases archives
10. Ping a server or group of servers and have them report their latest running kernel
11. Rollback to a previous release
12. Set permissions on a web folder
13. Create an expected folder structure
14. Show MYSQL databases
15. Create symlinks to folders outside of version control eg. media; var; app/etc/local.xml

Installation Instructions
-------------------------
1. Install fabric on your laptop or local machine on ubuntu so : sudo apt-get install fabric
2. Download and configure the fabfile.py with your settings
3. run fab -A -R [role/host] [command]

Web root directory structure
----------------------------
<pre>
/var/
    └── www
        ├──domain.com
            ├── db
            ├── releases
            │   ├── 20140320-2057
            │   ├── 20140320-2200
            │   ├── 20140321-1056
            │   ├── 20140321-1127
            │   └── 20140321-1133
            ├── repo
            ├── shared
            ├── shared
            │   ├── media
            │   └── var
            └── web -> /var/www/domain.com/releases/20140321-1133
</pre>

Examples
--------
fab -A -R [role,host] [command]

examples:
- fab -A -R dev deploy
- fab -A -R dev deploy:master
- fab -A -R dev rollback:2

Available commands
------------------

    add_remote
    check
    create_database
    deploy
    import_database_archive
    link_to_web
    list_remote
    migrate
    prune_releases
    report
    rollback
    set_permissions
    setup
    show_databases
    symlink

Support
-------
If you have any issues with this extension, open an issue on GitHub (see URL above)

Contribution
------------
Any contributions are highly appreciated. The best way to contribute code is to open a
[pull request on GitHub](https://help.github.com/articles/using-pull-requests).

Developer
---------
Winston Nolan

Licence
-------
[OSL - Open Software Licence 3.0](http://opensource.org/licenses/osl-3.0.php)

Copyright
---------
Copyright (c) 2014 Winston Nolan


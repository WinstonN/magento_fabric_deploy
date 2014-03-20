magento_fabric_deploy
=====================

Magento Python Fabric Deploy Script with extra functions

This file will take care of setting your magento project up and deploying it to
your beta and production servers. It can also do a bunch of other things

To view how to use any of these tasks, run fab -d COMMAND

What this file expect
=====================

This file expects your web root to look like

    - /path/to/vhost/root
        - db #keeps a snapshot of your latest db
        - shared #keeps your assets such as a media mount, and var, and perhaps app/etc/local.xml
        - releases #stores your release archives (used for backups [quick rollbacks])
        - repo #where your source will be checkout out to
        - web -> symlink to the latest release


How to run this
=====================

Typically one would do something like

fab -A -R [role,host] [command]

examples:
- fab -A -R dev deploy
- fab -A -R dev deploy:master
- fab -A -R dev rollback:2  

Available commands:

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


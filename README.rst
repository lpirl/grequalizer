The **gr**\ oup **equalizer** helps you to manage the consistency of a 
UNIX user group.

This includes its user's accounts as well as their home directories.

features
--------

* pure Python 3.3
* users to consider are defined by a UNIX user group
* a minimum count of users is configurable
  (so that - for exmaple - grequalizer does not rampage your system
  upon NIS outages)

available plug-ins
******************

* create missing home directories
* archive and remove obsolete home directories

* check and correct the permissions of the home directories
* check and correct the owner of the home directories
* check and correct the group of the home directories

* check and correct the shell of the accounts (passwd)
* check and correct the home directory of the accounts (passwd)

usage
-----

#. Check out the repository
#. Copy ``example_confs/full.conf`` to a place of your preference
#. Read and adapt your configuration carefully
#. Backup
#. In your configuration, set ``simulate = yes``
#. Execute ``python3.3 -O grequalizer.py your_configuration.conf``
   and check the output
#. If you agree with the actions printed there, set ``simulate = no``
#. Re-run ``python3.3 -O grequalizer.py your_configuration.conf``
#. Check if everything went well
#. Put a line like this in your crontab (``crontab -e``):

    ``42 23 * * * python3.3 -O /wherever/grequalizer/grequalizer.py /wherever/grequalizer/your_configuration.conf``

    or, if you are not willing to receive mails with what has been done:

    ``42 23 * * * (python3.3 -O /wherever/homes/grequalizer.py /wherever/grequalizer/your_configuration.conf) > /dev/null``


how to add plug-ins
-------------------

You'll have to implement either of the interfaces specified in
``lib/checks/__init__.py``:

* ``AbstractPerDirectoryCheck``
* ``AbstractPerUserCheck``
* ``AbstractAllUsersAndAllDirectoriesCheck``

Please refer to the existing checks as examples
(``home_permissions.py`` might be a good point to start).

Probably you also want to extend the configuration file with the symbols
you need.

Save your implementation in the module/directory ``lib.checks``
and get started.

contact…
--------

…me if you have any questions.

This script maintains the home directories for users.

For example, use this script to provide an
`Apache UserDir <http://httpd.apache.org/docs/2.2/mod/mod_userdir.html>`_
or a chroot or … for every user in a specific user group.

features
--------

* pure Python 3.3
* works on YP/NIS-enabled systems
* users may be limited to a specific group
* checks for a minimum numbers of users (in case of NIS failures)
* create **missing** home directories
* archive and remove **obsolete** home directories
* check and correct the following configurable properties
  of the home directories

    * **permissions**
    * **owner**
    * **group**

* new checks can be added easily (read the docstrings - there are plenty)

usage
-----

#. Check out the repository
#. Read and adapt ``homes.conf`` carefully

    (for easier updating, put your modified configuration to a separate
    file)

#. Backup
#. In your configuration, set ``simulate = yes``
#. Execute ``python3.3 -O homes.py your_configuration.conf``
   and check the output
#. If you agree with the actions printed there, set ``simulate = no``
#. Re-run ``python3.3 -O homes.py your_configuration.conf``
#. Check if everything went well
#. Put a line like this in your crontab (``crontab -e``):

    ``42 23 * * * python3.3 -O /wherever/homes/homes.py /wherever/homes/your_configuration.conf``

    or, if you are not willing to receive mails with what has been done:
    ``42 23 * * * (python3.3 -O /wherever/homes/homes.py /wherever/homes/your_configuration.conf) > /dev/null``

contact…
--------

…me if you have any questions.

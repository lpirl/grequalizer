# still under development - don't use this yet #

This script aids in managing the users and their chroot directories
of a sftp-only server.

features
--------

* pure Python 3.3
* users may be limited to a specific group
* creates **missing** chroot directories
* archives and removes **obsolete** chroot directories
* checks and corrects the following configurable properties

  * of the chroot directories

    * permissions
    * owner
    * group

  * of the users passwd entries

    * shell
    * home directory

* new checks can be added easily (read the docstrings - there are plenty)

usage
-----

#. Check out the repository
#. Read and adapt ``sftponly.conf`` carefully

    for easier updating, put your modified configuration into a new
    file

#. Backup
#. In your configuration, set ``simulate = yes``
#. Execute ``python3.3 -O sftponly.py your_configuration.conf``
   and check the output
#. If you agree with the actions printed there, set ``simulate = no``
#. Re-run ``python3.3 -O sftponly.py your_configuration.conf``
#. Check if everything went well
#. Put a line like this in your crontab (``crontab -e``):

    ``42 23 * * * python3.3 -O /wherever/sftponly/sftponly.py /wherever/sftponly/your_configuration.conf``

    or, if you are not willing to receive mails with what has been done:

    ``42 23 * * * (python3.3 -O /wherever/homes/sftponly.py /wherever/sftponly/your_configuration.conf) > /dev/null``

contact…
--------

…me if you have any questions.

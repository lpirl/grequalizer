from lib.checks import AbstractPerUserCheck

class UserHomeDirectoryCheck(AbstractPerUserCheck):
    """
    Checks whether the home directory in passwd is set according to the
    configuration..
    """

    config_section = "user_home"

    order = 50

    def get_expanded_home_path_for_user(self, user):
        return UserHomeDirectoryCheck.expand_string_for_user(
            self.options.get_str('home_path'), user
        )

    def is_correct(self, user):
        """
        Checks correctness for a single user home directory passwd entry.
        """
        desired_path = self.get_expanded_home_path_for_user(user)
        return user.pw_dir == desired_path

    def correct(self, user):
        """
        Corrects a users home directory passwd entry.
        """
        self.execute_subprocess_safely(
            'usermod',
            '-d',
            self.get_expanded_home_path_for_user(user),
            user.pw_name
        )

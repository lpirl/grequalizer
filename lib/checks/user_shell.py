from lib.checks import AbstractPerUserCheck

class UserShellCheck(AbstractPerUserCheck):
    """
    Checks whether the shell in passwd is set according to the
    configuration.
    """

    config_section = "user_shell"

    order = 50

    def get_expanded_shell_for_user(self, user):
        return UserShellCheck.expand_string_for_user(
            self.options.get_str('shell'), user
        )

    def is_correct(self, user):
        """
        Checks correctness for a single users shell passwd entry.
        """
        desired_path = self.get_expanded_shell_for_user(user)
        return user.pw_shell == desired_path

    def correct(self, user):
        """
        Corrects a users shell passwd entry.
        """
        self.execute_subprocess_safely([
            'usermod',
            '-s',
            self.get_expanded_shell_for_user(user),
            user.pw_name
        ])

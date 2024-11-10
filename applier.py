import os
import argparse


def arg_parse():
    parser = argparse.ArgumentParser(
        prog="applier",
        description="Automatically apply cherry-picks to multiple repos at the same time.",
        epilog="Cherry-pick Applier - ThinkShield Enterprise v1.0",
    )

    return Args(parser).parse()


class Args:

    _OPTIONS_FILEPATH_DEFAULT = {
        "type": str,
        "required": True,
        "help": "The absolute path to a file with a list of Gerrit links.",
    }

    _OPTIONS_USERNAME_DEFAULT = {
        "type": str,
        "default": os.getenv("GERRIT_USERNAME"),
        "help": "Set a Gerrit user to use with this session. Otherwise, export a GERRIT_USER enviroment variable.",
    }

    _OPTIONS_PASSWORD_DEFAULT = {
        "type": str,
        "default": os.getenv("GERRIT_PASSWORD"),
        "help": "Set a Gerrit password to use with this session. Otherwise, export a GERRIT_PASSWORD enviroment variable.",
    }

    _OPTIONS_BRANCH_DEFAULT = {
        "type": str,
        "metavar": "BRANCH_NAME",
        "help": "Choose a branch name to be created in the repos where the cherry-picks will took place.",
    }

    _OPTIONS_AOSP_PATH_DEFAULT = {
        "type": str,
        "help": "The absolute path of the AOSP root. If not set, execute this program from the root.",
    }

    _OPTIONS_THREADS_DEFAULT = {
        "action": "store_false",
        "help": "If you don't want the program using threads.",
    }

    _ARGUMENTS = [
        [["-f", "--filepath"], _OPTIONS_FILEPATH_DEFAULT],
        [["-u", "--username"], _OPTIONS_USERNAME_DEFAULT],
        [["-p", "--password"], _OPTIONS_PASSWORD_DEFAULT],
        [["-b", "--new-branch"], _OPTIONS_BRANCH_DEFAULT],
        [["-a", "--aosp-path"], _OPTIONS_AOSP_PATH_DEFAULT],
        [["--no-threads"], _OPTIONS_THREADS_DEFAULT],
    ]

    _parser = None

    def __init__(self, parser):
        self._set_parser(parser)

    def _set_parser(self, parser) -> None:
        if parser is None:
            raise ValueError("Parser parameter cannot be None")

        self._parser = parser

    def _get_parser(self):
        return self._parser

    def parse(self):
        self._set_arguments()
        return self._get_parser().parse_args()

    def _set_arguments(self):
        for item in self._ARGUMENTS:
            self._get_parser().add_argument(*item[0], **item[1])


class Applier:

    def __init__(self, parser):
        pass


class Connector:

    def __init__(self, user, password):
        pass


if __name__ == "__main__":
    arg = arg_parse()

    print(f"filepath: {arg.filepath}")
    print(f"username: {arg.username}")
    print(f"password: {arg.password}")
    print(f"new_branch: {arg.new_branch}")
    print(f"aosp_path: {arg.aosp_path}")
    print(f"use_threads: {arg.no_threads}")

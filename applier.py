#!/usr/bin/env python3

from requests.auth import HTTPBasicAuth
from threading import Thread, Lock
from argparse import Namespace
from typing import Optional, Dict
import argparse
import json
import os
import re
import requests
import subprocess


class GerritConnectionError(Exception):
    pass


def arg_parse() -> Namespace:
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
        "help": "Set a Gerrit user to use with this session. Otherwise, export a GERRIT_USERNAME enviroment variable.",
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
        "help": "The absolute path of the AOSP root. If not set, execute this program from the AOSP root.",
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

    _parser: Optional[Namespace] = None

    def __init__(self, parser: Namespace):
        self._set_parser(parser)

    def _set_parser(self, parser: Namespace) -> None:
        if parser is None:
            raise ValueError("Parser parameter cannot be None")

        self._parser = parser

    def _get_parser(self) -> Namespace:
        return self._parser

    def parse(self):
        self._set_arguments()
        return self._get_parser().parse_args()

    def _set_arguments(self):
        for item in self._ARGUMENTS:
            self._get_parser().add_argument(*item[0], **item[1])


class Applier:

    _connector: Optional["GerritConnector"] = None

    _mutex = Lock()

    def __init__(self, parser: Namespace):
        self._parser: Namespace = parser
        self._set_connector()
        self._filepath: str = self._parser.filepath
        self._new_branch: Optional[str] = self._parser.new_branch
        self._use_threads: bool = self._parser.no_threads
        self._aosp_path: Optional[str] = self._parser.aosp_path
        self._reset: Optional[int] = self._parser.reset

        self._branches: Dict[str, bool] = {}

    def _set_connector(self):
        if self._parser.username is None or self._parser.password is None:
            raise ValueError(
                "Nor username or password cannot be None. Please export the enviroment variables or pass via arguments."
            )

        self._connector = GerritConnector(self._parser.username, self._parser.password)

    def _get_connector(self) -> "GerritConnector":
        return self._connector

    def apply(self) -> None:
        self._apply_internal()

    def _extract_path(self, url: str) -> str:
        pos = max(url.rfind("android"), url.rfind("platform"))
        return url[pos + len("android/") :].lstrip("/") if pos != -1 else None

    def _apply_internal(self) -> None:
        with open(self._filepath, "r") as f:
            urls = f.read().split("\n")

        if self._use_threads == True:
            self._run_with_threads(urls)
        else:
            self._run_without_threads(urls)

    def _apply_individual(self, url: str) -> None:
        change_id = re.findall(r"(\d+)", url)[0]
        cp_command = self._get_connector().get_cherry_pick_command(change_id)

        cp_url, refs = re.findall(r"(?:\w+ \w+) ([^ ]+) ([^ ]+)", cp_command)[0]

        path = self._get_aosp_path() + self._extract_path(cp_url)

        if self._new_branch is not None and len(self._new_branch) > 0:
            with self._mutex:
                if self._branches.get(path) is None:
                    self._run_command(self._build_new_branch_command(path, self._new_branch))
                    self._branches[path] = True

        self._run_command(self._build_cherry_pick_command(path, cp_url, refs))

    def _get_aosp_path(self) -> str:
        if self._aosp_path is not None:
            if self._aosp_path.endswith("/"):
                return self._aosp_path
            else:
                return self._aosp_path + "/"

        return ""

    def _run_with_threads(self, urls: str) -> None:
        threads = []
        for url in urls:
            if len(url) > 0:
                threads.append(Thread(target=self._apply_individual, args=(url,)))

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

    def _run_without_threads(self, urls: str) -> None:
        for url in urls:
            if len(url) > 0:
                self._apply_individual(url)

    def _build_cherry_pick_command(self, path: str, url: str, refs: str) -> str:
        return f"git -C {path} fetch {url} {refs} && git -C {path} cherry-pick FETCH_HEAD"

    def _build_new_branch_command(self, path: str, branch_name: str) -> str:
        return f"git -C {path} checkout -b {branch_name}"

    def _run_command(self, command: str) -> None:
        subprocess.run(command, shell=True, executable="/bin/bash")


class GerritConnector:

    _url = "https://gerrit.mot.com/a/changes/?q=CHANGE_ID&o=CURRENT_REVISION&o=CURRENT_COMMIT&o=CURRENT_FILES&o=DOWNLOAD_COMMANDS"

    def __init__(self, user: str, password: str):
        self.user = user
        self.password = password

    def _request(self, change_id: str):
        response = requests.get(
            self._url.replace("CHANGE_ID", change_id),
            auth=HTTPBasicAuth(self.user, self.password),
        )

        if response.status_code == 200:
            return response

        raise GerritConnectionError(f"Failed to access Gerrit API. Status code: {response.status_code}")

    def get_cherry_pick_command(self, change_id: str) -> str:
        response = self._request(change_id)

        response_text = response.text[5:] if response.text.startswith(")]}'") else response.text
        response_json = json.loads(response_text)[0]
        current_revision = response_json["current_revision"]
        return response_json["revisions"][current_revision]["fetch"]["ssh"]["commands"]["Cherry Pick"]


if __name__ == "__main__":
    Applier(arg_parse()).apply()

from collections import UserList
from typing import Iterable, List

from parser import ConfParser


class EmptyRawError(Exception):
    ...


class Host:
    def __init__(
            self,
            name: str,
            ethernet: str | None = None,
            is_deny_booting: bool = False,
            condition_true_filename: str | None = None,
            condition_false_filename: str | None = None,
            fixed_addr: str | None = None
    ):
        self.name = name
        self.is_child = "alt" in self.name
        self.ethernet = ethernet
        self.is_deny_booting = is_deny_booting
        self.condition_true_filename = condition_true_filename
        self.condition_false_filename = condition_false_filename
        self.fixed_addr = fixed_addr
        self._raw = ""
        self.child_hosts = []

    def get_config_body(self, use_raw: bool = False):
        if use_raw:
            return self._get_raw()
        options = "\tdeny booting;" if self.is_deny_booting else f"""if option arch = 00:07 {{
        filename "{self.condition_true_filename}";
    }} else {{
        filename "{self.condition_false_filename}";
    }}
    fixed-address {self.fixed_addr};
    """

        return f"""hardware ethernet {self.ethernet};
    {options}"""

    def get_config_string(self, use_raw: bool = False):
        return f"""host {self.name} {{
    {self.get_config_body(use_raw)}
}}"""

    def _get_raw(self):
        if not self._raw:
            raise EmptyRawError("Raw is empty")
        return self._raw

    def set_raw_value(self, raw: str):
        self._raw = raw
        self.is_deny_booting = ConfParser.is_deny_booting(raw)
        if not self.is_deny_booting:
            self.ethernet = ConfParser.get_ethernet(raw)
            self.condition_true_filename, self.condition_false_filename = ConfParser.get_filenames(raw)
            self.fixed_addr = ConfParser.get_fixed_addr(raw)
        else:
            self.ethernet = None
            self.condition_true_filename, self.condition_false_filename = None, None
            self.fixed_addr = None

    def __repr__(self):
        params = ", ".join([f"{key}: {getattr(self, key)}" for key in self.__dict__.keys() if not key.startswith("__")])
        return f"<{params}>"


class HostWithoutMother(Exception):
    ...


class Hosts(UserList):
    def __init__(self, iterable: Iterable | None = None):
        iterable = [] if iterable is None else iterable
        super().__init__(iterable)
        self.is_nested = False

    def make_nested(self):
        hosts = []
        child_hosts = []
        for host in self.data:
            if host.is_child:
                child_hosts.append(host)
            else:
                hosts.append(host)

        while child_hosts:
            parent_found = False
            child_host = child_hosts.pop()
            parent_name = child_host.name.split("alt")[0]
            for host in hosts:
                if host.name == parent_name:
                    parent_found = True
                    host.child_hosts.append(child_host)

            if not parent_found:
                raise HostWithoutMother(f"{child_host.name} has no mother!")

        self.data = hosts
        self.is_nested = True

    def sort_hosts_by_name(self, sort_child=False):
        self.sort(key=lambda x: x.name)
        if sort_child:
            for host in self.data:
                host.child_hosts.sort(key=lambda x: x.name)

    def find_by_name(self, name: str) -> Host | None:
        for host in self.data:
            if host.name == name:
                return host

            if self.is_nested:
                for child_host in host.child_hosts:
                    if child_host.name == name:
                        return child_host
        return None


def get_all_hosts_from_config_lines(lines: str) -> Hosts:
    all_hosts = Hosts()
    for re_host in ConfParser.get_host_matches(lines):
        start_brackets_pointer, end_brackets_pointer = ConfParser.get_host_boundaries(re_host, lines)
        host_lines = lines[start_brackets_pointer:end_brackets_pointer]
        ethernet = ConfParser.get_ethernet(host_lines)
        name = ConfParser.get_name(re_host)

        if ConfParser.is_deny_booting(host_lines):
            all_hosts.append(Host(name=name, ethernet=ethernet, is_deny_booting=True))
        else:
            condition_true_filename, condition_false_filename = ConfParser.get_filenames(host_lines)
            fixed_addr = ConfParser.get_fixed_addr(host_lines)
            all_hosts.append(
                Host(
                    name=name,
                    ethernet=ethernet,
                    condition_true_filename=condition_true_filename,
                    condition_false_filename=condition_false_filename,
                    fixed_addr=fixed_addr
                )
            )
    return all_hosts


def save_host_changes(filename: str, host: Host, use_raw: bool = False):
    with open(filename, "r") as f:
        lines = f.read()

    re_host = ConfParser.get_host_match(host.name, lines)
    start_brackets_pointer, end_brackets_pointer = ConfParser.get_host_boundaries(re_host, lines)
    new_lines = lines[:re_host.start()] + host.get_config_string(use_raw) + lines[end_brackets_pointer:]

    with open(filename, "w") as f:
        f.write(new_lines)


def add_host(filename: str, host: Host, use_raw: bool = False):
    with open(filename, "a+") as f:
        try:
            f.seek(0, 2)
            f.seek(f.tell() - 1)
            start_symbol = "\n" if f.read(1) == "\n" else ""
        except ValueError:
            start_symbol = ""
        f.write(f"{start_symbol}{host.get_config_string(use_raw)}\n")


def delete_host(filename: str, host: Host):
    with open(filename, "r") as f:
        lines = f.read()

    re_host = ConfParser.get_host_match(host.name, lines)
    start_host_pointer = re_host.start()
    start_brackets_pointer, end_brackets_pointer = ConfParser.get_host_boundaries(re_host, lines)
    new_lines = lines[:start_host_pointer] + lines[end_brackets_pointer:]

    with open(filename, "w") as f:
        f.write(new_lines)


def delete_host_names(filename: str, host_names: List[str]):
    with open(filename, "r") as f:
        lines = f.read()
    for host_name in host_names:
        re_host = ConfParser.get_host_match(host_name, lines)
        start_host_pointer = re_host.start()
        start_brackets_pointer, end_brackets_pointer = ConfParser.get_host_boundaries(re_host, lines)
        lines = lines[:start_host_pointer] + lines[end_brackets_pointer:]

    with open(filename, "w") as f:
        f.write(lines)

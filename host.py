from collections import UserList
from typing import Iterable

from parser import ConfParser


class Host:
    def __init__(
        self,
        name: str,
        ethernet: str,
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
        options = "deny booting;" if self.is_deny_booting else f"""
        if option arch = 00:07 {{
            filename "{self.condition_true_filename}";
        }} else {{
            filename "{self.condition_false_filename}";
        }}
        fixed-address {self.fixed_addr};
        """

        return f"""
        hardware ethernet {self.ethernet};
        {options}
        """

    def get_config_string(self, use_raw: bool = False):
        return f"""host {self.name} {{
            {self.get_config_body(use_raw)}
        }}"""

    def _get_raw(self):
        if not self._raw:
            raise Exception("Raw is empty")
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
            child_host = child_hosts.pop()
            parent_name = child_host.name.split("alt")[0]
            for host in hosts:
                if host.name == parent_name:
                    host.child_hosts.append(child_host)
        self.data = hosts
        self.is_nested = True

    def find_by_name(self, name: str) -> Host | None:
        for host in self.data:
            if host.name == name:
                return host

            if self.is_nested:
                for child_host in host.child_hosts:
                    if child_host.name == name:
                        return child_host
        return None

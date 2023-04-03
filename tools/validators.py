import re

from host import Hosts


def validate_new_hostname(hostname: str, hosts: Hosts):
    if len(hostname) < 2:
        raise ValueError("Hostname must be > 2 symbols")

    if hosts.find_by_name(hostname) is not None:
        raise ValueError("Hostname already exists")


def validate_ethernet(ethernet: str):
    pattern = re.compile("^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$")
    if not pattern.match(ethernet):
        raise ValueError("Ethernet not valid!")


def validate_host_pattern_option(option: str):
    if option not in ("d", "r", "ie"):
        raise ValueError("Not supported pattern option!")


def validate_ipv4_address(ip: str):
    pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if re.match(pattern, ip):
        octets = ip.split('.')
        if all(0 <= int(octet) <= 255 for octet in octets):
            return
    raise ValueError("Not valid IPv4!")


def validate_filename(filename):
    """Return True if filename is a valid filename."""
    reserved_chars = ['<', '>', ':', '"', '\\', '|', '?', '*']

    if any(char in reserved_chars for char in filename):
        raise ValueError("Not valid filename! You can't use reserved chars!")

    if len(filename) < 2:
        raise ValueError("Not valid filename! filename cant be < 2 symbols!")

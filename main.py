from host import Hosts, Host
from parser import ConfParser


def get_all_hosts_from_file(filename: str) -> Hosts:
    with open(filename) as f:
        lines = f.read()

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


def update_host(filename: str, host: Host, use_raw: bool = False):
    with open(filename, "r") as f:
        lines = f.read()

    re_host = ConfParser.get_host_match(host.name, lines)
    start_brackets_pointer, end_brackets_pointer = ConfParser.get_host_boundaries(re_host, lines)
    new_lines = lines[:start_brackets_pointer + 1] + host.get_config_body(use_raw) + lines[end_brackets_pointer - 1:]

    with open(filename, "w") as f:
        f.write(new_lines)


def add_host(filename: str, host: Host, use_raw: bool = False):
    with open(filename, "a") as f:
        f.write(f"\n{host.get_config_string(use_raw)}")


def delete_host(filename: str, host: Host):
    with open(filename, "r") as f:
        lines = f.read()

    re_host = ConfParser.get_host_match(host.name, lines)
    start_host_pointer = re_host.start()
    start_brackets_pointer, end_brackets_pointer = ConfParser.get_host_boundaries(re_host, lines)
    new_lines = lines[:start_host_pointer] + lines[end_brackets_pointer:]

    with open(filename, "w") as f:
        f.write(new_lines)


if __name__ == "__main__":
    hosts = get_all_hosts_from_file("dhcpd.conf")
    hosts.make_nested()
    host = hosts.find_by_name("srv2alt1")
    delete_host("dhcpd.conf", host)

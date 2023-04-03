from typing import List

from host import get_all_hosts_from_file, Host, add_host, delete_host_names, save_host_changes, EmptyRawError
from tools.input import multiple_line_input
from tools.validators import validate_new_hostname, validate_ethernet, validate_host_pattern_option, validate_filename, \
    validate_ipv4_address


def _get_ethernet():
    while True:
        ethernet = input("Ethernet: ").strip()
        try:
            validate_ethernet(ethernet)
            break
        except ValueError as error:
            print(f"Error: {error}\n")
    return ethernet


def _get_condition_filename(condition: str):
    while True:
        condition_filename = input(f"{condition} filename: ").strip()
        try:
            validate_filename(condition_filename)
            break
        except ValueError as error:
            print(f"Error: {error}\n")
    return condition_filename


def _get_fixed_addr():
    while True:
        fixed_addr = input("fixed-address: ").strip()
        try:
            validate_ipv4_address(fixed_addr)
            break
        except ValueError as error:
            print(f"Error: {error}\n")
    return fixed_addr


def add_new_host_with_cli(filename: str):
    while True:
        hostname = input("Hostname: ").strip()
        hosts = get_all_hosts_from_file(filename)
        try:
            validate_new_hostname(hostname, hosts)
            break
        except ValueError as error:
            print(f"Error: {error}\n")

    print("\nHost pattern options:")
    print("1) Raw (R)")
    print("2) Deny booting (D)")
    print("3) If-else filenames (IE)")
    while True:
        host_pattern = input("Host pattern (R/D/IE): ").lower().strip()
        try:
            validate_host_pattern_option(host_pattern)
            break
        except ValueError as error:
            print(f"Error: {error}\n")

    if host_pattern == "r":
        print("""Warning! We don't validate RAW value,
    but lines at least must contain 'deny booting;' or 'hardware ethernet', if-else filenames and fixed-address
    Raw config value: """)
        raw = multiple_line_input(with_left_strip=True)
        host = Host(name=hostname)
        host.set_raw_value(raw)
        add_host(filename, host, use_raw=True)

    elif host_pattern == "d":
        ethernet = _get_ethernet()
        host = Host(name=hostname, ethernet=ethernet, is_deny_booting=True)
        add_host(filename, host)
    elif host_pattern == "ie":
        ethernet = _get_ethernet()
        condition_true_filename = _get_condition_filename("if option arch = 00:07")
        condition_false_filename = _get_condition_filename("else")
        fixed_addr = _get_fixed_addr()

        host = Host(
            name=hostname,
            ethernet=ethernet,
            condition_true_filename=condition_true_filename,
            condition_false_filename=condition_false_filename,
            fixed_addr=fixed_addr
        )
        add_host(filename, host)


def update_host_with_cli(filename: str, hostname: str):
    hosts = get_all_hosts_from_file(filename)
    host = hosts.find_by_name(hostname)

    if host is None:
        raise ValueError(f"Host {hostname} do not exist!")

    while True:
        print(f"\nCurrent host configuration:\n{host.get_config_string()}")
        print("\nChoose an option:")
        print("1. Change Ethernet")
        print("2. Toggle deny booting")
        print("3. Change condition true filename")
        print("4. Change condition false filename")
        print("5. Change fixed address")
        print("6. Set raw value")
        print("7. Save and exit")
        print("e. Exit without saving")

        action = input("Option: ").strip().lower()

        if action.lower() == "e":
            break

        if action == "7":
            try:
                print(f"Raw: \n{host.get_config_string(True)}")
                print(f"Not raw: \n{host.get_config_string(False)}")

                use_raw = None
                while use_raw is None:
                    option = input("Use raw(y, n):")
                    if option.lower() == "y":
                        use_raw = True
                    elif option.lower() == "n":
                        use_raw = False
            except EmptyRawError:
                use_raw = False

            save_host_changes(filename, host, use_raw)
            break

        if action == "1":
            ethernet = _get_ethernet()
            host.ethernet = ethernet
        elif action == "2":
            host.is_deny_booting = not host.is_deny_booting
            if not host.is_deny_booting:
                condition_true_filename = _get_condition_filename("if option arch = 00:07")
                host.condition_true_filename = condition_true_filename

                condition_false_filename = _get_condition_filename("else")
                host.condition_false_filename = condition_false_filename

                fixed_addr = _get_fixed_addr()
                host.fixed_addr = fixed_addr
        elif action == "3":
            condition_true_filename = _get_condition_filename("if option arch = 00:07")
            host.condition_true_filename = condition_true_filename
        elif action == "4":
            condition_false_filename = _get_condition_filename("else")
            host.condition_false_filename = condition_false_filename
        elif action == "5":
            fixed_addr = _get_fixed_addr()
            host.fixed_addr = fixed_addr
        elif action == "6":
            print("""\nWarning! We don't validate RAW value,
                    but lines at least must contain 'deny booting;' or 'hardware ethernet', if-else filenames and fixed-address\nRaw config value: """)
            raw = multiple_line_input(with_left_strip=True)
            host.set_raw_value(raw)
        else:
            print(f"Invalid option: {action}")


def remove_hosts_from_file(filename: str, host_names: List[str]):
    hosts = get_all_hosts_from_file(filename)
    for hostname in host_names:
        if hosts.find_by_name(hostname) is None:
            raise ValueError(f"Host {hostname} do not exist!")
    delete_host_names(filename, host_names)

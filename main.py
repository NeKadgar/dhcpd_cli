import os
import argparse

from tools.cli import add_new_host_with_cli, remove_hosts_from_file, update_host_with_cli


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='DHCPD Internal CLI tool')
    parser.add_argument('--file', type=str, help='Path to DHCPD config file', required=True)

    add_upd_rm_group = parser.add_mutually_exclusive_group(required=True)
    add_upd_rm_group.add_argument('--add', action='store_true', help='Add new host')
    add_upd_rm_group.add_argument('--update', type=str, help='Update hostname')
    add_upd_rm_group.add_argument('--rm', nargs='+', type=str, help='Host names to be removed')
    args = parser.parse_args()

    if not os.path.exists(args.file):
        parser.error(f'{args.file} not exist. Please check for typo!!')

    if args.add:
        add_new_host_with_cli(args.file)
    elif args.rm:
        remove_hosts_from_file(args.file, args.rm)
    elif args.update:
        update_host_with_cli(args.file, args.update)

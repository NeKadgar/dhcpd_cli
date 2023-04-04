import os
import argparse

from tools.cli import add_new_host_with_cli, remove_hosts_from_file, update_host_with_cli, refactor_config_file, \
    sort_hosts_in_file


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='DHCPD Internal CLI tool')
    parser.add_argument('--file', type=str, help='Path to DHCPD config file', required=True)

    parser.add_argument('--refactor', action='store_true', help='Refactor file')
    parser.add_argument('--sort', action='store_true', help='Sort hosts')
    parser.add_argument('--backup', action='store_true', help='Create backup file')

    add_upd_rm_group = parser.add_mutually_exclusive_group()
    add_upd_rm_group.add_argument('--add', action='store_true', help='Add new host')
    add_upd_rm_group.add_argument('--update', type=str, help='Update hostname')
    add_upd_rm_group.add_argument('--rm', nargs='+', type=str, help='Host names to be removed')
    args = parser.parse_args()

    if not os.path.exists(args.file):
        parser.error(f'{args.file} not exist. Please check for typo!!')

    if args.backup:
        with open(args.file, "r") as f:
            with open(f"{args.file}.backup", "w") as backup_file:
                backup_file.write(f.read())

    if args.add:
        add_new_host_with_cli(args.file)
    elif args.rm:
        remove_hosts_from_file(args.file, args.rm)
    elif args.update:
        update_host_with_cli(args.file, args.update)

    if args.sort:
        sort_hosts_in_file(args.file)

    if args.refactor:
        refactor_config_file(args.file)

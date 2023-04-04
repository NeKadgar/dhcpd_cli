# DHCPD Internal CLI tool
This is a command-line tool for managing DHCPD hosts in the dhcpd.conf file.


## How to use:
### Add host:
```shell
python main.py --file dhcpd.conf --add
```
This command adds a new host to the dhcpd.conf file.

### Update host:
```shell
python main.py --file dhcpd.conf --update srv1
```
This command updates an existing host with the specified name srv1 in the dhcpd.conf file.

### Remove hosts:
```shell
python main.py --file dhcpd.conf --rm srv1 srv2 srv3
```
This command removes the specified hosts (srv1, srv2, and srv3) from the dhcpd.conf file.

## Optional: 
You can combine optional flags with any command you want to use.
Example of use:
```shell
python main.py --file dhcpd.conf --add --backup --sort --refactor
```
This command create backup file before any operation, after shows CLI to add new host and after sort all the hosts and fixes a whitespaces.

### Refactor file:
```shell
python main.py --file dhcpd.conf --refactor
```
This command fix all the spaces in the dhcpd.conf file.

### Sort hosts in file:
```shell
python main.py --file dhcpd.conf --sort
```
This command sort by name all hosts in file, if host have any child hosts they will be placed right after parent.

### Create backup file:
```shell
python main.py --file dhcpd.conf --backup
```
This command create filename.backup file that contains a version before any changes.

## To run tests use:
```shell
python -m unittest discover -s tests/
```

## Supported host types:
Our tool supports only the following types of hosts in the dhcpd.conf file:
```shell
host srv2 {
    hardware ethernet 00:8C:FA:5B:0C:48;
	if option arch = 00:07 {
        filename "srv2/ipxe64.efi";
    } else {
        filename "srv2/undionly.kpxe";
    }
    fixed-address 38.68.33.3;
    option option-151 "http://10.32.47.6:1500/dcimini?func=dcimini.osinstall.info&id=zL0vPX8iGvwkfl";
}
```
In this host definition, you can change the ethernet address, filenames for both conditions, and fixed-address.
```shell
host srv2alt1 {
    hardware ethernet F0:4D:A2:74:E0:4C;
      deny booting;
}
```
This host definition denies booting and sets the hardware ethernet address.

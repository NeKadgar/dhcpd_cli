import os
import tempfile
import unittest
import sys
from unittest.mock import patch
from io import StringIO
from tempfile import NamedTemporaryFile

from host import Host, Hosts
from tools.cli import add_new_host_with_cli, update_host_with_cli


class TestAddNewHostWithCLI(unittest.TestCase):
    def setUp(self):
        suppress_text = StringIO()
        sys.stdout = suppress_text
        # Create a temporary file to use as the hosts file
        self.hosts_file = NamedTemporaryFile(mode='w', delete=False)

    def tearDown(self):
        # Delete the temporary hosts file
        self.hosts_file.close()
        os.unlink(self.hosts_file.name)
        sys.stdout = sys.__stdout__

    @patch('tools.cli.multiple_line_input', side_effect=["hardware ethernet F0:4D:A2:74:E0:4C;\ndeny booting;"])
    @patch('builtins.input', side_effect=['srv1', 'R', 'deny booting;', ''])
    def test_add_raw_host(self, *args):
        # Call add_new_host_with_cli with the mocked input values
        add_new_host_with_cli(self.hosts_file.name)

        # Check that the host was added to the file correctly
        with open(self.hosts_file.name, 'r') as f:
            lines = f.read()
        self.assertIn('srv1', lines)
        self.assertIn('deny booting;', lines)
        self.assertIn('F0:4D:A2:74:E0:4C', lines)

    @patch('builtins.input', side_effect=['srv1', 'D', '00:11:22:33:44:55', ''])
    def test_add_deny_boot_host(self, mock_input):
        # Call add_new_host_with_cli with the mocked input values
        add_new_host_with_cli(self.hosts_file.name)

        # Check that the host was added to the file correctly
        with open(self.hosts_file.name, 'r') as f:
            lines = f.read()

        self.assertIn('deny booting;', lines)
        self.assertIn('hardware ethernet 00:11:22:33:44:55;', lines)
        self.assertIn('srv1', lines)

    @patch(
        'builtins.input',
        side_effect=['srv1', 'IE', '00:11:22:33:44:55', 'true.conf', 'false.conf', '192.168.0.1', '']
    )
    def test_add_if_else_host(self, mock_input):
        # Call add_new_host_with_cli with the mocked input values
        add_new_host_with_cli(self.hosts_file.name)

        # Check that the host was added to the file correctly
        with open(self.hosts_file.name, 'r') as f:
            lines = f.read()
        self.assertIn('hardware ethernet 00:11:22:33:44:55;', lines)
        self.assertIn('if option arch = 00:07 {', lines)
        self.assertIn('filename "true.conf";', lines)
        self.assertIn('else {', lines)
        self.assertIn('filename "false.conf";', lines)
        self.assertIn('fixed-address 192.168.0.1;', lines)
        self.assertIn('host srv1', lines)


class TestUpdateHostWithCli(unittest.TestCase):
    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.host1 = Host("test1", "11:11:11:11:11:11", False, "filename1", "filename2", "10.0.0.2")
        self.host2 = Host("test2", "22:22:22:22:22:22", False, "filename3", "filename4", "10.0.0.4")
        self.host3 = Host("test3", "33:33:33:33:33:33", False, "filename5", "filename6", "10.0.0.6")
        self.host4 = Host("test4", "44:33:33:33:33:33", True)
        self.hosts = Hosts([
            self.host1, self.host2, self.host3, self.host4
        ])
        with open(self.temp_file.name, "w") as f:
            for host in self.hosts:
                f.write(host.get_config_string() + "\n")
        suppress_text = StringIO()
        sys.stdout = suppress_text

    def tearDown(self):
        os.unlink(self.temp_file.name)
        sys.stdout = sys.__stdout__

    def test_update_ethernet(self):
        with patch('builtins.input', side_effect=['1', '12:12:12:12:12:12', '7']):
            with patch('tools.cli.get_all_hosts_from_config_lines', return_value=self.hosts):
                with patch('tools.cli.save_host_changes') as save_changes:
                    update_host_with_cli(self.temp_file.name, self.host2.name)
                    self.assertEqual(self.host2.ethernet, '12:12:12:12:12:12')
                    self.assertEqual(save_changes.call_count, 1)

    def test_toggle_deny_booting__to_true(self):
        with patch('builtins.input', side_effect=['2', '7']):
            with patch('tools.cli.get_all_hosts_from_config_lines', return_value=self.hosts):
                with patch('tools.cli.save_host_changes') as save_changes:
                    update_host_with_cli(self.temp_file.name, self.host2.name)
                    self.assertTrue(self.host2.is_deny_booting)
                    self.assertEqual(save_changes.call_count, 1)

    def test_toggle_deny_booting__to_false(self):
        condition_true_filename = "/dev/condition_true_filename.txt"
        condition_false_filename = "./condition_false_filename.txt"
        fixed_addr = "12.12.12.12"
        with patch('builtins.input',
                   side_effect=['2', condition_true_filename, condition_false_filename, fixed_addr, '7']):
            with patch('tools.cli.get_all_hosts_from_config_lines', return_value=self.hosts):
                with patch('tools.cli.save_host_changes') as save_changes:
                    update_host_with_cli(self.temp_file.name, self.host4.name)
                    self.assertFalse(self.host4.is_deny_booting)
                    self.assertEqual(self.host4.fixed_addr, fixed_addr)
                    self.assertEqual(self.host4.condition_true_filename, condition_true_filename)
                    self.assertEqual(self.host4.condition_false_filename, condition_false_filename)
                    self.assertEqual(save_changes.call_count, 1)

    def test_change_condition_true_filename(self):
        condition_true_filename = "/dev/condition_true_filename.txt"
        with patch('builtins.input', side_effect=['3', condition_true_filename, '7']):
            with patch('tools.cli.get_all_hosts_from_config_lines', return_value=self.hosts):
                with patch('tools.cli.save_host_changes') as save_changes:
                    update_host_with_cli(self.temp_file.name, self.host1.name)
                    self.assertEqual(self.host1.condition_true_filename, condition_true_filename)
                    self.assertEqual(save_changes.call_count, 1)

    def test_change_condition_false_filename(self):
        condition_false_filename = "/dev/condition_false_filename.txt"
        with patch('builtins.input', side_effect=['4', condition_false_filename, '7']):
            with patch('tools.cli.get_all_hosts_from_config_lines', return_value=self.hosts):
                with patch('tools.cli.save_host_changes') as save_changes:
                    update_host_with_cli(self.temp_file.name, self.host1.name)
                    self.assertEqual(self.host1.condition_false_filename, condition_false_filename)
                    self.assertEqual(save_changes.call_count, 1)

    def test_change_fixed_addr(self):
        fixed_addr = "255.255.255.255"
        with patch('builtins.input', side_effect=['5', fixed_addr, '7']):
            with patch('tools.cli.get_all_hosts_from_config_lines', return_value=self.hosts):
                with patch('tools.cli.save_host_changes') as save_changes:
                    update_host_with_cli(self.temp_file.name, self.host1.name)
                    self.assertEqual(self.host1.fixed_addr, fixed_addr)
                    self.assertEqual(save_changes.call_count, 1)

    def test_change_fixed_addr__with_wrong_addr(self):
        fixed_addr = "255.255.255.255"
        wrong_fixed_addr = "255.255.255.256"
        with patch('builtins.input', side_effect=['5', wrong_fixed_addr, fixed_addr, '7']):
            with patch('tools.cli.get_all_hosts_from_config_lines', return_value=self.hosts):
                with patch('tools.cli.save_host_changes') as save_changes:
                    update_host_with_cli(self.temp_file.name, self.host1.name)
                    self.assertEqual(self.host1.fixed_addr, fixed_addr)
                    self.assertEqual(save_changes.call_count, 1)

    def test_set_raw_value(self):
        new_ethernet = "00:8C:FA:5B:0C:48"
        new_condition_true_filename = "srv2/ipxe64.efi"
        new_condition_false_filename = "srv2/undionly.kpxe"
        new_address = "38.68.33.3"
        options = 'option option-151 "http://10.32.47.6:1500/dcimini?func=dcimini.osinstall.info&id=zL0vPX8iGvwkfl";'
        with patch('builtins.input', side_effect=['6', '7', 'y']):
            with patch('tools.cli.multiple_line_input', return_value=f"""
                hardware ethernet {new_ethernet};
                if option arch = 00:07 {{
                    filename "{new_condition_true_filename}";
                }} else {{
                    filename "{new_condition_false_filename}";
                }}
                fixed-address {new_address};
                {options}
            """):
                with patch('tools.cli.get_all_hosts_from_config_lines', return_value=self.hosts):
                    with open(self.temp_file.name, "r") as f:
                        lines = f.read()
                    self.assertNotIn(options, lines)
                    self.assertNotIn(new_address, lines)
                    self.assertNotIn(new_condition_true_filename, lines)
                    self.assertNotIn(new_condition_false_filename, lines)

                    update_host_with_cli(self.temp_file.name, self.host1.name)

                    body = self.host1.get_config_body(use_raw=True)
                    self.assertIn(new_address, body)
                    self.assertIn(new_condition_true_filename, body)
                    self.assertIn(new_condition_false_filename, body)
                    self.assertIn(new_ethernet, body)
                    self.assertIn(options, body)
                    self.assertEqual(self.host1.ethernet, new_ethernet)
                    self.assertEqual(self.host1.condition_false_filename, new_condition_false_filename)
                    self.assertEqual(self.host1.condition_true_filename, new_condition_true_filename)
                    self.assertEqual(self.host1.fixed_addr, new_address)

                    with open(self.temp_file.name, "r") as f:
                        lines = f.read()
                    self.assertIn(options, lines)
                    self.assertIn(new_address, lines)
                    self.assertIn(new_condition_true_filename, lines)
                    self.assertIn(new_condition_false_filename, lines)

    def test_set_raw_value_without_saving_options(self):
        new_ethernet = "00:8C:FA:5B:0C:48"
        new_condition_true_filename = "srv2/ipxe64.efi"
        new_condition_false_filename = "srv2/undionly.kpxe"
        new_address = "38.68.33.3"
        options = 'option option-151 "http://10.32.47.6:1500/dcimini?func=dcimini.osinstall.info&id=zL0vPX8iGvwkfl";'
        with patch('builtins.input', side_effect=['6', '7', 'n']):
            with patch('tools.cli.multiple_line_input', return_value=f"""
                hardware ethernet {new_ethernet};
                if option arch = 00:07 {{
                    filename "{new_condition_true_filename}";
                }} else {{
                    filename "{new_condition_false_filename}";
                }}
                fixed-address {new_address};
                {options}
            """):
                with patch('tools.cli.get_all_hosts_from_config_lines', return_value=self.hosts):
                    update_host_with_cli(self.temp_file.name, self.host1.name)
                    with open(self.temp_file.name, "r") as f:
                        lines = f.read()
                    self.assertNotIn(options, lines)
                    self.assertIn(new_address, lines)
                    self.assertIn(new_condition_true_filename, lines)
                    self.assertIn(new_condition_false_filename, lines)
                    self.assertIn(new_ethernet, lines)

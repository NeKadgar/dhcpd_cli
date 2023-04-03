import unittest
import re

from parser import ConfParser


class TestConfParser(unittest.TestCase):
    def setUp(self):
        self.conf_parser = ConfParser()
        self.host_with_deny_booting = """
        host srv2alt1 {
            hardware ethernet F0:4D:A2:74:E0:4C;
            deny booting;
        }
        """
        self.host = """
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
        """
        self.hosts = self.host + "\n" + self.host_with_deny_booting

    def test_is_all_brackets_closed__is_true(self):
        lines = "{{{{}}}}"
        self.assertTrue(self.conf_parser._is_all_brackets_closed(lines))
        self.assertTrue(self.conf_parser._is_all_brackets_closed(self.host_with_deny_booting))
        self.assertTrue(self.conf_parser._is_all_brackets_closed(self.host))

    def test_is_all_brackets_closed__is_false(self):
        lines = "{{{{}}}"
        self.assertFalse(self.conf_parser._is_all_brackets_closed(lines))
        lines = """
                    if (something) {
                        ...
                    }
                    else { ... 
                """
        self.assertFalse(self.conf_parser._is_all_brackets_closed(lines))

    def test_get_host_matches(self):
        matches = list(self.conf_parser.get_host_matches(self.host_with_deny_booting))
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].start(), 9)
        self.assertEqual(matches[0].end(), 24)
        self.assertEqual(matches[0].group(), "host srv2alt1 {")

        matches = list(self.conf_parser.get_host_matches(self.hosts))
        self.assertEqual(len(matches), 2)
        self.assertEqual(matches[0].group(), "host srv2 {")
        self.assertEqual(matches[0].start(), 9)
        self.assertEqual(matches[0].end(), 20)
        self.assertEqual(matches[1].group(), "host srv2alt1 {")
        self.assertEqual(matches[1].start(), 417)
        self.assertEqual(matches[1].end(), 432)

    def test_get_host_match(self):
        host_name = "srv2"
        host_match = self.conf_parser.get_host_match(host_name, self.hosts)
        self.assertIsNotNone(host_match)
        self.assertEqual(host_match.group(), "host srv2 {")
        self.assertEqual(host_match.start(), 9)

    def test_get_host_boundaries(self):
        host_match = re.search("host\ssrv2alt1\s{", self.host_with_deny_booting)
        start, end = self.conf_parser.get_host_boundaries(host_match, self.hosts)
        self.assertEqual(start, 23)
        self.assertEqual(end, 168)

    def test_get_ethernet(self):
        host_lines = self.host_with_deny_booting
        ethernet = self.conf_parser.get_ethernet(host_lines)
        self.assertEqual(ethernet, "F0:4D:A2:74:E0:4C")

    def test_get_ethernet__fail(self):
        host_lines = "some other line"
        with self.assertRaises(AttributeError):
            self.conf_parser.get_ethernet(host_lines)

    def test_get_name(self):
        host_match = re.search("host\s+(\w+)\s+{", self.host)
        name = self.conf_parser.get_name(host_match)
        self.assertEqual(name, "srv2")

    def test_is_deny_booting__is_true(self):
        self.assertTrue(self.conf_parser.is_deny_booting(self.host_with_deny_booting))

    def test_is_deny_booting__is_false(self):
        self.assertFalse(self.conf_parser.is_deny_booting(self.host))

    def test_get_filenames(self):
        true_filename, false_filename = self.conf_parser.get_filenames(self.host)
        self.assertEqual(true_filename, "srv2/ipxe64.efi")
        self.assertEqual(false_filename, "srv2/undionly.kpxe")

    def test_get_fixed_addr(self):
        fixed_addr = self.conf_parser.get_fixed_addr(self.host)
        self.assertEqual(fixed_addr, "38.68.33.3")

    def test_get_fixed_addr__fail(self):
        with self.assertRaises(AttributeError):
            self.conf_parser.get_fixed_addr(self.host_with_deny_booting)


if __name__ == '__main__':
    unittest.main()

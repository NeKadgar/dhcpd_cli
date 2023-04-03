import unittest
from host import Host, Hosts


class TestHosts(unittest.TestCase):
    def setUp(self) -> None:
        self.hosts = Hosts()

    def test_make_nested(self):
        # Create a parent host and two child hosts
        parent_host = Host("srv1")
        child_host_1 = Host("srv1alt1")
        child_host_2 = Host("srv1alt2")
        self.hosts.append(parent_host)
        self.hosts.append(child_host_1)
        self.hosts.append(child_host_2)

        # Call make_nested method to create nested structure
        self.hosts.make_nested()

        # Check if parent host contains child hosts
        self.assertEqual(len(parent_host.child_hosts), 2)
        self.assertIn(child_host_1.name, [host.name for host in parent_host.child_hosts])

    def test_find_by_name(self):
        # Create a list of hosts
        hosts_list = [Host("host1"), Host("host2"), Host("parent"), Host("host1alt"), Host("host2alt")]
        self.hosts = Hosts(hosts_list)
        self.hosts.make_nested()
        # Test if find_by_name method returns correct host object
        self.assertEqual(self.hosts.find_by_name("host1"), hosts_list[0])
        self.assertEqual(self.hosts.find_by_name("parent"), hosts_list[2])
        self.assertEqual(self.hosts.find_by_name("host1alt"), hosts_list[3])
        self.assertEqual(self.hosts.find_by_name("host2alt"), hosts_list[4])

        # Test if find_by_name method returns None if host is not found
        self.assertIsNone(self.hosts.find_by_name("non-existent-host"))

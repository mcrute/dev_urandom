from codemanager.tests import EnvironmentTest
from codemanager.projects import get_code_list

class CheckMP(EnvironmentTest):
    pydriver = "/disk2/ns-home/nsapi/pd/pydriver"

    def test_pydriver_symlinks(self):
        for item in get_code_list(self.project):
            pydriver_link = item.filesystem + "/cgi-bin/pydriver"
            self.assert_links_to(pydriver_link, self.pydriver)

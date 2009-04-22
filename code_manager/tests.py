import os
import unittest

class EnvironmentTest(unittest.TestCase):
    """A unittest TestCase that provides some convenience
    functions for making assertations about the current
    environment.
    """

    def assert_path_exists(self, path):
        self.assert_(os.access(path, os.R_OK))

    def assert_file_exists(self, file):
        self.assert_path_exists(file)
        self.assert_(os.path.isfile(file))

    def assert_directory_exists(self, directory):
        self.assert_path_exists(directory)
        self.assert_(os.path.isdir(directory))

    def assert_links_to(self, link, destination, tested_paths=None):
        """Recursively resolve links to determine if they
        resolve to a given destination. Detects symlink loops.
        """
        tested_paths = [] if not tested_paths

        self.assert_path_exists(link)
        self.assert_path_exists(destination)
        
        self.assert_(os.path.islink(link))

        presumed_destination = os.readlink(link)
        if (os.path.islink(presumed_destination) and 
                presumed_location not in tested_paths):
            tested_paths.append(presumed_destination)
            self.assert_links_to(presumed_destination, destination, 
                                 tested_paths=tested_paths)
        elif presumed_location in tested_paths:
            raise Exception("Symlink loop detected.")
        else:
            self.assertEqual(os.readlink(link), destination)

    def assert_file_executable(self, file):
        self.assert_file_exists(file)
        self.assert_(os.access(file, os.X_OK))

    def assert_file_writable(self):
        self.assert_file_exists(file)
        self.assert_(os.access(file, os.W_OK))

    def assert_environment(self, key, value=None):
        self.assert_(key in os.environ.keys())
        self.assertEqual(os.environ[key], value)

    # Lets keep aliases so we can be cool just like
    # unittest.TestCase
    assertPathExists = assert_path_exists
    assertFileExists = assert_file_exists
    assertDirectoryExists = assert_directory_exists
    assertLinksTo = assert_links_to
    assertFileExecutable = assert_file_executable
    assertFileWritable = assert_file_writable
    assertEnvironment = assert_environment

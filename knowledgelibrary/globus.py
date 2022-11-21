"""Globus helper library

Globus / ESnet DTN helper library.

"""

import subprocess
import argparse
import os
import time


class Globus(object):
    """ Globus connection
    """
    def __init__(self, user=None, key=None):
        """Globus connection.
        Args:
            user (str, optional): Globus user name
            key (string, optional): path of the RSA key file
        Raises:
            RuntimeError: Description
        """
        self.user = user
        self.key = key
        if self.user is None:
            if 'GLOBUS_USER' in os.environ:
                self.user = os.environ['GLOBUS_USER']
            else:
                raise RuntimeError('no credential found')
        if self.key is None:
            if 'GLOBUS_KEY' in os.environ:
                self.key = os.environ['GLOBUS_KEY']
            else:
                raise RuntimeError('no credential found')

    def execute(self, argv):
        """Executes a Globus CLI command and return its output.
        Args:
            argv (list): Globus CLI command and arguments.
        Returns:
            (str): Output of the CLI command
        """
        cmd = 'ssh -i ' + self.key + ' ' + self.user + '@cli.globusonline.org'
        for arg in argv:
            cmd += ' ' + arg
        proc = subprocess.Popen(
            [cmd],
            shell=True,
            stdout=subprocess.PIPE
        )
        lines = proc.stdout.readlines()
        res = []
        for line in lines:
            res.append(line[0:-1])
        return res

    def endpoints_search(self, match=""):
        """List endpoints with a match
        Args:
            user (dict): Globus User
            match (str, optional): match
        Returns:
            dir: List endpoints
        """
        output = self.execute(argv=['endpoint-search', match])
        endpoints = []
        endpoint = None
        for line in output:
            line_key_value = line.split(':')
            if len(line_key_value) != 2:
                continue
            line_key = line_key_value[0].strip(' ')
            line_value = line_key_value[1].strip(' ')
            if line_key == 'ID':
                if endpoint is not None:
                    endpoints.append(endpoint)
                endpoint = Endpoint(globus=self)
                endpoint.eid = line_value
            elif line_key == 'Display Name':
                endpoint.name = line_value
            elif line_key == 'Legacy Name':
                endpoint.legacy_name = line_value
            elif line_key == 'Owner':
                endpoint.owner = line_value
            elif line_key == 'Credential Status':
                endpoint.credential_status = line_value
            elif line_key == 'Host Endpoint':
                endpoint.host_endpoint = line_value
            elif line_key == 'Host Endpoint Name':
                endpoint.host_name = line_value
        if endpoint is not None:
            endpoints.append(endpoint)
        return endpoints

    def transfer(self, src_endpoint, dest_endpoint, src_file, dest_file=None):
        """Transfer a file or a directory between two endoints. If the destination
        file is not provided, identical name as the source will be assumed.
        Args:
            src_endpoint (Endpoint): source endpoint
            dest_endpoint (TYPE): destination endpoint
            src_file (str): source file or directory
            dest_file (str, optional): destination endpoint
        Returns:
            (boolean, str): Globus task identifier
        """
        src = src_endpoint.legacy_name
        if src_file[0] != '/':
            src += '/'
        src += src_file
        is_src_dir = src_endpoint.is_dir(src_file)
        if is_src_dir and src_file[-1] != '/':
            src += '/'

        dest = dest_endpoint.legacy_name
        if dest_file[0] != '/':
            dest += '/'
        dest += dest_file
        is_dest_dir = dest_endpoint.is_dir(dest_file)
        if is_src_dir and not is_dest_dir:
            raise RuntimeError('destination must be a directory')
        if is_src_dir and is_dest_dir and dest_file[-1] != '/':
            dest += '/'

        # checks if the file exists
        file_name = os.path.basename(src_file)
        dir_name = '/' + os.path.dirname(src_file)
        files = src_endpoint.list_files(dir_name)
        if file_name not in files:
            msg = file_name + " does not exist. Existing files:\n"
            for file_item in files:
                msg += '\t' + file_item + '\n'
            return (False, msg)
        args = ['transfer', '--', src, dest]
        if is_src_dir:
            args.append('-r')
        output = self.execute(args)
        res = False
        msg = output[0]
        for line in output:
            if 'Error' in line:
                res = False
                msg = line
                break
            if 'Task' in line:
                res = True
                msg = line.split(':')[1].strip('')
                break
        if not res:
            return (res, msg)
        else:
            status = self.poll_status(task_id=msg)
            res = status[0]
            task_status = status[1]
            return (res, task_status['Task ID'])

    def task_get_status(self, task_id):
        """Retrieves the status of a task.
        Args:
            task_id (str): Globus task ID.
        Returns:
            (dict): Returns the task's status.
        """
        lines = self.execute(argv=['details', task_id])
        status = {}
        for line in lines:
            item = line.strip().split(':')
            status[item[0].strip()] = item[1].strip()
        return status

    def poll_status(self, task_id):
        """Summary
        Args:
            task_id (TYPE): Description
        Returns:
            TYPE: Description
        """
        time.sleep(12)
        task_status = self.task_get_status(task_id=task_id)
        status = task_status['Status']
        while status not in ("ACTIVE", "FAILED", "SUCCEEDED"):
            time.sleep(2)
        if status == "SUCCEEDED":
            return (True, task_status)
        else:
            if task_status['Faults'] == '0':
                return (True, task_status)
            else:
                return (False, task_status)



class Endpoint(object): #pylint: disable=R0902
    """Globus Endpoint
    """
    def __init__(self, globus, name=None):
        self.globus = globus
        if self.globus is None:
            self.globus = Globus()
        self.name = name
        self.legacy_name = None
        self.eid = None
        self.owner = None
        self.credential_status = None
        self.host_endpoint = None
        self.host_name = None

    def list_files(self, directory="/"):
        """Returns the list of files in a directory. Does not return subdirectories.
        Args:
            dir (str, optional): Target directory on the endpoint
        Returns:
            (str): List of sub directories
        """
        inodes = self.globus.execute(argv=['ls', self.legacy_name + directory])
        # remove directories
        res = []
        for inode in inodes:
            if inode[-1] == '/':
                continue
            res.append(inode)
        return res

    def list_dirs(self, directory='/'):
        """Returns the list of sub directories in a directory. Does not return files.
        Args:
            dir (str, optional): Target directory on the endpoint

        Returns:
            (str): List of sub directories
        """
        inodes = self.globus.execute(argv=['ls', self.legacy_name + directory])
        # remove directories
        res = []
        for inode in inodes:
            if inode[-1] != '/':
                continue
            res.append(inode[0:-1])
        return res

    def is_dir(self, path_name):
        """Checks if a path name is a directory
        Args:
            path_name (str): path name
        Returns:
            boolean: true if the path name is a directory. False otherwise
        """
        # Even if the provided path_name ends with '/', verifies with the
        # endpoint that it is really a directory.
        if path_name[-1] == '/':
            path_name = path_name[0: -1]
        file_name = os.path.basename(path_name)
        dir_name = os.path.dirname(path_name)
        # always assumes absolute paths
        if len(dir_name) == 0 or not dir_name.startswith('/'):
            dir_name = '/' + dir_name
        inodes = self.list_dirs(directory=dir_name)
        for inode in inodes:
            if os.path.basename(inode) == file_name:
                return True
        return False

    def is_file(self, path_name):
        """Checks if a the path name is a file
        Args:
            path_name (str): path name
        Returns:
            boolean: true if the path name is a file. False otherwise
        """
        return not self.is_dir(path_name)

    def __str__(self):
        res = "Name: " + str(self.name) + '\n'
        res += "Status: " + str(self.credential_status) + '\n'
        res += "Host Endpoint: " + str(self.host_endpoint) + '\n'
        res += "Host Name: " + str(self.host_name) + '\n'
        res += "Owner: " + str(self.owner) + '\n'
        res += "Id: " + str(self.eid) + '\n'
        res += "Legacy Name: " + str(self.legacy_name)
        return res

    def __repr__(self):
        return self.__str__()

def do_cli():
    """Execute Globus CLI.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--user", nargs=1, help="Globus user name")
    parser.add_argument("--key", nargs=1, help="Globus user key")
    parser.add_argument("--endpoint-search", nargs=1,
                        help="List endpoints which names includes the match.")
    parser.add_argument("--list2", nargs='*', help="Displays all profiles.")
    args = parser.parse_args()
    globus = Globus(user=args.user[0], key=args.key[0])
    if args.endpoint_search is not None:
        match = args.endpoint_search[0]
        endpoints = globus.endpoints_search(match=match)
        for endpoint in endpoints:
            print (endpoint)
            print

if __name__ == "__main__":
    do_cli()

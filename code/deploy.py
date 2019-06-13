import paramiko
import os
from os.path import expanduser
from user_definition import *
import warnings

warnings.filterwarnings("ignore")

git_repo_owner = "MSDS698"
git_repo_name = "product-analytics-group7"


def ssh_client():
    """Return ssh client object"""
    return paramiko.SSHClient()


def ssh_connection(ssh, ec2_address, user, key_file):
    """Login via SSH to the server"""
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(
        ec2_address, username=user, key_filename=expanduser("~") + key_file
    )
    return ssh


def git_clone(ssh):
    """
    clone the repository from github repo to the server
    """
    stdin, stdout, stderr = ssh.exec_command("git --version")
    if b"" is stderr.read():
        ssh.exec_command("rm -rf " + git_repo_name)
        git_clone_command = (
            "git clone https://github.com/"
            + git_repo_owner
            + "/"
            + git_repo_name
            + ".git"
        )
        stdin, stdout, stderr = ssh.exec_command(git_clone_command)
        if b"already exists" in stderr.read():
            git_pull_command = "cd " + git_repo_name + ";" + "git pull"
            stdin, stdout, stderr = ssh.exec_command(git_pull_command)


def create_or_update_environment(ssh):
    """
    create the environment with the environment.yml file,
    update the environment if the environment already exists
    """
    stdin, stdout, stderr = ssh.exec_command(
        "conda env create -f ~/" + git_repo_name + "/environment.yml"
    )
    if b"already exists" in stderr.read():
        stdin, stdout, stderr = ssh.exec_command(
            "conda env update -f ~/" + git_repo_name + "/environment.yml"
        )


def run_server(ssh):
    """
    run the web server, connect the frontend and the backend
    """
    stdin, stdout, stderr = ssh.exec_command(
        "~/.conda/envs/MSDS603/bin/python "
        + "product-analytics-group7/server/server.py"
    )
    stdout.read()


def main():
    """
    call all the functions, make the connection, repo clone,
    environment setup and run the server
    """
    ssh = ssh_client()
    print("connect to ssh")
    ssh_connection(ssh, ec2_address, user, key_file)
    print("clone/update the repository")
    git_clone(ssh)
    print("create/update the environment")
    create_or_update_environment(ssh)
    print("run the server at port 5000")
    run_server(ssh)
    print("log out")
    ssh.close()


if __name__ == "__main__":
    main()

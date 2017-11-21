import os
from fabric.api import *
from fabric.operations import sudo
from fabric.contrib.console import confirm

USER_CONFIRMATION = "Are you sure?"
ABORT_MESSAGE = "Aborting ..."

env.user = os.environ["USER"]

##########################################################

def confirmn(msg):
    return confirm(msg, default = False)

##########################################################

@task
def uname():
    run("uname -a")

###################

@task
def ps_os():
    run("ps auxww")

###################

@task
def pstree():
    run("pstree")

###################

@task
def uptime():
    run("uptime")

###################

@task
def os_reboot():
    if not confirmn(USER_CONFIRMATION):
        abort(ABORT_MESSAGE)

    reboot(wait=5)

###################

@task
def os_update():
    sudo("apt update")
    sudo("apt upgrade")

###################

@task
def apt_installed():
    env.output_prefix = False
    sudo("apt list --installed | cat")

###################

@task
def needs_reboot():
    run("find /var/run -name reboot-required")

###################

@task
def bootstrap(root_password, password):
    if root_password == "":
        print "Root password is not set"
        return

    if root_password == "":
        print "Password is not set"
        return

    # Log in as root for the first and last time
    env.user = "root"
    env.password = root_password
    username = os.environ["USER"]

    # Create user with same name as current system user
    run("useradd -d /home/{user} -m {user} -s /bin/bash".format(user=username))
    run("echo {user}:{password} | chpasswd".format(user=username, password=password))
    run("usermod -aG sudo {user}".format(user=username))

    # Add public key to authorized keys
    public_key = "{home}/.ssh/id_rsa.pub".format(home=os.environ["HOME"])
    temp_key_path = "/home/{user}/.ssh/temp.key".format(user=username)
    run("mkdir /home/{user}/.ssh".format(user=username))
    put(public_key, temp_key_path)
    run("echo `cat {key}` >> /home/{user}/.ssh/authorized_keys".format(key=temp_key_path, user=username))
    run("rm {key}".format(key=temp_key_path))
    run("chmod 700 /home/{user}".format(user=username))
    run("chmod 700 /home/{user}/.ssh".format(user=username))
    run("chmod 600 /home/{user}/.ssh/authorized_keys".format(user=username))
    run("chown -R {user}:{user} /home/{user}/.ssh".format(user=username))

    # Update the system and install basic tools
    run("apt update")
    run("apt -y upgrade")

    # Enable firewall
    run("apt -y install ufw")
    run("ufw allow 22")
    run("ufw allow 10022")
    run("ufw allow 80")
    run("ufw allow 443")
    run("ufw --force enable")

    # Secure the system a bit more, search for default ssh config patterns
    run("sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config")
    run("sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config")

    run("service sshd restart")

    # Install other software
    run("apt -y install tmux htop bash-completion subversion pigz psmisc ncdu bmon bonnie++ dos2unix hdparm iftop iptraf iotop iputils-tracepath man zip unzip lshw lsof mdadm manpages ntpdate p7zip realpath slurm smartmontools traceroute linux-tools-generic sysstat git build-essential")

    # Install Docker
    run("apt -y install apt-transport-https ca-certificates curl software-properties-common")
    run("curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -")
    run('add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"')
    run("apt update")
    run("apt -y install docker-ce")
    run("usermod -aG docker {user}".format(user=username))
    run("docker run hello-world")

    # Install docker-compose
    run("git clone https://gist.github.com/824b0c2b475464de596aaff1e4591010.git tmp")
    run("chmod +x ./tmp/*")
    run("./tmp/install-docker-compose-latest.sh")
    run("rm -rf tmp")

    # System status check
    run("docker-compose -v")


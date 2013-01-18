#!/usr/bin/env python

import os
import stat
import shlex
import config
from subprocess import Popen, PIPE

class ExistsError(Exception):
    def __init__(self, message):
        self.message = message

def create(container):
    """Create a container"""
    if config.settings['debug']:
        print("Container %s: Creating" % (container['name']))
    args = "%s/lxc-create" % (config.settings['lxc-bindir'])
    args += " -n %s" % (container['name'])
    args += " -t %s" % (container['profile']['template'])
    args += " -- %s" % (container['profile']['template_opts'])
    try:
        p = Popen(shlex.split(args), stdout=PIPE, stdin=PIPE, stderr=PIPE)
        p.communicate()
        if p.returncode is 1:
            raise ExistsError("Container already exists")
    except ExistsError as e:
        print("Error creating container %s: %s" % (container['name'], e.message))
        if config.settings['continue_anyway']:
            return()
        exit(1)
    if container['profile']['lxc_config'] is not "":
        apply_lxc(container)
    install_puppet(container)
    apply_puppet(container)

def start(container, command=False):
    """Handle the starting up of a container, creating it if it doesn't already exist."""
    # Create the container if it doesn't exist
    if not exists(container):
        create(container)
    if config.settings['debug']:
        print("Container %s: Starting" % (container['name']))

    args = "%s/lxc-start" % (config.settings['lxc-bindir'])
    args += " -d " # Daemonize
    args += "-n %s " % (container['name'])
    if command:
        args += " -- %s" % (command)
    print(args)
    try:
        p = Popen(shlex.split(args), stdout=PIPE, stdin=PIPE, stderr=PIPE)
        p.communicate()
    except:
        print("Container %s: Error starting" % container['name'])
        exit(1)


def exists(container):
    """Determine if a container is running"""
        # Make a list of running containers
    if config.settings['debug']:
        print("Container %s: Determining existence: " % (container['name']), end='')
    try:
        p = Popen("%s/lxc-ls" % (config.settings['lxc-bindir']), stdout=PIPE, stdin=PIPE, stderr=PIPE)
        running_containers = str(p.communicate()[0])[2:-3].split("\\n") # Get rid of buffer API bytes
    except:
        print("Error listing VMs")
        exit(1)

        # Check to see if any of the running container names match
    for c in running_containers:
        if c == container['name']:
            if config.settings['debug']:
                print("Yes")
            return(True)
    print("No")
    return(False)

def shutdown(container, timeout=60):
    """Shut down a container. Optional timeout of 60 seconds."""
    try:
        # lxc.shutdown(container)
        p = Popen(shlex.split("%s/lxc-shutdown -n %s -t %d" % (config.settings['lxc-bindir'], container['name'], timeout)), stdout=PIPE, stderr=PIPE, stdin=PIPE)
        #print(p.communicate())
        p.communicate()
    except:
        print("Error shutting down container: %s, Reason: %s" % (container['name'], "Error"))
        exit(1)

def destroy(container):
    """Destroy a container. Note that a container should be shut down before destroying."""
    if config.settings['debug']:
        print("Container %s: Destroying" % (container['name']))
    p = Popen(shlex.split("%s/lxc-destroy -n %s" % (config.settings['lxc-bindir'], container['name'])), stdout=PIPE, stderr=PIPE, stdin=PIPE)

def apply_lxc(container):
    """Applies custom lxc config settings defined in profiles."""
    if config.settings['debug']:
        print("Container %s: Inserting lxc settings" % (container['name']))
    fh = open("%s/%s/config" % (config.settings['lxc-rootdir'], container['name']), "a+")
    fh.write("\n# Added for Vee\n\n")
    for line in container['profile']['lxc_config']:
        fh.write(line + "\n")
    fh.close()

def apply_puppet(container):
    """Apply a puppet class."""
    if config.settings['debug']:
        print("Container %s: Applying puppet class '%s'" % (container['name'], container['profile']['puppet_class']))
    # TODO: Copy puppet class into container and lxc-execute -n $name puppet apply -e 'include $puppetclass'

def install_puppet(container):
    if config.settings['debug']:
        print("Container %s: Installing puppet" % (container['name']))
    fh = open("%s/%s/rootfs/tmp/install-puppet.sh" % (config.settings['lxc-rootdir'], container['name']),"w+")
    os.chmod("%s/%s/rootfs/tmp/install-puppet.sh" % (config.settings['lxc-rootdir'], container['name']), stat.S_IXUSR)
    fh.write(container['profile']['install_puppet_script'])
    fh.close()

    start(container, "/tmp/install-puppet.sh")

if __name__ == "__main__":
    for container in config.containers:
        start(container)
        apply_puppet(container)

    if config.settings['destroy_after_running']:
        for container in config.containers:
            shutdown(container)
            destroy(container)

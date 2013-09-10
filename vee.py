#!/usr/bin/env python3
"""Vee - an LXC cluster automation tool """

import os
import stat
import shlex
import shutil
import time
import config
from distutils import dir_util
from subprocess import Popen, PIPE

class ExistsError(Exception):
    """Custom error that is raised if an LXC container already exists."""
    pass

def create(container):
    """Create a container"""
    if config.SETTINGS['debug']:
        print("Container %s: Creating" % (container['name']))
    args = "%s/lxc-create" % (config.SETTINGS['lxc_bindir'])
    args += " -n %s" % (container['name'])
    args += " -t %s" % (container['profile']['template'])
    args += " -- %s" % (container['profile']['template_opts'])
    try:
        proc = Popen(shlex.split(args),
                     stdout=PIPE, stdin=PIPE, stderr=PIPE)
        proc.communicate()
        if proc.returncode is 1:
            raise ExistsError("Container already exists")
    except ExistsError as error:
        print("Error creating container %s: %s" %
              (container['name'], error))
        if config.SETTINGS['continue_anyway']:
            return()
        exit(1)
    install_lxc(container)
    install_puppet(container)
    #apply_puppet(container)

def start(container, command=False):
    """Start a container with an optional command.
       If invoked with command, will shutdown afterwards."""
    if config.SETTINGS['debug']:
        print("Container %s: Starting" % (container['name'])),
        if command is not False:
            print(" with command: %s" % (command))
        else:
            print("")

    args = "%s/lxc-start" % (config.SETTINGS['lxc_bindir'])
    args += " -d " # Daemonize
    args += "-n %s " % (container['name'])
    if command:
        args += " -- %s" % (command)
    try:
        proc = Popen(shlex.split(args), stdout=PIPE, stdin=PIPE, stderr=PIPE)
        proc.communicate()
    except:
        print("Container %s: Error starting" % container['name'])
        exit(1)

def exists(container):
    """Determine if a container is running"""
        # Make a list of running CONTAINERS
    if config.SETTINGS['debug']:
        print("Container %s: Determining existence: " % (container['name']), end='')
    try:
        proc = Popen("%s/lxc-ls" % (config.SETTINGS['lxc_bindir']),
                     stdout=PIPE, stdin=PIPE, stderr=PIPE)
        # Get rid of buffer API bytes
        running_containers = str(proc.communicate()[0])[2:-3].split("\\n")
    except:
        print("Error listing VMs")
        exit(1)

        # Check to see if any of the running container names match
    for possible_container in running_containers:
        if possible_container == container['name']:
            if config.SETTINGS['debug']:
                print("Yes")
            return(True)
    if config.SETTINGS['debug']:
        print("No")
    return(False)

def shutdown(container, timeout=60):
    """Shut down a container. Optional timeout of 60 seconds."""
    try:
        proc = Popen(shlex.split("%s/lxc-shutdown -n %s -t %d" %
                   (config.SETTINGS['lxc_bindir'], container['name'], timeout)),
                   stdout=PIPE, stderr=PIPE, stdin=PIPE)
        proc.communicate()
    except:
        print("Error shutting down container: %s, Reason: %s" %
             (container['name'], "Error"))
        exit(1)

def destroy(container):
    """Destroy a container. Note that a container should be
       shut down before destroying."""
    if config.SETTINGS['debug']:
        print("Container %s: Destroying" % (container['name']))
    proc = Popen(shlex.split("%s/lxc-destroy -n %s" %
                (config.SETTINGS['lxc_bindir'], container['name'])),
                 stdout=PIPE, stderr=PIPE, stdin=PIPE)
    proc.communicate()

def install_lxc(container):
    """Applies custom lxc config settings defined globally and in profiles."""
    if config.SETTINGS['debug']:
        print("Container %s: Inserting lxc settings" % (container['name']))

    file = open("%s/%s/config" %
             (config.SETTINGS['lxc_rootdir'], container['name']),
              "a+")
    file.write("\n# Added for Vee\n\n")

        # Write global lxc config
    for line in config.SETTINGS['common_lxc_config']:
        file.write(line + "\n")

        # Write profile lxc config
    for line in container['profile']['lxc_config']:
        file.write(line + "\n")

        # Write specific lxc config
    for line in container['lxc_config']:
        file.write(line + "\n")

    file.close()

def apply_puppet(container):
    """Apply a puppet class."""
    if config.SETTINGS['debug']:
        print("Container %s: Applying puppet class '%s'" %
             (container['name'], container['profile']['puppet_class']))

    # Create a file that will run puppet when the host starts
    file = open("%s/%s/rootfs/%s" %
               (config.SETTINGS['lxc_rootdir'], container['name'],
                container['profile']['puppet_trigger_location']),
                'a+')
    file.write("puppet apply --modulepath=/opt/puppet_modules/ -e 'include %s' >> /tmp/log\n" % (container['profile']['puppet_class']))

    # This is a hack
    file.write("touch /tmp/done")
    file.close()

    fromdir = config.SETTINGS['puppet_classdir']
    todir = "%s/%s/rootfs/opt/puppet_modules" % (config.SETTINGS['lxc_rootdir'], container['name'])

    if config.SETTINGS['debug']:
        print("Container %s: Copying from: %s" % (container['name'], fromdir))
        print("Container %s: Copying to  : %s" % (container['name'], todir))

    dir_util.copy_tree(fromdir, todir)


def install_puppet(container):
    """Put a script in place to install puppet on first run."""

    # Assemble filename and open file
    filename = ("%s/%s/rootfs%s" %
               (config.SETTINGS['lxc_rootdir'],
                container['name'],
                container['profile']['puppet_trigger_location']))

    file = open(filename, "w")

    # Print filename
    if config.SETTINGS['debug']:
        print("Container %s: Installing puppet trigger script to: %s" % (container['name'], filename))

    # Make this executable
    os.chmod(filename, stat.S_IXUSR)

    file.write(container['profile']['install_puppet_script'])
    file.close()

    # Now install the script to apply puppet class at boot
    apply_puppet(container)

    # Start the container just enough to run install script
    #start(container, "/tmp/install-puppet.sh")

if __name__ == "__main__":
    print("Creating Containers...")
    for container in config.CONTAINERS:
        if not exists(container):
            create(container)
        start(container)

    # This is a hack
    print("Waiting for puppet catalogs to apply on containers...")
    containerlist = list(config.CONTAINERS)
    while len(containerlist) > 0:
        for container in containerlist:
            if config.SETTINGS['debug']:
                print("Waiting for container %s..." % container['name'])
            if os.path.exists("%s/%s/rootfs/tmp/done" % (config.SETTINGS['lxc_rootdir'], container['name'])):
                containerlist.remove(container)
            else:
                time.sleep(1)

    print("Running tests...")
    for test in config.TESTS:
        if config.SETTINGS['debug']:
            print("Executing test: %s... " % test, end='')
        proc = Popen("%s/%s" % (config.SETTINGS['vee_testdir'], test), stdout=PIPE, stdin=PIPE, stderr=PIPE)
        proc.communicate()
        if proc.returncode is 1:
            print("Error executing test! Non-zero return code.")
        else:
            print("OK!")

    if config.SETTINGS['destroy_after_running']:
        print("Destroying containers...")
        for container in config.CONTAINERS:
            shutdown(container)
            destroy(container)

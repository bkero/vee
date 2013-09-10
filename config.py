"""This is the configuration file. All modification to the
   application should happen here."""

import os
import sys

SETTINGS = {
    "templates": "/homedir",
    "lxc_bindir": "/usr/bin",
    "lxc_rootdir": "/var/lib/lxc",
    "vee_testdir": os.path.dirname(sys.argv[0]) + "tests",
    "puppet_classdir": os.path.dirname(sys.argv[0]) + "puppet_classes",
    "destroy_after_running": True,
    "reboot_if_already_running": False,
    "continue_anyway": True,
    "debug": False,
    "common_lxc_config": [],
}

CONTAINER_PROFILE = {
    "db": {  
        "name": "db",
        "template": "ubuntu",
        "template_opts": "",
        "puppet_class": "db",
        "puppet_trigger_location": "/etc/rc.local",
        "install_puppet_script":
            "apt-get install --force-yes -y puppet >> /tmp/log\n",
        "lxc_config": [],
    },

    "web": {
        "name": "web",
        "template": "ubuntu",
        "template_opts": "",
        "puppet_class": "web",
        "puppet_trigger_location": "/etc/rc.local",
        "install_puppet_script":
            "apt-get install --force-yes -y puppet >> /tmp/log\n",
        "lxc_config": [],
    },
    
    "lb": {
        "name": "lb",
        "template": "ubuntu",
        "template_opts": "",
        "puppet_class": "lb",
        "puppet_trigger_location": "/etc/rc.local",
        "install_puppet_script":
            "apt-get install --force-yes -y puppet >> /tmp/log\n",
        "lxc_config": [],
    },
}

CONTAINERS = [
    {
        "name": "db1",
        "profile": CONTAINER_PROFILE['db'],
        "lxc_config": [
         "lxc.console = /var/log/lxc/db1",
        ],
    },
    {
        "name": "db2",
        "profile": CONTAINER_PROFILE['db'],
        "lxc_config": [
            "lxc.console = /var/log/lxc/db2",
        ],
    },
    {
        "name": "web1",
        "profile": CONTAINER_PROFILE['web'],
        "lxc_config": [
            "lxc.console = /var/log/lxc/web1",
        ],
    },
    {
        "name": "web2",
        "profile": CONTAINER_PROFILE['web'],
        "lxc_config": [
            "lxc.console = /var/log/lxc/web2",
        ],
    },
    {
        "name": "lb1",
        "profile": CONTAINER_PROFILE['lb'],
        "lxc_config": [
            "lxc.console = /var/log/lxc/lb1",
        ],
    },
    {
        "name": "lb2",
        "profile": CONTAINER_PROFILE['lb'],
        "lxc_config": [
            "lxc.console = /var/log/lxc/lb2",
        ],
    }
]

TESTS = [
    'up.sh',
    'good.sh',
]

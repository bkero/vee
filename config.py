"""This is the configuration file. All modification to the
   application should happen here."""

SETTINGS = {
    "templates": "/homedir",
    "lxc-bindir": "/usr/sbin",
    "lxc-rootdir": "/etc/lxc",
    "puppet-classdir": "/home/bkero/code/vee/puppet-classes",
    "destroy_after_running": False,
    "reboot_if_already_running": False,
    "continue_anyway": True,
    "debug": True,
    "common_lxc_config": [
        "lxc.network.type  = veth",
        "lxc.network.link  = br0",
        "lxc.network.flags = up",
    ],
}

CONTAINER_PROFILE = {
    "db": {  
        "name": "db",
        "template": "debian",
        "template_opts": "",
        "puppet_class": "db-stage",
        "puppet_trigger_location": "/etc/rc.local",
        "install_puppet_script":
            "apt-get install --force-yes -y puppet >> /tmp/log\n",
        "lxc_config": [],
    },

    "web": {
        "name": "web",
        "template": "debian",
        "template_opts": "",
        "puppet_class": "web-stage",
        "puppet_trigger_location": "/etc/rc.local",
        "install_puppet_script":
            "apt-get install --force-yes -y puppet >> /tmp/log\n",
        "lxc_config": [],
    },
    
    "lb": {
        "name": "lb",
        "template": "debian",
        "template_opts": "",
        "puppet_class": "lb-stage",
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

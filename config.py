settings = {
    "templates": "/homedir",
    "lxc-bindir": "/usr/sbin",
    "lxc-rootdir": "/etc/lxc",
    "puppet-classdir": "/home/bkero/code/vee/puppet-classes",
    "destroy_after_running": False,
    "reboot_if_already_running": False,
    "continue_anyway": True,
    "debug": True,
}

network = {
    "type":        "bridge",
    "bridge_name": "br0",
    "as_root":     True,
}

container_profile = {
    "db": {  
        "name": "db",
        "template": "debian",
        "template_opts": "",
        "puppet_class": "db-stage",
        "install_puppet_script": "#!/bin/bash\ndhclient eth0\napt-get update\napt-get install -y puppet",
        "lxc_config": [
            "lxc.network.type = veth",
            "lxc.network.link = br0",
            "lxc.network.flags = up",
        ],
    },
    "web": {
        "name": "web",
        "template": "debian",
        "template_opts": "",
        "puppet_class": "web-stage",
        "install_puppet_script": "#!/bin/bash\ndhclient eth0\napt-get update\napt-get install -y puppet",
        "lxc_config": [
            "lxc.network.type = veth",
            "lxc.network.link = br0",
            "lxc.network.flags = up",
        ],
    }
}

containers = [
    {
        "name": "db1",
        "profile": container_profile['db'],
    },
    {
        "name": "web1",
        "profile": container_profile['web'],
    }
]

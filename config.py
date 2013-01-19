settings = {
    "templates": "/homedir",
    "lxc-bindir": "/usr/sbin",
    "destroy_after_running": True,
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
        "puppet-class": "db-stage",
    },
    "web": {
        "name": "web",
        "template": "debian",
        "template_opts": "",
        "puppet-class": "web-stage",
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

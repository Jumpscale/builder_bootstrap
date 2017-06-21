from js9 import j
import subprocess
import time
import json

def ovh(config):
    appkey = config["ovh"]["appkey"]
    appsecret = config["ovh"]["appsecret"]
    consumerkey = config["ovh"]["consumerkey"]
    ztnetwork = config["zerotier"]["networkid"]

    cl = j.clients.ovh.get(appkey, appsecret, consumerkey)

    serverlist = cl.serversGetList()
    serverid = j.tools.console.askChoice(serverlist, "Select server to boot zero-os, be careful !")

    pxescript = "%s/%s" % (config["zerohub"]["bootstrapipxe"].rstrip("/"), ztnetwork)
    task = cl.zeroOSBoot(serverid, pxescript)

    print("[+] waiting for reboot")
    cl.waitServerReboot(serverid, task['taskId'])

    ip_pub = cl.serverGetDetail(serverid)["ip"]

    return ip_pub

def containerZt(cn):
    while True:
        ztinfo = cn.zerotier.list()
        ztdata = ztinfo[0]

        if len(ztdata['assignedAddresses']) == 0:
            time.sleep(1)
            continue

        return ztdata['assignedAddresses'][0].split('/')[0]


if __name__ == '__main__':
    print("[+] loading configuration")
    config = j.core.state.config
    zt = j.clients.zerotier.get()

    print("[+] loading server list")
    ip_pub = ovh(config)

    print("[+] looking for physical server: %s" % ip_pub)
    while True:
        try:
            member = zt.getNetworkMemberFromIPPub(ip_pub, networkId="", online=True)
            ipaddr_priv = member["ipaddr_priv"][0]
            break

        except RuntimeError as e:
            time.sleep(1)

    print("[+] server found: %s" % member['id'])
    print("[+] contacting zero-os server: %s" % ipaddr_priv)
    while True:
        try:
            cl = j.clients.g8core.get(ipaddr_priv)
            cl.timeout = 180
            break

        except RuntimeError as e:
            time.sleep(1)
            pass

    print("[+] configuring ubuntu container")
    ubuntu = "https://hub.gig.tech/maxux/ubuntu1604.flist"
    ztnetwork = config["zerotier"]["networkid"]

    print("[+] starting ubuntu container")
    network = [
        {'type': 'default'},
        {'type': 'zerotier', 'id': ztnetwork}
    ]
    containerid = cl.container.create(ubuntu, nics=network).get()
    cn = cl.container.client(json.loads(containerid.data))

    print("[+] setting up and starting ssh server")
    cn.bash('dpkg-reconfigure openssh-server').get()
    cn.bash('/etc/init.d/ssh start').get()

    print("[+] allowing local ssh key")
    keys = subprocess.run(["ssh-add", "-L"], stdout=subprocess.PIPE)
    strkeys = keys.stdout.decode('utf-8')

    fd = cn.filesystem.open("/root/.ssh/authorized_keys", "w")
    cn.filesystem.write(fd, strkeys.encode('utf-8'))
    cn.filesystem.close(fd)

    print("[+] waiting for zerotier")
    containeraddr = containerZt(cn)

    print("[+]")
    print("[+] your ubuntu on zero-os is ready !")
    print("[+] please ssh over zerotier network: %s" % ztnetwork)
    print("[+]     root@%s" % containeraddr)
    print("[+]")

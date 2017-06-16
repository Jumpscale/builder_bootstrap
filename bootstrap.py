
from js9 import j

try:
    import ovh
except:
    j.do.execute("pip3 install ovh")
    j.do.execute("js9_init")
    print("ovh was not installed, please retry")
    j.application.stop()

try:
    import packet
except:
    j.do.execute("pip3 install packet-python")
    j.do.execute("js9_init")
    print("ovh was not installed, please retry")
    j.application.stop()

c = j.core.state.config


def ovh():

    cl = j.clients.ovh.get(c["ovh"]["appkey"], c["ovh"]["appsecret"], c["ovh"]["consumerkey"])

    serverid = j.tools.console.askChoice(cl.serversGetList(), "select server to boot g8os, be careful !")

    # cl.zeroOSBoot(serverid, "%s/%s" % (c["zerohub"]["bootstrapipxe"].rstrip("/"), c["zerotier"]["networkid"]))

    ip_pub = cl.serverGetDetail(serverid)["ip"]

    return ip_pub


ip_pub = ovh()
cl = j.clients.zerotier.get()

member = cl.getNetworkMemberFromIPPub(ip_pub, networkId="", online=True)
ipaddr_priv = member["ipaddr_priv"][0]

c = j.clients.g8core.get(ipaddr_priv)

containerid = c.container.create("https://hub.gig.tech/gig-official-apps/ubuntu1604.flist",
                                 zerotier=j.core.state.config["zerotier"]["networkid"])

from IPython import embed
print("DEBUG NOW uyuy")
embed()
raise RuntimeError("stop debug here")

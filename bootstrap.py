
try:
    import ovh
except:
    j.do.execute("pip3 install ovh")

from js9 import j


c = j.core.state.config

if "ovh" not in c:
    c["ovh"] = {}
    c["ovh"]["appkey"] = ""
    c["ovh"]["appsecret"] = ""
    c["ovh"]["consumerkey"] = ""
    c["ovh"]["enable"] = False

if "zerotier" not in c:
    c["zerotier"] = {}
    c["zerotier"]["networkid"] = ""
    c["zerotier"]["apitoken"] = ""
    c["zerotier"]["enable"] = False

if "packetnet" not in c:
    c["packetnet"] = {}
    c["packetnet"]["apitoken"] = ""
    c["packetnet"]["sshkey"] = ""
    c["packetnet"]["enable"] = False

if "zerohub" not in c:
    c["zerohub"] = {}

keys = ["ovh", "zerotier", "packetnet", "zerohub"]
for key0 in keys:
    for key, val in c[key0].items():
        if key == "enable":
            continue
        if val == None or val.strip() is "":
            c[key0][key] = j.tools.console.askString("Please specify %s:%s" % (key0, key))

c["ovh"]["endpoint"] = "soyoustart-eu"
c["ovh"]["enable"] = True
c["zerohub"]["bootstrapipxe"] = 'https://bootstrap.gig.tech/ipxe/master/'
c["zerotier"]["enable"] = True
c["redis"]["unixsocket"] = "/tmp/redis.sock"
# c["packetnet"]["enable"] = True

j.core.state.configSave()


def ovh():
    cl = j.clients.ovh.get(c["ovh"]["appkey"], c["ovh"]["appsecret"], c["ovh"]["consumerkey"])

    serverid = j.tools.console.askChoice(cl.serversGetList(), "select server to boot g8os, be careful !")

    cl.zeroOSBoot(serverid, "https://bootstrap.gig.tech/ipxe/master/%s" % c["zerotier"]["networkid"])

    from IPython import embed
    print("DEBUG NOW 87")
    embed()
    raise RuntimeError("stop debug here")

    # cl.reboot(serverid)


ovh()

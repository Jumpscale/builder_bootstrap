import requests
import ovh
import pytoml


class ZeroOS_Ovh():
    def __init__(self, appkey, appsecret, consumerkey):
        self.client = ovh.Client(
            endpoint='soyoustart-eu',
            application_key=appkey,
            application_secret=appsecret,
            consumer_key=consumerkey,
        )

        self.scriptId = -1

    def clientStatus(self):
        print(self.client.get("/auth/currentCredential"))
        print(self.client.get("/me/api/application"))
        print(self.client.get("/me/api/credential"))

        """
        rulz = [
            {'method': 'GET', 'path': '/*'},
            {'method': 'PUT', 'path': '/*'},
            {'method': 'POST', 'path': '/*'},
            {'method': "DEL", 'path': '/*'},
        ]

        print(self.client.post('/auth/credential', accessRules=rulz))
        """

        return True

    def listNetworkBootloader(self):
        return self.client.get("/me/ipxeScript")

    def inspectNetworkBootloader(self, name):
        return self.client.delete("/me/ipxeScript/%s" % name)

    def deleteNetworkBootloader(self, name):
        return self.client.delete("/me/ipxeScript/%s" % name)

    def installNetworkBootloader(self, ipxe):
        return self.client.post("/me/ipxeScript", **ipxe)

    def isAvailable(self, name):
        existing = self.listNetworkBootloader()

        for item in existing:
            if item == name:
                return True

        return None

    def _setBootloader(self, target, bootid):
        print("[+] bootloader selected: %s" % bootid)

        payload = {"bootId": int(bootid)}
        self.client.put("/dedicated/server/%s" % target, **payload)

        return True

    def setBootloader(self, target, name):
        bootlist = self.client.get("/dedicated/server/%s/boot?bootType=ipxeCustomerScript" % target)
        checked = None

        for bootid in bootlist:
            data = self.client.get("/dedicated/server/%s/boot/%s" % (target, bootid))
            if data['kernel'] == name:
                return self._setBootloader(target, bootid)

        return False

    def reboot(self, target):
        return self.client.post("/dedicated/server/%s/reboot" % target)

    #
    # custom builder
    #
    def build(self, url):
        # strip trailing flash
        url = url.rstrip('/')

        # downloading original ipxe script
        script = requests.get(url)
        if script.status_code != 200:
            raise RuntimeError("Invalid script URL")

        # going unsecure, because ovh
        fixed = script.text.replace('https://bootstrap.', 'http://unsecure.bootstrap.')

        # setting name and description according to the url
        fields = url.split('/')

        if len(fields) == 7:
            # branch name, zerotier network, arguments
            description = "Zero-OS: %s (%s, %s)" % (fields[4], fields[5], fields[6])
            name = "zero-os-%s-%s,%s" % (fields[4], fields[5], fields[6])

        elif len(fields) == 6:
            # branch name, zerotier network, no arguments
            description = "Zero-OS: %s (%s, no arguments)" % (fields[4], fields[5])
            name = "zero-os-%s-%s" % (fields[4], fields[5])

        else:
            # branch name, no zerotier, no arguments
            description = "Zero-OS: %s (no zerotier, no arguments)" % fields[4]
            name = "zero-os-%s" % fields[4]

        return {'description': description, 'name': name, 'script': fixed}

    def configure(self, target, url):
        ipxe = self.build(url)

        print("[+] description: %s" % ipxe['description'])
        print("[+] boot loader: %s" % ipxe['name'])

        if not self.isAvailable(ipxe['name']):
            print("[+] installing the bootloader")
            self.installNetworkBootloader(ipxe)

        zos.setBootloader(target, ipxe['name'])


if __name__ == '__main__':

    from IPython import embed
    print("DEBUG NOW lll")
    embed()
    raise RuntimeError("stop debug here")

    target = "{target}"

    print("[+] initializing client")
    zos = ZeroOS_Ovh('{Application Key}', '{Application Key}', '{Consumer Key}')

    print("[+] setting up machine: %s" % target)
    zos.configure(target, "https://bootstrap.gig.tech/ipxe/master/17d709436c7366d8/debug")

    print("[+] rebooting the server")
    zos.reboot(target)

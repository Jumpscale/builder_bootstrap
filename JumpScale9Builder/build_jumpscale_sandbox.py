from js9 import j


def packager(flistName='js9Flist'):
    """
    @param: flistName name of the flist to be created
    """
    prefab = j.tools.prefab.local
    print("Copying jumpscale bins")
    prefab.core.file_copy('/usr/local/bin/js9', '$BINDIR')
    prefab.core.file_copy('/usr/local/bin/ays', '$BINDIR')
    paths = ["/usr/lib/python3/dist-packages", "/usr/lib/python3.5/", "/usr/local/lib/python3.5/dist-packages"]
    excludeFileRegex = ["-tk/", "/lib2to3", "-34m-", "lsb_release"]
    excludeDirRegex = ["/JumpScale", "config-x86_64-linux-gnu", "pygtk"]
    dest = j.sal.fs.joinPaths(prefab.core.dir_paths['BASEDIR'], 'lib')
    print("Copying python libs")
    for path in paths:
        j.tools.sandboxer.copyTo(path, dest, excludeFileRegex=excludeFileRegex, excludeDirRegex=excludeDirRegex)
    base = prefab.core.dir_paths['BASEDIR']
    prefab.core.file_copy('/usr/bin/python3.5', '$BINDIR')
    j.sal.fs.symlink("%s/bin/python3.5" % base, "%s/bin/python3" % base)
    print("Sandboxing python")
    j.tools.sandboxer.sandboxLibs("%s/lib" % base, recursive=True)
    j.tools.sandboxer.sandboxLibs("%s/bin" % base, recursive=True)

    # Create flist
    # Make sure python-rocksdb is installed with http://python-rocksdb.readthedocs.io/en/latest/installation.html

    kvs = j.data.kvs.getRocksDBStore(name=flistName, namespace=None, dbpath="/tmp/%s.db" % flistName)
    flist = j.tools.flist.getFlist(rootpath='/opt', kvs=kvs)
    print("Creating flist")
    flist.add('/opt', [".*\.pyc", ".*__pycache__", ".*\.bak"])
    print("Uploading flist data")
    flist.upload('https://hub.gig.tech')
    prefab.core.run('tar zcf /tmp/{val}.tar.gz /tmp/{val}.db'.format(val=flistName))
    print("Flist ready to use")

    # In order to use the flist on an ubuntu machine, you need to source env.sh.
    # To use g8ufs download following files:
    # https://stor.jumpscale.org/public/g8ufs
    # https://stor.jumpscale.org/public/lib-dep.tar.gz
    # Move g8ufs to /bin directory. Extract the contents of lib-dep to /usr/lib
    # in a tmux window run the following:
    # g8ufs -meta {path of the flist} {mount point}
    # In our case mount point is /opt
    # You'll need the mascot to properly use jumpscale:
    # curl -s https://raw.githubusercontent.com/Jumpscale/developer/master/mascot?$RANDOM > ~/.mascot.txt

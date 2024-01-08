APP_VERSION = "0.1"

ALERTS_FILE = "alerts.txt"
HISTORY_FILE = "history.txt"
SERVER_HISTORY_FILE = "server-history.txt"
CLUSTER_HISTORY_FILE = "cluster-history.txt"
ZONE_HISTORY_FILE = "zone-history.txt"


# define fastpath nouns
FP_ALERT = "alert"
FP_BLOCK_DEVICE = "blk"
FP_BOND = "bond"
FP_BUCKET = "bucket"
FP_CLUSTER = "cluster"
FP_CONFIG = "cfg"
FP_ENDPOINT = "url"
FP_ERROR = "err"
FP_FILESYSTEM = "fs"
FP_FREE_SPACE = "df"
FP_GATEWAY = "gw"
FP_GROUP = "grp"
FP_HEALTH = "health"
FP_HISTORY = "history"
FP_LOG = "log"
FP_LV = "lv"   # logical volume
FP_LVM = "lvm"  # logical volume manager
FP_MON = "mon"
FP_NET = "net"
FP_NIC = "nic"
FP_OSD = "osd"
FP_PERF = "perf"
FP_PG = "pg"   # ceph placement group
FP_POOL = "pool"
FP_PORT = "port"
FP_PV = "pv"   # physical volume
FP_QUOTA = "quota"
FP_REALM = "realm"
FP_SERVER = "server"
FP_USER = "user"
FP_VG = "vg"   # volume group
FP_VLAN = "vlan"
FP_ZONE = "zone"

# define fastpath verbs
FP_ACTIVATE = "activate"
FP_CHANGE = "ch"  # e.g., chown, chuser, chgrp
FP_COMPRESS = "zip"
FP_CONTRACT = "contract"
FP_COPY = "cp"
FP_CREATE = "mk"
FP_DEACTIVATE = "deactivate"
FP_DESTROY = "destroy"
FP_DIFF = "diff"
FP_DOWN = "down"
FP_EXCLUDE = "exclude"
FP_EXPAND = "expand"
FP_EXPORT = "export"
FP_GRANT = "grant"
FP_IMPORT = "import"
FP_IN = "in"
FP_INCLUDE = "include"
FP_LIST = "ls"
FP_MOUNT = "mount"
FP_MOVE = "mv"
FP_OUT = "out"
FP_QUIT = "quit"
FP_REBOOT = "reboot"
FP_REMOVE = "rm"
FP_RESTART = "restart"
FP_REVOKE = "revoke"
FP_SHARE = "share"
FP_START = "start"
FP_STOP = "stop"
FP_UNCOMPRESS = "unzip"
FP_UNMOUNT = "umount"
FP_UP = "up"
FP_VIEW = "view"

# define actions
FP_CREATE_PV = "%s%s" % (FP_CREATE, FP_PV)
FP_CREATE_VG = "%s%s" % (FP_CREATE, FP_VG)
FP_CREATE_LV = "%s%s" % (FP_CREATE, FP_LV)

FP_LIST_PV = "%s%s" % (FP_LIST, FP_PV)
FP_LIST_VG = "%s%s" % (FP_LIST, FP_VG)
FP_LIST_LV = "%s%s" % (FP_LIST, FP_LV)

FP_REMOVE_PV = "%s%s" % (FP_REMOVE, FP_PV)
FP_REMOVE_VG = "%s%s" % (FP_REMOVE, FP_VG)
FP_REMOVE_LV = "%s%s" % (FP_REMOVE, FP_LV)

FP_CREATE_ALERT = "%s%s" % (FP_CREATE, FP_ALERT)
FP_LIST_ALERT = "%s%s" % (FP_LIST, FP_ALERT)

FP_LIST_BLOCK_DEVICE = "%s%s" % (FP_LIST, FP_BLOCK_DEVICE)
FP_VIEW_BLOCK_DEVICE = "%s%s" % (FP_VIEW, FP_BLOCK_DEVICE)

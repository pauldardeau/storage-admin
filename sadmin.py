#! /usr/bin/env python3

import locale
import os
import os.path
import platform
import subprocess
import sys
from dialog import Dialog
from datetime import datetime
import constants as c


# TODO: functionality to add:
#  Read-only/view-only mode
#  Preview-only mode
#  Provisions for running admin/superuser mode

# Commands to implement:
# ethtool --statistics interface


class MenuOption:
    def __init__(self, title, fastpath, callback):
        self.title = title
        self.fastpath = fastpath
        self.callback = callback


class Menu:
    def __init__(self, title, base_fastpath, parent_fastpath):
        self.title = title
        self.base_fastpath = base_fastpath
        self.parent_fastpath = parent_fastpath
        self.full_fastpath = update_parent_fastpath(self.parent_fastpath, self.base_fastpath)
        self.options = []

    def add_option(self, menu_option):
        self.options.append(menu_option)

    def number_options(self):
        return len(self.options)

    def get_option(self, index):
        return self.options[index]

    def get_title(self):
        if len(self.full_fastpath) > 0:
            return "%s%s" % (self.title, format_fastpath(self.full_fastpath))
        else:
            return self.title


def do_execute_command(command):
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out, err = p.communicate()
    return {'stdout': out, 'stderr': err, 'rc': p.returncode}


def execute_command(command):
    d = do_execute_command(command)
    stdout = d['stdout']
    rc = d['rc']
    if stdout is not None and len(stdout) > 0:
        stdout_text = stdout.decode("utf-8")
    else:
        stdout_text = ""
    if rc == 0:
        return True, stdout_text
    else:
        stderr = d['stderr']
        if stderr is not None and len(stderr) > 0:
            stderr_text = stderr.decode("utf-8")
        else:
            stderr_text = ""

        if len(stderr_text) > 0:
            text = stderr_text
        elif len(stdout_text) > 0:
            text = stdout_text
        else:
            text = "command failed, rc=%d" % rc
        return False, text


def show_output(d, title, output):
    d.msgbox(width=70, height=40, title=str(title), text=str(output))


def ui_execute_command(d, command, title):
    success, output = execute_command(command)
    if success:
        show_output(d, "Success: %s" % title, output)
    else:
        show_output(d, "Failed: %s" % title, output)


def get_hostname():
    return platform.node()


def view_file(d, title, file_path):
    d.programbox(file_path=file_path)


def format_fastpath(fastpath):
    return " (%s)" % fastpath


def err_invalid_fastpath(fp):
    print("error: invalid fastpath '%s'" % fp)
    sys.exit(1)


def update_parent_fastpath(parent_fastpath, fastpath):
    if len(parent_fastpath) > 0:
        parent_fastpath = parent_fastpath + "."
    parent_fastpath = parent_fastpath + fastpath
    return parent_fastpath


def to_datetime(yyyy_mm_dd_string):
    try:
        dt = datetime.strptime(yyyy_mm_dd_string, '%Y-%m-%d')
        return dt
    except ValueError:
        return None


def is_valid_date_yyyy_mm_dd(date_string):
    if to_datetime(date_string) is not None:
        return True
    else:
        return False


def is_past_date(date_string):
    dt = to_datetime(date_string)
    if dt is not None:
        now = datetime.now()
        if now > dt:
            return True
        else:
            return False
    return False


def message_box(d, title, message):
    d.msgbox(width=0, height=0, title=title, text=message)


def run_menu(d, menu, fastpath_array, parent_fastpath):
    if fastpath_array is not None and len(fastpath_array) > 0:
        fastpath = fastpath_array[0]
        fastpath_array.pop(0)
        for i in range(menu.number_options()):
            menu_option = menu.get_option(i)
            if fastpath == menu_option.fastpath:
                full_fastpath = update_parent_fastpath(parent_fastpath, fastpath)
                callback = menu_option.callback
                callback(d, fastpath_array, full_fastpath)
                break
        err_invalid_fastpath(fastpath)
    else:
        in_menu = True
        menu_choices = []
        for i in range(menu.number_options()):
            menu_option = menu.get_option(i)
            opt_tuple = ("%d" % (i+1), "%s %s" % (menu_option.title, format_fastpath(menu_option.fastpath)))
            menu_choices.append(opt_tuple)

        while in_menu:
            code, tag = d.menu(menu.get_title(), choices=menu_choices)
            if code == d.OK:
                tag_as_int = int(tag)
                index = tag_as_int - 1
                menu_option = menu.get_option(index)
                full_fastpath = update_parent_fastpath(parent_fastpath, menu_option.fastpath)
                callback = menu_option.callback
                callback(d, fastpath_array, full_fastpath)
            else:
                in_menu = False


def create_alert_form(d, fastpath_array, parent_fastpath):
    base_fastpath = c.FP_CREATE_ALERT
    full_fastpath = update_parent_fastpath(parent_fastpath, base_fastpath)
    title = "Create Alert %s" % format_fastpath(full_fastpath)
    col1 = 2
    col2 = col1 + 10
    current_date = datetime.today().strftime('%Y-%m-%d')

    running_form = True

    note_text = ""
    category = ""
    eff_date = current_date
    is_active = "Y"

    while running_form:
        elements = [
                ("Note",      1, col1, note_text, 1, col2, 60, 60),
                ("Category",  2, col1, category, 2, col2, 20, 20),
                ("Eff. Date", 3, col1, eff_date, 3, col2, 10, 10),
                ("Active",    4, col1, is_active, 4, col2, 1, 1)]
        code, form_fields = d.form(title, elements, width=77)
        if code == d.OK:
            note_text = form_fields[0]
            category = form_fields[1]
            eff_date = form_fields[2]
            is_active = form_fields[3]

            if len(note_text) == 0:
                # error: alert note text cannot be empty
                pass
            # TODO: validate date
            # if not is_valid_date_yyyy_mm_date(eff_date):

            upper_is_active = is_active.upper()
            if upper_is_active != 'Y' and upper_is_active != 'N':
                # error: active must be either 'Y' or 'N'
                pass

            with open(c.ALERTS_FILE, "a") as f:
                file_record = "%s|%s|%s|%s\n" % (upper_is_active, eff_date, category, note_text)
                f.write(file_record)

            message_box(d, "Alerts", "New alert posted")
            running_form = False
        else:
            running_form = False


def view_block_device(d, blk_device):
    ui_execute_command(d, "/usr/bin/udevadm info --query=all --name=%s" % blk_device, "View block device")
    # lsblk /dev/sda


def do_server_lsblk(d, fastpath_array, parent_fastpath):
    ui_execute_command(d, "/usr/bin/lsblk | grep disk", "List block devices")


def server_view_block_device(d, fastpath_array, parent_fastpath):
    # TODO: implement server_view_block_device
    pass


def do_server_lvm_mkpv(d, fastpath_array, parent_fastpath):
    # TODO: implement do_server_lvm_mkpv
    # /usr/sbin/pvcreate
    pass


def do_server_lvm_lspv(d, fastpath_array, parent_fastpath):
    ui_execute_command(d, "/usr/sbin/pvscan", "List physical volumes")


def do_server_lvm_rmpv(d, fastpath_array, parent_fastpath):
    # TODO: implement do_server_lvm_rmpv
    # /usr/sbin/pvremove
    pass


def do_server_lvm_mkvg(d, fastpath_array, parent_fastpath):
    # TODO: implement do_server_lvm_mkvg
    # /usr/sbin/vgcreate
    pass


def do_server_lvm_lsvg(d, fastpath_array, parent_fastpath):
    ui_execute_command(d, "/usr/sbin/vgscan", "List volume groups")


def do_server_lvm_rmvg(d, fastpath_array, parent_fastpath):
    # TODO: implement do_server_lvm_rmvg
    # /usr/sbin/vgremove
    pass


def lvm_pv_menu(d, fastpath_array, parent_fastpath):
    menu = Menu("Physical Volumes", c.FP_PV, parent_fastpath)
    menu.add_option(MenuOption("Create physical volume", c.FP_CREATE_PV, do_server_lvm_mkpv))
    menu.add_option(MenuOption("List physical volumes", c.FP_LIST_PV, do_server_lvm_lspv))
    menu.add_option(MenuOption("Remove physical volume", c.FP_REMOVE_PV, do_server_lvm_rmpv))
    run_menu(d, menu, fastpath_array, parent_fastpath)


def lvm_vg_menu(d, fastpath_array, parent_fastpath):
    menu = Menu("Volume Groups", c.FP_VG, parent_fastpath)
    menu.add_option(MenuOption("Create volume group", c.FP_CREATE_VG, do_server_lvm_mkvg))
    menu.add_option(MenuOption("List volume groups", c.FP_LIST_VG, do_server_lvm_lsvg))
    menu.add_option(MenuOption("Remove volume group", c.FP_REMOVE_VG, do_server_lvm_rmvg))
    run_menu(d, menu, fastpath_array, parent_fastpath)


def do_server_lvm_mklv(d, fastpath_array, parent_fastpath):
    # TODO: implement do_server_lvm_mklv
    # /usr/sbin/lvcreate
    pass


def do_server_lvm_lslv(d, fastpath_array, parent_fastpath):
    ui_execute_command(d, "/usr/sbin/lvscan", "List logical volumes")


def do_server_lvm_rmlv(d, fastpath_array, parent_fastpath):
    # TODO: implement do_server_lvm_rmlv
    # /usr/sbin/lvremove
    pass


def lvm_lv_menu(d, fastpath_array, parent_fastpath):
    menu = Menu("Logical Volumes", c.FP_LV, parent_fastpath)
    menu.add_option(MenuOption("Create logical volume", c.FP_CREATE_LV, do_server_lvm_mklv))
    menu.add_option(MenuOption("List logical volumes", c.FP_LIST_LV, do_server_lvm_lslv))
    menu.add_option(MenuOption("Remove logical volume", c.FP_REMOVE_LV, do_server_lvm_rmlv))
    run_menu(d, menu, fastpath_array, parent_fastpath)


def server_health_menu(d, fastpath_array, parent_fastpath):
    # TODO: implement server health checks
    #   memory swapping?
    #   all required NICs up and connected?
    #   cpu not pegged?
    #   iostat/vmstat not indicating anything bad?
    #   all required filesystems mounted?
    pass


def server_lvm_menu(d, fastpath_array, parent_fastpath):
    menu = Menu("LVM", c.FP_LVM, parent_fastpath)
    menu.add_option(MenuOption("Physical Volumes", c.FP_PV, lvm_pv_menu))
    menu.add_option(MenuOption("Volume Groups", c.FP_VG, lvm_vg_menu))
    menu.add_option(MenuOption("Logical Volumes", c.FP_LV, lvm_lv_menu))
    run_menu(d, menu, fastpath_array, parent_fastpath)


def server_block_devices_menu(d, fastpath_array, parent_fastpath):
    menu = Menu("Block Devices", c.FP_BLOCK_DEVICE, parent_fastpath)
    menu.add_option(MenuOption("List Block Devices", c.FP_LIST_BLOCK_DEVICE, do_server_lsblk))
    menu.add_option(MenuOption("View Block Device", c.FP_VIEW_BLOCK_DEVICE, server_view_block_device))
    run_menu(d, menu, fastpath_array, parent_fastpath)


def server_bonds_menu(d, fastpath_array, parent_fastpath):
    # TODO: implement server_bonds_menu
    pass


def server_vlans_menu(d, fastpath_array, parent_fastpath):
    # TODO: implement server_vlans_menu
    pass


def server_nic_ports_menu(d, fastpath_array, parent_fastpath):
    ui_execute_command(d, "/usr/sbin/ip link show", "Display network interfaces")


def server_nics_menu(d, fastpath_array, parent_fastpath):
    # TODO: implement server_nics_menu
    pass


def server_network_menu(d, fastpath_array, parent_fastpath):
    menu = Menu("Network", c.FP_NET, parent_fastpath)
    menu.add_option(MenuOption("Bonds", c.FP_BOND, server_bonds_menu))
    menu.add_option(MenuOption("VLANs", c.FP_VLAN, server_vlans_menu))
    menu.add_option(MenuOption("NIC Ports", c.FP_PORT, server_nic_ports_menu))
    menu.add_option(MenuOption("NICs", c.FP_NIC, server_nics_menu))
    run_menu(d, menu, fastpath_array, parent_fastpath)


def server_perf_menu(d, fastpath_array, parent_fastpath):
    # TODO: implement server_perf_menu
    pass


def server_history_menu(d, fastpath_array, parent_fastpath):
    title = "Server History"
    if os.path.isfile(c.SERVER_HISTORY_FILE):
        view_file(d, title, c.SERVER_HISTORY_FILE)
    else:
        message_box(d, title, "No server updates have been made")


def server_logs_menu(d, fastpath_array, parent_fastpath):
    # TODO: implement server_logs_menu
    pass


def server_filesystems_menu(d, fastpath_array, parent_fastpath):
    ui_execute_command(d, "/usr/bin/mount -t ext4 | grep -v snap", "List mounted filesystems")


def server_free_space_menu(d, fastpath_array, parent_fastpath):
    ui_execute_command(d, "/usr/bin/df", "Show free space")


def zone_menu(d, fastpath_array, parent_fastpath):
    message_box(d, "Not Implemented", "Zone functionality not implemented yet")


def cluster_health_menu(d, fastpath_array, parent_fastpath):
    # TODO: implement cluster health checks
    #   all nodes online?
    #   all OSDs online?
    #   ceph -s indicating HEALTH_OK?
    #   anything degraded or misplaced?
    #   gateway checks?
    pass


def cluster_pools_menu(d, fastpath_array, parent_fastpath):
    # TODO: implement cluster_pools_menu
    pass


def cluster_osds_menu(d, fastpath_array, parent_fastpath):
    # TODO: implement cluster_osds_menu
    pass


def cluster_mons_menu(d, fastpath_array, parent_fastpath):
    # TODO: implement cluster_mons_menu
    pass


def cluster_gw_menu(d, fastpath_array, parent_fastpath):
    # TODO: implement cluster_gw_menu
    pass


def cluster_servers_menu(d, fastpath_array, parent_fastpath):
    # TODO: implement cluster_servers_menu
    pass


def cluster_perf_menu(d, fastpath_array, parent_fastpath):
    # TODO: implement cluster_perf_menu
    pass


def cluster_history_menu(d, fastpath_array, parent_fastpath):
    title = "Cluster History"
    if os.path.isfile(c.CLUSTER_HISTORY_FILE):
        view_file(d, title, c.CLUSTER_HISTORY_FILE)
    else:
        message_box(d, title, "No cluster updates have been made")


def cluster_df_menu(d, fastpath_array, parent_fastpath):
    # TODO: implement cluster_df_menu
    pass


def cluster_menu(d, fastpath_array, parent_fastpath):
    menu = Menu("Cluster Menu", c.FP_CLUSTER, parent_fastpath)
    menu.add_option(MenuOption("Health", c.FP_HEALTH, cluster_health_menu))
    menu.add_option(MenuOption("Pools", c.FP_POOL, cluster_pools_menu))
    menu.add_option(MenuOption("OSDs", c.FP_OSD, cluster_osds_menu))
    menu.add_option(MenuOption("MONs", c.FP_MON, cluster_mons_menu))
    menu.add_option(MenuOption("Gateways", c.FP_GATEWAY, cluster_gw_menu))
    menu.add_option(MenuOption("Servers", c.FP_SERVER, cluster_servers_menu))
    menu.add_option(MenuOption("Performance", c.FP_PERF, cluster_perf_menu))
    menu.add_option(MenuOption("History", c.FP_HISTORY, cluster_history_menu))
    menu.add_option(MenuOption("Space", c.FP_FREE_SPACE, cluster_df_menu))
    run_menu(d, menu, fastpath_array, parent_fastpath)


def server_menu(d, fastpath_array, parent_fastpath):
    menu = Menu("Server Menu", c.FP_SERVER, parent_fastpath)
    menu.add_option(MenuOption("Health", c.FP_HEALTH, server_health_menu))
    menu.add_option(MenuOption("LVM", c.FP_LVM, server_lvm_menu))
    menu.add_option(MenuOption("Block devices", c.FP_BLOCK_DEVICE, server_block_devices_menu))
    menu.add_option(MenuOption("Network", c.FP_NET, server_network_menu))
    menu.add_option(MenuOption("Filesystems", c.FP_FILESYSTEM, server_filesystems_menu))
    menu.add_option(MenuOption("Free space", c.FP_FREE_SPACE, server_free_space_menu))
    menu.add_option(MenuOption("Logs", c.FP_LOG, server_logs_menu))
    menu.add_option(MenuOption("Performance", c.FP_PERF, server_perf_menu))
    menu.add_option(MenuOption("History", c.FP_HISTORY, server_history_menu))
    run_menu(d, menu, fastpath_array, parent_fastpath)


def history_menu(d, fastpath_array, parent_fastpath):
    title = "History"
    if os.path.isfile(c.HISTORY_FILE):
        view_file(d, title, c.HISTORY_FILE)
    else:
        message_box(d, title, "No updates have been made")


def list_alerts_menu(d, fastpath_array, parent_fastpath):
    title = "Alerts"
    if os.path.isfile(c.ALERTS_FILE):
        view_file(d, title, c.ALERTS_FILE)
    else:
        message_box(d, title, "No alerts have been posted")


def alerts_menu(d, fastpath_array, parent_fastpath):
    menu = Menu("Alerts Menu", c.FP_ALERT, parent_fastpath)
    menu.add_option(MenuOption("Create alert", c.FP_CREATE_ALERT, create_alert_form))
    menu.add_option(MenuOption("List alerts", c.FP_LIST_ALERT, list_alerts_menu))
    run_menu(d, menu, fastpath_array, parent_fastpath)


def do_quit(d, fastpath_array, parent_fastpath):
    sys.exit(0)


def main():
    # This is almost always a good thing to do at the beginning of your programs.
    locale.setlocale(locale.LC_ALL, '')

    # You may want to use 'autowidgetsize=True' here (requires pythondialog >= 3.1)
    d = Dialog(dialog="dialog")
    # Dialog.set_background_title() requires pythondialog 2.13 or later
    d.set_background_title("Storage Admin v%s [%s]" % (c.APP_VERSION, get_hostname()))

    argc = len(sys.argv) - 1

    if argc > 0:
        fastpath_array = sys.argv[1].split('.')
    else:
        fastpath_array = None

    menu = Menu("MAIN MENU", "", "")
    menu.add_option(MenuOption("Server", c.FP_SERVER, server_menu))
    menu.add_option(MenuOption("Cluster", c.FP_CLUSTER, cluster_menu))
    menu.add_option(MenuOption("Zone", c.FP_ZONE, zone_menu))
    menu.add_option(MenuOption("History", c.FP_HISTORY, history_menu))
    menu.add_option(MenuOption("Alerts", c.FP_ALERT, alerts_menu))
    menu.add_option(MenuOption("Quit", c.FP_QUIT, do_quit))
    run_menu(d, menu, fastpath_array, "")


if __name__ == '__main__':
    main()

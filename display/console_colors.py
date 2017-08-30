
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def color_ok(msg):
    return bcolors.OKGREEN + msg + bcolors.ENDC

def color_error(msg):
    return bcolors.FAIL + msg + bcolors.ENDC

def has_color_ok(msg):
    if bcolors.OKGREEN in msg and bcolors.ENDC in msg:
        return True
    return False

def has_color_error(msg):
    if bcolors.FAIL in msg and bcolors.ENDC in msg:
        return True
    return False

def del_color_ok(msg):
    if bcolors.OKGREEN in msg and bcolors.ENDC in msg:
        msg = msg.replace(bcolors.OKGREEN, '')
        msg = msg.replace(bcolors.ENDC, '')
    return msg

def del_color_error(msg):
    if bcolors.FAIL in msg and bcolors.ENDC in msg:
        msg = msg.replace(bcolors.FAIL, '')
        msg = msg.replace(bcolors.ENDC, '')
    return msg

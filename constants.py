CAS_SERVER  = "https://websso.wwu.edu:443"

# If we're in the labs, use the fully qualified domain name of the system.
# This is temporary and should be removed in release-worthy versions.
import socket
if socket.gethostname()[0:5].lower() in ["cf405", "cf416", "cf162", "cf164"]:
    SERVICE_URL = "https://{}:8080/".format(socket.getfqdn())
else:
    SERVICE_URL = "https://localhost:8080/"

DATA_DIR = STUDENTS_DIR = "./data"
STUDENTS_DIR = "./data/students"
TEMPLATES_DIR = "./data/templates"
TRASH_DIR = "./data/trash"

PROJECT_DATA_EXTENSIONS = [".cpp", ".c", ".h", ".text", ".txt"]

COOKIE_SECRET = "g9Usc0wTSMWxV5a7G5o5YcXPb3ftcUBwhUoFT62KJks="

PERMISSION_LEVEL_ADMIN = 4
PERMISSION_LEVEL_PROF = 3
PERMISSION_LEVEL_TA = 2
PERMISSION_LEVEL_USER = 1
PERMISSION_LEVEL_NONE = 0

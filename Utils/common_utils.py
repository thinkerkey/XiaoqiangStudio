from os import stat_result
from PySide2.QtWidgets import QFileDialog
import json
import re


PCD_MODE = 1
PCAP_MODE = 2
REGRESSION_MODE = 3

INSTALL_MODE = 1
DEPLOY_MODE = 2
OTHER = 0

ERROR = 0
NORMAL = 1

info_color_list = [
    "#ff0000",
    "#00ff00",
]

KEYPRIVATE = "w09f*1l.kl~7tl-t0hmc-eizlsk3jo*+b72wjz*!"

# Regular expression for comments
comment_re = re.compile(
    '(^)?[^\S\n]*/(?:\*(.*?)\*/[^\S\n]*|/[^\n]*)($)?',
    re.DOTALL | re.MULTILINE
)
def parse_json(filename):
    # start = time.time()
    """ Parse a JSON file
        First remove comments and then use the json module package
        Comments look like :
            // ...
        or
            /*
            ...
            */
    """
    with open(filename, encoding="utf-8") as f:
        content = ''.join(f.readlines())
        ## Looking for comments
        match = comment_re.search(content)
        while match:
            # single line comment
            content = content[:match.start()] + content[match.end():]
            match = comment_re.search(content)
        # Return json file
    # print(filename, time.time()-start)
    return json.loads(content)


def write_json(json_data,json_name):
    # Writing JSON data
    with open(json_name, 'w', encoding="utf-8") as f:
        json.dump(json_data, f,indent=4)


def get_mac_address():
    import uuid
    node = uuid.getnode()
    mac = uuid.UUID(int = node).hex[-12:]
    return mac

def choose_file(ui_,info,ename,file_path = "./"):
    selected_file_path, _ = QFileDialog.getOpenFileName(ui_,
                                        info,
                                        file_path,
                                        ename)
    return selected_file_path

def choose_folder(ui_,info,file_path = "./"):
    directory = QFileDialog.getExistingDirectory(ui_, info, file_path)
    return directory

# 将列表递归创建成字典
def creat_dic_from_list(veh,key_value):
    dic = {}
    if veh == []:
        return key_value
    else:
        key = veh[0]
        veh.pop(0)
        dic[key] = creat_dic_from_list(veh,key_value)
    return dic
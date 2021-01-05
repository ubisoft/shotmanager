import re


def start_with_act(s):
    res = re.match(r"^Act(\d\d)", s)
    if res is not None:
        return True, res.group(1)
    return False, ""


def start_with_seq(s):
    res = re.match(r"^Act(\d\d)_Seq(\d\d\d\d)", s)
    if res is not None:
        return True, res.group(1), res.group(2)
    return False, "", ""


def start_with_shot(s):
    res = re.match(r"^Act(\d\d)_Seq(\d\d\d\d)_Sh(\d\d\d\d)", s)
    if res is not None:
        return True, res.group(1), res.group(2), res.group(3)
    return False, "", "", ""

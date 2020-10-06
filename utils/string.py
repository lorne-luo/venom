import re


def format_dict(d):
    ret_str = ''
    para_list = sorted(d.keys())
    for para in para_list:
        ret_str += '{:18}{}\n'.format(para + ':', d[para])
    return ret_str

def extract_number(s):
    n = re.findall("[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", s)
    if n:
        return n[0].replace(',', '')
    return None
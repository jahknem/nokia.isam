import itertools
import logging
import re
from datetime import datetime
from unittest import result
from xml.etree.ElementTree import ElementTree

LOG_FORMAT = '%(asctime)-15s %(filename)s %(funcName)s line %(lineno)d %(levelname)s:  %(message)s'


def init_logging():
    date = datetime.now()
    new_date = date.strftime('%Y-%m-%d %H.%M.%S')
    file_path = "./logs_{}.log".format(new_date)
    logging.basicConfig(filename=file_path, format=LOG_FORMAT, level=logging.DEBUG)
    return logging.getLogger()

def getFirstXMLElement(tree, attrib, name=None):
    iteration = tree.iter(attrib)
    for i in iteration:
        if name is not None:
            if i.attrib.get("name") ==name:
                return i

def getFirstXMLElementText(tree, attrib,name=None):
    iteration = tree.iter(attrib)
    for i in iteration:
        if name is not None:
            if i.attrib.get("name") ==name:
                return i.text

def getXMLElements(tree, attrib, name=None):
    iteration = tree.iter(attrib)
    result = []
    for i in iteration:
        if name is not None:
            if i.attrib.get("name") ==name:
                result.append(i)
        else:
            result.append(i)
    return result

def removeCtrlChars(s):
    control_chars = ''.join(map(chr, itertools.chain(range(0x00,0x20), range(0x7f,0xa0))))
    control_char_re = re.compile('[%s]' % re.escape(control_chars))
    satinized_s = control_char_re.sub('', s)
    difference = diff(s,satinized_s)
    return satinized_s

def removeAlarms(s):
    out = ''
    for l in s.splitlines(keepends=True):
        if not re.search('^\d{2}\/\d{2}\/\d{2}',l):
            out +=l
    return out


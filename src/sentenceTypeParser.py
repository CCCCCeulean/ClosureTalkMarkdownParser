import re
from enum import Enum
from typing import List, Tuple

""" 
1. 选择 1
"""
class ListType(Enum):
    无缩列表 = 100
    临时命名无缩列表 = 101
    主角无缩列表 = 102
    线上角色专用右倾斜列表 = 103
    选择列表 = 104
    缩进列表 = 200
    缩进旁白 = 201 
    缩进羁绊 = 202 
    插入本地图片 = 203
    插入线上图片 = 204
    接续缩进文本 = 210
    接续缩进旁白 = 211
    分割输出符 = 900
    章节分割 = 901
    OTHER = 9999999
    CLOSURE_TALK_OKAY = 1

PATTERN_MAP = {
    r"\t*(\d)\.\s+(.*[^\s\t\n])\s*$": ListType.选择列表,
    r">\s*\[\!\s*info\s*\]\s*(ClosureTalk)\s*$": ListType.CLOSURE_TALK_OKAY,
    r"\t-\s*\*(.*[^ \t\n])\*\s*$": ListType.缩进旁白,
    r"\t-\s*\=(进入羁绊剧情)\=\s*$": ListType.缩进羁绊,
    r"\t!\[\[(.*)\]\]\s*$": ListType.插入本地图片,
    r"\s*[^ \t\n]*\s*!\[\[(.*)\]\]\s*$": ListType.插入本地图片,
    r"\s*[^ \t\n]*\s*!\[.*\]\(\s*(.*)\s*\)\s*$": ListType.插入线上图片,
    r"\s*-\s*==(.*[^ \t\n]?)\s*=?=?\s*$": ListType.主角无缩列表,
    r"\s*\t+\s*-\s*(.*[^ \t\n])\s*$": ListType.缩进列表,
    r"\s*-\s*\_\s*(.*[^ \t\n])s*\_\s*\\+\|\s*\_\s*(.*[^ \t\n])s*\_\s*$": ListType.线上角色专用右倾斜列表,
    r"\s*-\s*(.*[^ \t\n])\s*\\+\|\s*(.*[^ \t\n])\s*$": ListType.临时命名无缩列表,
    r"\s*(---)-*\s*$": ListType.分割输出符,
    r"\s*-\s*(.*[^ \t\n])\s*$": ListType.无缩列表,
    r"#{1,6}\s*(.*[^ \t\n])\s*$": ListType.章节分割,
    r"\s*\t+\s*\*(.*[^ \t\n])\*\s*$": ListType.接续缩进旁白,
    r"\s*\t+\s*(.*[^ \t\n])\s*$": ListType.接续缩进文本,
}

isEasySplit = True 
if(isEasySplit):
    PATTERN_MAP = {
    r"\t*(\d)\.\s+(.*[^\s\t\n])\s*$": ListType.选择列表,
    r">\s*\[\!\s*info\s*\]\s*(ClosureTalk)\s*$": ListType.CLOSURE_TALK_OKAY,
    r"\t-\s*\*(.*[^ \t\n])\*\s*$": ListType.缩进旁白,
    r"\s*-\s*==\s*(.*[^ \t\n\\])s*==\s*\\*\|\s*==\s*(.*[^ \t\n])s*==\s*$": ListType.线上角色专用右倾斜列表,
    r"\ *-\s*(.*[^ \t\n\\])\s*\\*\|\s*(.*[^ \t\n])\s*$": ListType.临时命名无缩列表,
    r"\t-\s*==(.*[^\s\t\n])==\s*$": ListType.缩进羁绊,
    r"\s*[^ \t\n]*\s*!?\[\[(.*?)(?:\|[^]]+)?\]\]\s*$": ListType.插入本地图片,
    r"\s*[^ \t\n]*\s*!?\[.*\]\(\s*(.*)\s*\)\s*$": ListType.插入线上图片,
    r"\s*-\s*==(.*[^ \t\n]?)\s*=?=?\s*$": ListType.主角无缩列表,
    r"\s*\t+\s*-\s*(.*[^ \t\n])\s*$": ListType.缩进列表,
    r"\s*(---)-*\s*$": ListType.分割输出符,
    r"\ *-\s*(.*[^ \t\n])\s*$": ListType.无缩列表,
    r"#{1,6}\s*(.*[^ \t\n])\s*$": ListType.章节分割,
    r"\s*\t+\s*\*(.*[^ \t\n])\*\s*$": ListType.接续缩进旁白,
    r"\s*\t+\s*(.*[^ \t\n])\s*$": ListType.接续缩进文本,
}

def reverse_pattern_map(pattern_map: dict) -> dict:
    reversed_map = {}
    for pattern, list_type in pattern_map.items():
        reversed_map[list_type] = pattern
    return reversed_map

# 在模块级别创建反向映射
REV_PATTERN_MAP = reverse_pattern_map(PATTERN_MAP)

def getType(line: str) -> ListType:
    for pattern, list_type in PATTERN_MAP.items():
        if re.match(pattern, line):
            return list_type
    return ListType.OTHER

def extractBundles(line: str) -> Tuple[ListType,  List[str]]:
    currType = getType(line)
    if currType == ListType.OTHER:
        return currType, line
    pattern = REV_PATTERN_MAP[currType]
    match = re.match(pattern, line)
    if match:
        if currType==ListType.临时命名无缩列表 or currType==ListType.选择列表  or currType==ListType.线上角色专用右倾斜列表:
            return currType, [match[1],match[2]]
        else:
            return currType, [match[1]]
    return ListType.OTHER, []


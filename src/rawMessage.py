import logging
from charaParser import CharInfo
from pictureParser import PictureParser

from typing import Dict


class RawMessage:
    def __init__(self):
        self.isLeftInfo = False
        self.is_breaking = False
        self.content = ""  # or image
        self.yuzutalk = {
            "type": "TEXT",  # NARRATION,TEXT,CHOICES,IMAGE,RELATIONSHIPSTORY
            "avatarState": "AUTO",  # AUTO,SHOW
            "nameOverride": ""
        }
        self.char_id = ""
        self.img = "uploaded"
    
    def __init__(self,char:CharInfo=None,type="TEXT",*
                 ,content=""
                 ,is_breaking=False
                 ,avatarState="AUTO"
                 ,nameOverride=""):
        if(char==None):
            self.isLeftInfo = False
            
        else:
            self.isLeftInfo = True
            self.char_id = char.char_id
            self.img = char.img
            """ 至少要放置角色自己的图片 """
        
        self.content = content  # or image
        self.is_breaking = is_breaking
        self.yuzutalk = {
            "type": type,  # NARRATION,TEXT,CHOICES,IMAGE
            "avatarState": avatarState,  # AUTO,SHOW
            "nameOverride": nameOverride
        }
    
    def __json__(self) -> Dict:
        tempDict = {
            "is_breaking": self.is_breaking,
            "content": self.content,
            "yuzutalk": self.yuzutalk
        }
        if self.isLeftInfo:
            tempDict.get("char_id",self.char_id)
            tempDict.get("img",self.img)
        return tempDict
    def __str__(self):
        """
        返回 RawMessage 对象的字符串表示。
        """
        if self.isLeftInfo:
            return f"RawMessage(char_id={self.char_id}, img={self.img[:5]}, content='{self.content}', yuzutalk={self.yuzutalk}, is_breaking={self.is_breaking})"
        else:
            return f"RawMessage(content='{self.content}', yuzutalk={self.yuzutalk}, is_breaking={self.is_breaking})"
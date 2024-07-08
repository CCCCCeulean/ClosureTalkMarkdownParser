import logging
import os
from typing import Dict, List, List, Optional
from pictureParser import PictureParser
import sentenceTypeParser as stp
from sentenceTypeParser import ListType

pure_black = 'data:image/jpg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAIBAQIBAQICAgICAgICAwUDAwMDAwYEBAMFBwYHBwcGBwcICQsJCAgKCAcHCg0KCgsMDAwMBwkODw0MDgsMDAz/2wBDAQICAgMDAwYDAwYMCAcIDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAz/wAARCAABAAEDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD+f+iiigD/2Q=='

class CharInfo:
    def __init__(self, char_id: str, img: str, custom_name: Optional[str] = None):
        self.char_id: str = char_id
        self.img: str = img 
        self.custom_name: Optional[str] = custom_name
        
    def __str__(self):
        return f"{self.char_id} ({self.custom_name}) {self.img}"
    
    def set_image(self, img: str):
        self.img = img
    
""" 
拥有读取线上角色组和自定义角色组的功能
以及自定义的 alias -> (char_id,img) 功能
为了防止重复定义,建立了 alias -> key -> (char_id,img) 的模式 

对于线上角色，必须以:
- ==OnlineName== | ==OnlineImg==
    - alias 
的形态给出,且OnlineName将不会自动产生alias, 必须在后文给定。

自定义角色则:
- keyName | writtenName 
    - alias 
keyName 将默认成为 key与alias。

目前目标:
直接摆烂!
反正都是alias -> chars 
那么Custom_chars再单独开个表就完事了

假如遇到图片or线上图片，则尝试

"""
class CharaParser:
    custom_prev_token = "Custom_"
    
    def __init__(self,pp:PictureParser):
        self.chars: List[CharInfo] = []
        self.custom_chars: List[CharInfo] = []
        self.aliasToChars: dict[str, CharInfo] = {}
        self.currChara = None
        self.logger = logging.getLogger()
        """ self.parseLocalCharaInfo() """
        self.pp = pp
        
    def clearAll(self):
        self.chars.clear()
        self.custom_chars.clear()
        self.aliasToChars.clear()
        self.currChara = None
    
    """ 展示所有当前的字符串行 """
    def toDisplayString(self) -> str:
        lines = []
        reverseAliasDict: dict[tuple[str,str],list[str]] = {}
        
        for k,v in self.aliasToChars.items():
            id_img = (v.char_id,v.img)
            if(id_img not in reverseAliasDict.keys()):
                reverseAliasDict[id_img] = [k]
            else:
                reverseAliasDict[id_img].append(k)
    
        for char in self.chars:
            id_img = (char.char_id,char.img)
            
            tempstr = f"{char.char_id[len(self.custom_prev_token):]} | 正式名称:{char.custom_name}" \
                if char.img == "uploaded" else f"{char.char_id} ~ {char.img}"
            
            if char.img == "uploaded":
                    tempstr+=' | 用户图片' if self.pp.doHavePictures(char.char_id[len(self.custom_prev_token):])\
                        else '暂无图片'
            
            lines.append((tempstr) + '\n')
            
            if(id_img not in reverseAliasDict.keys()):
                lines .append(" |[警告: 没有任何指向该角色的词语!]\n")
                continue
                
            tempList = reverseAliasDict[id_img]
            tempList.sort()
            
            for alias in tempList:
                if alias.startswith(self.custom_prev_token):
                    alias = alias[len(self.custom_prev_token):]
                lines.append(f'\t| {alias}\n')
            # else 
        l = str()
        for line in lines:
            l+=line
        return l

    def parseCharaInfoByFile(self,file_path):        
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            self.logger.info(f"charaParser: 开始读取 {file_path}.")
        self.parseCharaInfoByLines(lines)

    def parseCharaInfoByLines(self,lines):
        meetClosureTalkHead = False
        line_number = 0
        for line in lines:
            line = line.rstrip('\n')
            self.logger.info(f"{line_number}|{line}:")
            line_number += 1
            currType, nameList = stp.extractBundles(line)
            if(not meetClosureTalkHead):
                if(currType==ListType.CLOSURE_TALK_OKAY):
                    self.logger.info(f"   检测到ClosureTalk头部,开始处理")
                    meetClosureTalkHead = True
                else:
                    self.logger.info(f"   还没有遇到ClosureTalk头部,已跳过")
                continue
            match currType:
                case ListType.线上角色专用右倾斜列表:
                    self.checkOnlineDeclaration(nameList)
                case ListType.临时命名无缩列表:
                    self.checkCustomDeclaration(nameList)
                case ListType.无缩列表:
                    self.checkUnfinishedCustomDeclation(nameList)
                case ListType.缩进列表:
                    self.checkAliasDeclaration(nameList)
                case ListType.插入本地图片:
                    self.insertLocalPicture(nameList)
                case ListType.插入线上图片:
                    self.insertOnlinePicture(nameList)
                case _:
                    self.logger.info("   该句不合法,未处理。")
        self.logger.info("===结束parseCharaInfo===")

    def insertLocalPicture(self, nameList):
        imgPureFileName = nameList[0] 
        if not self.currChara:
            self.logger.error(f"还没有任何角色!")
            return 
        if self.currChara.img!="uploaded":
            self.logger.error(f"{self.currChara} 为线上角色,不可指定图片！")
            return 
            
        if not self.pp.doHavePictures(imgPureFileName):
            self.logger.warning(f"向{self.currChara.char_id[len(self.custom_prev_token):]}映射的图片{imgPureFileName}还未加载入图片库!")
            return 
        # else 
        self.pp._forcedBase64Encoding(self.currChara.char_id[len(self.custom_prev_token):],self.pp.get_base64(imgPureFileName))
        self.logger.info(f"角色{self.currChara.char_id[len(self.custom_prev_token):]}拥有了强制映射图片{imgPureFileName}.")
        
    def insertOnlinePicture(self,nameList):
        imgUrl = nameList[0]
        
        if not self.currChara:
            self.logger.error(f"还没有任何角色!")
            return 
        
        if self.currChara.img!="uploaded":
            self.logger.error(f"{self.currChara} 为线上角色,不可指定图片！")
            return 
        
        if self.pp.doHavePictures(imgUrl):
            self.logger.info(f"图片 {imgUrl} 已经存在, 将使用本地图片映射。")
            self.pp._forcedBase64Encoding(self.currChara.char_id[len(self.custom_prev_token):],self.pp.get_base64(imgUrl))
            return
        
        self.logger.info(f"开始后台下载图片 {imgUrl} 并映射。")
        
        self.pp.parse_by_url(imgUrl,self.currChara.char_id[len(self.custom_prev_token):])
        

    def find_duplicated_char(self, chara: CharInfo) -> Optional[CharInfo]:
        existing_chars = {(c.char_id, c.img) for c in self.chars}
        if (chara.char_id, chara.img) in existing_chars or (
            self.custom_prev_token + chara.char_id,
            chara.img,
        ) in existing_chars or (
            chara.char_id,
            self.custom_prev_token + chara.char_id,
        ) in existing_chars:
            if chara.img!="uploaded":
                self.logger.error(f"   输入角色{chara.char_id},{chara.img}已重复")
            else:
                self.logger.error(f"   输入角色{chara.char_id}已重复")
            return next(
                c for c in self.chars
                if c.img == chara.img and (
                    c.char_id == chara.char_id or
                    self.custom_prev_token + c.char_id == chara.char_id or
                    c.char_id == self.custom_prev_token + chara.char_id
                )
            )
        return None

    def checkOnlineDeclaration(self, nameList):
        currCharId, currCharImg = nameList[0], nameList[1]
        self.logger.info(f"   检测到线上角色{currCharId},{currCharImg}")
        self.currChara = CharInfo(currCharId, currCharImg)
        possChara = self.find_duplicated_char(self.currChara)
        if possChara is None:
            self.logger.info(f"   成功载入线上角色{currCharId},{currCharImg}")
            self.chars.append(self.currChara)

    def checkCustomDeclaration(self, nameList:list[str]) -> None:
        currCharId, currCharName = nameList[0], nameList[1]
        self.logger.info(f"   检测到用户角色{currCharId},{currCharName}")
        self.currChara = CharInfo(currCharId, "uploaded" , currCharName)
        possChara = self.find_duplicated_char(self.currChara)
        if possChara is None:
            self.logger.info(f"   成功载入用户角色{currCharId},{currCharName}")
            self.currChara.char_id=self.custom_prev_token+self.currChara.char_id
            self.chars.append(self.currChara)
            self.custom_chars.append(self.currChara)
            self.aliasToChars[self.currChara.char_id] = self.currChara
        elif possChara.char_id == possChara.custom_name:
            self.logger.warning(f"   用户角色{currCharId}已存在,修订其显示名为{currCharName}")
            possChara.custom_name = self.currChara.custom_name
        else:
            self.logger.warning(f"   用户角色{currCharId}与其正式名称{possChara.custom_name}已存在,录入失败。")

    def checkUnfinishedCustomDeclation(self, nameList):
        currCharId = nameList[0]
        self.logger.info(f"   检测到用户角色{currCharId}")
        self.currChara = CharInfo(currCharId, "uploaded" , currCharId)
        possChara = self.find_duplicated_char(self.currChara)
        if possChara is None:
            self.currChara.char_id=self.custom_prev_token+self.currChara.char_id
            self.chars.append(self.currChara)
            self.custom_chars.append(self.currChara)
            self.aliasToChars[self.currChara.char_id] = self.currChara
            self.logger.info(f"   成功载入用户角色{currCharId},{currCharId}")
        else:
            self.currChara = possChara
            self.logger.info(f"   用户角色{currCharId},{possChara.custom_name}已存在,继续进行声明")

    def checkAliasDeclaration(self, nameList):
        currAlias = nameList[0]
        if currAlias in self.aliasToChars.keys() or not self.currChara:
            self.logger.error(f"   别名{currAlias}已与{self.aliasToChars[currAlias].char_id}建立联系!")
            return
        self.aliasToChars[currAlias] = self.currChara
        if(self.currChara.char_id.startswith(self.custom_prev_token)):
            self.logger.info(f"   成功载入别名 {currAlias} -> {self.currChara.char_id[len(self.custom_prev_token):]}")
        else:
            self.logger.info(f"   成功载入别名 {currAlias} -> {self.currChara.char_id}")

    def get_charinfo(self,alias:str) -> CharInfo:
        if alias in self.aliasToChars.keys():
            return self.aliasToChars[alias]
        if self.custom_prev_token+ alias in self.aliasToChars.keys():
            return self.aliasToChars[self.custom_prev_token+ alias]
        return None
        
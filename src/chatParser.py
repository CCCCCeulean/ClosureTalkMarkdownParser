
from enum import Enum
import json
import logging
import os
import time
from typing import Dict, List
from messageFactory import MessageFactory
from rawMessage import RawMessage
from charaParser import CharaParser
from pictureParser import PictureParser
from sentenceTypeParser import ListType
import sentenceTypeParser as stp
from charaParser import CharaParser
import tempfile

class chatParser:
    def __init__(self,cp:CharaParser,pp:PictureParser):
        self.chatList : List[RawMessage] = []
        self.pp : PictureParser = pp
        self.cp : CharaParser = cp
        self.currTitle : str = "Untitled"
        self.logger = logging.getLogger()
        """ self.parsePath() """
    
    """     
    def parseMarkdownByPath(self,base_path=None):
        base_path = base_path if base_path else os.getcwd()
        if not os.path.exists(base_path):
            self.logger.warning(f"警告: 路径 {base_path} 不存在!")
            return
        for root, _, files in os.walk(base_path):
            for file in files:
                file_path = os.path.join(root, file)
                if file_path.endswith(('.md')) and file!="_CustomCharaSet.md":
                    result = self.parseMarkdownByFile(file_path)
                    if result==True:
                        self.save_to_file(file_path)
                    self.chatList.clear()
    """
                    
    def parseMarkdownByFile(self,file_path:str):
        with open(file_path, 'r', encoding='utf-8') as md_file:
            lines = md_file.readlines()
        self.parseMarkdownByLines(lines)
    
    def parseMarkdownByLines(self,lines:list[str]):
        self.chatList.clear()
        mf = MessageFactory(self.cp,self.pp)
        self.logger.info(f"开始处理Markdown转为正文:")
        line_number = 0
        for line in lines:
            line = line.rstrip('\n')
            self.logger.info(f"{line_number}|{line}:")
            line_number += 1
            currType,strList = stp.extractBundles(line)
            self.logger.info(f"   {currType}: {strList}:")
            temp = mf.getMessage(currType,strList)
            if(temp):
                self.chatList.append(temp)
        return True

        
    def to_json(self) -> Dict[str, List[Dict]]:
        self.logger.info(f"正在转换json文件......")
        chat = []
        chars = []
        cusmtom_chars = []
        tempDict = {"chat": chat,"chars": chars,"custom_chars": cusmtom_chars}
        
        if not self.pp.task_queue.empty():
            self.logger.warning("下载队列仍在工作,正在等待。")
            while not self.pp.task_queue.empty():
                time.sleep(1)
        
        for msg in self.chatList:
            chat_item = {}
            if msg.isLeftInfo:
                chat_item["char_id"] = msg.char_id
                chat_item["img"] = msg.img
            chat_item["is_breaking"] = msg.is_breaking
            chat_item["content"] = msg.content
            chat_item["yuzutalk"] = msg.yuzutalk

            if msg.yuzutalk["type"]=="IMAGE":
                if self.pp.doHavePictures(msg.content) == False:
                    self.logger.warning(f"{msg.content} 没有图片，默认为黑。")
                chat_item["content"] = self.pp.get_base64(msg.content)
            chat.append(chat_item)
        for char in self.cp.chars:
            char_item = {
                "char_id": char.char_id,
                "img": char.img
            }
            chars.append(char_item)
        for char in self.cp.custom_chars:
            if self.pp.doHavePictures(char.char_id[len(CharaParser.custom_prev_token):]) == False:
                self.logger.warning(f"{char.char_id} 没有图片，默认头像为黑。")
            char_item = {
                "char_id": char.char_id,
                "img": self.pp.get_base64(char.char_id[len(CharaParser.custom_prev_token):]),
                "name": char.custom_name
            }
            cusmtom_chars.append(char_item)        
        return tempDict
    
    def save_to_str(self) -> str:
        with tempfile.NamedTemporaryFile(mode="w", delete=False,encoding="utf-8") as temp_file:
            json.dump(self.to_json(),temp_file,ensure_ascii=False,indent=2)
        with open(temp_file.name, "r",encoding="utf-8") as temp_file:
            formatted_json = temp_file.read()
        return formatted_json
    
    def save_to_file(self, file_path: str):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.to_json(), f, ensure_ascii=False, indent=2)
            
from rawMessage import RawMessage
from charaParser import CharInfo, CharaParser
from pictureParser import PictureParser
from sentenceTypeParser import ListType


from typing import List

pure_black = 'data:image/jpg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAIBAQIBAQICAgICAgICAwUDAwMDAwYEBAMFBwYHBwcGBwcICQsJCAgKCAcHCg0KCgsMDAwMBwkODw0MDgsMDAz/2wBDAQICAgMDAwYDAwYMCAcIDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAz/wAARCAABAAEDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD+f+iiigD/2Q=='


class MessageFactory:
    def __init__(self,cp:CharaParser,pp:PictureParser):
        self.pp:PictureParser= pp
        self.prevMessage :RawMessage = None
        self.cs:CharaParser = cp
        self.currChara :CharInfo = None
        self.wantSelection = 0
        
        self.doStartMessage = False
        self.nameOverride = ""
        
        self.beginToWork = False

    def getMessage(self,currType:ListType,wordList:List[str])->RawMessage:
        if not (self.beginToWork==True or currType==ListType.CLOSURE_TALK_OKAY):
            return None
        self.beginToWork = True
        content = None 
        if(len(wordList)>0):
            content = wordList[0]
        match currType:
            case ListType.CLOSURE_TALK_OKAY:
                print("检测到ClosureTalkKey,不应该啊......")
                return None
            case ListType.无缩列表:
                print("处理无缩列表: 新角色")
                self.currChara = self.cs.get_charinfo(content)
                if(self.currChara==None):
                    print("你所提供的_CustomCharaSet.md不支持该角色！")
                self.doStartMessage  = True
                self.nameOverride = ""
                return None
            case ListType.临时命名无缩列表:
                print("处理临时命名无缩列表: 临时命名")
                self.nameOverride = wordList[1]
                self.currChara = self.cs.get_charinfo(content)
                if(self.currChara==None):
                    print("你所提供的_CustomCharaSet.md不支持该角色！")
                self.doStartMessage  = True
                return None
            case ListType.主角无缩列表:
                print("处理主角无缩列表: 开始右侧对话")
                self.currChara = None 
                return None
            case ListType.线上角色专用右倾斜列表:
                print("处理线上角色专用右倾斜列表: 这里不应该处理这玩意......")
                return None
            case ListType.选择列表:
                print("处理选择列表: 开始输出选择")
                if(self.prevMessage):
                    if self.prevMessage.yuzutalk["type"]=="CHOICES" and\
                        str(self.wantSelection) == content:
                        self.prevMessage.content+="\n"+ wordList[1]
                        self.wantSelection = int(content) + 1
                        return None
                tempMessage = RawMessage(self.currChara
                                        ,content=wordList[1]
                                        ,avatarState="SHOW" if self.doStartMessage else "AUTO"
                                        ,nameOverride=self.nameOverride if self.doStartMessage else ""
                                        ,type="CHOICES"
                                        )
                self.prevMessage = tempMessage
                self.wantSelection = 2
                return tempMessage
            case ListType.缩进列表:
                print("处理缩进列表: 接着上一角色继续叙事")
                tempMessage = RawMessage(self.currChara
                                         ,content=content
                                         ,avatarState="SHOW" if self.doStartMessage else "AUTO"
                                         ,nameOverride=self.nameOverride if self.doStartMessage else ""
                                         )
                self.nameOverride = ""
                self.doStartMessage = False
                self.prevMessage = tempMessage
                return tempMessage
            case ListType.缩进旁白:
                print("处理缩进旁白: 输出一段旁白")
                tempMessage = RawMessage(self.currChara,type="NARRATION",content=content)
                self.prevMessage = tempMessage
                return tempMessage
            case ListType.缩进羁绊:
                print("处理缩进羁绊剧情: 进入羁绊剧情")
                tempMessage = RawMessage(self.currChara
                                         ,content=content
                                         ,avatarState="SHOW" if self.doStartMessage else "AUTO"
                                         ,nameOverride=self.nameOverride if self.doStartMessage else ""
                                         ,type="RELATIONSHIPSTORY"
                                         )
                self.prevMessage = tempMessage
                return tempMessage
            case ListType.插入本地图片:
                print("处理图片: 发图!")
                tempMessage = RawMessage(self.currChara
                                         ,content=content
                                         ,type="IMAGE")
                self.prevMessage = tempMessage
                return tempMessage
            case ListType.插入线上图片:
                print("插入线上图片,有点难办啊......")
                self.pp.parse_by_url(content)
                tempMessage = RawMessage(self.currChara,
                                         content=content,
                                         type="IMAGE")
                self.prevMessage = tempMessage
                return tempMessage                
            case ListType.接续缩进文本:
                print("处理接续缩进文本: 接连在一起的对话")
                if(self.prevMessage):
                    self.prevMessage.content+="\n"+content
                return None
            case ListType.接续缩进旁白:
                print("处理接续缩进旁白: 接连的旁白")
                if(self.prevMessage):
                    self.prevMessage.content+="\n"+content
                return None
            case ListType.分割输出符:
                print("处理分割输出符: 切割！")
                # 输出符要求对上一个Message进行处理。使得breaking = True
                if(self.prevMessage):
                    self.prevMessage.is_breaking=True
                return None
            case ListType.章节分割:
                print("处理章节")
                # 按理说应该输出文件了。随后将新的章节名作为新List的开头创建新文本。
                # 实际上就做一个分割差不多得了（
                if self.prevMessage:
                    self.prevMessage.is_breaking=True
                tempMessage = RawMessage(self.currChara,type="NARRATION",content=str("~"+content+"~"))
                self.prevMessage = tempMessage
                return tempMessage
            case ListType.OTHER:
                print("处理其他类型")
                return None
            case _:
                print("未知类型")
                return None
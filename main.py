
# This file was generated by the Tkinter Designer by Parth Jadhav
# https://github.com/ParthJadhav/Tkinter-Designer


from pathlib import Path

import time
import datetime
import logging
import os
import sys
import threading
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage, filedialog
import tkinter
import pictureParser
import chatParser
import charaParser
import tkinter as tk
import images

pp = pictureParser.PictureParser()
cs = charaParser.CharaParser(pp)
cp = chatParser.chatParser(cs,pp)

logging.basicConfig(filename=__file__.replace('.py', '.log'),
                    level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
logger.addHandler(logging.StreamHandler(sys.stdout))

class TextHandler(logging.Handler):
    def __init__(self, widget):
        logging.Handler.__init__(self)
        self.setLevel(logging.DEBUG)
        self.widget:tkinter.Text = widget
        self.widget.config(state='disabled')
        self.widget.tag_config("INFO", foreground="black")
        self.widget.tag_config("DEBUG", foreground="grey")
        self.widget.tag_config("WARNING", foreground="orange")
        self.widget.tag_config("ERROR", foreground="red")
        self.widget.tag_config("CRITICAL", foreground="red", underline=1)
        self.red = self.widget.tag_configure("red", foreground="red")

    def emit(self, record:logging.LogRecord):
        def t_emit():
            self.widget.config(state='normal')
            # Append message (record) to the widget
            self.widget.insert(tkinter.END, self.format(record) + '\n', record.levelname)
            self.widget.see(tkinter.END)  # Scroll to the bottom
            self.widget.config(state='disabled')
            self.widget.update()  # Refresh the widget
        t= threading.Thread(target=t_emit,args=())
        t.start()

myFont = "方正兰亭圆简体_中"
fontBundles = (myFont, 18 * -1)
fontSMBundles = (myFont, 14 * -1)
fontInputBundles = (myFont, 18 * -1)
fontLogBundles = (myFont, 12 * -1)
updatelock = threading.Lock()

def updateText(text:tkinter.Text,str:str):
    text.config(state='normal')
    text.delete("1.0", tk.END)
    text.insert('1.0',str,"end")
    text.config(state='disabled')

def readLinesFromText(text:tkinter.Text):
    textContent = text.get('1.0',"end")
    lines = textContent.split('\n')
    return lines

def clearChara():
    cs.clearAll()
    updateText(CharaOutputEntry,'')
    logger.info("已清除所有当前的角色信息。\n")
    pass

def readPictureFromPath():
    folder_path = filedialog.askdirectory()
    if folder_path:
        pp.parse_by_path(folder_path)
        updateText(recognizedPictureEntry,pp.toDisplayString())
        updateText(CharaOutputEntry,cs.toDisplayString())
    pass 

def readPictureFromFile():
    file_path = filedialog.askopenfilename()
    if file_path:
        pp.parseFile(file_path)
        updateText(recognizedPictureEntry,pp.toDisplayString())
        updateText(CharaOutputEntry,cs.toDisplayString())
    pass 

def clearPicture():
    pp.filenameToBase64.clear()
    updateText(recognizedPictureEntry,'')
    pass 

def readCustomCharSetFromFile():
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.md")])
    if file_path:
        cs.parseCharaInfoByFile(file_path)
        updateText(CharaOutputEntry,cs.toDisplayString())

def readCustomCharSetFromWindow():
    lines = readLinesFromText(charaInputEntry)
    lines.insert(0,'> [!info] ClosureTalk')
    cs.parseCharaInfoByLines(lines)
    updateText(CharaOutputEntry,cs.toDisplayString())

def readMarkdownFromFile():
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.md")])
    if file_path:
        cp.parseMarkdownByFile(file_path)
        updateText(markdownWorkoutEntry,f"已读取完毕Markdown From\n  {file_path}")

def readMarkdownFromWindow():
    lines = readLinesFromText(markdownInputEntry)
    lines.insert(0,'> [!info] ClosureTalk')
    cp.parseMarkdownByLines(lines)
    updateText(markdownWorkoutEntry,"已读取完毕工作区Markdown.")
    pass 

def saveJsonAsFile():
    if cp.chatList == []:
        updateText(markdownWorkoutEntry,f"尚无合法Markdown输入!")
        return
    file_path = filedialog.asksaveasfilename(filetypes=[("Text Files", "*.json")])
    if file_path:
        cp.save_to_file(file_path)
        updateText(markdownWorkoutEntry,f"已完成json文件生成:\n  {file_path}")

def outputJsonFile():
    if cp.chatList == []:
        updateText(markdownWorkoutEntry, "尚无合法Markdown输入!")
        return

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"{timestamp}_closuretalk.json"
    
    # 获取当前工作目录并添加 'output' 文件夹
    output_dir = os.path.join(os.getcwd(), "output")
    
    # 检查 'output' 文件夹是否存在，如果不存在，则创建一个
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 更新文件路径以包含 'output' 文件夹
    filepath = os.path.join(output_dir, file_name)
    
    cp.save_to_file(filepath)
    updateText(markdownWorkoutEntry, f"已完成json文件生成: {filepath}")

def quickBuild():
    doCustomCharaSetExist = os.path.isfile("_CustomCharaSet.md")
    doPictureFolderExist = os.path.isdir("pictures")
    updateText(markdownWorkoutEntry,f"快速构建用于快速使用本地资源构建角色信息和图片信息。")
    if not doCustomCharaSetExist:
        logger.warning("没有在程序的路径下找到 _CustomCharaSet.md 文件")
    if not doPictureFolderExist:
        logger.warning("没有在程序的路径下找到 pictures 文件夹")
    if doPictureFolderExist:
        pp.parse_by_path(os.path.abspath("pictures"))
    if doCustomCharaSetExist:
        cs.parseCharaInfoByFile(os.path.abspath("_CustomCharaSet.md"))
    logger.info("快速环境构建结束。")

""" Tkinter Declaration Segment """

window = Tk()

window.geometry("1148x924")
window.configure(bg = "#FFFFFF")

canvas = Canvas(
    window,
    bg = "#FFFFFF",
    height = 924,
    width = 1148,
    bd = 0,
    highlightthickness = 0,
    relief = "ridge"
)

canvas.place(x = 0, y = 0)
canvas.create_rectangle(
    0.0,
    0.0,
    1148.0,
    924.0,
    fill="#D9D9D9",
    outline="")

charaInputEntry = Text(
    tabs=40,
    font=fontInputBundles,
    bd=0,
    bg="#FBFBFB",
    fg="#000716",
    highlightthickness=0
)
charaInputEntry.place(
    x=787.0,
    y=51.0,
    width=326.0,
    height=170.0
)

button_image_1 = PhotoImage(
    data=images.button_1_png)
button_1 = Button(
    image=button_image_1,
    borderwidth=0,
    highlightthickness=0,
    command=readCustomCharSetFromWindow,
    relief="flat"
)
button_1.place(
    x=1019.0,
    y=232.0,
    width=110.0,
    height=44.0
)

button_image_2 = PhotoImage(
    data=images.button_2_png)
button_2 = Button(
    image=button_image_2,
    borderwidth=0,
    highlightthickness=0,
    command=readCustomCharSetFromFile,
    relief="flat"
)
button_2.place(
    x=900.0,
    y=232.0,
    width=110.0,
    height=44.0
)

image_image_2 = PhotoImage(
    data=images.image2Img)
image_2 = canvas.create_image(
    950.0,
    441.0,
    image=image_image_2
)


markdownInputEntry = Text(
    tabs=40,
font=fontInputBundles,
    bd=0,
    bg="#FBFBFB",
    fg="#000716",
    highlightthickness=0
)
markdownInputEntry.place(
    x=787.0,
    y=310.0,
    width=326.0,
    height=229.0
)

button_image_3 = PhotoImage(
    data=images.button_3_png)
button_3 = Button(
    image=button_image_3,
    borderwidth=0,
    highlightthickness=0,
    command=readMarkdownFromFile,
    relief="flat"
)
button_3.place(
    x=900.0,
    y=582.0,
    width=110.0,
    height=44.0
)

button_image_4 = PhotoImage(
    data=images.button_4_png)
button_4 = Button(
    image=button_image_4,
    borderwidth=0,
    highlightthickness=0,
    command=readMarkdownFromWindow,
    relief="flat"
)
button_4.place(
    x=1019.0,
    y=582.0,
    width=110.0,
    height=44.0
)

button_image_5 = PhotoImage(
    data=images.button_5_png)
button_5 = Button(
    image=button_image_5,
    borderwidth=0,
    highlightthickness=0,
    command=clearChara,
    relief="flat"
)
button_5.place(
    x=643.0,
    y=458.0,
    width=110.0,
    height=44.0
)

image_image_3 = PhotoImage(
    data=images.image3Img)
image_3 = canvas.create_image(
    574.0,
    234.0,
    image=image_image_3
)

CharaOutputEntry = Text(
    tabs=40,
    state='disabled',
    font=fontSMBundles,
    bd=0,
    bg="#F7F7F7",
    fg="#000716",
    highlightthickness=0
)
CharaOutputEntry.place(
    x=411.0,
    y=51.0,
    width=326.0,
    height=396.0
)

""" button_image_6 = PhotoImage(
    data=images.button_6_png)
button_6 = Button(
    image=button_image_6,
    borderwidth=0,
    highlightthickness=0,
    command=readCustomCharSetFromFile,
    relief="flat"
)
button_6.place(
    x=524.0,
    y=458.0,
    width=110.0,
    height=44.0
) """

image_image_4 = PhotoImage(
    data=images.image4Img)
image_4 = canvas.create_image(
    198.0,
    462.0,
    image=image_image_4
)


logEntry = Text(
    tabs=40,
    state='disabled',
    font=fontLogBundles,
    bd=0,
    bg="#F7F7F7",
    fg="#000716",
    highlightthickness=0,
    wrap="none"
)
logEntry.place(
    x=35.0,
    y=51.0,
    width=326.0,
    height=852.0
)

button_image_7 = PhotoImage(
    data=images.button_7_png)
button_7 = Button(
    image=button_image_7,
    borderwidth=0,
    highlightthickness=0,
    command=clearPicture,
    relief="flat"
)
button_7.place(
    x=643.0,
    y=861.0,
    width=110.0,
    height=44.0
)

image_image_5 = PhotoImage(
    data=images.image5Img)
image_5 = canvas.create_image(
    574.0,
    682.0,
    image=image_image_5
)


recognizedPictureEntry = Text(
    tabs=40,
    font=fontInputBundles,
    bd=0,
    bg="#F7F7F7",
    fg="#000716",
    highlightthickness=0,
    state="disabled",
    wrap="none"
)
recognizedPictureEntry.place(
    x=411.0,
    y=544.0,
    width=326.0,
    height=306.0
)


button_image_8 = PhotoImage(
    data=images.button_8_png)

button_8 = Button(
    image=button_image_8,
    borderwidth=0,
    highlightthickness=0,
    command=readPictureFromFile,
    relief="flat"
)
button_8.place(
    x=524.0,
    y=861.0,
    width=110.0,
    height=44.0
)

button_image_9 = PhotoImage(
    data=images.button_9_png)

button_9 = Button(
    image=button_image_9,
    borderwidth=0,
    highlightthickness=0,
    command=readPictureFromPath,
    relief="flat"
)

button_9.place(
    x=405.0,
    y=861.0,
    width=110.0,
    height=44.0
)

image_image_6 = PhotoImage(
    data=images.image6Img)

image_6 = canvas.create_image(
    950.0,
    742.0,
    image=image_image_6
)


markdownWorkoutEntry = Text(
    tabs=40,
font=fontInputBundles,
    bd=0,
    bg="#F7F7F7",
    fg="#000716",
    highlightthickness=0,
    state="disabled"
)
markdownWorkoutEntry.place(
    x=787.0,
    y=670.0,
    width=326.0,
    height=180.0
)

button_image_10 = PhotoImage(
    data=images.button_10_png)
button_10 = Button(
    image=button_image_10,
    borderwidth=0,
    highlightthickness=0,
    command=outputJsonFile,
    relief="flat"
)

button_10.place(
    x=900.0,
    y=861.0,
    width=110.0,
    height=44.0
)

button_image_11 = PhotoImage(
    data=images.button_11_png)

button_11 = Button(
    image=button_image_11,
    borderwidth=0,
    highlightthickness=0,
    command=saveJsonAsFile,
    relief="flat"
)
button_11.place(
    x=1019.0,
    y=861.0,
    width=110.0,
    height=44.0
)

button_image_12 = PhotoImage(
    data=images.button_12_png)

button_12 = Button(
    image=button_image_12,
    borderwidth=0,
    highlightthickness=0,
    command=quickBuild,
    relief="flat"
)
button_12.place(
    x=781.0,
    y=861.0,
    width=110.0,
    height=44.0
)

window.resizable(False, False)

image_image_1 = PhotoImage(
    data = images.image1Img)
image_1 = canvas.create_image(
    950.0,
    121.0,
    image=image_image_1
)

entry_image_1 = PhotoImage(
    data=images.entry_1_png)

entry_bg_1 = canvas.create_image(
    950.0,
    137.0,
    image=entry_image_1
)

entry_image_2 = PhotoImage(
    data = images.entry_2_png)
entry_bg_2 = canvas.create_image(
    950.0,
    425.5,
    image=entry_image_2
)

entry_image_3 = PhotoImage(
    data = images.entry_3_png)
entry_bg_3 = canvas.create_image(
    574.0,
    250.0,
    image=entry_image_3
)

entry_image_4 = PhotoImage(
    data = images.entry_4_png)
entry_bg_4 = canvas.create_image(
    198.0,
    478.0,
    image=entry_image_4
)

entry_image_5 = PhotoImage(
    data = images.entry_5_png)
entry_bg_5 = canvas.create_image(
    574.0,
    698.0,
    image=entry_image_5
)

entry_image_6 = PhotoImage(
    data = images.entry_6_png)
entry_bg_6 = canvas.create_image(
    950.0,
    761.0,
    image=entry_image_6
)

canvas.create_text(
    778.0,
    285.0,
    anchor="nw",
    text="临时MarkdownMomotalk",
    fill="#484646",
    font=fontBundles
)

canvas.create_text(
    779.0,
    549.0,
    anchor="nw",
    text="*将会丢失前文，重新构造整个文本",
    fill="#8D8D8D",
    font=fontSMBundles
)

canvas.create_text(
    778.0,
    25.0,
    anchor="nw",
    text="临时CustomCharSet",
    fill="#484646",
    font=fontBundles
)

canvas.create_text(
    402.0,
    25.0,
    anchor="nw",
    text="识别到的角色组",
    fill="#484646",
    font=fontBundles
)

canvas.create_text(
    26.0,
    25.0,
    anchor="nw",
    text="日志",
    fill="#484646",
    font=fontBundles
)

canvas.create_text(
    402.0,
    519.0,
    anchor="nw",
    text="识别到的图片",
    fill="#484646",
    font=fontBundles
)

canvas.create_text(
    778.0,
    645.0,
    anchor="nw",
    text="导出ClosureTalk.Json",
    fill="#484646",
    font=fontBundles
)

def thread_log_work():
    log_handler = TextHandler(logEntry)
    logger.addHandler(log_handler)

t1 = threading.Thread(target=thread_log_work,args=())
t1.start()

def helpInform():
    time.sleep(1)
    logger.info("""
欢迎使用 Markdown-ClosureTalkJson-Parser
推荐放在Obsidian环境下使用
""")
    
t2 = threading.Thread(target=helpInform,args=())
t2.start()

def checkInfoAndUpdate():
    charalen = len(cs.chars)
    piclen = len(pp.filenameToBase64)
    while(True):
        time.sleep(0.5)
        if not piclen==len(pp.filenameToBase64):
            logger.info("检测到图片变动.")
            updateText(recognizedPictureEntry,pp.toDisplayString())
            recognizedPictureEntry.see(tkinter.END)
            updateText(CharaOutputEntry,cs.toDisplayString())
            CharaOutputEntry.see(tkinter.END)
            piclen = len(pp.filenameToBase64)
            continue
        if not charalen==len(cs.chars):
            logger.info("检测到角色变动.")
            updateText(CharaOutputEntry,cs.toDisplayString())
            CharaOutputEntry.see(tkinter.END)
            charalen=len(cs.chars)
            continue

t3 = threading.Thread(target=checkInfoAndUpdate,args=())
t3.start()

window.mainloop()

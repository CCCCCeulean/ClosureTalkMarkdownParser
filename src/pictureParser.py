pure_black = 'data:image/jpg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAIBAQIBAQICAgICAgICAwUDAwMDAwYEBAMFBwYHBwcGBwcICQsJCAgKCAcHCg0KCgsMDAwMBwkODw0MDgsMDAz/2wBDAQICAgMDAwYDAwYMCAcIDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAz/wAARCAABAAEDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD+f+iiigD/2Q=='
from queue import Queue
from concurrent.futures import ThreadPoolExecutor
import logging
import os
import base64
import threading
from time import sleep
from typing import Tuple

import requests
suffixes = [".jpg", ".jpeg", ".png", ".gif", ".bmp"]

class PictureParser:
    def __init__(self, max_workers=5, max_queue_size=100):
        self.filenameToBase64 = {}
        self.logger = logging.getLogger()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.task_queue:Queue[Tuple[str,str]] = Queue(maxsize=max_queue_size)
        self.lock = threading.Lock()
        self.newPictureEnrolled = 0
        for _ in range(max_workers):
            threading.Thread(target=self.worker, args=(self.filenameToBase64,)).start()

    def download_image(self, url: str, storage: dict):
        try:
            response = requests.get(url, timeout=20)
            if response.status_code == 200:
                with self.lock:
                    storage[url] = response.content  # 将图片内容存储到字典中
                    self.newPictureEnrolled += 1
            else:
                with self.lock:
                    storage[url] = "Pureblack"
                    self.newPictureEnrolled += 1
        except requests.exceptions.RequestException:
            with self.lock:
                storage[url] = "Pureblack"
                self.newPictureEnrolled += 1

    def toDisplayString(self)->str:
        while not self.task_queue.empty():
            sleep(0.5)
        temp = str()
        lines = []
        oversizedLines = []
        maxL = 30
        assert(maxL>0)
        with self.lock:
            for k in self.filenameToBase64.keys():
                temp = k 
                if len(k)>maxL:
                    k = '... ' + k[len(k)-maxL:]
                    oversizedLines.append(k)
                else:
                    lines.append(k)
            lines.sort()
            oversizedLines.sort()
            temp = str()
            for l in lines:
                temp+= l + '\n'
            for l in oversizedLines:
                temp+= l + '\n'
            self.newPictureEnrolled = 0
        return temp
    
    def parseFile(self,file_path:str):
        if any(file_path.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']):  # 支持更多格式
            file_name = os.path.basename(file_path)
            pure_filename = \
                file_name
                # os.path.splitext(file_name)[0]
            if pure_filename in self.filenameToBase64:
                self.logger.warning(f"pictureParser: 文件 {pure_filename} 将被替换。")
            else:
                self.logger.info(f"pictureParser: 读入 {pure_filename} 文件并序列化")
            with self.lock:
                self.filenameToBase64[pure_filename] = self.file_to_base64(file_path)
                self.newPictureEnrolled+=1
        
    
    def parse_by_path(self, path):
        """递归搜索路径下的所有图片文件并转换为Base64编码存储。"""
        if not os.path.exists(path):
            self.logger.warning(f"pictureParser: 路径 {path} 不存在!\n")
            return
        for root, _, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                self.parseFile(file_path)

    def parse_by_url(self,url,askedKey=None):
        """ 从url下载资源,链接大概率不会重复,则若已发现主码,会直接跳过 """
        if self.doHavePictures(url):
            self.logger.info(f"线上图片 {url} 已存在。")
            return 
        """ 投递任务 """
        self.logger.info(f"发起了 {url} 的下载。")
        self.task_queue.put((url,askedKey))
        
    def t_download_img_tran(self,url,askedKey=None):
        try:
            response = requests.get(url,timeout=20)
            if response.status_code == 200:
                file_extension = os.path.splitext(url)[1].lower()[1:]
                img_base64 = base64.b64encode(response.content).decode('utf-8')
                with self.lock:
                    self.filenameToBase64[url] = f"data:image/{file_extension};base64,{img_base64}"
                    if askedKey:
                        self.filenameToBase64[askedKey] = self.filenameToBase64[url]
            else:
                self.logger.error(f"下载 {url} 超时。")
        except requests.exceptions.RequestException:
            self.logger.error(f"下载 {url} 寄了。")
                
    def worker(self, storage: dict):
        while True:
            url,askedKey = self.task_queue.get()
            if url is None:  # Sentinel value to stop the worker
                break
            self.t_download_img_tran(url, askedKey)
            self.task_queue.task_done()
        
    def file_to_base64(self, file_path) -> str:
        with open(file_path, 'rb') as img_file:
            img_byte = img_file.read()
            img_base64 = base64.b64encode(img_byte).decode('utf-8')
        file_extension = os.path.splitext(file_path)[1].lower()[1:]  # 移除点号
        return f"data:image/{file_extension};base64,{img_base64}"

    def get_base64(self, filename):
        if filename in self.filenameToBase64:
            return self.filenameToBase64[filename]

        # 依次尝试附加常见后缀名
        for suffix in suffixes:
            if filename + suffix in self.filenameToBase64:
                return self.filenameToBase64[filename + suffix]

        # 如果没有找到匹配的文件名，返回 "Pureblack"
        return pure_black
    
    def doHavePictures(self,filename):
        if filename in self.filenameToBase64:
            return True

        for suffix in suffixes:
            if filename + suffix in self.filenameToBase64:
                return True

        # 如果没有找到匹配的文件名，返回 "Pureblack"
        return False

    def _forcedBase64Encoding(self,key,value):
        self.filenameToBase64[key]=value
    
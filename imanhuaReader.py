# -*- coding:utf-8 -*-
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys
import os

manhuadir = r'd:/sketdance'
manhuainx = os.listdir(manhuadir)
manhuainx = [key.decode('gbk') for key in manhuainx]
nowPage   = 0

class MainChapters(QWidget):
	def __init__(self,parent = None):
		super(MainChapters,self).__init__(parent)
		self.resize(640,480)
		self.button = [QPushButton(key,self) for key in manhuainx]
		layout = QGridLayout()
		count  = 0
		startX = 0
		for inx,key in enumerate(self.button):
			layout.addWidget(key,startX,inx % 7)
			count += 1
			if count >= 7:
				count = 0
				startX += 1
		self.setWindowTitle('imanhuaReader')
		self.setLayout(layout)

	def connectToChap(self,chapter):
		self.chapter = chapter
		for inx,key in enumerate(self.button):
			self.connect(key,SIGNAL('clicked()'),chapter.come)
		
	def come(self):
		global nowPage
		nowPage = 0
		self.chapter.hide()
		self.show()
		
class Chapter(QWidget):
	def __init__(self,parent = None):
		super(Chapter,self).__init__(parent)	
		self.resize(1024,768)
		self.button   = QPushButton(u'主界面',self)
		self.nextPa   = QPushButton(u'下一页',self)
		self.imgScrol = QScrollArea(self)
		self.imgLabel = QLabel(self.imgScrol)
		
		self.imgScrol.setWidget(self.imgLabel)
		self.imgScrol.setWidgetResizable(True) # 关键！否则不能正常显示
		
		layout = QGridLayout(self)
		layout.addWidget(self.button,0,3)
		layout.addWidget(self.nextPa,0,1)
		layout.addWidget(self.imgScrol,1,0)
		self.setLayout(layout)
		
		self.connect(self.nextPa,SIGNAL('clicked()'),self.nextImg)

	def connectToMain(self,mainChapter):
		self.mainChapter = mainChapter
		self.connect(self.button,SIGNAL('clicked()'),mainChapter.come)
	
	def cmp(self,str1,str2):
		inx1 = str1.find('.')
		inx2 = str2.find('.')
		str1 = str1[:inx1]
		str2 = str2[:inx2]
		str1 = int(str1)
		str2 = int(str2)
		return str1 - str2
			
	
	def come(self):
		self.move(0,0)
		sender = self.sender().text()
		sender = unicode(sender)
		self.imgdir = sender.encode('gbk')
		self.setWindowTitle(sender)
		self.imglist = os.listdir(manhuadir + '/' + sender.encode('gbk'))
		self.imglist.sort(self.cmp)
		self.mainChapter.hide()
		self.showMaximized()
		self.showImg()
		
	def showImg(self):
		global nowPage
		target = manhuadir + '/' + self.imgdir + '/' + self.imglist[nowPage]
		target = QString.fromLocal8Bit(target)  # 关键！！将gbk路径名转化为Qt能够识别的名字
		pixmap = QPixmap(target)
		
		self.imgLabel.setPixmap(pixmap)
			
	def nextImg(self):
		global nowPage
		if nowPage >= len(self.imglist):
			return
		nowPage += 1
		self.showImg()
		
app = QApplication(sys.argv)
main = MainChapters()
chap = Chapter()
chap.connectToMain(main)
main.connectToChap(chap)
main.show()
app.exec_()
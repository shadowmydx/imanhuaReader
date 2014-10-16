# -*- coding:utf-8 -*-
'''
	该软件一共有四个类：
	0、继承QPushButton的Mybutton类，主要是为了实现发送参数的clicked事件。
	1、MainChapter类，显示主界面
	2、BookMark类，负责MainChapter类和Chapter类之间的通信，是实现书签的关键类。
	3、Chapter类，负责显示图片
	类之间的通信：
	MainChapter to BookMark ：章节 + 页数。如果不点击书签而点击章节，则默认页数为0
	BookMark to Chapter ： 图片路径 + 章节 + 页。为了防止当前页面越界，除了发送图片路径给Chapter，还需要发送页面值给Chapter
	Chapter to BookMark ： 章节 + 页。向BookMark请求对应章节 + 页的图片路径。
	Chapter to MainChapter : 隐藏自己后，通知MainChapter现身
	
	为了实现书签功能所搭建的复杂信号通信终于实现完成。。怀念第一个版本的简单粗暴
	过几天在搞书签 OMG
'''
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys
import os

manhuadir = r'd:/sketdance'
manhuainx = os.listdir(manhuadir)
manhuainx = [key.decode('gbk') for key in manhuainx]

class MyButton(QPushButton):
	myclicked = pyqtSignal(int)
	def __init__(self,id,*args, **kwargs):
		super(MyButton,self).__init__(*args, **kwargs)
		self.id = id
		
		self.connect(self,SIGNAL('clicked()'),self.emitMyclicked)
		
	def emitMyclicked(self):
		self.myclicked.emit(self.id)

class BookMark(QWidget):
	sendAddr = pyqtSignal(QString,int,int)
	#senddir  = QtCore.pyqtSignal(str)
	def __init__(self,parent = None):
		super(BookMark,self).__init__(parent)
		self.nowChapter = 0
		self.nowPage    = 0
		self.flag       = 0 # 这里写的太丑了。为了效率，setDictReady应该尽可能少的执行，因此标记下第一次执行setDictReady的情况

	def connectToChapter(self,chapter):
		self.chapter = chapter
		self.connect(self,SIGNAL('sendAddr(QString,int,int)'),self.chapter.setChapterPage)
		#self.connect(self,SIGNAL('senddir(str)'),self.chapter.showImg)
		
	def cmp(self,str1,str2):
		inx1 = str1.find('.')
		inx2 = str2.find('.')
		str1 = str1[:inx1]
		str2 = str2[:inx2]
		str1 = int(str1)
		str2 = int(str2)
		return str1 - str2
		
	def setDictReady(self):
		self.dir     = manhuainx[self.nowChapter]
		self.imgList = os.listdir(manhuadir + '/' + self.dir.encode('gbk'))
		self.imgList.sort(self.cmp)
		
	def setChapterPage(self,page,chapter):
		self.nowPage  = page
		if self.flag == 0: # 执行本应该在构造函数中执行的代码
			self.flag = 1
			self.setDictReady()
		if self.nowChapter != chapter: # 如果不需要更改当前文件夹，则不重新设置工作目录
			self.nowChapter = chapter
			self.setDictReady()
		self.target = self.generateAddr(page,chapter)

		self.sendAddr.emit(QString(self.target),self.nowPage,self.nowChapter)
	
	def generateAddr(self,page,chapter):
		if page > len(self.imgList):
			self.nowChapter += 1
			if self.nowChapter > len(manhuainx):
				self.nowChapter = 0
			self.nowPage = 0
			self.setDictReady()
		elif page < 0:
			self.nowPage = 0
			if chapter > 1:
				self.nowChapter = chapter - 1
			else:
				self.nowChapter = 0
			self.setDictReady()
		else:
			self.nowPage = page
		return manhuadir + '/' + self.dir + '/' + self.imgList[self.nowPage]	

		

class MainChapters(QWidget):
	addrSignal = pyqtSignal(int,int) 
	def __init__(self,parent = None):
		super(MainChapters,self).__init__(parent)

		self.resize(640,480)
		self.button = [MyButton(inx,key,self) for inx,key in enumerate(manhuainx)]
		for inx,key in enumerate(self.button):
			self.connect(key,SIGNAL('myclicked(int)'),self.emitAddr)		
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
	
	def connectToBook(self,bookmark):
		self.bookmark = bookmark
		self.connect(self,SIGNAL('addrSignal(int,int)'),self.bookmark.setChapterPage)
	
	def emitAddr(self,id):
		self.hide()
		self.addrSignal.emit(0,id)
		
		
class Chapter(QWidget):
	getTarget = pyqtSignal(int,int)
	ret2Main  = pyqtSignal()
	def __init__(self,parent = None):
		super(Chapter,self).__init__(parent)	
		self.resize(1024,768)
		self.button   = QPushButton(u'主界面',self)
		self.nextPa   = QPushButton(u'下一页',self)
		self.prePa    = QPushButton(u'上一页',self)
		self.imgScrol = QScrollArea(self)
		self.imgLabel = QLabel(self.imgScrol)
		
		self.imgScrol.setWidget(self.imgLabel)
		self.imgScrol.setWidgetResizable(True) # 关键！否则不能正常显示
		
		layout = QGridLayout(self)
		layout.addWidget(self.button,1,1)
		layout.addWidget(self.nextPa,1,0)
		layout.addWidget(self.prePa,1,2)
		layout.addWidget(self.imgScrol,0,0)
		self.setLayout(layout)

	def connectToMain(self,mainChapter):
		self.mainChapter = mainChapter
		self.connect(self.button,SIGNAL('clicked()'),self.returnToMain)
		self.connect(self,SIGNAL('ret2Main()'),mainChapter.show)
	
	def connectToBook(self,bookmark):
		self.bookmark = bookmark
		self.connect(self.nextPa,SIGNAL('clicked()'),self.nextImg) # 信号不能重复连接！否则会发两个
		self.connect(self.prePa,SIGNAL('clicked()'),self.preImg)
		self.connect(self,SIGNAL('getTarget(int,int)'),self.bookmark.setChapterPage)
		
	def showImg(self):
		self.target = unicode(self.target)
		pixmap = QPixmap(self.target)
		self.imgLabel.setPixmap(pixmap)
				
	def setChapterPage(self,target,page,chapter):
		self.showMaximized()
		self.chapter = chapter
		self.page    = page
		self.target  = target
		self.showImg()
	
	def nextImg(self):
		self.page += 1 # 越界在BookMark中处理
		self.getTarget.emit(self.page,self.chapter)
		
	def preImg(self):
		self.page -= 1
		self.getTarget.emit(self.page,self.chapter)
		
	def returnToMain(self):
		self.ret2Main.emit()
		self.hide()
		
		
app = QApplication(sys.argv)
main = MainChapters()
chap = Chapter()
book = BookMark()
chap.connectToMain(main)
chap.connectToBook(book)
main.connectToBook(book)
book.connectToChapter(chap)
main.show()
app.exec_()
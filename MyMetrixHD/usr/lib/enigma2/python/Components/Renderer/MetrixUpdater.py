#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
#######################################################################
#
#    MetrixWeather for VU+
#    Coded by iMaxxx (c) 2013
#    Support: www.vuplus-support.com
#
#
#  This plugin is licensed under the Creative Commons
#  Attribution-NonCommercial-ShareAlike 3.0 Unported License.
#  To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/3.0/
#  or send a letter to Creative Commons, 559 Nathan Abbott Way, Stanford, California 94305, USA.
#
#  Alternatively, this plugin may be distributed and executed on hardware which
#  is licensed by Dream Multimedia GmbH.
#
#
#  This plugin is NOT free software. It is open source, you are allowed to
#  modify it (if you keep the license), but it may not be commercially
#  distributed other than under the conditions noted above.
#
#
#######################################################################
from Renderer import Renderer
from Components.VariableText import VariableText
import urllib2
from enigma import ePixmap
from ConfigParser import SafeConfigParser
import ConfigParser
import sys
import os
from xml.dom.minidom import parseString
from Components.config import config, ConfigSubsection, configfile, ConfigText, ConfigNumber, ConfigDateTime, ConfigSelection

config.plugins.MetrixUpdater = ConfigSubsection()
config.plugins.MetrixUpdater.refreshInterval = ConfigNumber(default=30)
config.plugins.MetrixUpdater.UpdateAvailable = ConfigNumber(default=0)
config.plugins.MetrixUpdater.Reboot = ConfigNumber(default=0)
config.plugins.MetrixUpdater.Revision = ConfigNumber(default=1000)


class MetrixUpdater(Renderer, VariableText):



	def __init__(self):
		Renderer.__init__(self)
		VariableText.__init__(self) 
		config.plugins.MetrixUpdater.save()    
		configfile.save()
		self.configFile = "/etc/MetrixUpdater.config"
		self.timer = 1
		
		
	GUI_WIDGET = ePixmap
	
	def changed(self, what):
		if self.timer == 1:
			try:
				self.updateLookup()
			except:
				pass
		elif self.timer >= int(config.plugins.MetrixUpdater.refreshInterval.value) * 60:
			self.timer = 0
		self.timer = self.timer + 1
			
		
			
	def onShow(self):
		print ''


	def downloadFile(self,storePath,localPath):
		webFile = urllib2.urlopen(self.getValue('updater', 'storeAddress') + storePath)
		localFile = open(localPath, 'w')
		localFile.write(webFile.read())
		webFile.close()
		localFile.close()
	
	def updateLookup(self):
		url = self.getValue('updater', 'storeAddress') + "/update.xml"
		file = urllib2.urlopen(url)
		data = file.read()
		#print data
		file.close()
		dom = parseString(data)
		#fileUpdate = dom.getElementsByTagName('fileupdate')[0]
		for fileUpdate in dom.getElementsByTagName('fileupdate'):
			storePath = str(fileUpdate.getAttributeNode('storepath').nodeValue)
			localPath = str(fileUpdate.getAttributeNode('localpath').nodeValue)
			revision = str(fileUpdate.getAttributeNode('revision').nodeValue)
			reboot = str(fileUpdate.getAttributeNode('reboot').nodeValue)
			product = str(fileUpdate.getAttributeNode('product').nodeValue)
			if int(revision) > int(self.getValue("files",localPath.replace('/','_'))):
				try:
					self.downloadFile(storePath,localPath)
					self.setValue("files",localPath.replace('/','_'),revision)
					if int(reboot) == 1:
						config.plugins.MetrixUpdater.Reboot.value = 1
						
					print 'MetrixUpdater: ' +localPath + ' updated successfully'
					self.saveUpdateAvailable(product)
				except:
					print 'MetrixUpater: error downloading ' + localPath
		for commandUpdate in dom.getElementsByTagName('commandupdate'):
			command = str(commandUpdate.getAttributeNode('command').nodeValue)
			revision = str(commandUpdate.getAttributeNode('revision').nodeValue)
			reboot = str(commandUpdate.getAttributeNode('reboot').nodeValue)
			product = str(fileUpdate.getAttributeNode('product').nodeValue)
			if int(revision) > int(self.getValue("commands","revision")):
				try:
					self.runCommand(command)
					self.setValue("commands","revision",revision)
					print 'MetrixUpdater: command "'+command+'" executed successfully'
					if int(reboot) == 1:
						config.plugins.MetrixUpdater.Reboot.value = 1
					print 'MetrixUpdater: ' +localPath + ' updated successfully'
					self.saveUpdateAvailable(product)
				except:
					print 'MetrixUpdater: error executing command "' + command + '"'
		try:
			
			product_revision =  dom.getElementsByTagName('revision')[0]
			product_revision_value = str(product_revision.getAttributeNode('value').nodeValue)
			if int(product_revision_value) > config.plugins.MetrixUpdater.Revision.value:
				config.plugins.MetrixUpdater.Revision.value = int(product_revision_value)
				config.plugins.MetrixUpdater.save()    
				configfile.save()
				print "MetrixUpdater: New resivion " + str(product_revision_value) + "!"
		except:
			pass
		
		
	def setValue(self, section, key, value):
		parser = SafeConfigParser()
		parser.read(self.configFile)
		parser.set(section, key, value)
		parser.write(open(self.configFile,'w'))
		
	def getValue(self, section, key):
		parser = SafeConfigParser()
		parser.read(self.configFile)
		try:
			return parser.get(section, key)
		except:
			return "0"
		
	def saveUpdateAvailable(self, product):
		config.plugins.MetrixUpdater.UpdateAvailable.value = 1
		config.plugins.MetrixUpdater.save()    
		configfile.save()
		
	def runCommand(self, command):
		os.system(command)
		
	
	def getText(self,nodelist):
	    rc = []
	    for node in nodelist:
	        if node.nodeType == node.TEXT_NODE:
	            rc.append(node.data)
	    return ''.join(rc)
	
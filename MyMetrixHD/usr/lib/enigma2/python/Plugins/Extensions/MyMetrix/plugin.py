#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
#######################################################################
#
#    MyMetrix 
#    Coded by iMaxxx (c) 2013
#    
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

from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
from twisted.web.client import downloadPage
from Screens.Console import Console
from Screens.Standby import TryQuitMainloop
from Components.ActionMap import ActionMap
from Components.AVSwitch import AVSwitch
from Components.config import config, configfile, ConfigYesNo, ConfigSubsection, getConfigListEntry, ConfigSelection, ConfigNumber, ConfigText, ConfigInteger
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.Language import language
from os import environ, listdir, remove, rename, system
from skin import parseColor
from Components.Pixmap import Pixmap
from Components.Label import Label
import urllib
import gettext
from enigma import ePicLoad
from Tools.Directories import fileExists, resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS

#############################################################

lang = language.getLanguage()
environ["LANGUAGE"] = lang[:2]
gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain("enigma2")
gettext.bindtextdomain("MyMetrix", "%s%s" % (resolveFilename(SCOPE_PLUGINS), "Extensions/MyMetrix/locale/"))

def _(txt):
	t = gettext.dgettext("MyMetrix", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t

def translateBlock(block):
	for x in TranslationHelper:
		if block.__contains__(x[0]):
			block = block.replace(x[0], x[1])
	return block

#############################################################

config.plugins.MyMetrix = ConfigSubsection()
config.plugins.MetrixWeather = ConfigSubsection()
config.plugins.MetrixUpdater = ConfigSubsection()

config.plugins.MetrixUpdater.refreshInterval = ConfigNumber(default=30)
config.plugins.MetrixUpdater.UpdateAvailable = ConfigNumber(default=0)
config.plugins.MetrixUpdater.Reboot = ConfigNumber(default=0)
config.plugins.MetrixUpdater.Revision = ConfigNumber(default=1000)
#config.skin = ConfigSubsection()
#General
config.plugins.MyMetrix.SkinColor = ConfigSelection(default="#00149baf", choices = [
				("#00F0A30A", _("Amber")),
				("#00825A2C", _("Brown")),
				("#000050EF", _("Cobalt")),
				("#00911d10", _("Crimson")),
				("#001BA1E2", _("Cyan")),
				("#00a61d4d", _("Magenta")),
				("#00A4C400", _("Lime")),
				("#006A00FF", _("Indigo")),
				("#0070ad11", _("Green")),
				("#00008A00", _("Emerald")),
				("#0076608A", _("Mauve")),
				("#006D8764", _("Olive")),
				("#00c3461b", _("Orange")),
				("#00F472D0", _("Pink")),
				("#00E51400", _("Red")),
				("#007A3B3F", _("Sienna")),
				("#00647687", _("Steel")),
				("#00149baf", _("Teal")),
				("#006c0aab", _("Violet")),
				("#00bf9217", _("Yellow"))
				])
#MetrixWeather
config.plugins.MetrixWeather.refreshInterval = ConfigNumber(default=10)
config.plugins.MetrixWeather.woeid = ConfigNumber(default=640161) #Location (visit metrixhd.info)
config.plugins.MetrixWeather.tempUnit = ConfigSelection(default="Celsius", choices = [
				("Celsius", _("Celsius")),
				("Fahrenheit", _("Fahrenheit"))
				])
config.plugins.MyMetrix.AutoUpdate = ConfigSelection(default="metrixupdater", choices = [
				("metrixupdater", _("On")),
				("metrixupdater-symbol", _("On with symbol")),
				("metrixupdater-none", _("Off"))
				])
config.plugins.MyMetrix.EMCStyle = ConfigSelection(default="emc-classic", choices = [
				("emc-classic", _("Classic")),
				("emc-cover", _("Cover"))
				])
config.plugins.MyMetrix.MerlinMusicPlayerStyle = ConfigSelection(default="merlin_music_player_classic", choices = [
				("merlin_music_player_classic", _("Classic")),
				("merlin_music_player_new", _("New"))
				])					
config.plugins.MyMetrix.WebradioFSStyle = ConfigSelection(default="webradioFS-classic", choices = [
				("webradioFS-classic", _("Classic")),
				("webradioFS-new", _("New"))
				])	
config.plugins.MyMetrix.EPGStyle = ConfigSelection(default="epg-selection-classic", choices = [
				("epg-selection-classic", _("Classic")),
				("epg-selection-running-text", _("RunningText"))
				])
config.plugins.MyMetrix.ChannelSelectionStyle = ConfigSelection(default="channel-selection-classic", choices = [
				("channel-selection-classic", _("Classic")),
				("channel-selection-new", _("New"))
				])					
config.plugins.MyMetrix.InfobarProgressbarStyle = ConfigSelection(default="infobar-classic", choices = [
				("infobar-classic", _("On")),
				("infobar-colored", _("Off"))
				])
				
				#InfoBar
config.plugins.MyMetrix.InfobarWeatherWidget = ConfigSelection(default="infobar-weatherwidget-none", choices = [
				("infobar-weatherwidget-image", _("On")),
				("infobar-weatherwidget-none", _("Off"))
				])

config.plugins.MyMetrix.InfobarClockWidget = ConfigSelection(default="infobar-clockwidget", choices = [
				("infobar-clockwidget", _("Classic")),
				("infobar-clockwidget-colored", _("Colored")),
				("infobar-clockwidget-none", _("Off"))
				])
				
config.plugins.MyMetrix.InfobarInfoWidget = ConfigSelection(default="infobar-infowidget-none", choices = [
				("infobar-infowidget-provider", _("Show Provider")),
				("infobar-infowidget-cam", _("Show Provider and CAM/ECM")),
				("infobar-infowidget-provider-frequenzy", _("Show Provider and Frequency")),
				("infobar-infowidget-none", _("Off"))
				])
config.plugins.MyMetrix.InfobarTunerInfo = ConfigSelection(default="infobar-tunerinfo-ab", choices = [
				("infobar-tunerinfo-abcd", _("4 Tuner (DVB-X ABCD)")),
				("infobar-tunerinfo-abc", _("3 Tuner (DVB-X ABC)")),
				("infobar-tunerinfo-ab", _("2 Tuner (DVB-X AB)")),
				("infobar-tunerinfo", _("1 Tuner (DVB-X)")),
				("infobar-tunerinfo-none", _("Off"))
				])	
config.plugins.MyMetrix.InfobarResolutionInfo = ConfigSelection(default="infobar-resolutioninfo-none", choices = [
				("infobar-resolutioninfo", _("On")),
				("infobar-resolutioninfo-none", _("Off"))
				])
config.plugins.MyMetrix.InfobarCryptInfo = ConfigSelection(default="infobar-cryptinfo", choices = [
				("infobar-cryptinfo", _("On")),
				("infobar-cryptinfo-none", _("Off"))
				])	
config.plugins.MyMetrix.InfobarShowChannelname = ConfigSelection(default="infobar-channelname", choices = [
				("infobar-channelname", _("Name")),
				("infobar-channelname-number", _("Name and number")),
				("infobar-channelname-none", _("Off"))
				])	
config.plugins.MyMetrix.InfobarStyle = ConfigSelection(default="infobar-style-classic", choices = [
				("infobar-style-classic", _("Classic")),
				("infobar-style-new", _("New")),
				("infobar-style-running-text", _("RunningText"))
				])
config.plugins.MyMetrix.InfobarProgressStyle = ConfigSelection(default="infobar-style-progress-classic", choices = [
				("infobar-style-progress-classic", _("Classic")),
				("infobar-style-progress-colored", _("MetrixColor")),
				])				
config.plugins.MyMetrix.InfobarHealthWidget = ConfigSelection(default="secondinfobar-healthwidget-none", choices = [
				("secondinfobar-healthwidget", _("On")),
				("secondinfobar-healthwidget-none", _("Off"))
				])			
				
				#SecondInfoBar
config.plugins.MyMetrix.SecondInfobarStyle = ConfigSelection(default="infobar-style-classic", choices = [
				("infobar-style-classic", _("Classic")),
				("infobar-style-new", _("New"))
				])
config.plugins.MyMetrix.SecondInfobarProgressStyle = ConfigSelection(default="infobar-style-progress-classic", choices = [
				("infobar-style-progress-classic", _("Classic")),
				("infobar-style-progress-colored", _("MetrixColor")),
				])				
config.plugins.MyMetrix.SecondInfobarShowChannelname = ConfigSelection(default="infobar-channelname-none", choices = [
				("infobar-channelname", _("Name")),
				("infobar-channelname-number", _("Name and number")),
				("infobar-channelname-none", _("Off"))
				])	
config.plugins.MyMetrix.SecondInfobarWeatherWidget = ConfigSelection(default="infobar-weatherwidget-none", choices = [
				("infobar-weatherwidget-image", _("On")),
				("infobar-weatherwidget-none", _("Off"))
				])
config.plugins.MyMetrix.SecondInfobarClockWidget = ConfigSelection(default="infobar-clockwidget", choices = [
				("infobar-clockwidget", _("Classic")),
				("infobar-clockwidget-colored", _("Colored")),
				("infobar-clockwidget-none", _("Off"))
				])
config.plugins.MyMetrix.SecondInfobarHealthWidget = ConfigSelection(default="secondinfobar-healthwidget", choices = [
				("secondinfobar-healthwidget", _("On")),
				("secondinfobar-healthwidget-none", _("Off"))
				])
config.plugins.MyMetrix.SecondInfobarEPGWidget = ConfigSelection(default="secondinfobar-epgwidget", choices = [
				("secondinfobar-epgwidget", _("On")),
				("secondinfobar-epgwidget-none", _("Off"))
				])
config.plugins.MyMetrix.SecondInfobarInfoWidget = ConfigSelection(default="infobar-infowidget-none", choices = [
				("infobar-infowidget-provider", _("Show Provider")),
				("infobar-infowidget-cam", _("Show Provider and CAM/ECM")),
				("infobar-infowidget-provider-frequenzy", _("Show Provider and Frequenzy")),
				("infobar-infowidget-none", _("Off"))
				])
config.plugins.MyMetrix.SecondInfobarTunerInfo = ConfigSelection(default="infobar-tunerinfo-ab", choices = [
				("infobar-tunerinfo-abcd", _("4 Tuner (DVB-X ABCD)")),
				("infobar-tunerinfo-abc", _("3 Tuner (DVB-X ABC)")),
				("infobar-tunerinfo-ab", _("2 Tuner (DVB-X AB)")),
				("infobar-tunerinfo", _("1 Tuner (DVB-X)")),
				("infobar-tunerinfo-none", _("Off"))
				])	
config.plugins.MyMetrix.SecondInfobarResolutionInfo = ConfigSelection(default="infobar-resolutioninfo-none", choices = [
				("infobar-resolutioninfo", _("On")),
				("infobar-resolutioninfo-none", _("Off"))
				])
config.plugins.MyMetrix.SecondInfobarCryptInfo = ConfigSelection(default="infobar-cryptinfo", choices = [
				("infobar-cryptinfo", _("On")),
				("infobar-cryptinfo-none", _("Off"))
				])	

def main(session, **kwargs):
	session.open(MyMetrix,"/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/images/metrixcolors.jpg")

def Plugins(**kwargs):
	return PluginDescriptor(name="MyMetrix", description=_("Configuration tool for MetrixHD"), where = PluginDescriptor.WHERE_PLUGINMENU, icon="plugin.png", fnc=main)



#######################################################################


class MyMetrix(ConfigListScreen, Screen):
	skin = """
<screen name="MyMetrix-Setup" position="40,40" size="1200,640" flags="wfNoBorder" backgroundColor="#40000000">
  <eLabel font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#40000000" halign="left" position="37,605" size="250,33" text="Cancel" transparent="1" />
  <eLabel font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#40000000" halign="left" position="335,605" size="250,33" text="Save" transparent="1" />
    <eLabel font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#40000000" halign="left" position="642,605" size="250,33" text="Reboot" transparent="1" />
 <widget name="config" position="21,77" scrollbarMode="showOnDemand" size="590,506" transparent="1" />
  <eLabel position="20,15" size="348,50" text="MyMetrix" font="Regular; 40" valign="center" transparent="1" backgroundColor="#40000000" />
  <eLabel position="223,18" size="349,50" text="Setup" foregroundColor="#00ffffff" font="Regular; 30" valign="center" backgroundColor="#40000000" transparent="1" halign="left" />
  <eLabel position="625,600" size="5,40" backgroundColor="#00ffff00" />
  <eLabel position="320,600" size="5,40" backgroundColor="#0000ff00" />
  <eLabel position="20,600" size="5,40" backgroundColor="#00ff0000" />
  <widget name="helperimage" position="629,81" size="550,500" zPosition="1" />
  <widget name="metrixUpdate" position="671,41" size="517,30" backgroundColor="#40000000" font="Regular; 18" foregroundColor="#00ffffff" transparent="1" halign="right" />
  <widget name="metrixVersion" position="987,11" size="200,30" backgroundColor="#40000000" foregroundColor="#00ffffff" transparent="1" halign="right" />
</screen>
"""

	def __init__(self, session, args = None, picPath = None):
		self.version = "v1.1b"
		self["metrixVersion"] = Label(_(self.version + " (Rev." + str(config.plugins.MetrixUpdater.Revision.value) + ") by iMaxxx. OpenPLI mod by IPMAN & Misenko."))
		self["metrixUpdate"] = Label(_(" "))
		if config.plugins.MetrixUpdater.UpdateAvailable.value == 1:
			self["metrixUpdate"] = Label(_("Update available, save to apply!"))
			if config.plugins.MetrixUpdater.Reboot.value == 1:
				self["metrixUpdate"] = Label(_("Update available, please reboot first to apply the update!"))
		else:
			self["metrixUpdate"] = Label(_(" "))
		self.skin_lines = []
		Screen.__init__(self, session)
		self.session = session
		self.datei = "/usr/share/enigma2/MetrixHD/skin.xml"
		self.dateiTMP = "/usr/share/enigma2/MetrixHD/skin.xml.tmp"
		self.daten = "/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/data/"
		self.komponente = "/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/comp/"
		self.picPath = picPath
		self.Scale = AVSwitch().getFramebufferScale()
		self.PicLoad = ePicLoad()
		self["helperimage"] = Pixmap()
		list = []
		list.append(getConfigListEntry(_("MetrixColor"), config.plugins.MyMetrix.SkinColor))
		list.append(getConfigListEntry(_("MetrixUpdater"), config.plugins.MyMetrix.AutoUpdate))
		list.append(getConfigListEntry(_("EMC Style"), config.plugins.MyMetrix.EMCStyle))
		list.append(getConfigListEntry(_("Merlin Music Player Style"), config.plugins.MyMetrix.MerlinMusicPlayerStyle))
		list.append(getConfigListEntry(_("WebradioFS Style"), config.plugins.MyMetrix.WebradioFSStyle))
		list.append(getConfigListEntry(_("EPG Style"), config.plugins.MyMetrix.EPGStyle))
		list.append(getConfigListEntry(_("Channel Selection Style"), config.plugins.MyMetrix.ChannelSelectionStyle))
		list.append(getConfigListEntry(_("----------------------------- MetrixWeather  --------------------------------"), ))
		list.append(getConfigListEntry(_("MetrixWeather ID"), config.plugins.MetrixWeather.woeid))
		list.append(getConfigListEntry(_("Unit"), config.plugins.MetrixWeather.tempUnit))
		list.append(getConfigListEntry(_("Refresh Interval (min)"), config.plugins.MetrixWeather.refreshInterval))
		list.append(getConfigListEntry(_("---------------------------------- InfoBar ----------------------------------"), ))
		list.append(getConfigListEntry(_("Clock Widget"), config.plugins.MyMetrix.InfobarClockWidget))
		list.append(getConfigListEntry(_("Info Widget"), config.plugins.MyMetrix.InfobarInfoWidget))
		list.append(getConfigListEntry(_("Weather Widget"), config.plugins.MyMetrix.InfobarWeatherWidget))
		list.append(getConfigListEntry(_("Health Widget"), config.plugins.MyMetrix.InfobarHealthWidget))
		list.append(getConfigListEntry(_("Style"), config.plugins.MyMetrix.InfobarStyle))
		list.append(getConfigListEntry(_("Progress Bar Style"), config.plugins.MyMetrix.InfobarProgressStyle))
		list.append(getConfigListEntry(_("Channel name"), config.plugins.MyMetrix.InfobarShowChannelname))
		list.append(getConfigListEntry(_("Show tuner info"), config.plugins.MyMetrix.InfobarTunerInfo))
		list.append(getConfigListEntry(_("Show resolution info"), config.plugins.MyMetrix.InfobarResolutionInfo))
		list.append(getConfigListEntry(_("Show crypt info"), config.plugins.MyMetrix.InfobarCryptInfo))
		list.append(getConfigListEntry(_("----------------------------- SecondInfoBar --------------------------------"), ))
		list.append(getConfigListEntry(_("Clock Widget"), config.plugins.MyMetrix.SecondInfobarClockWidget))
		list.append(getConfigListEntry(_("Info Widget"), config.plugins.MyMetrix.SecondInfobarInfoWidget))
		list.append(getConfigListEntry(_("Health Widget"), config.plugins.MyMetrix.SecondInfobarHealthWidget))
		list.append(getConfigListEntry(_("Weather Widget"), config.plugins.MyMetrix.SecondInfobarWeatherWidget))
		list.append(getConfigListEntry(_("EPG Widget"), config.plugins.MyMetrix.SecondInfobarEPGWidget))
		list.append(getConfigListEntry(_("Style"), config.plugins.MyMetrix.SecondInfobarStyle))
		list.append(getConfigListEntry(_("Progress Bar Style"), config.plugins.MyMetrix.SecondInfobarProgressStyle))
		list.append(getConfigListEntry(_("Channel name"), config.plugins.MyMetrix.SecondInfobarShowChannelname))
		list.append(getConfigListEntry(_("Show tuner info"), config.plugins.MyMetrix.SecondInfobarTunerInfo))
		list.append(getConfigListEntry(_("Show resolution info"), config.plugins.MyMetrix.SecondInfobarResolutionInfo))
		list.append(getConfigListEntry(_("Show crypt info"), config.plugins.MyMetrix.SecondInfobarCryptInfo))

		ConfigListScreen.__init__(self, list)
		self["actions"] = ActionMap(["OkCancelActions","DirectionActions", "InputActions", "ColorActions"], {"left": self.keyLeft,"down": self.keyDown,"up": self.keyUp,"right": self.keyRight,"red": self.exit,"yellow": self.reboot, "blue": self.showInfo, "green": self.save,"cancel": self.exit}, -1)
		self.onLayoutFinish.append(self.UpdateComponents)
		#if config.plugins.MetrixUpdater.UpdateAvailable.value = 1

		
	def GetPicturePath(self):
		try:
			returnValue = self["config"].getCurrent()[1].value
			#print "\n selectedOption: " + returnValue + "\n"
			path = "/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/images/" + returnValue + ".jpg"
			return path
		except:
			return "/usr/lib/enigma2/python/Plugins/Extensions/MyMetrix/images/metrixweather.jpg"
		
	def UpdatePicture(self):
		self.PicLoad.PictureData.get().append(self.DecodePicture)
		self.onLayoutFinish.append(self.ShowPicture)
	
	def ShowPicture(self):
		self.PicLoad.setPara([self["helperimage"].instance.size().width(),self["helperimage"].instance.size().height(),self.Scale[0],self.Scale[1],0,1,"#002C2C39"])
		self.PicLoad.startDecode(self.GetPicturePath())
		#print "showing image"
		
	def DecodePicture(self, PicInfo = ""):
		#print "decoding picture"
		ptr = self.PicLoad.getData()
		self["helperimage"].instance.setPixmap(ptr)	

	def UpdateComponents(self):
		self.UpdatePicture()
		#if not fileExists(self.datei + self.release):
		#	system('cp -f ' + self.komponente + 'hardyPicon2.py /usr/lib/enigma2/python/Components/Renderer/hardyPicon2.py')
		#	system("tar -xzvf " + self.komponente + "MetrixHD.tar.gz" + " -C /")
		#	system("touch " + self.datei + self.release)
				

	def keyLeft(self):	
		ConfigListScreen.keyLeft(self)	
		self.ShowPicture()

	def keyRight(self):
		ConfigListScreen.keyRight(self)
		self.ShowPicture()
	
	def keyDown(self):
		#print "key down"
		self["config"].instance.moveSelection(self["config"].instance.moveDown)
		#ConfigListScreen.keyDown(self)
		self.ShowPicture()
		
	def keyUp(self):
		#print "key up"
		self["config"].instance.moveSelection(self["config"].instance.moveUp)
		#ConfigListScreen.keyUp(self)
		self.ShowPicture()
	
	def reboot(self):
		restartbox = self.session.openWithCallback(self.restartGUI,MessageBox,_("Do you really want to reboot now?"), MessageBox.TYPE_YESNO)
		restartbox.setTitle(_("Restart GUI"))
		
	def showInfo(self):
		self.session.open(MessageBox, _("Information"), MessageBox.TYPE_INFO)

	def save(self):
		for x in self["config"].list:
			if len(x) > 1:
        			x[1].save()
			else:
       				pass
       			
		###########READING DATA FILES
		try:
			self.appendSkinFile(self.daten + "header.xml")
				
			###InfoBar
			self.appendSkinFile(self.daten + "infobar-header.xml")
			#ClockWidget
			self.appendSkinFile(self.daten + config.plugins.MyMetrix.InfobarClockWidget.value + ".xml")
			#ProgressBar
			self.appendSkinFile(self.daten + config.plugins.MyMetrix.InfobarProgressStyle.value + ".xml")
			#MetrixUpdater
			self.appendSkinFile(self.daten + config.plugins.MyMetrix.AutoUpdate.value + ".xml")
			#InfoWidget
			self.appendSkinFile(self.daten + config.plugins.MyMetrix.InfobarInfoWidget.value + ".xml")
			#WeatherWidget
			self.appendSkinFile(self.daten + config.plugins.MyMetrix.InfobarWeatherWidget.value + ".xml")
			#Style
			self.appendSkinFile(self.daten + config.plugins.MyMetrix.InfobarStyle.value + ".xml")
			#HealthWidget
			self.appendSkinFile(self.daten + config.plugins.MyMetrix.InfobarHealthWidget.value + ".xml")
			#ChannelName
			self.appendSkinFile(self.daten + config.plugins.MyMetrix.InfobarShowChannelname.value + ".xml")
			#TunerInfo
			self.appendSkinFile(self.daten + config.plugins.MyMetrix.InfobarTunerInfo.value + ".xml")
			#ResolutionInfo
			self.appendSkinFile(self.daten + config.plugins.MyMetrix.InfobarResolutionInfo.value + ".xml")
			#CryptInfo
			self.appendSkinFile(self.daten + config.plugins.MyMetrix.InfobarCryptInfo.value + ".xml")
			#Footer
			self.appendSkinFile(self.daten + "screen-footer.xml")
			
			###SecondInfoBar
			self.appendSkinFile(self.daten + "secondinfobar-header.xml")
			#ClockWidget
			self.appendSkinFile(self.daten + config.plugins.MyMetrix.SecondInfobarClockWidget.value + ".xml")
			#ProgressBar
			self.appendSkinFile(self.daten + config.plugins.MyMetrix.SecondInfobarProgressStyle.value + ".xml")
			#MetrixUpdater
			self.appendSkinFile(self.daten + config.plugins.MyMetrix.AutoUpdate.value + ".xml")
			#InfoWidget
			self.appendSkinFile(self.daten + config.plugins.MyMetrix.SecondInfobarInfoWidget.value + ".xml")
			#WeatherWidget
			self.appendSkinFile(self.daten + config.plugins.MyMetrix.SecondInfobarWeatherWidget.value + ".xml")
			#HealthWidget
			self.appendSkinFile(self.daten + config.plugins.MyMetrix.SecondInfobarHealthWidget.value + ".xml")
			#EPGWidget
			self.appendSkinFile(self.daten + config.plugins.MyMetrix.SecondInfobarEPGWidget.value + ".xml")
			#Style
			self.appendSkinFile(self.daten + config.plugins.MyMetrix.SecondInfobarStyle.value + ".xml")
			#ChannelName
			self.appendSkinFile(self.daten + config.plugins.MyMetrix.SecondInfobarShowChannelname.value + ".xml")
			#TunerInfo
			self.appendSkinFile(self.daten + config.plugins.MyMetrix.SecondInfobarTunerInfo.value + ".xml")
			#ResolutionInfo
			self.appendSkinFile(self.daten + config.plugins.MyMetrix.SecondInfobarResolutionInfo.value + ".xml")
			#CryptInfo
			self.appendSkinFile(self.daten + config.plugins.MyMetrix.SecondInfobarCryptInfo.value + ".xml")
			#Footer
			self.appendSkinFile(self.daten + "screen-footer.xml")
			
			#EMCSTYLE
			self.appendSkinFile(self.daten + config.plugins.MyMetrix.EMCStyle.value +".xml")
			#MERLINMUSICPLAYERSTYLE
			self.appendSkinFile(self.daten + config.plugins.MyMetrix.MerlinMusicPlayerStyle.value +".xml")
			#WEBRADIOFSStyle
			self.appendSkinFile(self.daten + config.plugins.MyMetrix.WebradioFSStyle.value +".xml")
			#EPGSTYLE
			self.appendSkinFile(self.daten + config.plugins.MyMetrix.EPGStyle.value +".xml")
			#CHANNELSELECTIONSTYLE
			self.appendSkinFile(self.daten + config.plugins.MyMetrix.ChannelSelectionStyle.value +".xml")
			
			###Main XML
			self.appendSkinFile(self.daten + "main.xml")

			xFile = open(self.dateiTMP, "w")
			for xx in self.skin_lines:
				xFile.writelines(xx)
			xFile.close()
			#Replaces <color name="metrixSelection" value="#00149bae" /> with SkinColor.value
			o = open(self.datei,"w")
			for line in open(self.dateiTMP):
				line = line.replace("#00149bae", config.plugins.MyMetrix.SkinColor.value )
				o.write(line)
			o.close()
			system('rm -rf ' + self.dateiTMP)

		except:
			self.session.open(MessageBox, _("Error creating Skin!"), MessageBox.TYPE_ERROR)
		#config.skin.primary_skin.value = "MetrixHD/skin.xml"
		config.plugins.MetrixUpdater.UpdateAvailable.value = 0
		config.plugins.MetrixUpdater.save()    
		configfile.save()
		restartbox = self.session.openWithCallback(self.restartGUI,MessageBox,_("GUI needs a restart to apply a new skin.\nDo you want to Restart the GUI now ?"), MessageBox.TYPE_YESNO)
		restartbox.setTitle(_("Restart GUI"))

	def restartGUI(self, answer):
		if answer is True:
			config.plugins.MetrixUpdater.Reboot.value = 0
			config.plugins.MetrixUpdater.save()    
			configfile.save()
			self.session.open(TryQuitMainloop, 3)
		else:
			self.close()
			
	def appendSkinFile(self,appendFileName):
		skFile = open(appendFileName, "r")
		file_lines = skFile.readlines()
		skFile.close()	
		for x in file_lines:
			self.skin_lines.append(x)
			

	def exit(self):
		for x in self["config"].list:
			if len(x) > 1:
					x[1].cancel()
			else:
       				pass
		self.close()

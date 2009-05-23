/*
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 * Copyright 2009 Abhishek Mukherjee <abhishek.mukher.g@gmail.com
 */
/* Originally written by dot_j on the mumbles project, could not find a date */

var download_complete_notify = {
  onLoad: function() {
    // initialization code
    this.initialized = true;
    this.strings = document.getElementById("download_complete_notify-strings");
    
    this.dlMgr = Components.classes["@mozilla.org/download-manager;1"]
                           .getService(Components.interfaces.nsIDownloadManager);
              
    this.dlMgr.addListener(download_complete_notify);

    // disable native firefox download notifications
    var prefs = Components.classes["@mozilla.org/preferences-service;1"]
                    .getService(Components.interfaces.nsIPrefService);
    prefs.setBoolPref("browser.download.manager.showAlertOnComplete",false);
  },
  
  notify: function(aDownload) {

        var exec = Components.classes["@mozilla.org/file/local;1"].createInstance(Components.interfaces.nsILocalFile);

	const MY_ID = 'firefoxnotify@abhishek.mukherjee';
	const DIR_SERVICE = Components.classes["@mozilla.org/extensions/manager;1"].
		getService(Components.interfaces.nsIExtensionManager);
    try {
        try {
            var file = DIR_SERVICE.getInstallLocation(MY_ID).
		    getItemFile(MY_ID, "chrome/content/download_complete_notify.py");
        } catch (e) {
            alert("error finding download_complete_notify.py: "+error);
        }

        exec.initWithPath(file.path);

        if (exec.exists()) {
            var process = Components.classes["@mozilla.org/process/util;1"].createInstance(Components.interfaces.nsIProcess);

            var args = [aDownload.displayName, aDownload.targetFile.path];

            process.init(exec);

            var exitvalue = process.run(false, args, args.length);
        } else {
            alert("Error running download_complete_notify.py");
        }
    } catch (e) {
        alert("FirefoxNotify Failed"+e);
        return;
    }
  },
  
  onDownloadStateChange: function(aState, aDownload) {
    
    switch(aDownload.state) {
      case Components.interfaces.nsIDownloadManager.DOWNLOAD_DOWNLOADING:
      case Components.interfaces.nsIDownloadManager.DOWNLOAD_FAILED:
      case Components.interfaces.nsIDownloadManager.DOWNLOAD_CANCELED:
        break;
        
      case Components.interfaces.nsIDownloadManager.DOWNLOAD_FINISHED:
        this.notify(aDownload);
        break;
    }
  },

};

window.addEventListener("load", function(e) { download_complete_notify.onLoad(e); }, false);

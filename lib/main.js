var _ = require('localization').get;

function showAlertNotification(imageUrl, title, text,
                        textClickable, cookie, alertListener, name) {
  var classObj = Components.classes['@mozilla.org/alerts-service;1'];
  var alertService = classObj.getService(
	  Components.interfaces.nsIAlertsService);
   
  alertService.showAlertNotification(imageUrl, title, text,
                        textClickable, cookie, alertListener, name);
}

var downloadNotify = {
  onDownloadStateChange: function(aState, aDownload) {
    var statement;
    switch(aDownload.state) {
    case Components.interfaces.nsIDownloadManager.DOWNLOAD_FINISHED:
      showAlertNotification("firefox", "test", "done");
      console.log("Downloaded file");
      console.log(_("downloadsCompleteTitle"));
      console.log(_("downloadsCompleteMsg"));
    }
  }
}

exports.main = function(options, callbacks) {
  var dlMgr = Components.classes["@mozilla.org/download-manager;1"]
    .getService(Components.interfaces.nsIDownloadManager);
  dlMgr.addListener(downloadNotify);
}


      

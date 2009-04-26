package:
	(cd src && find . \( -iname "*.pyc" -or -iname ".*.swp" \) -delete && \
	zip -r ../FirefoxNotify-nightly.xpi chrome chrome.manifest defaults/ install.rdf)
.PHONY: package clean
clean:
	rm -f FirefoxNotify-nightly.zip

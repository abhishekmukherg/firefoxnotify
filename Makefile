package:
	(cd src && find . \( -iname "*.pyc" -or -iname ".*.swp" \) -delete && \
	zip -r ../FirefoxNotify-nightly.zip chrome chrome.manifest defaults/ install.rdf)
.PHONY: package clean
clean:
	rm -f FirefoxNotify-nightly.zip

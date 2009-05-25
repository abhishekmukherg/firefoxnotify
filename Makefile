package: logo
	(cd src && find . \( -iname "*.pyc" -or -iname ".*.swp" \) -delete && \
	zip -r ../FirefoxNotify-nightly.xpi chrome chrome.manifest defaults/ install.rdf)

logo: src/chrome/content/logo.png

src/chrome/content/logo.png: logo.svg
	rsvg-convert logo.svg -o src/chrome/content/logo.png --width=32 --keep-aspect-ratio --format=png

.PHONY: package clean
clean:
	rm -f FirefoxNotify-nightly.zip

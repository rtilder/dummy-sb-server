.PHONY: clean easylist easyprivacy

mozpub: clean easylist
	./lists2safebrowsing.py tmp_in tmp_out/mozpub-track-digest256

mozpubmini: clean disconnect
	./lists2safebrowsing.py tmp_in tmp_out/mozpubmini-track-digest256

abp: easylist easyprivacy

tpl: abine privacychoice truste

easylist:
	mkdir -p tmp_in/abp/ && mkdir -p tmp_out/abp/ && \
curl https://easylist-downloads.adblockplus.org/easylist.txt \
-o tmp_in/abp/easylist.txt && \
./lists2safebrowsing.py tmp_in/abp tmp_out/abp/mozpub-track-digest256

easyprivacy:
	mkdir -p tmp_in/abp/ && mkdir -p tmp_out/abp/ && \
curl https://easylist-downloads.adblockplus.org/easyprivacy.txt \
-o tmp_in/abp/easyprivacy.txt && \
./lists2safebrowsing.py tmp_in/abp tmp_out/abp/mozpub-track-digest256

abine:
	mkdir -p tmp_in/tpl/ && mkdir -p tmp_out/tpl/ && \
curl http://www.abine.com/tpl/abineielist.txt -o tmp_in/tpl/abine.txt && \
./lists2safebrowsing.py tmp_in/tpl tmp_out/tpl/mozpubmini-track-digest256

privacychoice:
	mkdir -p tmp_in/tpl/ && mkdir -p tmp_out/tpl/ && \
curl http://www.privacychoice.org/trackerblock/all_companies_tpl \
-o tmp_in/tpl/privacychoice.txt && \
./lists2safebrowsing.py tmp_in/tpl tmp_out/tpl/mozpubmini-track-digest256

truste:
	mkdir -p tmp_in/tpl/ && mkdir -p tmp_out/tpl/ && \
curl http://easy-tracking-protection.truste.com/easy.tpl \
-o tmp_in/tpl/truste.txt && \
./lists2safebrowsing.py tmp_in/tpl tmp_out/tpl/mozpubmini-track-digest256

disconnect:
	mkdir -p tmp_in/disconnect && mkdir -p tmp_out/disconnect/ && \
curl http://services.disconnect.me/disconnect-plaintext.json \
-o tmp_in/disconnect/disconnect-plaintext.json && \
./lists2safebrowsing.py tmp_in/disconnect tmp_out/disconnect/mozpubmini-track-digest256

domainslist: tpl disconnect
	mkdir -p tmp_out/domainlist
	grep '^\[m\]' tmp_out/{tpl,disconnect}/mozpubmini-track-digest256.log | \
	sed -e 's/^.*>> //' | cut -d" " -f1 | sort | uniq | sed -e 's/\///' > tmp_out/domainlist/domains.txt

clean:
	rm -rf tmp_in tmp_out

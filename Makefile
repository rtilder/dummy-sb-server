.PHONY: clean easylist easyprivacy

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

clean:
	rm -rf tmp_in tmp_out

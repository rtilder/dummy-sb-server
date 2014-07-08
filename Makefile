.PHONY: clean easylist easyprivacy

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

clean:
	rm -rf tmp_in tmp_out

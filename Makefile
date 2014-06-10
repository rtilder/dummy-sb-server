.PHONY: clean easylist easyprivacy

easylist:
	mkdir -p tmp_easylist_in && mkdir -p tmp_easylist_out && \
curl https://easylist-downloads.adblockplus.org/easylist.txt -o tmp_easylist_in/easylist.txt && \
./abp_hosts.py tmp_easylist_in tmp_easylist_out/mozpub-track-digest256

easyprivacy:
	mkdir -p tmp_easyprivacy_in && mkdir -p tmp_easyprivacy_out && \
	curl https://easylist-downloads.adblockplus.org/easyprivacy.txt -o tmp_easyprivacy_in/easyprivacy.txt && ./abp_hosts.py tmp_easyprivacy_in tmp_easyprivacy_out/mozpub-track-digest256

clean:
	rm -rf tmp_easylist_in tmp_easylist_out tmp_easyprivacy_in tmp_easyprivacy_out log;

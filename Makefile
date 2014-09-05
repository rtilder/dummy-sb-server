.PHONY: clean mozpub tpl abine privacychoice truste disconnect mozpub_domainslist

mozpub: clean disconnect
	cp tmp_out/disconnect/mozpub-track-digest256 tmp_out
	cp tmp_out/disconnect/mozpub-track-digest256 safebrowsing_server

mozpub_scrubbed: clean tpl disconnect
	# generate list using domains that appear in both tpl and disconnect
	# This does not seem to be working on Linux, kontaxis.
	mkdir -p tmp_in/txt && \
	cat tmp_out/{tpl,disconnect}/domains.txt | sort | uniq -c | \
	sort -rn | egrep "^   2 " | sed s/"   2 "/""/g > tmp_in/txt/domains.txt && \
	./lists2safebrowsing.py txt tmp_in/txt tmp_out/mozpub-track-digest256

tpl: abine privacychoice truste
# get tpl domains from parsed log
	./lists2safebrowsing.py tpl tmp_in/tpl tmp_out/tpl/mozpub-track-digest256 && \
grep '^\[m\]' tmp_out/tpl/mozpub-track-digest256.log | \
sed -e 's/^.*>> //' | cut -d" " -f1 | sort | \
uniq > tmp_out/tpl/domains.txt

abine:
# get tpl domains from parsed log
	mkdir -p tmp_in/tpl/abine && mkdir -p tmp_out/tpl/abine && \
curl http://www.abine.com/tpl/abineielist.txt -o tmp_in/tpl/abine/abine.txt && \
./lists2safebrowsing.py tpl tmp_in/tpl/abine tmp_out/tpl/abine/mozpub-track-digest256 && \
grep '^\[m\]' tmp_out/tpl/abine/mozpub-track-digest256.log | \
sed -e 's/^.*>> //' | cut -d" " -f1 | sort | \
uniq > tmp_out/tpl/abine/domains.txt

privacychoice:
	mkdir -p tmp_in/tpl/privacychoice && mkdir -p tmp_out/tpl/privacychoice && \
curl http://www.privacychoice.org/trackerblock/all_companies_tpl \
-o tmp_in/tpl/privacychoice/privacychoice.txt && \
./lists2safebrowsing.py tpl tmp_in/tpl/privacychoice tmp_out/tpl/privacychoice/mozpub-track-digest256 && \
grep '^\[m\]' tmp_out/tpl/privacychoice/mozpub-track-digest256.log | \
sed -e 's/^.*>> //' | cut -d" " -f1 | sort | \
uniq > tmp_out/tpl/privacychoice/domains.txt

truste:
	mkdir -p tmp_in/tpl/truste && mkdir -p tmp_out/tpl/truste && \
curl http://easy-tracking-protection.truste.com/easy.tpl \
-o tmp_in/tpl/truste/truste.txt && \
./lists2safebrowsing.py tpl tmp_in/tpl/truste tmp_out/tpl/truste/mozpub-track-digest256 && \
grep '^\[m\]' tmp_out/tpl/truste/mozpub-track-digest256.log | \
sed -e 's/^.*>> //' | cut -d" " -f1 | sort | \
uniq > tmp_out/tpl/truste/domains.txt

disconnect:
# get disconnect domains from parsed log for debugging later
	mkdir -p tmp_in/disconnect && mkdir -p tmp_out/disconnect/ && \
curl http://services.disconnect.me/disconnect-plaintext.json \
-o tmp_in/disconnect/disconnect-plaintext.json && \
./lists2safebrowsing.py disconnect tmp_in/disconnect tmp_out/disconnect/mozpub-track-digest256 && \
grep '^\[m\]' tmp_out/disconnect/mozpub-track-digest256.log | \
sed -e 's/^.*>> //' | cut -d" " -f1 | sort | \
uniq > tmp_out/disconnect/domains.txt

mozpub_domainslist: mozpub
	grep '^\[m\]' tmp_out/mozpub-track-digest256.log | \
	sed -e 's/^.*>> //' | cut -d" " -f1 | sort | uniq | sed -e 's/\///' > tmp_out/domains.txt

clean:
	rm -rf tmp_in tmp_out

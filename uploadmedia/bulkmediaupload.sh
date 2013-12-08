rm $1.step2.csv
rm $1.step3.csv
./postblob.sh /tmp/upload_cache $1.step1.csv
python uploadMedia.py $1.step2.csv
mv $1.step1.csv $1.processed.csv

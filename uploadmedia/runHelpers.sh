#cp /home/developers/pahma/4solr.pahma.media.csv media.csv
perl checkObj.pl > MediaNBlobs.txt
grep OK MediaNBlobs.txt > OK.txt
grep 'NoMatch|None' MediaNBlobs.txt  | grep -v NoObjectFound> NotInDB.txt
grep NoObjectFound MediaNBlobs.txt  > NoObjectFound.txt
grep -v 'NoMatch|None' MediaNBlobs.txt  | grep -v NoObjectFound | grep -v OK> OtherIssues.txt
cut -f1 NotInDB.txt > NotInDB.jpgfilenames.txt
for f in `cat NotInDB.jpgfilenames.txt ` ; do grep  -h "$f" /tmp/upload_cache/*.step2.csv ; done | sort -u >  NotInDB.step2.csv 
for f in `cat NotInDB.jpgfilenames.txt ` ; do grep  "$f" /tmp/upload_cache/*.step2.csv ; done | sort -u > NotInDB.step2.txt  
sort -u NotInDB.step2.txt  | cut -f1 -d":" | sort | uniq -c >RerunFiles.txt
cat NoObjectFound.txt NotInDB.txt | cut -f1 > ToCheck.txt
./verifyObjectsAndMedia.sh < ToCheck.txt > ToCheck.results.txt &
perl -ne 'print if /\|\s*$/' ToCheck.results.txt > NoObjectFoundv2.txt 
wc -l *.txt

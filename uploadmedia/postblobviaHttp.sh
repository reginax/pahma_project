#!/bin/bash

PROTO="https://"
HOST="pahma-dev.cspace.berkeley.edu"
SRVC="cspace-services/blobs"
URL="${PROTO}${HOST}/$SRVC"
CONTENT_TYPE="Content-Type: application/xml"
USER="admin@pahma.cspace.berkeley.edu:xxxxxxx"
MEDIACONFIG="uploadmediaDev"

JOB=$1
IMGDIR=$(dirname $1)

# claim this job...by renaming the input file
mv $JOB.step1.csv $JOB.inprogress.csv
INPUTFILE=$JOB.inprogress.csv

OUTPUTFILE=$JOB.step2.csv
LOGDIR=$IMGDIR
CURLLOG="$LOGDIR/curl.log"
CURLOUT="$LOGDIR/curl.out"
TRACELOG="$JOB.trace.log"

rm -f $OUTPUTFILE
rm -f $JOB.step3.csv

TRACE=2

function trace()
{
   tdate=`date "+%Y-%m-%d %H:%M:%S"`
   [ "$TRACE" -eq 1 ] && echo "TRACE: $1"
   [ "$TRACE" -eq 2 ] && echo "TRACE: [$JOB : $tdate ] $1" >> $TRACELOG
}

trace "**** START OF RUN ******************** `date` **************************"
trace "media directory: $1"
trace "output file: $OUTPUTFILE"

if [ ! -f "$INPUTFILE" ]
then
    trace "Missing input file: $INPUTFILE"
    echo "Missing input file: $INPUTFILE exiting..."
    exit
else
    trace "input file: $INPUTFILE"
fi

while IFS=$'\t' read FILENAME size objectnumber digitizedDate creator contributor rightsholder
do
  FILEPATH="$IMGDIR/$FILENAME"

  # skip header
  if [ "$FILENAME" == "name" ]
  then
    continue
  fi

  trace ">>>>>>>>>>>>>>> Starting: $objectnumber | $digitizedDate | $FILENAME"

  if [ ! -f "$FILEPATH" ]
  then
    trace "Missing file: $FILEPATH"
    continue
  fi

  /bin/rm -f $CURLOUT

  # if filename contains commas, translate them to colons (cf CSPACE-5497)
  FILEPATH2="$FILEPATH"
  if [[ "$FILEPATH" == *,* ]]
  then
     trace "renaming $FILEPATH..."
     FILEPATH2=$(echo $FILEPATH | sed -e 's/,/:/g')
     cp "$FILEPATH" "$FILEPATH2"
  fi

  trace "curl -i -u \"xxxxx\"  --form file=\"@${FILEPATH2}\" --form press=\"OK\" \"$URL\""
  curl -i -u "$USER" --form file="@${FILEPATH2}" --form press="OK" "$URL" -o $CURLOUT

  # NB: we should someday get rid of the extra files created...

  if [ ! -f $CURLOUT ]
  then
    trace "No output file, something failed for $FILEPATH"
    continue
  fi

  if ! grep -q "HTTP/1.1 201 Created" $CURLOUT
  then
    trace "Post did not return a 201 status code for $FILEPATH"
    continue
  fi

  LOC=`grep "^Location: .*cspace-services/blobs/" $CURLOUT`
  trace "LOC $LOC"
  CSID=${LOC##*cspace-services/blobs/}
  CSID=${CSID//$'\r'}
  #trace "CSID $CSID"

  cat $CURLOUT >> $CURLLOG
  rh=${rightsholder//$'\r'}
  echo "$FILENAME|$size|$objectnumber|$CSID|$digitizedDate|$creator|$contributor|$rh|$FILEPATH" >>  $OUTPUTFILE
done < $INPUTFILE

trace ">>>>>>>>>>>>>>> End of Blob Creation, starting Media and Relation record creation process: `date` "
python /var/www/cgi-bin/uploadMedia.py $OUTPUTFILE $MEDIACONFIG >> $TRACELOG
trace "Media record and relations created."

mv $INPUTFILE $JOB.original.csv
mv $JOB.step3.csv $JOB.processed.csv
rm $JOB.step2.csv

trace "**** END OF RUN ******************** `date` **************************"
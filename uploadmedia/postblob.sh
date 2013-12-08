#!/bin/bash

PROTO="https://"
HOST="dev.cspace.berkeley.edu"
SRVC="cspace-services/blobs"
URL="${PROTO}${HOST}/$SRVC"
CONTENT_TYPE="Content-Type: application/xml"
USER="admin@pahma.cspace.berkeley.edu:Ph02b2-admin"

IMGDIR=$1
LOGDIR=""
OUTPUTFILE=${2/step1/step2}
LOGDIR="."
CURLLOG="$LOGDIR/curl.log"
TRACELOG="$LOGDIR/trace.log"

TRACE=2

function trace()
{
   [ "$TRACE" -eq 1 ] && echo "TRACE: $1"
   [ "$TRACE" -eq 2 ] && echo "TRACE: $1" >> $TRACELOG
}

trace "**** START OF RUN ******************** `date` **************************"
trace "media directory: $1"
trace "output file: $OUTPUTFILE"

if [ ! -f "$2" ]
then
    trace "Missing input file: $2"
    echo "Missing input file: $2 exiting..."
    exit
else
    trace "input file: $2"
fi

while IFS=$'\t' read FILENAME size objectnumber digitizedDate creator contributor rightsholder
do
  FILEPATH="$IMGDIR/$FILENAME"
  trace ">>>>>>>>>>>>>>> Starting: $objectnumber | $digitizedDate | $FILENAME"

  if [ ! -f "$FILEPATH" ]
  then
    trace "Missing file: $FILEPATH"
    continue
  fi

  /bin/rm -f curl.out

  trace "curl -i -u \"$USER\"  --form file=\"@$FILEPATH\" --form press=\"OK\" \"$URL\""
  curl -i -u "$USER" --form file="@$FILEPATH" --form press="OK" "$URL" -o curl.out
  if [ ! -f curl.out ]
  then
    trace "No output file, something failed for $FILEPATH"
    continue
  fi

  if ! grep -q "HTTP/1.1 201 Created" curl.out
  then
    trace "Post did not return a 201 status code for $FILEPATH"
    continue
  fi

  LOC=`grep "^Location: .*cspace-services/blobs/" curl.out`
  trace "LOC $LOC"
  CSID=${LOC##*cspace-services/blobs/}
  CSID=${CSID//$'\r'}
  trace "CSID $CSID"

  cat curl.out >> $CURLLOG
  rh=${rightsholder//$'\r'}
  echo "$FILENAME|$size|$objectnumber|$CSID|$digitizedDate|$creator|$contributor|$rh|$FILEPATH" >>  $OUTPUTFILE
done < $2

trace "**** END OF RUN ******************** `date` **************************"

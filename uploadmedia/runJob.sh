#rm /tmp/upload_cache/$1*
if [ -f /tmp/upload_cache/$1.original.csv ]
then
  echo "/tmp/upload_cache/$1.original.csv already exists; job has already been run"
  echo "please cleanup then runJob"
  #cp -p /tmp/upload_cache/$1.original.csv /tmp/upload_cache/$1.step1.csv
fi
if [ -f /tmp/upload_cache/$1.step1.csv ]
then
  echo "running $1..."
  echo  Starting `date` $1 >> /tmp/upload_cache/batches.log
  su -s /bin/bash apache -c "/usr/local/share/django/pahma_project/uploadmedia/postblob.sh /tmp/upload_cache/$1 >> /tmp/upload_cache/batches.log"
  echo  Ending `date` $1 >> /tmp/upload_cache/batches.log
else
  echo "Input file /tmp/upload_cache/$1.step1.csv does not exist..."
fi

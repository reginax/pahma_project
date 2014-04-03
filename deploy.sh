#
# usage:
#
# ./deploy <project> <branch>
#
# where: project is the (already deployed) django project you wish to update.
#        branch is the GitHub branch of that project you wish to deploy
#
# notes:
#
# * you'll need priveleges to update that code, so you may need to sudo this script.
#
# * note that this deploy attempts to preserve local changes. This may interfere
#   with the correct updating if the new branch contains revisions to a changed file!
#
cd /usr/local/share/django/$1_project/
git stash
git pull origin $2 -v
#git checkout -b $2
git branch
python manage.py collectstatic --noinput
git stash apply
service httpd graceful

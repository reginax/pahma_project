pahma-project
=============

This Django project supports several webapps used by the Hearst Museum (PAHMA).

It is based on the "cspace_django_project" which provide basic authentication of webapps against
the configured CSpace server (see the documentation for this project on GitHub).

Some things to note when deploying this project:

* Most webapps require a config file, and an example configuration file, is included in the app's directory.
Each of these needs to be copied to the *project configuration directory* (config/)
with the file name expected by the webapp (usually "webapp.cfg" where "webapp" is the
directory name of the webapp) and then edited to specific deployment-specific parameters.

* In particular, this project has a webapp (uploadmedia), which integrates with other batch
components and these need to be configured not only in confg directory but in the webapp directory
and /var/www/cgi-bin. See the README for this webapp for details.

* There are installation and update scripts which deploy these "cspace_django_project"-type projects in UCB's RHEL
environments. These may be found in Tools/deployandrelease repo, which should normally be deployed alongside the
projects themselves.
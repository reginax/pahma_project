pahma-project
=============

This Django project supports several webapps used by the Hearst Museum (PAHMA).

Is is based on the "cspace_django_project" which provide basic authentication of webapps against
the configured CSpace server (see the documentation for this project on GitHub).

Some things to note when deploying this project:

* Each webapp has an example configuration file, usually something like "exampleWebappname.cfg" in
the application's root directory. Each of these needs to be copied to the project config directory
with the file name expected by the webapp (usually "webapp.cfg" where "webapp" is the
directory name of the webapp) and then edited to specific deployment-specific parameters.

* In particular, this project has a webapp (uploadmedia), which integrates with other batch
components and these need to be configured not only in confg directory but in the webapp directory
and /var/www/cgi-bin. See the README for this webapp for details.
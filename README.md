# eudat.pcp.site
Build and configuration files for EUDATs Project Coordination Portal 

## Quickstart

Clone, bootstrap and build as usual ...

## Details

Clone this repository to start a new instance of the Project Coordination Portal (PCP). From within the resulting folder call `bootstrap.py` using Python 2. Recommended version is 2.7.x but 2.6 should also be supported. Note that Plone and therefore the PCP does not support Python 3 yet. If all goes well you will now find a `bin` directory containing the `buildout` command. Call this now (`bin/buildout`). It will take a while to download, compile and install everything you need provided you have meet the basic requirements of your OS for any Plone site. See http://docs.plone.org/manage/installing/requirements.html for the details. There will be a lot of debug info and also some spurious error messages like `SyntaxError: 'return' outside function` - those can safely be ignored.

On completion you will find a command `instance` in your `bin` folder. Use this to start the PCP instance. When doing so for the first time or for development use the `foreground` mode to turn into debug mode: `bin/instance fg`. Now point your browser to `http://localhost:8080`,create your site and take it from there. 

Enjoy,

  Raphael
  

#
# sync_rct_projects.py
#
# simple script to be invoked via
#
#  cd <your-buildout-root-dir>
#  bin/instance run scripts/sync_rct_projects.py
#
#  reads source information from data/rct_dump_20150609.json
#  
#  The SITE_ID is hard coded as 'pcp'

FILE_NAME = 'data/rct_dump_20150609.json'
SITE_ID = site_id = 'pcp'

from Products.PlonePAS.utils import cleanId

# RR: why can't I pull this from another module as it used to be possible?

import json
from collections import defaultdict

from AccessControl.SecurityManagement import newSecurityManager
from Testing import makerequest

from zope.component.hooks import setSite


def getSite(app, site_id, admin_id='admin'):
    app = makerequest.makerequest(app)
    admin = app.acl_users.getUser(admin_id)  # RR: should we have a dedicated sync admin?
    admin = admin.__of__(app.acl_users)
    newSecurityManager(None, admin)

    site = app.get(site_id, None)

    if site is None:
        print "'%s' not found (maybe a typo?)." % site_id
        print "To create a site call 'import_structure' first."
        raise ValueError

    setSite(site)  # enable lookup of local components

    return site
    

def getData(path, model=None):
    source = open(path,'r')
    raw = json.load(source)
    rct_data = defaultdict(dict)

    # cast the raw data into some nested structure for easy access later
    for item in raw:
        rct_data[item['model']][item['pk']] = item.copy()
    if not model:
        return rct_data.copy()
    else:
        return rct_data[model].copy()

# end of what should be the 'utils.py' module :-(


site = getSite(app, site_id)
targetfolder = site.projects
rct_projects = getData(FILE_NAME, 'rct.project')

def prepareid(values):
    id = values['fields']['name'].encode('utf8')
    id = id.replace(' ','')
    return cleanId(id)

def preparedata(values):

    fields = values['fields'].copy()
    
    data = {}
    additional = []
    additional.append({'key': 'contact',
                       'value': str(fields['contact']),
                       },
                      )
    additional.append({'key': 'community',
                       'value': str(fields['community']),
                       },
                      )
    additional.append({'key': 'rct_pk',
                       'value': str(values['pk']),
                       },
                      )

    rct_uid = fields['uuid']
    identifiers = [{'type':'rct_uid',
                    'value': rct_uid},
                    ]

    data['title'] = fields['name']
    data['description'] = fields['description']
    data['website'] = fields['website']
    data['identifiers'] = identifiers
    data['additional'] = additional
    
    return data.copy()


for pk, values in rct_projects.items():
    id = prepareid(values)
    if id is None:
        print "Couldn't generate id for ", line
        continue
    if id not in targetfolder.objectIds():
        targetfolder.invokeFactory('Project', id)
        print "Added %s to the projects folder" % id

    data = preparedata(values)
    print data
    targetfolder[id].edit(**data)
    targetfolder[id].reindexObject()
    print "Updated %s in the projects folder" % id

import transaction
transaction.commit()

print "Done"

#
# sync_rct_communities.py
#
# simple script to be invoked via
#
#  cd <your-buildout-root-dir>
#  bin/instance run scripts/sync_rct_communities.py
#
#  reads source information from data/rct_dump_20150609.json
#  
#  The SITE_ID is hard coded as 'pcp'


import json
from collections import defaultdict


FILE_NAME = 'data/rct_dump_20150609.json'

from StringIO import StringIO

from AccessControl.SecurityManagement import newSecurityManager
from Testing import makerequest

from zope.component.hooks import setSite
SITE_ID = site_id = 'pcp'

from Products.PlonePAS.utils import cleanId

# allow for command line override of SITE_ID
#import sys
#try:
#    site_id = sys.argv[1]
#except IndexError:
#    site_id = SITE_ID

app = makerequest.makerequest(app)

admin = app.acl_users.getUser('admin')  # RR: should we have a dedicated sync admin?
admin = admin.__of__(app.acl_users)
newSecurityManager(None, admin)


site = app.get(site_id, None)

if site is None:
    print "'%s' not found (maybe a typo?)." % site_id
    print "To create a site call 'import_structure' first."
    raise ValueError

setSite(site)  # enable lookup of local components

targetfolder = site.communities

source = open(FILE_NAME,'r')
raw = json.load(source)
rct_data = defaultdict(dict)

# cast the raw data into some nested structure for easy access later
for item in raw:
    rct_data[item['model']][item['pk']] = item.copy()

rct_communities = rct_data['rct.community'].copy()


def preparedata(values):

    fields = values['fields'].copy()
    
    data = {}
    additional = []
    additional.append({'key': 'representative',
                       'value': str(fields['representative']),
                       },
                      )
    additional.append({'key': 'admins',
                       'value': str(fields['admins']),
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
    data['identifiers'] = identifiers
    data['additional'] = additional
    
    return data.copy()

def normalize(id):
    return cleanId(id) 

def prepareid(values):
    id = values['fields']['name'].encode('utf8')
    id = id.replace(' ','')
    return normalize(id)
    
for pk, values in rct_communities.items():

    id = prepareid(values)
    if id is None:
        print "Couldn't generate id for ", line
        continue
    if id not in targetfolder.objectIds():
        targetfolder.invokeFactory('Community', id)
        print "Added %s to the communities folder" % id

    data = preparedata(values)
    print data
    targetfolder[id].edit(**data)
    targetfolder[id].reindexObject()
    print "Updated %s in the communities folder" % id


import transaction
transaction.commit()

print "Done"



#
# sync_rct_people.py
#
# simple script to be invoked via
#
#  cd <your-buildout-root-dir>
#  bin/instance run scripts/sync_rct_people.py [site_id]
#
#  reads source information from data/rct_dump_20150609.json
#  
#  The SITE_ID is set to 'pcp' unless
#  a first command line argument is provided.

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

targetfolder = site.people

source = open(FILE_NAME,'r')
raw = json.load(source)
rct_data = defaultdict(dict)

# cast the raw data into some nested structure for easy access later
for item in raw:
    rct_data[item['model']][item['pk']] = item.copy()

rct_people = rct_data['rct.contactdata'].copy()


def preparedata(values):

    fields = values['fields'].copy()
    
    data = {}
    name = {}
    phone = []
    identifiers = []
    additional = []

    name['firstnames'] = fields['first_name']
    name['lastname'] = fields['last_name']
    title = ' '.join([name['firstnames'], name['lastname']])

    phonenumber = fields['phone']
    if phonenumber:
        value = {}
        value['type'] = 'Office'
        value['number'] = phonenumber
        phone.append(value.copy())

    rct_uid = fields['uuid']
    identifiers = [{'type':'rct_uid',
                    'value': rct_uid},
                    ]

    additional.append({'key':'rct_user_id',
                       'value':fields['rct_user']}
                       )
    additional.append({'key':'website',
                       'value':fields['website']}
                       )
    additional.append({'key':'address',
                       'value':fields['address']}
                       )
    additional.append({'key':'organization',
                       'value':fields['organization']}
                       )
    additional.append({'key': 'rct_pk',
                       'value': str(values['pk']),
                       },
                      )

    data['name'] = name.copy()
    data['title'] = title
    if phone:
        data['phone'] = phone
    data['email'] = fields['email']
    data['identifiers'] = identifiers
    data['additional'] = additional
    
    return data.copy()

def normalize(id):
    return cleanId(id) 

def prepareid(values):
    ln = values['fields']['last_name'].encode('utf8')
    fn = values['fields']['first_name'].encode('utf8')
    id = "%s-%s" % (fn,ln)
    id = id.replace(' ','')
    if id == '-':
        return None
    return normalize(id)
    
for pk, values in rct_people.items():

    id = prepareid(values)
    if id is None:
        print "Couldn't generate id for ", line
        continue
    if id not in targetfolder.objectIds():
        targetfolder.invokeFactory('Person', id)
        print "Added %s to the people folder." % id
        
    data = preparedata(values)
    print data
    targetfolder[id].edit(**data)
    targetfolder[id].reindexObject()
    print "Updated %s in the people folder." % id


import transaction
transaction.commit()

print "Done"



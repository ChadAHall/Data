# Import needed libraries
import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json
from collections import defaultdict, Counter


### Independent lists and containers used in this script:

# Container use to hold expected street names
expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place",
            "Square", "Lane", "Road", "Trail", "Parkway", "Commons", "Way",
            "Hall", "Circle", "Bend", "Boggy", "Cave", "Clark", "Cove", "Dunes",
             "Highway", "Hollow", "Island", "Lake", "Loop", "Park", "Pass",
             "Parth", "Race", "Ridge", "Row", "Royale", "Run", "SB", "Terrace",
             "Turn", "Voyageurs", "Path"]

# Container to street name mapping info for auditing
mapping = { "Ct": "Court",
            "Cv": "Cove",
            "Dr.": "Drive",
            "Ln": "Lane",
            "Rd": "Road",
            "street": "Street"
            }

# Container to hold created info set
CREATED = ['version', 'changeset', 'timestamp', 'user', 'uid']

# Container to hold position lat and lon
POSITION = ['lat', 'lon']

### Regular Expressions:


# Contains only lowercase
lower = re.compile(r'^([a-z]|_)*$')

# Contains colon and lowercase
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')

# Contains problematic characters
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

# Contains tiger:
tigerfind = re.compile(r'^tiger:')

# Regular expression to check for street names
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

#Check for address in tag
address_ = re.compile(r'^addr\:')

#Check for colon in tag
colom_ = re.compile(r'\:')



# Assign osmfile to map file

#osmfile = 'oncrknew.osm'

# Count tags in osmfile, argument = osmfile
def count_tags(filename):
    tag_count = {} # Assign empty dictionary for counting tags
    for event, child in ET.iterparse(filename):
        if child.tag not in tag_count:
            tag_count[child.tag] = 1 # add new tags to dict
        if child.tag in tag_count:
            tag_count[child.tag] += 1 # add to count if tag in dict
        return tag_count

# Count attributes in osmfile, argument = osmfile
def count_att(filename):
    attributes = {} # Assign empty dict for counting attributes
    for event, elem in ET.iterparse(filename, events = ('start', 'end')):
        if event == 'end':
            for attr in elem.attrib:
                if attr not in attributes:
                    attributes[attr] = 1
                else:
                    attributes[attr] += 1
    return attributes

# Count unique users, argument = osmfile
def count_unique_users(filename):
    users = set() # Assign empty set for unique user count
    for _, element in ET.iterparse(filename):
        if 'uid' in element.attrib:
            users.add(element.attrib['uid'])
            # Unique entries will be added to the set
    return len(users)

# Count K tags, argument = osmfile
def k_count(filename):
    keys = {} #assign empty dict for counting k tags
    for event, elem in ET.iterparse(filename, events = ('start', 'end')):
        if event == 'end':
            key = elem.attrib.get('k')
            if key:
                # For new keys, add key to dict, or add for existing
                if key not in keys:
                    keys[key] = 1
                else:
                    keys[key] += 1
    return keys

# Function to count and return regular expression problem characters
# Arguments auto filled from prob_char function
def key_type(element, keys):
    if element.tag == "tag":
        m = lower.search(element.attrib['k'])
        q = lower_colon.search(element.attrib['k'])
        w = problemchars.search(element.attrib['k'])
        z = tigerfind.search(element.attrib['k'])
        if m:
            keys['lower'] += 1
        elif q:
            keys['lower_colon'] += 1
        elif w:
            keys['problemchars'] += 1
        elif z:
            keys['tiger'] += 1
        else:
            keys['other'] += 1
        pass

    return keys

# Count the problem characters, argument = osmfile
def prob_char(filename):
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0,
            "tiger": 0}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)

    return keys


# Checks if street name is in expected container
def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)

# Checks for street name
def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

# Checks for steet type
def audit_street_names(osmfile):
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osmfile, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    return street_types

# Updates using the mapping container
def update_name(name, mapping):
    words = name.split()
    for w in range(len(words)):
        if words[w] in mapping:
            words[w] = mapping[words[w]]
            name =" ".join(words)
    return name

# Counts the phone numbers
def count_phones(filename):
    count_number = 0
    for _, element in ET.iterparse(filename, ('start', 'end')):
        if  element.tag == "tag":
            if element.attrib['k'] == 'phone':
                count_number += 1
    return count_number

# Prints the phone numbers
def print_phones(filename):
    lst_phones = []
    for _, element in ET.iterparse(filename, ('start', 'end')):
        if  element.tag == "tag":
            if element.attrib['k'] == 'phone':
                lst_phones.append(element.attrib['v'])
    return lst_phones

# Reformats the phone numbers
def phone_format(phone_number):
    clean_phone_number = re.sub('[^0-9]+', '', phone_number)
    formatted_phone_number = re.sub('(\d)(?=(\d{3})+(?!\d))', r'\1-', '%d' % int(clean_phone_number[:-1])) + clean_phone_number[-1]
    return formatted_phone_number

# This function will parse the xml data to JSON, while doing the data auditing
def shape_element(element): #this function will parse the xml data to JSON, while doing the data auditing
    node = {}
    address = {}
    if element.tag == 'node' or element.tag == 'way':
        #add type
        node['type'] = element.tag
        #add created and others
        for attrbt in element.attrib:
            if attrbt in CREATED:
                if 'created' not in node:
                    node['created'] = {}
                node['created'][attrbt] = element.attrib[attrbt]
            elif attrbt in POSITION:
                continue
            else:
                node[attrbt] = element.attrib[attrbt]

        #put lat and lon into the pos container
        if 'lat' in element.attrib and 'lon' in element.attrib:
            node['pos'] = [float(element.get('lat')), float(element.get('lon'))]

        #look at the secondary tag
        for tag_2nd in element:
            #add node refs
            if tag_2nd.tag == 'nd':
                if 'node_refs' not in node:
                    node['node_refs'] = []
                if 'ref' in tag_2nd.attrib:
                    node['node_refs'].append(tag_2nd.get('ref'))

            #ensure tag key and value are valid
            if tag_2nd.tag != 'tag' or 'k' not in tag_2nd.attrib or 'v' not in tag_2nd.attrib:
                continue
            key = tag_2nd.get('k')
            val = tag_2nd.get('v')
            if problemchars.search(key):
                continue #skip elements that come up in search
            elif tigerfind.search(key):
                continue #skip elements that come up in search
            elif address_.search(key):
                key = key.replace('addr:', '') #replace name
                if not colom_.search(key): #search again for second colon:
                    address[key] = val
            elif [key] == 'phone':
                val == phone_format(val)
            else:
                node[key] = val

        #look for address
        if len(address) > 0:
            node['address'] = address
            #update street name
            if 'street' in node['address']:
                node['address']['street'] = update_name(node['address']['street'], mapping)
                #format the address, with the updated mappings
        return node
    else:
        return None

 # Function to produce JSON file as output, provided by Udacity
def process_map(filename, pretty = False): #function to produce the JSON file as output
    file_out = '{0}.json'.format(filename)
    data = []
    with codecs.open(file_out, 'w') as fo:
        for _, element in ET.iterparse(filename):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent = 2)+'\n')
                else:
                    fo.write(json.dumps(el) + '\n')
    return data

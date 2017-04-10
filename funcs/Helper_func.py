street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons","Way", "Circle", "Key","Terrace", "Garden"]

# UPDATE THIS VARIABLE
mapping = { "St": "Street",
            "St.": "Street",
            "Ave": "Avenue",
            "Ave.":"Avenue",
            "Rd.": "Road",
            "BLVD": "Boulevard",
            "Dr.": "Drive",
            "PL": "Place",
            "Pl": "Place",
            "Ln":"Lane",
            "Ct": "Court",
            "Blvd": "Boulevard",
            "Cir": "Circle",
            "Dr": "Drive"
           
            }

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema.schema

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""
    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k : v for k, v in row.items()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


def update_name(name, mapping):
    street=street_type_re.search(name).group()

    name=name.replace(street, mapping[street])

    return name


#clean_element function take tag['value'] and tag['key'] as input and return the updated tag values 
def clean_element(tag_value, tag_key):
    
    ## clean postcode 
    if tag_key=='postcode':
        if (tag_value[0:2]!='94' and tag_value[0:2]!='95') or (len(tag_value)!=5):
            ## find postcode start with 'CA' and remove the 'CA' 
            if tag_value[0:2]=='CA': 
                    tag_value=tag_value[-5:]
     
                    #print (tag_value)
                            
            ##  find cases that using full address as postcode and extract the postcode using re module
            else:
                if len(tag_value)>10:
                    #print(tag.attrib['v'])
                    pc=re.search('\d{5}', tag_value)
                    if pc:
                        tag_value=pc.group()
              
    ## clean state name, use uniformat 'CA'       
    elif tag_key=='state':
        if tag_value=='Ca' or tag_value=='ca' or tag_value=='California':
            tag_value='CA'
        
    ## clean street suffix, change abbrivations to full street suffix        
    elif tag_key=='street':
        street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
        full_addr=tag_value
        m = street_type_re.search(full_addr)
        if m:
            street_type = m.group() #group(): Return the string matched by the RE
            if street_type not in expected:
                if street_type in mapping:
                    tag_value=update_name(full_addr, mapping) # call update_name function 
    ## return updated tag_value
    return tag_value
                             
## Clean and shape node or way XML element to Python dict

def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
   
    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements
   
    ## clean node element
    if element.tag=='node':
        for primary in element.iter():
            for i in node_attr_fields: 
                if i in primary.attrib: 
                    node_attribs[i]=primary.attrib[i]
        if len(element)!=0:
            for j in range(0, len(element)): 
                childelem=element[j]
                tag={}
                if not problem_chars.search(childelem.attrib['k']): ## ignor problematic element
                    tag["id"]=element.attrib["id"]
                    tag["type"]=default_tag_type
                    tag['value']=childelem.attrib['v']
                    if ":" in childelem.attrib['k']:
                        k_and_v=childelem.attrib['k'].split(':',1)
                        tag["type"]=k_and_v[0]
                        tag["key"]=k_and_v[1]
                        if tag["type"]=='addr':
                            tag["value"]=clean_element(tag["value"],tag["key"]) ## call clean_element function
                    else:
                        tag["key"]=childelem.attrib['k']
                        if tag["type"]=='addr':
                            print(tag_value, tag["key"])
                            tag["value"]=clean_element(tag["value"],tag["key"])
                tags.append(tag)
                
        return ({'node': node_attribs, 'node_tags': tags})            
                    
    ## handle way element               
    elif element.tag=='way':
        for primary in element.iter():
            for i in way_attr_fields: 
                if i in primary.attrib: 
                    way_attribs[i]=primary.attrib[i]   
        
        if len(element)!=0: 
            for j in range(0, len(element)): 
                childelem=element[j]
                tag={}
                if childelem.tag=='tag':
                    if not problem_chars.search(childelem.attrib['k']):
                        tag["id"]=element.attrib["id"]
                        tag["type"]=default_tag_type
                        tag["value"]=childelem.attrib['v']
                        if ":" in childelem.attrib['k']:
                            k_and_v=childelem.attrib['k'].split(':',1)
                            tag["key"]=k_and_v[1]
                            tag["type"]=k_and_v[0]
                            if tag["type"]=='addr':
                                tag["value"]=clean_element(tag["value"],tag["key"]) #call clean_element function
                        else:
                            tag["key"]=childelem.attrib['k']
                            if tag["type"]=='addr':
                                tag["value"]=clean_element(tag["value"],tag["key"]) #update tag values
                    tags.append(tag)
                    
                elif childelem.tag=='nd':
                    #print (childelem.attrib['ref'])
                    way_node={}
                    way_node['id']=element.attrib['id'] 
                    way_node['node_id']=childelem.attrib['ref']
                    way_node['position']=j
                    #print(way_node)
                    way_nodes.append(way_node)
                    
        return ({'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags})
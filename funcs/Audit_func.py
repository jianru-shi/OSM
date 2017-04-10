# audit_address function audits the data from the open street map and try to find problems associated with addresses
# the argument 'content' can take 'postcode', 'street','state', 'city' or 'county'.
def audit_address(filename, content):
        key='addr:'+ content
        expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons","Way", "Circle", "Key","Terrace", "Garden"]
    
# When the content is 'postcode', the function audits the validity of the postcode
# For CA, the postcode starts with 94 or 95. 
# To make the data consistent, I use 5 digitals postcode format

        if content=='postcode':
            i=0   #set a records tracker 
            for event, elem in ET.iterparse(filename, events=("start",)):
                i+=1
                if elem.tag == "node" or elem.tag == "way":
                    for tag in elem.iter("tag"):
                        if tag.attrib['k']== key:
                            if (tag.attrib['v'][0:2]!='94' and tag.attrib['v'][0:2]!='95') or (len(tag.attrib['v'])!=5): 
                                print(i)
                                print (tag.attrib['v'])

# When the content is 'street', the function audits the validity of the street name
# It returns a dictionary with street types as keys and corresponding counts as values. 

        elif content=='street':
            
            street_types = {}
            street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
            for event, elem in ET.iterparse(filename, events=("start",)):
                if elem.tag == "node" or elem.tag == "way":
                    for tag in elem.iter("tag"):
                        if tag.attrib['k']== key:
                            m = street_type_re.search(tag.attrib['v'])
                            if m:
                                street_type = m.group() #group(): Return the string matched by the RE
                                if street_type not in expected:
                                    street_types[street_type]=street_types.get(street_type,0)+1
            print (street_types)
                                
                            
                    
                                
# When the content is state, city, or county, the function audits the validity of data
# by returning a dictionary which give information of the values and counts of corresponding content
        
        else:
            values_dict={}
            key='addr:'+ content
            for event, elem in ET.iterparse(filename, events=("start",)):
                if elem.tag == "node" or elem.tag == "way":
                    for tag in elem.iter("tag"):
                        if tag.attrib['k']== key:
                            values_dict[tag.attrib['v']]=values_dict.get(tag.attrib['v'],0)+1
            print(values_dict)
            
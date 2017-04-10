# take samples from original osm file

OSM_FILE = "SFBay.osm" 
SAMPLE_FILE = "sample.osm" # small subset about  3M
TEST_FILE="test.osm" #intermediate subset about 300M 


def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag

    Reference:
    http://stackoverflow.com/questions/3095434/inserting-newlines-in-xml-file-generated-via-xml-etree-elementtree-in-python
    """
    context = iter(ET.iterparse(osm_file, events=('start', 'end')))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()         
            
## define function that take small and median size samples from full data file
def sample_data (full, small, median): 
    
    k = 1000 # Parameter: take every k-th top level element, take small sample
    m = 10 # take intermediate sample  
    with open(small, 'w') as output1, open(median,'w') as output2:
        output1.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        output1.write('<osm>\n  ')
        output2.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        output2.write('<osm>\n  ')
    # Write every kth top level element
        for i, element in enumerate(get_element(full)):
            if i % k == 0:
                output1.write(str(ET.tostring(element, encoding='utf-8')))
                output2.write(str(ET.tostring(element, encoding='utf-8')))
            elif i % m == 0:
                output2.write(str(ET.tostring(element, encoding='utf-8')))
        output1.write('</osm>')
        output2.write('</osm>')
        
sample_data(OSM_FILE, SAMPLE_FILE,TEST_FILE)
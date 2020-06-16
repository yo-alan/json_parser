import json
import re
import urllib.request


INDEXED_PROPERTY_PATTERN = r"(.+)\[([0-9]+)\]$"
DOT_SEPARATED_PROPERTIES_PATTERN = r".+\..*"


def get_json_files(url):
    """Returns a list of json strings found in the specified git folder as url."""
    
    r = urllib.request.Request(url)
    
    try:
        with urllib.request.urlopen(r) as git_folder:
            git_folder_content = git_folder.read().decode('utf-8')
    except urllib.error.URLError:
        raise Exception("Could not open git folder.")
    
    json_files = re.findall(">(attack\-pattern\-\-.+\.json)", git_folder_content)
    
    json_strings = []
    
    while json_files:
        
        jf = json_files.pop(0)
        
        print(f"Fetching: {jf}... Left: {len(json_files)}", end="\r")
        
        #We are going to try obtain the content of the json file if it
        #fails we try one more time... but only one
        for i in range(2):
            try:
                with urllib.request.urlopen(url + jf) as json_file:
                    json_strings.append(json_file.read().decode('utf-8'))
                    print(f"Fetching: {jf}... Done.                    ")
                    break
            
            except urllib.error.URLError:
                print()
                print(f"Fail fetching {jf}")
                print(f"Trying one more time..." if i == 0 else f"Skipping...")
        
    
    return json_strings


def get_index_name(json_obj, index):
    """Obtains the name of the key index in the json object."""
    
    return list(json_obj.keys())[index]


def split_with_index(p):
    """Splits the name of the property from the index found in p."""
    
    res = re.match(INDEXED_PROPERTY_PATTERN, p)

    g1, g2 = res.groups()
    
    return g1, g2
    

def split_property(p):
    """Obtains the first dot separated property from p and returns it
    along with the rest."""
    
    properties_list = p.split('.')
    
    head_property = properties_list.pop(0)
    
    tail_properties = '.'.join(properties_list)
    
    return [head_property, tail_properties]


def get(json_obj, prop):
    """Returns the value of the property found in the json object, None
    otherwise."""
    
    if isinstance(json_obj, dict) and prop in json_obj:
        return json_obj[prop]
    else:
        
        if re.match(DOT_SEPARATED_PROPERTIES_PATTERN, prop):
            
            pre_prop, new_prop = split_property(prop)
            
            if re.match(INDEXED_PROPERTY_PATTERN, pre_prop):
                
                g1, g2 = split_with_index(pre_prop)
                
                json_obj = json_obj[g1]
                
                if isinstance(json_obj, list):
                    json_obj = json_obj[int(g2)]
                
                elif isinstance(json_obj, dict):
                    new_prop = get_index_name(json_obj, int(g2)) + '.' + new_prop
                
            else:
                json_obj = json_obj[pre_prop]
        
        elif re.match(INDEXED_PROPERTY_PATTERN, prop):
            
            g1, g2 = split_with_index(prop)
            
            json_obj = json_obj[g1]
            
            if isinstance(json_obj, list):
                return json_obj[int(g2)]
            
            if isinstance(json_obj, dict):
                new_prop = get_index_name(json_obj, int(g2))
            
        else:
            return
        
        return get(json_obj, new_prop)


def parse_json(json_text, list_of_properties):
    """Returns, if found, the properties passed has param with its
    corresponding value on the json."""
    
    found_properties = {}
    
    json_object = json.loads(json_text)
    
    for p in list_of_properties:
        
        val = get(json_object, p)
        
        if val is not None:
            found_properties[p] = val
    
    return found_properties

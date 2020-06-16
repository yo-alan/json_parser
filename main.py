import json_parser as jp


def main():
    
    url = 'https://github.com/mitre/cti/raw/master/enterprise-attack/attack-pattern/'
    
    fields = [
        "id",
        "objects[0].name",
        "objects[0].kill_chain_phases"
    ]
    
    for f in jp.get_json_files(url):
        print(jp.parse_json(f, fields))
    
    return 0


if __name__ == '__main__':
    exit(main())

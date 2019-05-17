# import packages
import glob
import csv
import re
import xml.etree.ElementTree as ET
from copy import copy
from datetime import datetime
import tarfile
import sys

# set folder paths
INPUT = '/xx/_test/xml'
OUTPUT = '/xx/_test/csv'

# convert xml file to dictionary
def dictify(r, root=True):
    # credits to https://stackoverflow.com/a/30923963
    if root:
        return {r.tag : dictify(r, False)}
    d = copy(r.attrib)
    if r.text:
        d["_text"] = r.text
    for x in r.findall("./*"):
        if x.tag not in d:
            d[x.tag]=[]
        d[x.tag].append(dictify(x, False))
    return d


def parsing(xml_file, xml_filename):
    
    # defining output file name
    file_pattern = r'(DSTORE[A-Za-z0-9_-]+)\.[xmlXML]{3}'
    file_name = re.search(file_pattern, xml_filename).group(1)
    export = OUTPUT + '/' + file_name + '.csv'

    # convert to dict
    df = dictify(ET.parse(xml_file).getroot())
    
    # check if E1BPRETAILLINEITEM exists 
    check = list(df['POSDW']['E1POSTR_CREATEMULTIP'][0].keys())
    
    if 'E1BPRETAILLINEITEM' in check:
        lineitem = df['POSDW']['E1POSTR_CREATEMULTIP'][0]['E1BPRETAILLINEITEM']
        #transaction = df['POSDW']['E1POSTR_CREATEMULTIP'][0]['E1BPTRANSACTION']
        #lineitemtax = df['POSDW']['E1POSTR_CREATEMULTIP'][0]['E1BPLINEITEMTAX']
        #tender = df['POSDW']['E1POSTR_CREATEMULTIP'][0]['E1BPTENDER']
        
        first = True
        with open(export, 'w') as f:
            writer = csv.writer(f)
            for e in lineitem:
                data = {}
                for ee in e:
                    if ee != '_text':
                        try:
                            value = e[ee][0]['_text']
                        except:
                            value = None
                        data[ee] = value
                if first:
                    header = tuple(data.keys())
                    writer.writerow(header)
                row = tuple(data.values())
                writer.writerow(row)
                first = False

                
def main():
    
    # check Python version    
    if sys.version_info < (3, 0):
        sys.stdout.write("Sorry, requires Python 3.x, not Python 2.x\n")
        sys.exit(1)
    
    # localize input files
    xml_files = glob.glob('{}/**/*.XML'.format(INPUT), recursive=True) + glob.glob('{}/**/*.xml'.format(INPUT), recursive=True)
    tar_files = glob.glob('{}/**/*.TAR.GZ'.format(INPUT), recursive=True) + glob.glob('{}/**/*.tar.gz'.format(INPUT), recursive=True)
    
    print('Starting to parse XML files ...')
    print(datetime.now())

    # check if files are compressed or need to be extracted
    if len(xml_files) > 0:
        for f in xml_files:
            parsing(f, f)
    elif len(tar_files) > 0:
        for t in tar_files:
            tar = tarfile.open(t, "r:gz")
            for member in tar.getmembers():
                f = tar.extractfile(member)
                parsing(f, member.name)
    else:
        print("Warning: Couldn't find any XML or TAR files.")

    print()
    print(datetime.now())
    print('Done.')
    
    
if __name__ == '__main__':
    main()

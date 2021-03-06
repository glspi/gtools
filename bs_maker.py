import argparse
import os
import sys
import xml.dom.minidom

import ipcalc
from azure.storage.fileshare import ShareClient
from flask import Markup

import xmltodict
from jinja2 import Template


def create_xml_files(temp, filename):

    #Set data
    blah = {'root':temp}
    data = xmltodict.unparse(blah)
    data = data.replace('<?xml version="1.0" encoding="utf-8"?>', "")
    prettyxml = xml.dom.minidom.parseString(data).toprettyxml()

    with open(filename, "w") as fout:
        fout.write(temp)
    
    return None


def create_lb_bootstrap(templatefile1, templatefile2, **kwargs):

    # Create Bootstrap File
    with open(templatefile1) as fin:
        template1 = Template(fin.read())
    with open(templatefile2) as fin:
        template2 = Template(fin.read())

    # Web VM will be the 4th IP available on this subnet
    subnet = ipcalc.Network(kwargs["web_subnet"])
    kwargs["web_server_private"] = subnet.host_first() + 3

    bootstrap1 = template1.render(**kwargs)
    create_xml_files(bootstrap1, 'auto-bootstrap1.xml')

    bootstrap2 = template2.render(**kwargs)
    create_xml_files(bootstrap2, 'auto-bootstrap2.xml')

    # Begin Azure 
    AZURE_STORAGE_ACCOUNT_NAME = kwargs['storage_account_name']
    AZURE_STORAGE_ACCESS_KEY = kwargs['storage_access_key']
    AZURE_STORAGE_CONNECTION_STRING = f"DefaultEndpointsProtocol=https;AccountName={AZURE_STORAGE_ACCOUNT_NAME};AccountKey={AZURE_STORAGE_ACCESS_KEY};EndpointSuffix=core.windows.net"
    fullpath = kwargs['storage_folder_name']

    share = ShareClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING, "bootstrap")
    
    index = fullpath.rfind("/")
    if index == -1:
        index = fullpath.rfind("\\")
        if index == -1:
            folder = fullpath
            parentfolder = False
    else:
        parentfolder = fullpath[:index]
        folder = fullpath[index:].strip("/\\") # Remove leading / or \
        try:
            temp = share.get_directory_client(parentfolder)
            temp.get_directory_properties()
        except:
            share.create_directory(parentfolder)

    if not parentfolder:
        folderpath = folder
    else:
        folderpath = parentfolder + '/' + folder

    try:
        temp = share.get_directory_client(folderpath)
        temp.get_directory_properties()
    except:

        share.create_directory(folderpath)

    try:
        share.create_directory(f"{fullpath}/fw1")
        share.create_directory(f"{fullpath}/fw2")

        share.create_directory(f"{fullpath}/fw1/config")
        share.create_directory(f"{fullpath}/fw1/content")
        share.create_directory(f"{fullpath}/fw1/license")
        share.create_directory(f"{fullpath}/fw1/software")

        share.create_directory(f"{fullpath}/fw2/config")
        share.create_directory(f"{fullpath}/fw2/content")
        share.create_directory(f"{fullpath}/fw2/license")
        share.create_directory(f"{fullpath}/fw2/software")

    except Exception as e:
        return f"Error: {e}", "danger"

    # Create destination file names
    az_bootstrap_str1 = f"{fullpath}/fw1/config/bootstrap.xml"
    az_initcfg_str1 = f"{fullpath}/fw1/config/init-cfg.txt"
    az_bootstrap_str2 = f"{fullpath}/fw2/config/bootstrap.xml"
    az_initcfg_str2 = f"{fullpath}/fw2/config/init-cfg.txt"

    az_bootstrap1 = share.get_file_client(az_bootstrap_str1)
    az_init_cfg1 = share.get_file_client(az_initcfg_str1)
    az_bootstrap2 = share.get_file_client(az_bootstrap_str2)
    az_init_cfg2 = share.get_file_client(az_initcfg_str2)

    # [START upload_files]
    with open('auto-bootstrap1.xml', "rb") as source:
        az_bootstrap1.upload_file(source)
    with open('auto-bootstrap2.xml', "rb") as source:
        az_bootstrap2.upload_file(source)

    with open('static/init-cfg.txt', "rb") as source:
        az_init_cfg1.upload_file(source)
    with open('static/init-cfg.txt', "rb") as source:
        az_init_cfg2.upload_file(source)

    # [END upload_file]

    msg = Markup(
        f""\
        f"Bootstrap created. File uploaded to '{kwargs['storage_folder_name']}/config/fwX/bootstrap.xml'"\
        f"<br>"\
        f"To begin Azure deployment, Click Below. <a href='https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fcnetpalopublic.blob.core.windows.net%2Farm-public%2Fgenlb-sub.json'>"\
        f"<br> <img src='https://aka.ms/deploytoazurebutton'>"\
        f"</a>"\
        f"<br>"\
        f"To deploy without the subscriber vnet created, <a href='https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fcnetpalopublic.blob.core.windows.net%2Farm-public%2Fgenlb.json'>"\
        f"Click Here.</a>"\
    )
    return msg, "success"


def create_bootstrap(templatefile1, **kwargs):
    return None

# If run from the command line
if __name__ == "__main__":
    # Check arguments, if 'xml' then don't need the rest of the input
    #argrequired = '--xml' not in sys.argv and '-x' not in sys.argv
    parser = argparse.ArgumentParser(description="Please use this syntax:")
    parser.add_argument("-x", "--xml", help="Optional XML Filename", type=str, required=True)
    # parser.add_argument("-u", "--username", help="Username", type=str, required=argrequired)
    # parser.add_argument("-i", "--ipaddress", help="IP or FQDN of PA/Panorama", type=str, required=argrequired)
    args = parser.parse_args()

    filename = args.xml

    # Run program
    print("\nThank you...\n")
    create_bootstrap(filename)
    print("\nGood bye.\n")
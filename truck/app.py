
import os
import glob
import json
import requests
from bs4 import BeautifulSoup
from natsort import natsorted

from modules.decode_email import decodeEmail
from modules.request import get_total_page, get_urls
from modules.create_excel import create_excel

__location__ = os.path.join(os.path.dirname(__file__))
url = 'https://www.teralogistics.com/wp-admin/admin-ajax.php?action=utruckings&p={}&ob=rate&n=&c=&pr=&type=&class='

def get_trucks(tid):
    url_truck = 'https://www.teralogistics.com/wp-admin/admin-ajax.php?action=mytruckings&tid={}'.format(tid)
    
    res_json = requests.get(url_truck)
    data = res_json.json()

    return data['items']

def get_details(url, i):
    print('getting details {}... {}'.format(i, url))

    file_name = i+'-'+url.split('/')[len(url.split('/')) - 2]

    # get html from url
    res = requests.get(url)

    # save page as html
    f = open(os.path.join(__location__, 'detail_html/' + file_name + '.html'), 'w+')
    f.write(res.text)
    f.close()

    # parse respose use this if no local file
    # soup = BeautifulSoup(res.text, 'html.parser')

    # load html from local
    soup = BeautifulSoup(open(os.path.join(__location__, 'detail_html/' + file_name + '.html')), 'html5lib')

    company_name = soup.find('div', {'class': 'profile-head'}).find('h2').text.strip()
    content_profile = soup.find('div', {'class': 'content'}).find('p').text.strip()
    # ada detail yg gak ada imagenya
    # images = soup.find('div', {'class': 'box-gallery'}).find('div', {'class': 'row'}).findAll('div', {'class': 'col-sm-4'})
    company_info = soup.find(attrs={'class': 'company-info'}).find('dl').findAll('dd')
    offices = soup.findAll(attrs={'class': 'office'})
    
    all_images = ''
    # for image in images:
    #     imageUrl = image.find(attrs={'class': 'img'})['href']
    #     path = 'images/forwarder/' +basename(imageUrl)
    #     all_images += path + ','

    #     with open('./' + path, 'wb') as f:
    #         f.write(requests.get(imageUrl).content)    

    year_found = ''
    company_size = ''
    if len(company_info) > 0: 
        year_found = company_info[0].text.strip()

    if len(company_info) > 1: 
        company_size = company_info[1].text.strip()

    # Head office data
    head_office_address = ''
    office_contact = []
    branchs = []
    head_office_phone = ''
    head_office_fax = ''
    head_office_email = ''
    head_office_url = ''
    if len(offices) > 0:
        head_office_address = offices[0].find('p').text.strip().replace('\n', '')
        office_contact = offices[0].find('dl')

        office_contacts_key = office_contact.findAll('dt')
        office_contact_value = office_contact.findAll('dd')

        for key, val in zip(office_contacts_key, office_contact_value):
            office_contact_key = key.text.strip().replace(':', '').lower()
            email_val = val.find('a').find('span')
            contact_value = None

            if email_val is not None:
                contact_value = decodeEmail(email_val['data-cfemail'])
            else:
                contact_value = val.find('a').text.strip()
            
            if office_contact_key == 'tel':
                head_office_phone = contact_value
            elif office_contact_key == 'fax':
                head_office_fax = contact_value
            elif office_contact_key == 'email':
                head_office_email = contact_value
            elif office_contact_key == 'url':
                head_office_url = contact_value
    
    # if branch exists
    branchs = []
    branchs_dict = {}
    if len(offices) > 1:
        branchs += offices[1].findAll(attrs={'class': 'branch'})

        branch_offices = []
        branch_key = []
        for i, branch in enumerate(branchs):
            address = branch.find('p').text.strip().replace('\n', '')
            branch_contacts_key = branch.find('dl').findAll('dt')
            branch_contacts_value = branch.find('dl').findAll('dd')

            branch_contacts = ''
            j = 0
            for key, val in zip(branch_contacts_key, branch_contacts_value):
                contact_key = key.text.strip()
                email_val = val.find('a').find('span')
                contact_value = None

                if email_val is not None:
                    contact_value = decodeEmail(email_val['data-cfemail'])
                else:
                    contact_value = val.find('a').text.strip()

                branch_contacts += (contact_key + ' ' + contact_value)
                # add new line for contact row
                if (j < len(branch_contacts_key) - 1):
                    branch_contacts += '\n'
                
                j += 1
            
            new_branch = address + '\n\n' +branch_contacts
            branch_offices.append(new_branch)
            branch_key.append('branch_{}'.format(i+1))

        branchs_dict = dict(zip(branch_key, branch_offices))

    # Get truck data
    tab_content = soup.find(attrs={'class': 'tab-content'})
    forwarder_truck = tab_content.find(attrs={'id': 'forwarder-truck'})
    
    truck_dict = {}
    if forwarder_truck:
        truck_id = forwarder_truck['data-tid']
        trucks = get_trucks(truck_id)

        truck_keys = []
        truck_values = []
        for z, truck in enumerate(trucks):
            truck_keys.append('truck_{}'.format(z+1))
            truck_value = truck['display'] + '\nGVWR: ' + truck['basic']['class_html'] + '\nWeight Capacity: ' + truck['basic']['weight_html'] + '\nType: ' + truck['basic']['type_html'] + '\nTotal Unit: ' + truck['basic']['unit_html']

            truck_values.append(truck_value)
            truck_dict = dict(zip(truck_keys, truck_values))


    dict_data = {
        **{
            'company_name': company_name,
            # 'images': all_images,
            'year_found': year_found,
            'company_size': company_size,
            'head_office_address': head_office_address,
            'head_office_phone': head_office_phone,
            'head_office_fax': head_office_fax,
            'head_office_email': head_office_email,
            'head_office_url': head_office_url,
        },
        **{
            'content_profile': content_profile,
        },
        **branchs_dict,
        **truck_dict
    }
    
    # save data to json
    with open(os.path.join(__location__, 'results/{}.json'.format(file_name)), 'w+') as outfile:
        json.dump(dict_data, outfile)

    print('Done getting details {}... {}'.format(i, url))


def scrap_truck():

    total_urls = []
    total_page = get_total_page(url.format(1), __location__, 'trucks.json')

    # collect urls
    for i in range(total_page):
        page = i + 1
        url_page = url.format(page)
        urls = get_urls(url_page, page)
        total_urls += urls
    
    # save urls to json
    with open(os.path.join(__location__, 'trucks_urls.json'), 'w+') as outfile:
        json.dump(total_urls, outfile)

    # open local urls
    with open(os.path.join(__location__, 'trucks_urls.json')) as json_file:
        all_url = json.load(json_file)

    # get all detail page
    for i, url in enumerate(all_url):
        get_details(url, str(i+1))

    get_details('https://www.teralogistics.com/truck/dunex/', str(1))
    
    # collect all results
    files = natsorted(glob.glob(os.path.join(__location__, 'results/*.json')))

    return create_excel(files)
#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

''' Load necessary and sufficient python librairies that are used throughout the class'''
try:
    from numpy import isin
    import numpy as np
    from datetime import datetime, timedelta, date
    import pandas as pd
    import traceback

    print("All packages in ExtractLoadTransform loaded successfully!")

except Exception as e:
    print("Some packages didn't load\n{}".format(e))

'''
    CLASS with essential data extract, load, and transform processes specific to OTA properties:
        1) 
'''

class OTAWebScraper():

    ''' Function
            name: __init__
            parameters:

            procedure: Initialize the class
            return None

            author: nuwan.waidyanatha@rezgateway.com
    '''
    def __init__(self):
        
        self.path = "../data"
        self.file = "properties.json"

        self.scrape_start_date = date.today()
        self.scrape_end_date = self.scrape_start_date + timedelta(days=1)
        self.page_offset = 10
        self.page_upper_limit = 550
        self.checkout_offset = 1
        
        self.destination_ids = ["20079110", "20088325",
                          "20061717",
                          "20023488","20050264", "20030916", "20033173", "20135442", "20131185", "20090971", "20023181", "20014181", "20015732", "20021296"]

        return None

    ''' Function
            name: get_url_list
            parameters:
                dirPath - the relative or direct path to the file with urls
                fileName - the name of the file containing all the urls for scraping
            procedure: read the list of urls from the CSV file and compile a list
            return list (url_list)

            author: nuwan.waidyanatha@rezgateway.com
    '''
    def load_ota_list(self, dirPath:str, fileName:str):

        import os         # apply directory read functions
        import csv        # to read the csv
        import json       # to read the json file

        url_list = []     # initialize the return parameter
        property_data = {}
        
        try:

            ''' Get the list of urls from the CSV file '''        
            if dirPath:
                self.path = dirPath
            _l_files = os.listdir(self.path)
            ''' if fileName is not null check if it is in the director '''
            if fileName and fileName in _l_files:
                self.file = fileName
            else:
                raise ValueError("Invalid file name %s in dir: %s. Does not exist!" % (fileName, self.path))

            ''' read the list of urls from the file '''
            with open(self.path+"/"+self.file, newline='') as f:
                property_data = json.load(f)

        except Exception as err:
            _s_fn_id = "Class <WebScraper> Function <get_url_list>"
            print("[Error]"+_s_fn_id, err)
            print(traceback.format_exc())

        return property_data

    ''' Function
            name: get_scrape_input_params
            parameters:
                url - string comprising the url with place holders
                **kwargs - contain the plance holder key value pairs

            procedure: build the url by inserting the values from the **kwargs dict
            return string (url)
            
            author: nuwan.waidyanatha@rezgateway.com

            TODO - change the ota_scrape_tags_df to a list of dictionaries
    '''
    def get_scrape_input_params(self, property_dict:dict):
        try:
            if not property_dict:
                raise ValueError("Invalid properties dictionary")

            ''' loop through the dict to construct the scraper parameters '''
            ota_param_list = []
            _l_tag=[]
            for prop_detail in property_dict:
                param_dict = {}
                tag_dict = {}
                ''' create a dict with input params '''
                param_dict['ota'] = prop_detail
                for detail in property_dict[prop_detail]:
                    param_dict['url'] = detail['url']
                    param_dict['inputs'] = detail['inputs']
                    ''' append the input parameters into a list'''
                    ota_param_list.append(param_dict)
      
        except Exception as err:
            _s_fn_id = "Class <WebScraper> Function <get_scrape_input_params>"
            print("[Error]"+_s_fn_id, err)
            print(traceback.format_exc())

        return ota_param_list #, ota_scrape_tags_df

    ''' Function
            name: get_scrape_output_params
            parameters:
                property_dict - obtained from loading the property scraping parameters from the JSON

            procedure: loop through the loaded dictionary to retrieve the output variable names, tags, and values.
                        Then construcct and return a dataframe for all corresponding OTAs
            return dataframe (_scrape_tags_df)

            author: nuwan.waidyanatha@rezgateway.com
    '''
    def get_scrape_html_tags(self, property_dict:dict):

        _scrape_tags_df = pd.DataFrame()

        try:
            if not property_dict:
                raise ValueError("Invalid properties dictionary")

            ''' loop through the dict to construct html tags to retrieve the data elements '''
            for prop_detail in property_dict:
                for _prop_params in property_dict[prop_detail]:
                    for _out_vars in _prop_params['outputs']:
                        _out_vars['ota'] = prop_detail
                        _scrape_tags_df = pd.concat([_scrape_tags_df,\
                                                     pd.DataFrame([_out_vars.values()], columns=_out_vars.keys())],
                                                   ignore_index=False)

        except Exception as err:
            _s_fn_id = "Class <WebScraper> Function <get_scrape_output_params>"
            print("[Error]"+_s_fn_id, err)
            print(traceback.format_exc())

        return _scrape_tags_df

    ''' Function
            name: insert_params_in_url
            parameters:
                url - string comprising the url with place holders
                **kwargs - contain the plance holder key value pairs

            procedure: build the url by inserting the values from the **kwargs dict
            return string (url)

            author: nuwan.waidyanatha@rezgateway.com
    '''
    def insert_params_in_url(self, url: str, **kwargs ):

        import re

        url_w_params = None

        try:
            if not url:
                raise ValueError("Invalid url string %s" % (url))
            url_w_params = url

            ''' match the keys in dict with the placeholder string in the url''' 
            for key in kwargs.keys():
                _s_regex = r"{"+key+"}"
                urlRegex = re.compile(_s_regex, re.IGNORECASE)
                param = urlRegex.search(url_w_params)
                if param:
                    _s_repl_val = str(kwargs[key]).replace(" ","%20")
                    url_w_params = re.sub(_s_regex, _s_repl_val, url_w_params)
            
        except Exception as err:
            _s_fn_id = "Class <WebScraper> Function <insert_params_in_url>"
            print("[Error]"+_s_fn_id, err)
            print(traceback.format_exc())

        return url_w_params

    ''' Function
            name: build_scrape_url_list
            parameters:
                dirPath - path to the directory with property parameters JSON
                fileName - JSON file containing those parameters

            procedure: use the get_scrape_input_params function to load the the JSON file. 
                        Thenloop through all the OTAs to extract the input parameters
                        For each OTA template url use the insert_params_in_url function to
                        construct the list of parameterized URLs
            return: list with the set of urls (scrape_url_list)
            author: nuwan.waidyanatha@rezgateway.com

            TODO: the nested looping code to add the destination_id, checkin, checkout, page is dirty
                    Need a better method rather than nested loop because not all OTAs will consist
                    of the same input parameters
    '''
    def build_scrape_url_list(self, dirPath:str, fileName:str, **kwargs):

#        scrape_url_list = []
        _scrape_url_dict = {}
        _ota_parameterized_url_list = []

        try:
            ''' retrieve OTA input and output property data from json '''
            property_dict = self.load_ota_list(dirPath, fileName)
            if len(property_dict) <= 0:
                raise ValueError("No data found with %s with defined scrape properties"
                                 % (path+"/"+fileName))
            else:
                print("Loaded %d properties to begin scraping OTA data." % (len(property_dict)))
            ''' check and initialize **kwargs '''
            if 'pageOffset' in kwargs:
                self.page_offset = kwargs['pageOffset']
            if 'pageUpperLimit' in kwargs:
                self.page_upper_limit = kwargs['pageUpperLimit']
            if 'startDate' in kwargs:
                self.scrape_start_date = kwargs['startDate']
            else:
                print("Invalid scrape start date. Setting start date to today %s" %(str(self.scrape_start_date)))
            if 'endDate' in kwargs:
                if self.scrape_start_date < kwargs['endDate']:
                    self.scrape_end_date = kwargs['endDate']
                else:
                    self.scrape_end_date = self.scrape_start_date + timedelta(days=1)
                    print("Invalid scrape end date. Setting end date to %s %s" 
                          %(str(self.scrape_start_date),str(self.scrape_end_date)))
            if 'checkoutOffset' in kwargs:
                self.checkout_offset = kwargs['checkoutOffset']

            ''' ger the input parameters from the properties file '''
            _ota_input_param_list = self.get_scrape_input_params(property_dict)

            ''' loop through the  ota list to create the url list for each ota '''
            for ota in _ota_input_param_list:
                print("Processing %s ..." % (ota['ota']))
                _inert_param_dict = {}
                try:
                    _ota_url = None
                    if not ota['url']:
                        raise ValueError("Invalid url skip to next")

                    ''' build the dictionary to replace the values in the url place holder '''
                    for destination_id in self.destination_ids:
                        _inert_param_dict['destination_id'] = destination_id
                        if 'checkin' in ota['inputs']:
                            for day_count in range(0,(self.scrape_end_date - self.scrape_start_date).days):
                                _inert_param_dict['checkin'] = self.scrape_start_date + timedelta(days=day_count)
                                ''' if checkout date is a necessary parameter then add 1 day to checkout date'''
                                if 'checkout' in ota['inputs']:
                                    _inert_param_dict['checkout'] = self.scrape_start_date \
                                                                    + timedelta(days=day_count+self.checkout_offset)
                                if "page" in ota['inputs']:
                                    page_offset = 0
                                    _parameterized_url = None
                                    while page_offset <= self.page_upper_limit:
                                        _inert_param_dict['page'] = page_offset
                                        _parameterized_url = self.insert_params_in_url(ota['url'],**_inert_param_dict)
#                                        scrape_url_list.append(_parameterized_url)
                                        _scrape_url_dict = {}     # init otherwise will overwrite the list
                                        _scrape_url_dict['ota']=ota['ota']
                                        _scrape_url_dict['destination_id']=destination_id
                                        _scrape_url_dict['checkin']=_inert_param_dict['checkin']
                                        _scrape_url_dict['page_offset']=page_offset
                                        _scrape_url_dict['url']=_parameterized_url
                                        _ota_parameterized_url_list.append(_scrape_url_dict)
                                        page_offset += self.page_offset

                    ''' add to dict the paramterized url list for OTA as key '''
#                    print(scrape_url_list)
#                    _scrape_url_dict[ota] = scrape_url_list

                except Exception as err:
                    ''' skip to processing the next OTA url if this one is None '''
                    print(err)

        except Exception as err:
            _s_fn_id = "Class <WebScraper> Function <build_scrape_url_list>"
            print("[Error]"+_s_fn_id, err)
            print(traceback.format_exc())

        return _scrape_url_dict, _ota_parameterized_url_list


    ''' Function
            name: scrape_ota_to_csv
            parameters:
                url - string comprising the url with place holders
                **kwargs - contain the plance holder key value pairs

            procedure: build the url by inserting the values from the **kwargs dict
            return string (url)

            author: nuwan.waidyanatha@rezgateway.com
    '''
    def scrape_data_to_csv(self,url,_scrape_tags_df,fileName, path):

        from bs4 import BeautifulSoup # Import for Beautiful Soup
        import requests # Import for requests
        import lxml     # Import for lxml parser
        import csv
        from csv import writer

        try:
            if _scrape_tags_df.shape[0] <= 0:
                raise ValueError("Invalid scrape tags no data scraped")
            if not fileName:
                raise ValueError("Invalid file name no data scraped")
            if not path:
                raise ValueError("Invalid path name no data scraped")

            ''' define generic header '''
            headers = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36'}
            response = requests.get(url, headers=headers)
            # Make it a soup
            soup = BeautifulSoup(response.text,"lxml")
#            soup = BeautifulSoup(response.text,"html.parser")

            ''' extract the list of values from content block '''
            _cont_block = (_scrape_tags_df.loc[_scrape_tags_df['variable']=='content_block']).head(1)
            _l_scrape_text = soup.select(_cont_block.tag.item())

            if len(_l_scrape_text) <= 0:
                raise ValueError("no content block (area) for %s" %(_cont_block))

            ''' get the attribute list '''
            _l_col_names = list(_scrape_tags_df.variable)
            _l_col_names.remove('content_block')

            ''' init dataframe to store the scraped categorical text '''
            _prop_data_df = pd.DataFrame()

            ''' loop through the list to retrieve values from tags '''
            for row in _l_scrape_text:
                _scraped_data_dict = {}
                for colName in _l_col_names:
                    _tag = _scrape_tags_df.loc[_scrape_tags_df.variable==colName, 'tag'].item()
                    _code = _scrape_tags_df.loc[_scrape_tags_df.variable==colName, 'code'].item()

                    try:
                        _scraped_data_dict[colName] = row.find(_tag, class_ = _code).text

                    except Exception as err:
                        pass
                        
                if _scraped_data_dict:
                    _prop_data_df = pd.concat([_prop_data_df, pd.DataFrame(_scraped_data_dict, index=[0])])

        except Exception as err:
            _s_fn_id = "Class <WebScraper> Function <scrape_data_to_csv>"
            print("[Error]"+_s_fn_id, err)
            print(traceback.format_exc())

        return _prop_data_df

    ''' Function
            name: scrape_ota_to_csv
            parameters:
                url - string comprising the url with place holders
                **kwargs - contain the plance holder key value pairs

            procedure: build the url by inserting the values from the **kwargs dict
            return string (url)

            author: nileka.desilva@rezgateway.com
    '''
    def _scrape_bookings_to_csv(self,url,checkin_date,fileName, path):

        from bs4 import BeautifulSoup # Import for Beautiful Soup
        import requests # Import for requests
        import lxml     # Import for lxml parser
        import csv
        from csv import writer

        saveTo = None

        try:
            headers = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36'}
            response = requests.get(url, headers=headers)
            # Make it a soup
            soup = BeautifulSoup(response.text,"lxml")

            lists = soup.select(".d20f4628d0")
            lists2 = soup.select(".c8305f6688")

            saveTo = path+"/"+fileName
            with open(saveTo, 'a', encoding='utf8', newline='') as f:
                fieldnames = ['Checkin Date',      # presumed checkin date
                              'Property Name',     # hotel name
                              'Room Type',         # room type: queen bed, double
                              'Room Rate',         # room price for one night
                              'Review Score',      # rating based on review
                              'Property Location', # city and relative locality
                              'Other Info',             # other relevant info
                             ]
                thewriter = csv.DictWriter(f, fieldnames=fieldnames)
#                currentDateTime = datetime.datetime.now()
                currentDateTime = self.scrape_start_date

                for _list in lists:
                    property_name = _list.find('div', class_='fcab3ed991 a23c043802').text
                    room_type = _list.find('span', class_='df597226dd').text
                    room_rate = _list.find('span', class_='fcab3ed991 bd73d13072').text
                    review_score = _list.find('div', class_='b5cd09854e d10a6220b4').text
                    property_location = _list.find('div', class_='a1fbd102d9').text
                    other_info = _list.find('div', class_='d22a7c133b').text

                    thewriter.writerow({'Checkin Date':checkin_date,
                                        'Property Name':property_name,
                                        'Room Type' :room_type,
                                        'Room Rate' : room_rate,
                                        'Review Score': review_score,
                                        'Property Location' : property_location,
                                        'Other Info': other_info,
                                       })

        except Exception as err:
            _s_fn_id = "Class <WebScraper> Function <scrape_data_to_csv>"
            print("[Error]"+_s_fn_id, err)
            print(traceback.format_exc())

        return saveTo
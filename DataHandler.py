#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  DataHandler.py
#
#  Copyright 2019 ALLINDEX <info@allindex.com>
#
# Tiingo is primary source for news
# EODHistoricaldata.com is primary source for equity, fixed income, fundamental data, indices
#
#
import requests
import pandas as pd
from io import StringIO
import json

class Equity(object):
    """
    Class to download eod data for equities, forex, US corporate bonds
    and fundamental data von stock and corporate bonds from EODhistoricaldata.com
    
    Methods are:
    get_eod_data for end of day data
    eq_fundamentals for company fundamentals
    divis for historical dividends
    serach for stock ticker 
    
    """
    def __init__(self):
        self.EODHISTTOKEN = '5cea6c1629f72.63034330'
        self.URL_eod = "https://eodhistoricaldata.com/api/eod/"
        self.URL_fund = "https://eodhistoricaldata.com/api/fundamentals/"
        self.URL_div = "https://eodhistoricaldata.com/api/div/"
        self.URL_search = 'https://eodhistoricaldata.com/api/search/'
        self.URL_bond_fund = 'https://eodhistoricaldata.com/api/bond-fundamentals/'
    
    def get_eod_data(self, symbols, startdate, enddate, freq='d'):
        """
        Download eod equity data, eod forex data:
        
        list of Symbol.Exchange, ['AAPL.US','ROG.SW'], ['EURUSD.FOREX', GBPEUR.FOREX']
        startdate, dateformat:yyyy-mm-dd
        enddate, dateformat:yyyy-mm-dd
        freq: default is 'd', additionally w, m, q, y is available
        
        The result is a dictionary with pandas frame
        The index of the frame is the date and prices are float
        
        example: get_eod_data(['EURUSD.FOREX', 'GBPEUR.FOREX'], '2019-01-01', '2019-06-01', 'm')
        """
        
        PAYLOAD = {'api_token':self.EODHISTTOKEN, 'from':startdate, 'to':enddate, 'period':freq}

        if isinstance(symbols, list):
            hist_price = {}
            for symbol in symbols:
                URL = self.URL_eod + symbol #might be worthwhile to use regex for validation
                result = requests.get(URL, params=PAYLOAD)
                symbol_price = pd.read_csv(StringIO(result.text), parse_dates=[0], index_col=0)
                #for some reason the last row contains gibberish, which is removed
                symbol_price = symbol_price[:-1]
                
                hist_price[symbol] = symbol_price
                                
        else:
            hist_price = 0
        
        # Returns a symbol dict with a pandas frame, index is the date and prices are float
        return hist_price
    
    def eq_fundamentals(self, symbols, filters=''):
        """
        Get fundamental data for a stock

        list of Symbol.Exchange, ['AAPL.US','ROG.SW']

        Detailed information can be found under:
        https://eodhistoricaldata.com/knowledgebase/stock-etfs-fundamental-data-feeds/
        
        The result is dictionary with names of list as key and a list of
        dictionaries with fundamental information
        
        Example: eq_fundamentals(['AAPL.US','ROG.SW'], filters='General::Description')
         
        """ 
        PAYLOAD = {'api_token':self.EODHISTTOKEN, 'filter':filters}
        
        if isinstance(symbols, list):
            funda_dict = {}
            for symbol in symbols:
                URL = self.URL_fund + symbol #might be worthwhile to use regex for validation
                fundamental = requests.get(URL, params=PAYLOAD)
                funda_dict[symbol] = json.loads(fundamental.text)
        else:
            funda_dict = {}
        
        #Returns a symbol dict witprint(grandchild.attrib)h JSON
        return funda_dict
    
    
    def divis(self, symbols, startdate, enddate):
        """
        Download historical dividends 
        
        list of Symbol.Exchange, ['AAPL.US','ROG.SW']
        startdate, dateformat:yyyy-mm-dd
        enddate, dateformat:yyyy-mm-dd
        
        The result is a dictionary with pandas frame
        The index of the frame is the date and prices are float
        
        example: divis(['ROG.VX', 'GE.US'], '2019-01-01', '2019-06-01')        
        """
        PAYLOAD = {'api_token':self.EODHISTTOKEN, 'from':startdate, 'to':enddate}
        
        if isinstance(symbols, list):
            div_hist = {}
            for symbol in symbols:
                URL = self.URL_div + symbol #might be worthwhile to use regex for validation
                result = requests.get(URL, params=PAYLOAD)
                divi = pd.read_csv(StringIO(result.text), parse_dates=[0], index_col=0)
                div_hist[symbol] = divi
        else:
            div_hist = {}
            
        # Returns symbol dict with pandas frame, index is the date and divis are float
        return div_hist
        
    def search(self, search_item):
        """
        Search for company by name
        
        List of company names: ['General Electric', 'BASF']
        
        The result is dictionary with names of list as key and a list of
        dictionaries with information about
        'Code', 'Exchange', 'Name', 'Country', 'Currency' as keys
        
        Example: search(['Roche'])
		"""
        PAYLOAD = {'api_token':self.EODHISTTOKEN}
		
        if isinstance(search_item, list):
            search_hist = {}
            for item in search_item:
                URL = self.URL_search + item 
                search_result = requests.get(URL, params=PAYLOAD)
                search_hist[item] = json.loads(search_result.text)
        else:
            search_hist = {}
		
        return search_hist


class Rates(object):
    """
    Class to download Libor Rates and Govi Bonds for different ccy
    govi_bond loads government bonds from: USA, UK, France, Italy, Russia, China, India, Spain, Japan, Germany, Brazil, Canada, and others
    libor loads: LIBOR for differnt ccy, EURIBOR,and STIBOR
    """
    def __init__(self):
        self.EODHISTTOKEN = '5ce1a6c1629f72.63034330'
        self.URL_govi = "https://eodhistoricaldata.com/api/eod/"
        
    def govi_bond(self,symbols):
        """
        Download government bonds:
        symbol.GBOND, e.g. UK10Y.GBOND
        
        USA, UK, France, Italy, Russia, China, India, Spain, Japan, Germany, Brazil, Canada

        The result is a dictionary with pandas frame
        The index of the frame is the date and prices are float        
        """
        PAYLOAD = {'api_token':self.EODHISTTOKEN}
        
        if isinstance(symbols, list):
            hist_price = {}
            for symbol in symbols:
                URL = self.URL_govi + symbol #might be worthwhile to use regex for validation
                result = requests.get(URL, params=PAYLOAD)
                govi_bond = pd.read_csv(StringIO(result.text), parse_dates=[0], index_col=0)
                #for some reason the last row contains gibberish, which is removed
                govi_bond = govi_bond[:-1]
                
                hist_price[symbol] = govi_bond
                                
        else:
            hist_price = 0
        
        return hist_price


#====================================
if __name__ == '__main__':
    TESTING = Equity()
    
    print(Equity().__doc__)
    
    prices = TESTING.get_eod_data(['ROG.VX'], '2019-05-01', '2019-06-01')
    print(prices)
    print(TESTING.get_eod_data.__doc__)
    
    fundamental = TESTING.eq_fundamentals(['AAPL.US','ROG.SW', 'DEDAL.PA'], filters='General::Description')
    print(fundamental)
    print(TESTING.eq_fundamentals.__doc__)
    """
    dividends = TESTING.divis(['ROG.VX', 'GE.US'], '2019-05-01', '2019-06-01')
    print(dividends)
    print(TESTING.divis.__doc__)
    """
    searches = TESTING.search(['Dedalus', 'BASF'])
    print(searches)
    print(TESTING.search.__doc__)
    
    BOND = Rates()
    bond = BOND.govi_bond(['DE10Y.GBOND', 'UK1Y.GBOND'])
    print(bond)
    print(BOND.govi_bond.__doc__)

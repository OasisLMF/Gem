# ) -*- coding: utf-8 -*-

import io
import csv
import logging
from rtree import index
import pandas as pd

from shapely.geometry import (
    Point,
    MultiPoint,
)

from oasislmf.utils.coverages import COVERAGE_TYPES
from oasislmf.utils.peril import PERILS
from oasislmf.utils.status import OASIS_KEYS_STATUS

KEYS_STATUS_FAIL = OASIS_KEYS_STATUS['fail']['id']
KEYS_STATUS_NOMATCH = OASIS_KEYS_STATUS['nomatch']['id']
KEYS_STATUS_SUCCESS = OASIS_KEYS_STATUS['success']['id']

__all__ = ['AreaPerilLookup']


class AreaPerilLookup(object):
    '''
    Functionality to perform an area peril lookup.
    '''

    _cell_index = index.Index()
    _cell_dataframe = pd.DataFrame()

    def __init__(self, areas_file=None):
        if areas_file:
            with io.open(areas_file, 'r', encoding='utf-8') as f:
                dr = csv.DictReader(f)
                self.load_cell_index(dr)
            self._cell_dataframe = pd.read_csv(areas_file)

    def load_cell_index(self, data):
        '''
        Load the lookup data.
        Args:
            data: the lookup data.
        '''
        for r in data:
            if float(r['xmin']) > -9990:
                self._cell_index.insert(int(r['areaperil_id']), (float(r['xmin']), float(r['ymin']), float(r['xmax']), float(r['ymax'])), obj={'id': int(r['areaperil_id']), 'imt': r['IMTs']})

    def validate_lat(self, lat):
        '''
        Check that a string or number is a valid latitude.
        Args:
            s (string or number): the latitude
        Returns:
            True if string is a valid latitude, False otherwise
        '''
        try:
            return -90 <= float(lat) <= 90
        except ValueError:
            return False

    def validate_lon(self, lon):
        '''
        Check that a string or number is a valid longitude.
        Args:
            s (string or number): the longitude
        Returns:
            True if string is a valid longitude, False otherwise
        '''
        try:
            return -180 <= float(lon) <= 180
        except ValueError:
            return False

    def do_lookup_location(self, location):
        '''
        Perform a lookup on a specified location.
        Args:
            location: the location to lookup.
        Return:
            Lookup result
        '''
        logging.debug("Looking up location.")

        status = KEYS_STATUS_NOMATCH
        area_peril_id = None
        message = ''

        print(location)
        lat = location['lat']
        lon = location['lon']
        imt = location['imt']
        county = location['county']
        state = location['state']
        print("state:", state)
        print("county:", county)
        print("imt:", imt)

        if (self.validate_lat(lat) & self.validate_lon(lon) & ((abs(lon)>0.01) | (abs(lat)>0.01))):
            hits = list(self._cell_index.intersection((lon,lat,lon,lat), objects='raw'))
            if(len(hits)>0):
                for item in hits:
                    if(item['imt']==imt):
                        area_peril_id = item['id']
                        status = KEYS_STATUS_SUCCESS
                        break

        if (area_peril_id == None):
            # try county
            if type(county) == str:
                admin = self._cell_dataframe[(self._cell_dataframe['NAME_2']==county) & (self._cell_dataframe['IMTs']==imt)]
                if(admin.shape[0]>0):
                    area_peril_id = admin['areaperil_id'].iloc[0]
                    status = KEYS_STATUS_SUCCESS

        if (area_peril_id == None):
            # try state
            if type(state) == str:
                admin = self._cell_dataframe[(self._cell_dataframe['NAME_1']==state) & (self._cell_dataframe['IMTs']==imt)]
                if(admin.shape[0]>0):
                    area_peril_id = admin['areaperil_id'].iloc[0]
                    status = KEYS_STATUS_SUCCESS

        return {
            'status': status,
            'area_peril_id': area_peril_id,
            'message': message
        }

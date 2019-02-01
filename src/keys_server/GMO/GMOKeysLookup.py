# -*- coding: utf-8 -*-


# Python 2 standard library imports
import csv
import io
import logging
import os

# Python 2 non-standard library imports
import pandas as pd

# Imports from Oasis core repos + subpackages or modules within keys_server
from oasislmf.keys.lookup import OasisBaseKeysLookup
from oasislmf.utils.log import oasis_log
from oasislmf.utils.peril import PERIL_ID_QUAKE
from oasislmf.utils.status import (
    KEYS_STATUS_FAIL,
    KEYS_STATUS_NOMATCH,
    KEYS_STATUS_SUCCESS,
)
from oasislmf.utils.values import (
    to_int,
    to_float,
    to_string,
)

from .utils import (
    AreaPerilLookup,
    VulnerabilityLookup,
)

#
# Public entry point
#
__all__ = [
  'GMOKeysLookup'
]


class GMOKeysLookup(OasisBaseKeysLookup):
    """
    GMO keys lookup.
    """

    _LOCATION_RECORD_META = {
        'id': {
            'source_header': 'ROW_ID', 'csv_data_type': int,
            'validator': to_int, 'desc': 'Location ID'
        },
        'lon': {
            'source_header': 'LONGITUDE', 'csv_data_type': float,
            'validator': to_float, 'desc': 'Longitude'
        },
        'lat': {
            'source_header': 'LATITUDE', 'csv_data_type': float,
            'validator': to_float, 'desc': 'Latitude'
        },
        'county': {
            'source_header': 'COUNTY',
            'csv_data_type': str,
            'validator': to_string, 'desc': 'County'
        },
        'state': {
            'source_header': 'STATE',
            'csv_data_type': str,
            'validator': to_string, 'desc': 'State'
        },
        'country': {
            'source_header': 'COUNTRY',
            'csv_data_type': str,
            'validator': to_string, 'desc': 'Country'
        },
        'coverage': {
            'source_header': 'COV1', 'csv_data_type': int,
            'validator': to_int, 'desc': 'Coverage'
        },
        'taxonomy': {
            'source_header': 'BLDGCLASS',
            'csv_data_type': str,
            'validator': to_string, 'desc': 'Class #1'
        },
        'occupancy': {
            'source_header': 'OCCTYPE',
            'csv_data_type': str,
            'validator': to_string, 'desc': 'Class #2'
        },
        'imt': {
            'source_header': 'type',
            'csv_data_type': str,
            'validator': to_string, 'desc': 'Intensity Measure'
        }
    }

    @oasis_log()
    def __init__(
            self, keys_data_directory=None,
            supplier='GEMFoundation', model_name='GMO', model_version=None):
        """
        Initialise the static data required for the lookup.
        """
        super(self.__class__, self).__init__(
            keys_data_directory,
            supplier,
            model_name,
            model_version
        )

        self.area_peril_lookup = AreaPerilLookup(
            areas_file=os.path.join(
                self.keys_data_directory, 'areaperil_dict.csv')
        ) if keys_data_directory else AreaPerilLookup()

        self.vulnerability_lookup = VulnerabilityLookup(
            vulnerabilities_file=os.path.join(
                self.keys_data_directory, 'vulnerability_dict.csv')
        ) if keys_data_directory else VulnerabilityLookup()

    @oasis_log()
    def process_locations(self, loc_df):
        """
        Process location rows - passed in as a pandas dataframe.
        """

        # join IMTs with locs
        vulnDict = pd.read_csv(os.path.join(self.keys_data_directory, 'vulnerability_dict.csv'))
        loc_df = loc_df.merge(vulnDict, left_on="bldgclass", right_on="taxonomy")
        pd.set_option('display.max_columns', 500)
        # print(loc_df)
        
        for i in range(len(loc_df)):
            #record = loc_df.iloc[i].to_dict()
            record = self._get_location_record(loc_df.iloc[i])

            area_peril_rec = self.area_peril_lookup.do_lookup_location(record)

            vuln_peril_rec = \
                self.vulnerability_lookup.do_lookup_location(record)

            status = message = ''

            if area_peril_rec['status'] == \
                    vuln_peril_rec['status'] == KEYS_STATUS_SUCCESS:
                status = KEYS_STATUS_SUCCESS
            elif (
                area_peril_rec['status'] == KEYS_STATUS_FAIL or
                vuln_peril_rec['status'] == KEYS_STATUS_FAIL
            ):
                status = KEYS_STATUS_FAIL
                message = '{}, {}'.format(
                    area_peril_rec['message'],
                    vuln_peril_rec['message']
                )
            else:
                status = KEYS_STATUS_NOMATCH
                message = 'No area peril or vulnerability match'

            yield {
                "id": record['id'],
                "peril_id": PERIL_ID_QUAKE,
                "coverage": record['coverage'],
                "coverage_type": record['coverage'],
                "area_peril_id": area_peril_rec['area_peril_id'],
                "vulnerability_id": vuln_peril_rec['vulnerability_id'],
                "message": message,
                "status": status
            }

    def _get_location_record(self, loc_item):
        """
        Construct a location record (dict) from the location item, which in this
        case is a row in a Pandas dataframe.
        """
        # print("!! _get_location_record: {0}".format(loc_item))

        meta = self._LOCATION_RECORD_META
        return dict((
                k,
                meta[k]['validator'](loc_item[meta[k]['source_header'].lower()])
            ) for k in meta
        )

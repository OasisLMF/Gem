# -*- coding: utf-8 -*-

# Python 2 standard library imports
import csv
import io
import logging
import os

# Python 2 non-standard library imports
import pandas as pd

# Imports from Oasis core repos + subpackages or modules within keys_server
from oasislmf.utils.coverages import COVERAGE_TYPES
from oasislmf.utils.peril import PERILS
from oasislmf.utils.status import OASIS_KEYS_STATUS

KEYS_STATUS_FAIL = OASIS_KEYS_STATUS['fail']
KEYS_STATUS_NOMATCH = OASIS_KEYS_STATUS['nomatch']
KEYS_STATUS_SUCCESS = OASIS_KEYS_STATUS['success']

from oasislmf.model_preparation.lookup import OasisBaseKeysLookup
from oasislmf.utils.log import oasis_log

KEYS_STATUS_FAIL = OASIS_KEYS_STATUS['fail']['id']
KEYS_STATUS_NOMATCH = OASIS_KEYS_STATUS['nomatch']['id']
KEYS_STATUS_SUCCESS = OASIS_KEYS_STATUS['success']['id']

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

#
# START - deprecated oasislmf.utils.values
#

from datetime import datetime

import pytz

NULL_VALUES = [None, '', 'n/a', 'N/A', 'null', 'Null', 'NULL']

def get_timestamp(thedate=None, fmt='%Y%m%d%H%M%S'):
    """ Get a timestamp """
    d = thedate if thedate else datetime.now()
    return d.strftime(fmt)


def get_utctimestamp(thedate=None, fmt='%Y-%b-%d %H:%M:%S'):
    """
    Returns a UTC timestamp for a given ``datetime.datetime`` in the
    specified string format - the default format is::
        YYYY-MMM-DD HH:MM:SS
    """
    d = thedate.astimezone(pytz.utc) if thedate else datetime.utcnow()
    return d.strftime(fmt)


def to_string(val):
    """
    Converts value to string, with possible additional formatting.
    """
    return '' if val is None else str(val)


def to_int(val):
    """
    Parse a string to int
    """
    return None if val in NULL_VALUES else int(val)


def to_float(val):
    """
    Parse a string to float
    """
    return None if val in NULL_VALUES else float(val)

#
# END - deprecated oasislmf.utils.values
#

""" ---- Implementation note ----

In the original lookup implementation each location can map to multiple vulnerability ids,
each with difference levels of ductility and or material type.

Note from Malcolm:
   Ductility is largely a product of materials, with unreinforced
   masonry being the worst and wood the best.  The reason it’s probably
   not explicitly included in commercial cat models is
   likely that the ductility for a given material is largely a function of age,
   since better construction codes usually leads to more ductile structures.
   Age usually is explicitly included in cat models wheres
   the GEM functions capture this through the construction itself.

Original taxonomy:
    gem_taxonomy_by_oed_occupancy_and_number_of_storeys_df = pd.DataFrame.from_dict({
        'constructioncode': ['5156', '5150', '5150', '5150', '5150', '5150', '5150', '5109', '5109', '5109', '5109', '5109', '5109', '5109', '5105', '5105', '5105', '5105', '5105', '5105', '5105', '5105', '5101', '5103', '5103', '5103', '5000', '5050', '5050', '5050', '5050', '5050'],
        'numberofstoreys': [1, 2, 2, 3, 2, 3, 1, 2, 3, 2, 3, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3, 2, 2, 1, 2, 1, 1, 1, 2, 1, -1],
        'taxonomy': ['CR-PC_LWAL-DNO_H1', 'CR_LFINF-DNO_H2', 'CR_LFINF-DUH_H2', 'CR_LFINF-DUH_H3', 'CR_LFINF-DUM_H2', 'CR_LFINF-DUM_H3', 'CR_LFM-DNO_H1', 'MCF_LWAL-DNO_H2', 'MCF_LWAL-DNO_H3', 'MCF_LWAL-DUH_H2',	'MCF_LWAL-DUH_H3', 'MCF_LWAL-DUM_H2','MCF_LWAL-DUM_H3', 'MR_LWAL-DNO_H1','MR_LWAL-DNO_H2', 'MR_LWAL-DNO_H3','MR_LWAL-DUH_H1', 'MR_LWAL-DUH_H2', 'MR_LWAL-DUH_H3', 'MR_LWAL-DUM_H1', 'MR_LWAL-DUM_H2', 'MR_LWAL-DUM_H3', 'MUR-ADO_LWAL-DNO_H2', 'MUR-ST_LWAL-DNO_H2', 'MUR_LWAL-DNO_H1', 'MUR_LWAL-DNO_H2', 'UNK_H1', 'W-WBB_LPB-DNO_H1', 'W-WLI_LWAL-DNO_H1', 'W-WLI_LWAL-DNO_H2', 'W-WS_LPB-DNO_H1', 'W-']
    })

The below was changed so that each unique combination of ('constructioncode', 'numberofstoreys')
maps to a single 'taxonomy' code

"""

gem_taxonomy_by_oed_occupancy_and_number_of_storeys_df = pd.DataFrame.from_dict({
    'constructioncode': ['5156', '5150', '5150', '5150', '5109', '5109', '5109', '5105', '5105', '5105', '5101', '5103', '5103', '5000', '5050', '5050', '5050'],
    'numberofstoreys': [1, 2, 3, 1, 2, 3, 1, 1, 2, 3, 2, 1, 2, 1, 1, 2, -1],
    'taxonomy': ['CR-PC_LWAL-DNO_H1', 'CR_LFINF-DUM_H2', 'CR_LFINF-DUM_H3', 'CR_LFM-DNO_H1', 'MCF_LWAL-DNO_H2', 'MCF_LWAL-DNO_H3', 'MR_LWAL-DNO_H1', 'MR_LWAL-DUM_H1', 'MR_LWAL-DUM_H2', 'MR_LWAL-DUM_H3', 'MUR-ADO_LWAL-DNO_H2', 'MUR_LWAL-DNO_H1', 'MUR_LWAL-DNO_H2', 'UNK_H1', 'W-WLI_LWAL-DNO_H1', 'W-WLI_LWAL-DNO_H2', 'W-']
})



class GMOKeysLookup(OasisBaseKeysLookup):

    """
    GMO keys lookup.
    """

    _LOCATION_RECORD_META = {
        'id': {
            'source_header': 'loc_id', 'csv_data_type': int,
            'validator': to_int, 'desc': 'Location ID'
        },
        'lon': {
            'source_header': 'Longitude', 'csv_data_type': float,
            'validator': to_float, 'desc': 'Longitude'
        },
        'lat': {
            'source_header': 'Latitude', 'csv_data_type': float,
            'validator': to_float, 'desc': 'Latitude'
        },
        'county': {
            'source_header': 'GeogName1',
            'csv_data_type': str,
            'validator': to_string, 'desc': 'County'
        },
        'state': {
            'source_header': 'AreaName1',
            'csv_data_type': str,
            'validator': to_string, 'desc': 'State'
        },
        'country': {
            'source_header': 'CountryCode',
            'csv_data_type': str,
            'validator': to_string, 'desc': 'Country'
        },
        'coverage': {
            'source_header': 'BuildingTIV', 'csv_data_type': int,
            'validator': to_int, 'desc': 'Coverage'
        },
        'taxonomy': {
            'source_header': 'taxonomy',
            'csv_data_type': str,
            'validator': to_string, 'desc': 'Class #1'
        },
        'occupancy': {
            'source_header': 'OccupancyCode',
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
    def __init__(self,
                 keys_data_directory=None,
                 supplier='GEMFoundation',
                 model_name='GMO',
                 model_version=None,
                 complex_lookup_config_fp=None,
                 output_directory=None):
        """
        Initialise the static data required for the lookup.
        """
        super(self.__class__, self).__init__(
            keys_data_directory,
            supplier,
            model_name,
            model_version
        )

        # join IMTs with locs
        self.vulnDict = pd.read_csv(os.path.join(self.keys_data_directory, 'vulnerability_dict.csv'))

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

        # Mapping to OED
        set_dtype = {'constructioncode': 'int',
                     'numberofstoreys': 'int'}
        loc_df = loc_df.astype(set_dtype).merge(
            gem_taxonomy_by_oed_occupancy_and_number_of_storeys_df.astype(set_dtype),
            on=['constructioncode', 'numberofstoreys'])

        loc_df = loc_df.merge(self.vulnDict, on="taxonomy")
        pd.set_option('display.max_columns', 500)

        # Enforce single taxonomy per location row (Safe guard)
        loc_df.drop_duplicates(subset=['locperilscovered', 'loc_id'], keep='first', inplace=True)

        for i in range(len(loc_df)):
            record = self._get_location_record(loc_df.iloc[i])

            area_peril_rec = self.area_peril_lookup.do_lookup_location(record)

            vuln_peril_rec = \
                self.vulnerability_lookup.do_lookup_location(record)
            status = message = ''

            # print(area_peril_rec)
            # print(vuln_peril_rec)
            # print(KEYS_STATUS_SUCCESS)
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

            record = {
                "loc_id": record['id'],
                "peril_id": PERILS['earthquake']['id'],
                "coverage_type": COVERAGE_TYPES['buildings']['id'],
                "area_peril_id": area_peril_rec['area_peril_id'],
                "vulnerability_id": vuln_peril_rec['vulnerability_id'],
                "message": message,
                "status": status
            }
            yield(record)

    def process_locations_multiproc(self, locations):
        """
        Process location rows - passed in as a pandas dataframe.
        """

        # Mapping to OED
        set_dtype = {'constructioncode': 'int',
                     'numberofstoreys': 'int'}
        loc_df = locations.astype(set_dtype).merge(
            gem_taxonomy_by_oed_occupancy_and_number_of_storeys_df.astype(set_dtype),
            on=['constructioncode', 'numberofstoreys'])

        loc_df = loc_df.merge(self.vulnDict, on="taxonomy")
        pd.set_option('display.max_columns', 500)

        # Enforce single taxonomy per location row (Safe guard)
        loc_df.drop_duplicates(subset=['locperilscovered', 'loc_id'], keep='first', inplace=True)

        results = []
        for i in range(len(loc_df)):
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

            record = {
                    "loc_id": record['id'],
                    "peril_id": PERILS['earthquake']['id'],
                    "coverage_type": COVERAGE_TYPES['buildings']['id'],
                    "area_peril_id": area_peril_rec['area_peril_id'],
                    "vulnerability_id": vuln_peril_rec['vulnerability_id'],
                    "message": message,
                    "status": status
                }
            results.append(record)
        return(results)

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

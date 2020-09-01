
import datetime
import pathlib
import sys
from typing import Mapping

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import seaborn



def _args_to_dict() -> Mapping[str, str]:
    """Converts command line arguments into 'arguments' dict.
    
    The dictionary conversion is more forgiving than the typical argparse
    construction. It allows the package to check default options and give
    clearer error coding.
    
    This handy bit of code, as an alternative to argparse, was found here:
        https://stackoverflow.com/questions/54084892/
        how-to-convert-commandline-key-value-args-to-dictionary
        
    Returns:
        arguments(Mapping[str, str]): dict of command line options when the 
            options are separated by '='.
            
    """
    arguments = {}
    for argument in sys.argv[1:]:
        if '=' in argument:
            separated = argument.find('=')
            key, value = argument[:separated], argument[separated + 1:]
            arguments[key] = value
    return arguments

def _import_survey_results(key: str, file_name: str) -> pd.DataFrame:
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(key, scope)
    gc = gspread.authorize(credentials)
    worksheet = gc.open(file_name).Form_Responses
    data = worksheet.get_all_values()
    header = data.pop(0)
    return pd.DataFrame(data, columns = header)

def _limit_data_to_year(results: pd.DataFrame, year: int) -> pd.DataFrame:
    results['TimeStamp'] = pd.to_datetime(results['Timestamp'])
    return results[results['Timestamp'].dt.year == year]

if __name__ == '__main__':
    # Gets command line arguments and converts them to dict.
    # arguments = _args_to_dict()
    arguments = {
        'file': 'Criminal Law Survey (Responses)'}
    # Imports survey results from a google sheets
    key = arguments.get(
        'api_key', 
        pathlib.Path('..') / '..' / 'keys' / 'google_api_key.json')
    results = _import_survey_results(
        key = key,
        file_name = arguments.get('-file')) 
    results = _limit_data_to_year(
        results = results, 
        year = arguments.get('-year', datetime.datetime.today().year))
    print(results)
    

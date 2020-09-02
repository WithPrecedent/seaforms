"""
seaforms: command line script for the package
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

seaforms converts the results from a survey administerd with Google Forms, with
results stored in Google Sheets, into a set of seaborn charts.

"""
from __future__ import annotations
import datetime
import pathlib
import sys
from typing import (Any, Callable, ClassVar, Container, Generic, Iterable, 
                    Iterator, Mapping, Sequence, Tuple, TypeVar, Union)

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import seaborn as sns


def _args_to_dict() -> Mapping[str, str]:
    """Converts command line arguments into 'arguments' dict.
    
    The dictionary conversion is more forgiving than the typical argparse
    construction. It allows the package to check default options and give
    clearer error coding.
    
    This handy bit of code by Kevin He, as an alternative to argparse, is found
    here:
        https://stackoverflow.com/questions/54084892/how-to-convert-commandline-key-value-args-to-dictionary
        
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
    google_client = gspread.authorize(credentials)
    worksheets = google_client.open_by_url(file_name)
    worksheet = worksheets.get_worksheet(0)
    data = worksheet.get_all_values()
    header = data.pop(0)
    return pd.DataFrame(data, columns = header)

def _limit_data_to_year(results: pd.DataFrame, year: int) -> pd.DataFrame:
    print(results.dtypes)
    results['Timestamp'] = results['Timestamp'].dt.strftime(
        "%Y-%m-%d %H:%M:%S.%f")
    # results["To"] = results["To"].dt.strftime("%Y-%m-%d %H:%M:%S.%f")
    # results.update([results.columns.values.tolist()] + results.values.tolist())
    # results['TimeStamp'] = pd.to_datetime(results['Timestamp'])
    
    return results[results['Timestamp'].dt.year == year]

# def _get_counts(results: pd.DataFrame) -> pd.DataFrame:
#     counts = []
#     for column in results.columns:
        

# def _plot_results(results: pd.DataFrame, orientation: str) -> Sequence[object]:
#     plots = []
#     for column in results.columns:
#         plots.append(sns.barplot())
#     return plots

if __name__ == '__main__':
    # Gets command line arguments and converts them to dict.
    # arguments = _args_to_dict()
    arguments = {
        '-file': 'https://docs.google.com/spreadsheets/d/16wefUokMmfB9W_s6S5JH4b0LxBgwtjMnbpbT7p12oJg/edit?usp=sharing'}
    # Imports survey results from a google sheets
    key = arguments.get(
        'api_key', 
        pathlib.Path('..') / '..' / 'keys' / 'seaforms.json')
    results = _import_survey_results(
        key = key,
        file_name = arguments.get('-file')) 
    results = _limit_data_to_year(
        results = results, 
        year = arguments.get('-year', datetime.datetime.today().year))
    # plots = _plot_results(
    #     results = results,
    #     orientation = arguments.get('-orientation', 'horizontal')
    # )
    print(results)
    

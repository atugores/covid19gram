#!/bin/env python
# -*- coding: utf-8 -*-
import git
import json
import datetime
import pandas as pd
import numpy as np
import os


def pull_global(base_directory="covid19/", data_directory="data/"):
    # TODO: change to logging
    print("[" + datetime.datetime.now().strftime("%d.%b %Y %H:%M:%S") + "] " + "Start pulling global Data")
    import_file_path = base_directory + "docs/timeseries.json"

    if not repository_has_changes('world', base_directory, [import_file_path], data_directory):
        print("[" + datetime.datetime.now().strftime("%d.%b %Y %H:%M:%S") + "] " + "Finish pulling global Data. No changes in repository")
        return
    # generate files cases, recovered and deceased
    with open(import_file_path) as json_file:
        data = json.load(json_file)

    export_cases = data_directory + 'world_cases.csv'
    export_recovered = data_directory + 'world_recovered.csv'
    export_deceased = data_directory + 'world_deceased.csv'

    with open(export_cases, 'w') as cases_file, open(export_recovered, 'w') as recovered_file, open(export_deceased, 'w') as deceased_file:
        cases_file.write("date,region_code,CCAA,total\n")
        recovered_file.write("date,region_code,CCAA,total\n")
        deceased_file.write("date,region_code,CCAA,total\n")

        country_code = 0
        global_cases = {}
        global_recovered = {}
        global_deceased = {}
        for country in data:
            for row in data[country]:
                country_name = country.replace(",", "")
                date = row['date']
                confirmed = row['confirmed']
                recovered = row['recovered']
                deaths = row['deaths']

                # get global data
                if date in global_cases:
                    global_cases[date] += confirmed
                else:
                    global_cases[date] = confirmed
                if date in global_recovered:
                    global_recovered[date] += recovered
                else:
                    global_recovered[date] = recovered
                if date in global_deceased:
                    global_deceased[date] += deaths
                else:
                    global_deceased[date] = deaths

                cases_file.write(
                    f"{date},{country_code},{country_name},{confirmed}\n")
                recovered_file.write(
                    f"{date},{country_code},{country_name},{recovered}\n")
                deceased_file.write(
                    f"{date},{country_code},{country_name},{deaths}\n")
            country_code += 1

        # add global information for each date
        for date in global_cases.keys():
            cases_file.write(
                f"{date},{country_code},Global,{global_cases[date]}\n")
        for date in global_recovered.keys():
            recovered_file.write(
                f"{date},{country_code},Global,{global_recovered[date]}\n")
        for date in global_deceased.keys():
            deceased_file.write(
                f"{date},{country_code},Global,{global_deceased[date]}\n")

    # generate covid csv
    files = [export_cases, export_recovered, export_deceased]
    generate_covidgram_dataset('world', files, data_directory)
    print("[" + datetime.datetime.now().strftime("%d.%b %Y %H:%M:%S") + "] " + "Finish pulling global Data. New file created")


def pull_datasets(base_directory="datasets/", data_directory="data/"):
    # TODO: change to logging
    print("[" + datetime.datetime.now().strftime("%d.%b %Y %H:%M:%S") + "] " + "Start pulling Spain Data")
    import_file_path = base_directory + "COVID 19/"
    files = [import_file_path + 'ccaa_covid19_casos_long.csv',
             import_file_path + 'ccaa_covid19_altas_long.csv',
             import_file_path + 'ccaa_covid19_fallecidos_long.csv']
    if not repository_has_changes('spain', base_directory, files, data_directory):
        print("[" + datetime.datetime.now().strftime("%d.%b %Y %H:%M:%S") + "] " + "Finish pulling Spain Data. No changes in repository")
        return

    generate_covidgram_dataset('spain', files, data_directory)
    print("[" + datetime.datetime.now().strftime("%d.%b %Y %H:%M:%S") + "] " + "Finish pulling Spain Data. New file created")


def repository_has_changes(scope, base_directory, files, data_directory):
    # return True
    files_mtime = []
    for f in files:
        files_mtime.append(int(os.path.getmtime(f)))
    original_mtime = np.max(files_mtime)
    # update repository
    g = git.cmd.Git(base_directory)
    g.pull()

    # check if files changed
    files_mtime = []
    for f in files:
        files_mtime.append(int(os.path.getmtime(f)))
    new_mtime = np.max(files_mtime)
    if original_mtime != new_mtime:
        return True
    # check if exists covid19gram file for this scope and its mtime
    csv_covid19gram = f"{data_directory}/{scope}_covid19gram.csv"
    if not os.path.isfile(csv_covid19gram):
        return True
    csv_mtime = int(os.path.getmtime(csv_covid19gram))
    if csv_mtime < new_mtime:
        return True
    return False


def generate_covidgram_dataset(scope, files, data_directory):
    csv_cases, csv_recovered, csv_deceased = files

    df = pd.read_csv(csv_cases)
    # rename, convert date to datetime and set index
    df.rename(columns={
        'fecha': 'date', 'cod_ine': 'region_code',
        'total': 'cases', 'CCAA': 'region'}, inplace=True)
    df['date'] = pd.to_datetime(df['date'])
    df.set_index(['date', 'region_code'], inplace=True)

    # column recovered
    rec_df = pd.read_csv(csv_recovered)
    rec_df.drop(columns=['CCAA'], inplace=True)
    rec_df.rename(columns={
        'fecha': 'date', 'cod_ine': 'region_code',
        'total': 'recovered'}, inplace=True)
    rec_df['date'] = pd.to_datetime(rec_df['date'])
    rec_df.set_index(['date', 'region_code'], inplace=True)
    df = df.merge(rec_df, left_index=True, right_index=True, how='left')

    # column deceased
    dec_df = pd.read_csv(csv_deceased)
    dec_df.drop(columns=['CCAA'], inplace=True)
    dec_df.rename(columns={
        'fecha': 'date', 'cod_ine': 'region_code',
        'total': 'deceased'}, inplace=True)
    dec_df['date'] = pd.to_datetime(dec_df['date'])
    dec_df.set_index(['date', 'region_code'], inplace=True)
    df = df.merge(dec_df, left_index=True, right_index=True, how='left')

    # column population
    if os.path.isfile(f"{data_directory}/{scope}_population.csv"):
        pop_df = pd.read_csv(f"{data_directory}/{scope}_population.csv")
        if scope == 'world':
            pop_df.set_index('country_name', inplace=True)
            df = df.merge(pop_df, left_on='region',
                          right_index=True, how='left')
        else:
            pop_df.set_index('region_code', inplace=True)
            df = df.merge(pop_df, left_index=True,
                          right_index=True, how='left')
    else:
        df['population'] = 0

    df.fillna(0, inplace=True)
    df.sort_index()

    df['cases_per_100k'] = df['cases'] * 100_000 / df['population']
    df['deceased_per_100k'] = df['deceased'] * 100_000 / df['population']
    df['active_cases'] = df['cases'] - df['recovered'] - df['deceased']

    df['increase_cases'] = 0.0
    df['rolling_cases'] = 0.0
    df['rolling_cases_per_100k'] = 0.0
    df['increase_deceased'] = 0.0
    df['rolling_deceased'] = 0.0
    df['rolling_deceased_per_100k'] = 0.0
    for region in df['region'].unique():
        reg_df = df[df.region == region]
        # cases
        increase = reg_df['cases'] - reg_df['cases'].shift(1)
        rolling = increase.rolling(window=3).mean()
        df['increase_cases'].mask(df.region == region, increase, inplace=True)
        df['rolling_cases'].mask(df.region == region, rolling, inplace=True)
        df['rolling_cases_per_100k'] = df['rolling_cases'] * 100_000 / df['population']
        # deceased
        increase = reg_df['deceased'] - reg_df['deceased'].shift(1)
        rolling = increase.rolling(window=3).mean()
        df['increase_deceased'].mask(df.region == region, increase, inplace=True)
        df['rolling_deceased'].mask(df.region == region, rolling, inplace=True)
        df['rolling_deceased_per_100k'] = df['rolling_deceased'] * 100_000 / df['population']

    df.fillna(0, inplace=True)
    df.to_csv(f"{data_directory}/{scope}_covid19gram.csv")


if __name__ == "__main__":
    pull_datasets()
    pull_global()

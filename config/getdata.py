#!/bin/env python
# -*- coding: utf-8 -*-
import git
import json
import datetime
import pandas as pd
import numpy as np
import os

SCOPES = {
    'world': {
        'base_directory': 'external-data/world',
        'repo_url': 'https://github.com/pomber/covid19.git',
        'watch': [
            'docs/timeseries.json',
        ]
    },
    'spain': {
        'base_directory': 'external-data/spain',
        'repo_url': 'https://github.com/datadista/datasets',
        'watch': [
            'COVID 19/ccaa_covid19_casos_long.csv',
            'COVID 19/ccaa_covid19_altas_long.csv',
            'COVID 19/ccaa_covid19_fallecidos_long.csv'
        ]
    },
    'italy': {
        'base_directory': 'external-data/italy',
        'repo_url': 'https://github.com/pcm-dpc/COVID-19',
        'watch': [
            'dati-regioni/dpc-covid19-ita-regioni.csv'
        ]
    },
}


def update_data():
    for scope in SCOPES.keys():
        update_scope_data(scope)


def update_scope_data(scope, data_directory="data/"):
    print("[" + datetime.datetime.now().strftime("%d.%b %Y %H:%M:%S") + "] " + "Start update data for " + scope)
    if not repository_has_changes(scope, data_directory):
        print("[" + datetime.datetime.now().strftime("%d.%b %Y %H:%M:%S") + "] " + "Finish update data for " + scope + ". No changes in repository")
        return
    input_files = get_or_generate_input_files(scope, data_directory)
    generate_covidgram_dataset(scope, input_files, data_directory)
    print("[" + datetime.datetime.now().strftime("%d.%b %Y %H:%M:%S") + "] " + "Finish update data for " + scope + ". New file created")


def get_or_generate_input_files(scope, data_directory="data/"):
    if scope in ['spain', 'italy']:
        base_directory = SCOPES[scope]['base_directory']
        files = [base_directory + "/" + f for f in SCOPES[scope].get('watch', [])]
        return files

    if scope == 'world':
        generate_world_input_files(data_directory)

    return [
        data_directory + scope + '_cases.csv',
        data_directory + scope + '_recovered.csv',
        data_directory + scope + '_deceased.csv'
    ]


def repository_has_changes(scope, data_directory):
    # check if repository exists
    base_directory = SCOPES[scope]['base_directory']
    if not os.path.exists(base_directory):
        os.makedirs(base_directory)
        git.Repo.clone_from(SCOPES[scope]['repo_url'], base_directory)
        return True

    files = [base_directory + "/" + f for f in SCOPES[scope].get('watch', [])]
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


def generate_world_input_files(data_directory="data/"):
    import_file_path = SCOPES['world']['base_directory'] + "/docs/timeseries.json"
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


def generate_covidgram_dataset(scope, files, data_directory):
    csv_cases = None
    csv_recovered = None
    csv_deceased = None

    if len(files) == 3:
        csv_cases, csv_recovered, csv_deceased = files
    else:
        csv_cases = files[0]

    df = pd.read_csv(csv_cases)
    # rename, convert date to datetime and set index
    df.rename(columns={
        'fecha': 'date', 'cod_ine': 'region_code',
        'total': 'cases', 'CCAA': 'region'}, inplace=True)

    # italy: data,stato,codice_regione,denominazione_regione,lat,long,ricoverati_con_sintomi,terapia_intensiva,totale_ospedalizzati,isolamento_domiciliare,totale_positivi,variazione_totale_positivi,nuovi_positivi,dimessi_guariti,deceduti,totale_casi,tamponi,note_it,note_en
    if scope == 'italy':
        df.drop(columns=[
            'stato', 'lat', 'long', 'ricoverati_con_sintomi',
            'terapia_intensiva', 'totale_ospedalizzati', 'isolamento_domiciliare',
            'totale_positivi', 'variazione_totale_positivi',
            'nuovi_positivi', 'tamponi', 'note_it', 'note_en'], inplace=True)

        df.rename(columns={
            'data': 'date', 'codice_regione': 'region_code',
            'totale_casi': 'cases', 'denominazione_regione': 'region',
            'dimessi_guariti': 'recovered', 'deceduti': 'deceased'}, inplace=True)
        # avoid duplicates
        df['region_code'].mask(df.region == "P.A. Bolzano", '4A', inplace=True)
        df['region_code'].mask(df.region == "P.A. Trento", '4B', inplace=True)

    df['date'] = pd.to_datetime(df['date'])
    df.set_index(['date', 'region_code'], inplace=True)

    # column recovered
    if csv_recovered:
        rec_df = pd.read_csv(csv_recovered)
        rec_df.drop(columns=['CCAA'], inplace=True)
        rec_df.rename(columns={
            'fecha': 'date', 'cod_ine': 'region_code',
            'total': 'recovered'}, inplace=True)
        rec_df['date'] = pd.to_datetime(rec_df['date'])
        rec_df.set_index(['date', 'region_code'], inplace=True)
        df = df.merge(rec_df, left_index=True, right_index=True, how='left')

    # column deceased
    if csv_deceased:
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
        elif scope == 'italy':
            pop_df.set_index('region_name', inplace=True)
            df = df.merge(pop_df, left_on='region',
                          right_index=True, how='left')
        else:
            pop_df.set_index('region_code', inplace=True)
            df = df.merge(pop_df, left_index=True,
                          right_index=True, how='left')
    else:
        df['population'] = 0

    df.fillna(0, inplace=True)
    df.sort_index(inplace=True)

    # add total-italy
    if scope == 'italy':
        dates = df.index.get_level_values('date').unique()
        for date in dates:
            date_df = df.loc[date]
            total = date_df.sum()
            total['region'] = 'Total - Italy'
            df.loc[(date, 0), df.columns] = total.values

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
    df.sort_index(inplace=True)
    df.to_csv(f"{data_directory}/{scope}_covid19gram.csv")


if __name__ == "__main__":
    update_data()

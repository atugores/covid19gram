#!/bin/env python
# -*- coding: utf-8 -*-
import git
import json
import datetime
import pandas as pd
import numpy as np
import os
from shutil import copy2
import logging
import glob
import requests
import io

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

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
            'COVID 19/ccaa_covid19_datos_isciii_nueva_serie.csv',
            'COVID 19/ccaa_covid19_altas_long.csv',
            'COVID 19/ccaa_covid19_fallecidos_por_fecha_defuncion_nueva_serie_long.csv',
            'COVID 19/nacional_covid19_rango_edad.csv',
            'COVID 19/ccaa_pcr_realizadas_diarias.csv',
        ]
    },
    'italy': {
        'base_directory': 'external-data/italy',
        'repo_url': 'https://github.com/pcm-dpc/COVID-19',
        'watch': [
            'dati-regioni/dpc-covid19-ita-regioni.csv'
        ]
    },
    'france': {
        'base_directory': 'external-data/france',
        'repo_url': 'https://github.com/opencovid19-fr/data',
        'watch': [
            'dist/chiffres-cles.csv'
        ]
    },
    'austria': {
        'base_directory': 'external-data/austria',
        'repo_url': 'https://github.com/Daniel-Breuss/covid-data-austria',
        'watch': [
            'austriadata.json'
        ]
    },
    'balears': {
        'base_directory': 'external-data/balears',
        'repo_url': None,
        'watch': [
            'balears_total.csv'
        ]
    },
    'mallorca': {
        'base_directory': 'external-data/balears',
        'repo_url': None,
        'watch': [
            'mallorca_total.csv'
        ]
    },
    'menorca': {
        'base_directory': 'external-data/balears',
        'repo_url': None,
        'watch': [
            'menorca_total.csv'
        ]
    },
    'eivissa': {
        'base_directory': 'external-data/balears',
        'repo_url': None,
        'watch': [
            'eivissa_total.csv'
        ]
    },
}


def update_data(force=False):
    updated = {}
    # scope = 'spain'
    # updated[scope] = update_scope_data(scope, force=force)
    for scope in SCOPES.keys():
        updated[scope] = update_scope_data(scope, force=force)
    updated.update(generate_covidgram_dataset_from_api(force=force))
    return updated


def status_data():
    text = "**Data sources updated at:**\n"
    mtime = None
    for scope in SCOPES.keys():
        base_directory = SCOPES[scope]['base_directory']
        if SCOPES[scope]['repo_url']:
            repo = git.Repo(base_directory)
            headcommit = repo.head.commit
            mtime = datetime.datetime.fromtimestamp(headcommit.committed_date)
        else:
            csv_external = f"{SCOPES[scope]['base_directory']}/{SCOPES[scope]['watch'][0]}"
            mtime = datetime.datetime.fromtimestamp(os.path.getmtime(csv_external))
        text += f"- {scope}: {mtime:%d %b %Y %H:%M:%S}\n"
    return text


def update_scope_data(scope, data_directory="data/", force=False):
    logging.info("Start update data for " + scope)
    if not repository_has_changes(scope, data_directory) and not force:
        logging.info("Finish update data for " + scope + ". No changes in repository")
        return False
    input_files = get_or_generate_input_files(scope, data_directory)
    generate_covidgram_dataset(scope, input_files, data_directory)
    logging.info("Finish update data for " + scope + ". New file created")
    return True


def update_api_scope_data(day, ini_scopes, base_directory):
    filename = f'{base_directory}dapi{day}.json'
    scopes = []
    with open(filename) as json_file:
        d = json.load(json_file)
    if 'error' not in d:
        for country in d['dates'][day]['countries']:
            if country in ini_scopes:
                df = pd.json_normalize(d['dates'][day]['countries'][country], record_path='regions')
                lastupdates = df['date'].unique()
                if day in lastupdates:
                    scopes.append(country)
    return scopes


def get_or_generate_input_files(scope, data_directory="data/"):
    if scope in ['italy', 'france', 'balears', 'mallorca', 'menorca', 'eivissa']:
        base_directory = SCOPES[scope]['base_directory']
        files = [base_directory + "/" + f for f in SCOPES[scope].get('watch', [])]
        return files

    if scope in ['austria']:
        generate_austria_file(data_directory)
        base_directory = SCOPES[scope]['base_directory']
        return [data_directory + scope + '_data.csv']

    if scope == 'spain':
        generate_spain_cases_file(data_directory)
        generate_spain_deceased_file(data_directory)
        base_directory = SCOPES[scope]['base_directory']
        return [
            data_directory + scope + '_cases.csv',
            base_directory + "/" + SCOPES[scope]['watch'][1],
            data_directory + scope + "_deceased.csv",
            base_directory + "/" + SCOPES[scope]['watch'][3],
            base_directory + "/" + SCOPES[scope]['watch'][4]
        ]

    if scope == 'world':
        generate_world_input_files(data_directory)

    return [
        data_directory + scope + '_cases.csv',
        data_directory + scope + '_recovered.csv',
        data_directory + scope + '_deceased.csv'
    ]


def repository_last_changes(scope):
    base_directory = SCOPES[scope]['base_directory']
    files = [base_directory + "/" + f for f in SCOPES[scope].get('watch', [])]
    files_mtime = []
    for f in files:
        files_mtime.append(int(os.path.getmtime(f)))
    return np.max(files_mtime)


def repository_has_changes(scope, data_directory):
    # check if repository exists
    csv_mtime = None
    new_mtime = None
    base_directory = SCOPES[scope]['base_directory']
    if SCOPES[scope]['repo_url']:
        if not os.path.exists(base_directory):
            os.makedirs(base_directory)
            git.Repo.clone_from(SCOPES[scope]['repo_url'], base_directory)
            return True
        original_mtime = repository_last_changes(scope)

        # update repository
        g = git.cmd.Git(base_directory)
        try:
            g.pull()
        except git.GitCommandError as e:
            logging.info("Error pulling data from " + scope + ": " + e.stderr)
            try:
                g.reset('--hard', 'origin/master')
                g.pull()
                logging.info("Error solved with reset --hard")
            except git.GitCommandError as e:
                raise e
        # check if files changed
        new_mtime = repository_last_changes(scope)
        if original_mtime != new_mtime:
            return True
    else:
        # local dataset
        csv_external = f"{SCOPES[scope]['base_directory']}/{SCOPES[scope]['watch'][0]}"
        new_mtime = int(os.path.getmtime(csv_external))
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
                f"{date},{country_code},total-world,{global_cases[date]}\n")
        for date in global_recovered.keys():
            recovered_file.write(
                f"{date},{country_code},total-world,{global_recovered[date]}\n")
        for date in global_deceased.keys():
            deceased_file.write(
                f"{date},{country_code},total-world,{global_deceased[date]}\n")


def generate_spain_cases_file(data_directory):
    """
    The file ccaa_covid19_datos_isciii_nueva_serie.csv
    has information about how many cases are detected each day.
    We have to convert the data to accumulated info
    """
    base_directory = SCOPES['spain']['base_directory']
    csv_cases = base_directory + "/" + SCOPES['spain']['watch'][0]

    cases_df = pd.read_csv(csv_cases)
    cases_df['fecha'] = pd.to_datetime(cases_df['fecha'])
    cases_df.set_index(['fecha', 'cod_ine'], inplace=True)
    cases_df.sort_index(inplace=True)
    cases_df.rename(columns={'ccaa': 'CCAA'}, inplace=True)
    cases_df['total_pcr'] = cases_df.groupby(['CCAA'])['num_casos_prueba_pcr'].cumsum()
    cases_df['total_desc'] = cases_df.groupby(['CCAA'])['num_casos_prueba_desconocida'].cumsum()
    cases_df['total'] = cases_df['total_pcr'] + cases_df['total_desc']
    cases_df.drop(columns=[
        'num_casos', 'num_casos_prueba_pcr', 'num_casos_prueba_test_ac',
        'num_casos_prueba_otras', 'num_casos_prueba_desconocida', 'total_pcr', 'total_desc'], inplace=True)
    cases_df.to_csv(data_directory + 'spain_cases.csv')
    return


def generate_spain_deceased_file(data_directory):
    """
    The file ccaa_covid19_fallecidos_por_fecha_defuncion_nueva_serie_long.csv
    has information about deceases on each day.
    We have to convert the data to accumulated info
    """
    base_directory = SCOPES['spain']['base_directory']
    csv_deceased = base_directory + "/" + SCOPES['spain']['watch'][2]

    dec_df = pd.read_csv(csv_deceased)
    dec_df['fecha'] = pd.to_datetime(dec_df['fecha'])
    dec_df.set_index(['fecha', 'cod_ine'], inplace=True)
    dec_df.sort_index(inplace=True)
    dec_df.rename(columns={'total': 'deceased'}, inplace=True)
    dec_df['total'] = dec_df.groupby(['CCAA'])['deceased'].cumsum()
    dec_df.drop(columns=['deceased'], inplace=True)
    dec_df.to_csv(data_directory + 'spain_deceased.csv')
    return


def generate_austria_file(data_directory):
    """
    The file austriadata.json
    has all de information of a date on the same row for all regions.
    We have to convert the data to a region per row.
    """
    base_directory = SCOPES['austria']['base_directory']
    json_all_regions = base_directory + "/" + SCOPES['austria']['watch'][0]
    regions = ["Wien", "Niederösterreich", "Oberösterreich", "Steiermark", "Tirol", "Kärnten", "Salzburg", "Vorarlberg", "Burgenland"]
    reg_code = {"Wien": 1, "Niederösterreich": 2, "Oberösterreich": 3, "Steiermark": 4, "Tirol": 5, "Kärnten": 6, "Salzburg": 7, "Vorarlberg": 8, "Burgenland": 9, "total-austria": 0}
    text = "date,region_code,region,cases,deceased,hospitalized,recovered\n"
    with open(json_all_regions) as json_file:
        data = json.load(json_file)
        for p in data:
            if p["Tote_v1"]:
                text += "{},0,total-austria,{},{},{},{}\n".format(p['Datum'], p['Fälle_gesamt'], p["Tote_v1"], p["Hospitalisiert"], p["Genesene"])
            else:
                text += "{},0,total-austria,{},0,0,0\n".format(p['Datum'], p['Fälle_gesamt'])
            for region in regions:
                text += "{},{},{},{},{},{},{}\n".format(p['Datum'], reg_code[region], region, p[region], p[region + "_Tote"], p[region + "_Spital"], p[region + "_Genesene"])

    with open(data_directory + "austria_data.csv", "w") as outF:
        outF.writelines(text)
    return


def add_spain_history(scope, df):
    repo = git.Repo(SCOPES[scope]['base_directory'])
    path = f"{SCOPES[scope]['watch'][0]}"
    revlist = ((commit, (commit.tree / path).data_stream.read())for commit in repo.iter_commits(paths=path))
    order = 0
    previous_commited_date = None
    for commit, filecontents in revlist:
        ts = int(commit.committed_date)
        logging.info("Commited on " + datetime.datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S'))
        if order > 0:
            hist_df = pd.read_csv(io.BytesIO(filecontents), encoding='utf8')
            hist_df['fecha'] = pd.to_datetime(hist_df['fecha'])
            hist_df.rename(columns={'fecha': 'date', 'cod_ine': 'region_code'}, inplace=True)
            hist_df.set_index(['date', 'region_code'], inplace=True)
            hist_df.sort_index(inplace=True)
            hist_df.rename(columns={'ccaa': 'CCAA'}, inplace=True)
            hist_df.drop(columns=[
                'num_casos', 'num_casos_prueba_test_ac',
                'num_casos_prueba_otras', ], inplace=True)
            committed_date_pcr = hist_df['num_casos_prueba_pcr'].notnull()[::-1].idxmax()[0]
            commited_date = committed_date_pcr.strftime("%d/%m/%Y")
            commited_date_desc = hist_df['num_casos_prueba_desconocida'].notnull()[::-1].idxmax()[0]
            if commited_date_desc > committed_date_pcr:
                commited_date = commited_date_desc.strftime("%d/%m/%Y")
            if not(previous_commited_date and previous_commited_date == commited_date):
                previous_commited_date = commited_date
                hist_df['total_pcr'] = hist_df.groupby(['CCAA'])['num_casos_prueba_pcr'].cumsum()
                hist_df['total_desc'] = hist_df.groupby(['CCAA'])['num_casos_prueba_desconocida'].cumsum()
                hist_df['total'] = hist_df['total_pcr'] + hist_df['total_desc']
                hist_df.drop(columns=[
                    'num_casos_prueba_pcr', 'num_casos_prueba_desconocida', 'total_pcr', 'total_desc', 'CCAA'], inplace=True)
                hist_df.rename(columns={
                    'fecha': 'date', 'cod_ine': 'region_code',
                    'total': 'cases_' + str(order)}, inplace=True)
                df = df.merge(hist_df, left_index=True, right_index=True, how='left')
                order += 1
        else:
            order += 1
        if order == 10:
            break
    return df


def generate_covidgram_dataset(scope, files, data_directory):
    csv_cases = None
    csv_recovered = None
    csv_deceased = None
    csv_hospitalized = None
    csv_ages = None
    csv_tests = None

    if len(files) == 3:
        csv_cases, csv_recovered, csv_deceased = files
    elif len(files) == 4:
        csv_cases, csv_recovered, csv_deceased, csv_ages = files
    elif len(files) == 5:
        csv_cases, csv_recovered, csv_deceased, csv_ages, csv_tests = files
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
            'terapia_intensiva', 'isolamento_domiciliare',
            'totale_positivi', 'variazione_totale_positivi',
            'nuovi_positivi', 'tamponi', 'note'], inplace=True)

        df.rename(columns={
            'data': 'date', 'codice_regione': 'region_code',
            'totale_casi': 'cases', 'denominazione_regione': 'region',
            'totale_ospedalizzati': 'hospitalized',
            'dimessi_guariti': 'recovered', 'deceduti': 'deceased'}, inplace=True)
        # avoid duplicates
        df['region_code'].mask(df.region == "P.A. Bolzano", '4A', inplace=True)
        df['region_code'].mask(df.region == "P.A. Trento", '4B', inplace=True)
    elif scope == 'france':
        # france date,granularite,maille_code,maille_nom,cas_confirmes,cas_ehpad,cas_confirmes_ehpad,cas_possibles_ehpad,deces,deces_ehpad,reanimation,hospitalises,gueris,depistes,source_nom,source_url,source_archive,source_type
        # accept:
        #   - granularite=pays + source_type=ministere-sante
        #   - granularite=region + source_type=opencovid19-fr
        # columns: date,maille_code,maille_nom - deces,hospitalises,gueris and cas_confirmes (only availabre for pays)
        df = df[((df.granularite == 'pays') & (df.source_type == 'ministere-sante')) | ((df.granularite == 'region') & (df.source_type == 'opencovid19-fr'))]
        df.drop(columns=[
            'cas_ehpad', 'granularite', 'cas_confirmes_ehpad', 'cas_possibles_ehpad',
            'deces_ehpad', 'reanimation', 'depistes', 'source_nom', 'source_url', 'source_archive', 'source_type'], inplace=True)
        df.rename(columns={
            'maille_code': 'region_code',
            'cas_confirmes': 'cases', 'maille_nom': 'region',
            'hospitalises': 'hospitalized',
            'gueris': 'recovered', 'deces': 'deceased'}, inplace=True)
        df['region'].mask(df.region_code == 'FRA', 'total-france', inplace=True)

    df['date'] = pd.to_datetime(df['date'])
    df.set_index(['date', 'region_code'], inplace=True)
    dates = df.index.get_level_values(0)

    # history columns
    if scope == 'spain':
        df = add_spain_history(scope, df)

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

    # column deceased
    if csv_hospitalized:
        hos_df = pd.read_csv(csv_hospitalized)
        hos_df.drop(columns=['CCAA'], inplace=True)
        hos_df.rename(columns={
            'fecha': 'date', 'cod_ine': 'region_code',
            'total': 'hospitalized'}, inplace=True)
        hos_df['date'] = pd.to_datetime(hos_df['date'])
        hos_df.set_index(['date', 'region_code'], inplace=True)
        df = df.merge(hos_df, left_index=True, right_index=True, how='left')

    # column tests
    if csv_tests:
        test_df = pd.read_csv(csv_tests)
        test_df.drop(columns=['CCAA', 'Positividad'], inplace=True)
        test_df.rename(columns={
            'Fecha': 'date', 'cod_ine': 'region_code', 'PCR Realizadas': 'daily_tests'}, inplace=True)
        test_df['date'] = pd.to_datetime(test_df['date'])
        test_df['daily_tests'] = test_df['daily_tests'].str.replace(',', '.')
        test_df['daily_tests'].replace('-', np.nan, inplace=True)

        test_df['daily_tests'] = pd.to_numeric(test_df['daily_tests'])
        test_df.set_index(['date', 'region_code'], inplace=True)

    # jut copy by ages data to the date directory
    if csv_ages:
        copy2(csv_ages, f"{data_directory}/{scope}_ages.csv")

    # column population
    if os.path.isfile(f"{data_directory}/{scope}_population.csv"):
        pop_df = pd.read_csv(f"{data_directory}/{scope}_population.csv")
        if scope == 'world':
            pop_df.set_index('country_name', inplace=True)
            df = df.merge(pop_df, left_on='region',
                          right_index=True, how='left')
        elif scope in ['italy', 'france', 'austria', 'balears', 'mallorca', 'menorca', 'eivissa']:
            pop_df.set_index('region_name', inplace=True)
            df = df.merge(pop_df, left_on='region',
                          right_index=True, how='left')
        else:
            pop_df.set_index('region_code', inplace=True)
            df = df.merge(pop_df, left_index=True,
                          right_index=True, how='left')
    else:
        df['population'] = 0

    df.sort_index(inplace=True)
    # remove duplicated rows (fix France data)
    df = df[~df.index.duplicated(keep='last')]

    # add total-italy
    if scope in ['italy', 'spain']:
        dates = df.index.get_level_values('date').unique()
        for date in dates:
            date_df = df.loc[date]
            total = date_df.sum(min_count=1)
            total['region'] = f'total-{scope}'
            df.loc[(date, 0), df.columns] = total.values

    df['cases_per_100k'] = df['cases'] * 100_000 / df['population']
    df['deceased_per_100k'] = df['deceased'] * 100_000 / df['population']
    df['active_cases'] = df['cases'] - df['recovered'] - df['deceased']
    df['active_cases_per_100k'] = df['active_cases'] * 100_000 / df['population']
    if 'cases_1' in df.columns:
        for i in range(1, 10):
            df['acum14_cases_' + str(i)] = 0.0
            df['acum14_cases_per_100k_' + str(i)] = 0.0
            df['increase_cases_' + str(i)] = 0.0

    if 'hospitalized' in df.columns:
        df['hosp_per_100k'] = df['hospitalized'] * 100_000 / df['population']
        df['increase_hosp'] = 0.0
        df['rolling_hosp'] = 0.0
        df['rolling_hosp_per_100k'] = 0.0

    if 'daily_tests' in df.columns:
        df['testing_rate'] = 0.0
        df['positivity_rate'] = 0.0

    df['increase_cases'] = 0.0
    df['increase_cases_per_100k'] = 0.0
    df['rolling_cases'] = 0.0
    df['rolling_cases_per_100k'] = 0.0
    df['Rt'] = 0.0
    df['epg'] = 0.0
    df['acum14_cases'] = 0.0
    df['acum14_cases_per_100k'] = 0.0
    df['acum14_hosp'] = 0.0
    df['acum14_hosp_per_100k'] = 0.0

    df['increase_deceased'] = 0.0
    df['rolling_deceased'] = 0.0
    df['rolling_deceased_per_100k'] = 0.0
    df['acum14_deceased'] = 0.0
    df['acum14_deceased_per_100k'] = 0.0

    for region in df['region'].unique():
        reg_df = df[df.region == region]
        # cases
        increase = reg_df['cases'] - reg_df['cases'].shift(1)
        increase[increase < 0] = 0.0
        rolling = increase.rolling(window=7).mean()
        df['increase_cases'].mask(df.region == region, increase, inplace=True)
        df['rolling_cases'].mask(df.region == region, rolling, inplace=True)
        df['increase_cases_per_100k'] = df['increase_cases'] * 100_000 / df['population']
        df['rolling_cases_per_100k'] = df['rolling_cases'] * 100_000 / df['population']
        # cases acum
        rolling = increase.rolling(window=14).sum()
        df['acum14_cases'].mask(df.region == region, rolling, inplace=True)
        df['acum14_cases_per_100k'] = df['acum14_cases'] * 100_000 / df['population']
        # EPG
        p = increase.rolling(3).sum() / (increase.rolling(7).sum() - increase.rolling(4).sum())
        p.loc[~np.isfinite(p)] = np.nan
        p.fillna(method='ffill')
        p7 = p.rolling(7).mean()
        epg = p7 * df['acum14_cases']
        df['Rt'].mask(df.region == region, p7, inplace=True)
        df['epg'].mask(df.region == region, epg, inplace=True)
        # cases history
        if 'cases_1' in df.columns:
            for i in range(1, 10):
                increase = reg_df['cases_' + str(i)] - reg_df['cases_' + str(i)].shift(1)
                increase[increase < 0] = 0.0
                df['increase_cases_' + str(i)].mask(df.region == region, increase, inplace=True)
                rolling = increase.rolling(window=14).sum()
                df['acum14_cases_' + str(i)].mask(df.region == region, rolling, inplace=True)
                df['acum14_cases_per_100k_' + str(i)] = df['acum14_cases_' + str(i)] * 100_000 / df['population']
        # deceased
        increase = reg_df['deceased'] - reg_df['deceased'].shift(1)
        increase[increase < 0] = 0.0
        rolling = increase.rolling(window=7).mean()
        df['increase_deceased'].mask(df.region == region, increase, inplace=True)
        df['rolling_deceased'].mask(df.region == region, rolling, inplace=True)
        df['rolling_deceased_per_100k'] = df['rolling_deceased'] * 100_000 / df['population']
        # deceased acum
        rolling = increase.rolling(window=14).sum()
        df['acum14_deceased'].mask(df.region == region, rolling, inplace=True)
        df['acum14_deceased_per_100k'] = df['acum14_deceased'] * 100_000 / df['population']
        # test positivity rates
        if 'daily_tests' in df.columns:
            rolling = reg_df['daily_tests'].rolling(window=7).sum()
            df['testing_rate'].mask(df.region == region, increase, inplace=True)
            df['testing_rate'] = df['testing_rate'] * 100_000 / df['population']
            rolling_positive = reg_df['increase_cases'].rolling(window=7).sum()
            pos_rate = rolling_positive / rolling
            df['positivity_rate'].mask(df.region == region, pos_rate, inplace=True)
        # hospitalized
        if 'hospitalized' in df.columns:
            increase = reg_df['hospitalized'] - reg_df['hospitalized'].shift(1)
            increase[increase < 0] = 0.0
            rolling = increase.rolling(window=7).mean()
            df['increase_hosp'].mask(df.region == region, increase, inplace=True)
            df['rolling_hosp'].mask(df.region == region, rolling, inplace=True)
            df['rolling_hosp_per_100k'] = df['rolling_hosp'] * 100_000 / df['population']
            # hosp acum
            rolling = increase.rolling(window=14).sum()
            df['acum14_hosp'].mask(df.region == region, rolling, inplace=True)
            df['acum14_hosp_per_100k'] = df['acum14_hosp'] * 100_000 / df['population']

    df.sort_index(inplace=True)
    df.to_csv(f"{data_directory}/{scope}_covid19gram.csv")


def generate_covidgram_dataset_from_api(data_directory="data/", force=False, base_directory='external-data/acovid19tracking/'):
    ini_scopes = ['Argentina', 'Australia', 'Brazil', 'Canada', 'Chile', 'China', 'Colombia', 'Germany', 'India', 'Mexico', 'Portugal', 'US', 'United Kingdom']
    dfc = {}
    updated = {}
    has_country = []
    scopes = []
    start = datetime.datetime.strptime('2020-02-10 00:00:00', '%Y-%m-%d %H:%M:%S')
    url = 'https://api.covid19tracking.narrativa.com/api/'
    now = datetime.datetime.now()
    logging.info("Start update data for API")
    # default update to false
    for scope in ini_scopes:
        updated[scope.lower().replace(' ', '')] = False

    # Download data and check for new country data
    today = now.strftime("%Y-%m-%d")
    today_filename = f'{base_directory}dapi{today}.json'

    # create base directory if does not exist
    os.makedirs(base_directory, exist_ok=True)

    if not os.path.isfile(today_filename):
        r = requests.get(url + today, allow_redirects=True)
        with open(today_filename, 'wb') as f:
            f.write(r.content)
        if os.path.isfile(today_filename):
            scopes = update_api_scope_data(today, ini_scopes, base_directory)
    else:
        old_scopes = update_api_scope_data(today, ini_scopes, base_directory)
        r = requests.get(url + today, allow_redirects=True)
        with open(today_filename, 'wb') as f:
            f.write(r.content)
        new_scopes = update_api_scope_data(today, ini_scopes, base_directory)
        scopes = [item for item in new_scopes if item not in old_scopes]

    if force:
        scopes = ini_scopes

    # generate csv only if there is new data
    if len(scopes) > 0:
        filenames = glob.glob(f'{base_directory}*.json')

        for fname in filenames:
            with open(fname) as json_file:
                d = json.load(json_file)
            if 'error' not in d:
                for dates in d['dates']:
                    for scope in scopes:
                        if scope in has_country:
                            dfr = pd.json_normalize(d['dates'][dates]['countries'][scope], record_path='regions',)
                            dfr.drop(columns=['sub_regions', ], inplace=True)
                            dfc[scope] = dfc[scope].append(dfr, ignore_index=True)
                        else:
                            dfr = pd.json_normalize(d['dates'][dates]['countries'][scope], record_path='regions')
                            dfr.drop(columns=['sub_regions', ], inplace=True)
                            dfc[scope] = dfr
                            has_country.append(scope)

        # date,name,id,source,today_confirmed,today_deaths,today_new_confirmed,today_new_deaths,today_new_open_cases,today_new_recovered,today_new_tests,today_new_total_hospitalised_patients,today_open_cases,today_recovered,today_tests,today_total_hospitalised_patients,today_vs_yesterday_confirmed,today_vs_yesterday_deaths,today_vs_yesterday_open_cases,today_vs_yesterday_recovered,today_vs_yesterday_tests,today_vs_yesterday_total_hospitalised_patients,yesterday_confirmed,yesterday_deaths,yesterday_open_cases,yesterday_recovered,yesterday_tests,yesterday_total_hospitalised_patients
        for scope in scopes:
            logging.info("Start update data for " + scope.lower().replace(' ', ''))
            if scope == 'Canada':
                dfc[scope] = dfc[scope][dfc[scope]['name'] != 'Grand Princess']
            if scope == 'Colombia':
                dfc[scope].replace(to_replace="San Andrés y Provincia", value="San Andrés y Providencia")
            if scope == 'France':
                dfc[scope] = dfc[scope][dfc[scope]['name'] != 'Guyane']
            if scope == "Germany":
                oficial = {'Bavaria': 'Bayern', 'Rhineland-Palatinate': 'Rheinland-Pfalz', 'Niedersachsen': 'Lower Saxony', 'North Rhine-Westphalia': 'Nordrhein-Westfalen', 'Baden-Wuerttemberg': 'Baden-Württemberg', 'Mecklenburg-Vorpommern': 'Mecklenburg-Vorpommern', 'Saxony': 'Sachsen', 'Thuringia': 'Thüringen', 'Saxony-Anhalt': 'Sachsen-Anhalt', 'Hesse': 'Hessen'}
                for name in oficial.keys():
                    dfc[scope]['name'] = dfc[scope]['name'].str.replace(name, oficial[name])
            if scope == 'Portugal':
                dfc[scope] = dfc[scope][dfc[scope]['name'] != 'Estrangeiro']
            if scope == "Argentina":
                dfc[scope].loc[dfc[scope]['name'] == "Ciudad Autónoma de Buenos Aires", 'name'] = "Ciudad de Buenos Aires"

            dfc[scope].rename(columns={'id': 'region_code', 'name': 'region',
                                       'today_confirmed': 'cases', 'today_deaths': 'deceased',
                                       'today_recovered': 'recovered',
                                       'today_open_cases': 'active_cases',
                                       'today_total_hospitalised_patients': 'hospitalized',
                                       'today_intensive_care': 'intensivecare'}, inplace=True)

            if 'today_tests' in dfc[scope].columns:
                dfc[scope].rename(columns={'today_tests': 'tests'}, inplace=True)
                dfc[scope].drop(dfc[scope].columns.difference(['date', 'region_code', 'region', 'cases', 'deceased', 'recovered', 'active_cases', 'hospitalized', 'tests']), axis=1, inplace=True)
            else:
                dfc[scope].drop(dfc[scope].columns.difference(['date', 'region_code', 'region', 'cases', 'deceased', 'recovered', 'active_cases', 'hospitalized']), axis=1, inplace=True)

            dfc[scope]['date'] = pd.to_datetime(dfc[scope]['date'])
            # delete noisy data
            if scope != 'China':
                dfc[scope] = dfc[scope][dfc[scope]['date'] >= start]

            dfc[scope].set_index(['date', 'region_code'], inplace=True)
            dfc[scope].sort_index(inplace=True)
            dfc[scope] = dfc[scope][~dfc[scope].index.duplicated(keep='last')]

            # add total-scope
            dates = dfc[scope].index.get_level_values('date').unique()
            for date in dates:
                date_df = dfc[scope].loc[date]
                total = date_df.sum(min_count=1)
                total['region'] = 'total-' + scope.lower().replace(' ', '')
                dfc[scope].loc[(date, 'ñññ'), dfc[scope].columns] = total.values

            if os.path.isfile(f"{data_directory}/{scope.lower().replace(' ', '')}_population.csv"):
                pop_df = pd.read_csv(f"{data_directory}/{scope.lower().replace(' ', '')}_population.csv")
                pop_df.set_index('region_name', inplace=True)
                dfc[scope] = dfc[scope].merge(pop_df, left_on='region', right_index=True, how='left')
            dfc[scope]['cases_per_100k'] = dfc[scope]['cases'] * 100_000 / dfc[scope]['population']
            dfc[scope]['deceased_per_100k'] = dfc[scope]['deceased'] * 100_000 / dfc[scope]['population']
            dfc[scope]['active_cases_per_100k'] = dfc[scope]['active_cases'] * 100_000 / dfc[scope]['population']
            if 'hospitalized' in dfc[scope].columns:
                dfc[scope]['hosp_per_100k'] = dfc[scope]['hospitalized'] * 100_000 / dfc[scope]['population']
                dfc[scope]['increase_hosp'] = 0.0
                dfc[scope]['rolling_hosp'] = 0.0
                dfc[scope]['rolling_hosp_per_100k'] = 0.0
            dfc[scope]['increase_cases'] = 0.0
            dfc[scope]['increase_cases_per_100k'] = 0.0
            dfc[scope]['rolling_cases'] = 0.0
            dfc[scope]['rolling_cases_per_100k'] = 0.0
            dfc[scope]['Rt'] = 0.0
            dfc[scope]['epg'] = 0.0
            dfc[scope]['acum14_cases'] = 0.0
            dfc[scope]['acum14_cases_per_100k'] = 0.0
            dfc[scope]['acum14_hosp'] = 0.0
            dfc[scope]['acum14_hosp_per_100k'] = 0.0

            dfc[scope]['increase_deceased'] = 0.0
            dfc[scope]['rolling_deceased'] = 0.0
            dfc[scope]['rolling_deceased_per_100k'] = 0.0
            dfc[scope]['acum14_deceased'] = 0.0
            dfc[scope]['acum14_deceased_per_100k'] = 0.0

            for region in dfc[scope]['region'].unique():
                reg_df = dfc[scope][dfc[scope].region == region]
                # cases
                increase = reg_df['cases'] - reg_df['cases'].shift(1)
                increase[increase < 0] = 0.0
                rolling = increase.rolling(window=7).mean()
                dfc[scope]['increase_cases'].mask(dfc[scope].region == region, increase, inplace=True)
                dfc[scope]['rolling_cases'].mask(dfc[scope].region == region, rolling, inplace=True)
                dfc[scope]['increase_cases_per_100k'] = dfc[scope]['increase_cases'] * 100_000 / dfc[scope]['population']
                dfc[scope]['rolling_cases_per_100k'] = dfc[scope]['rolling_cases'] * 100_000 / dfc[scope]['population']
                # cases acum
                rolling = increase.rolling(window=14).sum()
                dfc[scope]['acum14_cases'].mask(dfc[scope].region == region, rolling, inplace=True)
                dfc[scope]['acum14_cases_per_100k'] = dfc[scope]['acum14_cases'] * 100_000 / dfc[scope]['population']
                # EPG
                p = increase.rolling(3).sum() / (increase.rolling(7).sum() - increase.rolling(4).sum())
                p.loc[~np.isfinite(p)] = np.nan
                p.fillna(method='ffill')
                p7 = p.rolling(7).mean()
                epg = p7 * dfc[scope]['acum14_cases']
                dfc[scope]['Rt'].mask(dfc[scope].region == region, p7, inplace=True)
                dfc[scope]['epg'].mask(dfc[scope].region == region, epg, inplace=True)
                # deceased
                increase = reg_df['deceased'] - reg_df['deceased'].shift(1)
                increase[increase < 0] = 0.0
                rolling = increase.rolling(window=7).mean()
                dfc[scope]['increase_deceased'].mask(dfc[scope].region == region, increase, inplace=True)
                dfc[scope]['rolling_deceased'].mask(dfc[scope].region == region, rolling, inplace=True)
                dfc[scope]['rolling_deceased_per_100k'] = dfc[scope]['rolling_deceased'] * 100_000 / dfc[scope]['population']
                # deceased acum
                rolling = increase.rolling(window=14).sum()
                dfc[scope]['acum14_deceased'].mask(dfc[scope].region == region, rolling, inplace=True)
                dfc[scope]['acum14_deceased_per_100k'] = dfc[scope]['acum14_deceased'] * 100_000 / dfc[scope]['population']
                # hospitalized
                if 'hospitalized' in dfc[scope].columns:
                    increase = reg_df['hospitalized'] - reg_df['hospitalized'].shift(1)
                    increase[increase < 0] = 0.0
                    rolling = increase.rolling(window=7).mean()
                    dfc[scope]['increase_hosp'].mask(dfc[scope].region == region, increase, inplace=True)
                    dfc[scope]['rolling_hosp'].mask(dfc[scope].region == region, rolling, inplace=True)
                    dfc[scope]['rolling_hosp_per_100k'] = dfc[scope]['rolling_hosp'] * 100_000 / dfc[scope]['population']
                # hosp acum
                rolling = increase.rolling(window=14).sum()
                dfc[scope]['acum14_hosp'].mask(dfc[scope].region == region, rolling, inplace=True)
                dfc[scope]['acum14_hosp_per_100k'] = dfc[scope]['acum14_hosp'] * 100_000 / dfc[scope]['population']

            dfc[scope].sort_index(inplace=True)
            dfc[scope].to_csv(f"{data_directory}/{scope.lower().replace(' ', '')}_covid19gram.csv")
            logging.info(f"Finish update data for {scope.lower().replace(' ', '')}. New file created")
            updated[scope.lower().replace(' ', '')] = True
    else:
        logging.info("Finish update data for API. No changes in repository")
    return updated


if __name__ == "__main__":
    update_data(force=True)

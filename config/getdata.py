#!/bin/env python
# -*- coding: utf-8 -*-
import git
import json
import datetime
from shutil import copy2


def pull_global(base_directory="covid19/", data_directory="data/"):
    g = git.cmd.Git(base_directory)
    g.pull()
    # TODO: change to logging
    print("[" + datetime.datetime.now().strftime("%d.%b %Y %H:%M:%S") + "] " + "Start pulling global Data")

    import_file_path = base_directory + "/public/data/all.json"

    with open(import_file_path) as json_file:
        data = json.load(json_file)

    export_cases = data_directory + 'world_cases.csv'
    export_recovered = data_directory + 'world_recovered.csv'
    export_deceased = data_directory + 'world_deceased.csv'
    with open(export_cases, 'w') as cases_file, open(export_recovered, 'w') as recovered_file, open(export_deceased, 'w') as deceased_file:
        cases_file.write("fecha,cod_ine,CCAA,total\n")
        recovered_file.write("fecha,cod_ine,CCAA,total\n")
        deceased_file.write("fecha,cod_ine,CCAA,total\n")

        country_code = 0
        for country in data.values():
            country_name = country.get('ENGLISH')
            cases = country.get('confirmedCount', {})
            for date, value in cases.items():
                cases_file.write(
                    f"{date},{country_code},{country_name},{value}\n")

            cured = country.get('curedCount', {})
            for date, value in cured.items():
                recovered_file.write(
                    f"{date},{country_code},{country_name},{value}\n")

            dead = country.get('deadCount', {})
            for date, value in dead.items():
                deceased_file.write(
                    f"{date},{country_code},{country_name},{value}\n")

            country_code = country_code + 1

    print("[" + datetime.datetime.now().strftime("%d.%b %Y %H:%M:%S") +
          "] " + "Finish pulling global Data")


def pull_datasets(base_directory="datasets/", data_directory="data/"):
    g = git.cmd.Git(base_directory)
    # TODO: change to logging
    print("[" + datetime.datetime.now().strftime("%d.%b %Y %H:%M:%S") + "] " + "Start pulling Spain Data")
    import_file_path = base_directory + "COVID 19/"
    g.pull()
    copy2(import_file_path + "ccaa_covid19_casos_long.csv", data_directory + "spain_cases.csv")
    copy2(import_file_path + "ccaa_covid19_altas_long.csv", data_directory + "spain_recovered.csv")
    copy2(import_file_path + "ccaa_covid19_fallecidos_long.csv", data_directory + "spain_deceased.csv")
    print("[" + datetime.datetime.now().strftime("%d.%b %Y %H:%M:%S") + "] " + "Finish pulling Spain Data")
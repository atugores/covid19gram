import csv
from collections import OrderedDict
from datetime import date, timedelta

CCAA = {
    "01": "Andalucía",
    "02": "Aragón",
    "03": "Asturias",
    "04": "Baleares",
    "05": "Canarias",
    "06": "Cantabria",
    "07": "Castilla y León",
    "08": "Castilla La Mancha",
    "09": "Cataluña",
    "10": "C. Valenciana",
    "11": "Extremadura",
    "12": "Galicia",
    "13": "Madrid",
    "14": "Murcia",
    "15": "Navarra",
    "16": "País Vasco",
    "17": "La Rioja",
    "18": "Ceuta",
    "19": "Melilla"
}

provincias = {
    "01": ["04", "11", "14", "18", "21", "23", "29", "41"],
    "02": ["22", "44", "50"],
    "03": ["33"],
    "04": ["07"],
    "05": ["35", "38"],
    "06": ["39"],
    "07": ["05", "09", "24", "34", "37", "40", "42", "47", "49"],
    "08": ["02", "13", "16", "19", "45"],
    "09": ["08", "17", "25", "43"],
    "10": ["03", "12", "46"],
    "11": ["06", "10"],
    "12": ["15", "27", "32", "36"],
    "13": ["28"],
    "14": ["30"],
    "15": ["31"],
    "16": ["01", "48", "20"],
    "17": ["26"],
    "18": ["51"],
    "19": ["52"],
}

codiCCAA = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19"]


def prov2caa(file, outfile):
    f = open(file)
    csv_f = csv.reader(f)
    dades = {}
    for row in csv_f:
        for codi in codiCCAA:
            if row[1] in provincias[codi]:
                if codi not in dades:
                    dades[codi] = {}
                casos = int(row[4])
                if codi == "08":
                    casos = int(row[4]) + int(row[7])
                if row[0] in dades[codi]:
                    dades[codi][row[0]][0] += int(row[3])
                    dades[codi][row[0]][1] += casos
                else:
                    dades[codi][row[0]] = [int(row[3]), casos]

    sum_dades = {}
    for codi in codiCCAA:
        sum_dades[codi] = {}
        ordered = OrderedDict(sorted(dades[codi].items(), key=lambda t: t[0]))
        total_acumulat = 0
        total_pcr_acumulat = 0
        for item in ordered.keys():
            total_acumulat += dades[codi][item][0]
            total_pcr_acumulat += dades[codi][item][1]
            sum_dades[codi][item] = [total_acumulat, total_pcr_acumulat]

    with open(outfile, 'w') as the_file:
        the_file.write("fecha,cod_ine,CCAA,total\n")
        for codi in codiCCAA:
            for day in sum_dades[codi].keys():
                the_file.write(day + "," + codi + "," + CCAA[codi] + "," + str(sum_dades[codi][day][1]) + "\n")


def decesed_long(file, outfile):
    f = open(file)
    csv_f = csv.reader(f)

    with open(outfile, 'w') as the_file:
        # the_file.write("fecha,cod_ine,CCAA,total\n")
        for line in csv_f:
            the_file.write(line[0] + "," + line[1] + "," + line[2] + "," + line[3] + "\n")
            if line[0] == "2020-05-24":
                sdate = date(2020, 5, 25)  # start date
                edate = date.today()  # end date
                delta = edate - sdate  # as timedelta
                for i in range(delta.days + 1):
                    day = sdate + timedelta(days=i)
                    the_file.write(day.strftime('%Y-%m-%d') + "," + line[1] + "," + line[2] + "," + line[3] + "\n")


if __name__ == "__main__":
    prov2caa('external-data/spain/COVID 19/provincias_covid19_datos_isciii_nueva_serie.csv', 'data/spain_pcr.csv')
    decesed_long('external-data/spain/COVID 19/ccaa_covid19_fallecidos_long.csv', 'data/spain_deceased.csv')

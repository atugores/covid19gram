import git
import json
from shutil import copy2


#fetch db data
def pull_global(base_directory="covid19/",data_directory="data"):
    g = git.cmd.Git(base_directory)
    g.pull()
    import_file_path = base_directory + "/public/data/all.json"
    export_file_path = "data/"
    casos = open(export_file_path+'global_covid19_casos_long.csv', 'w')
    altas = open(export_file_path+'global_covid19_altas_long.csv', 'w')
    defun = open(export_file_path+'global_covid19_fallecidos_long.csv', 'w')
    casos.write("fecha,cod_ine,CCAA,total\n")  # python will convert \n to os.linesep
    altas.write("fecha,cod_ine,CCAA,total\n")
    defun.write("fecha,cod_ine,CCAA,total\n")
    codi = 0
    with open(import_file_path) as json_file:
        data = json.load(json_file)
        for p in data:
            # print(p)
            # print(data[p]['ENGLISH'])
            if 'confirmedCount' in  data[p]:
                for d in data[p]['confirmedCount']:
                    try:
                        casos.write(d+","+str(codi)+","+data[p]['ENGLISH']+","+str(data[p]['confirmedCount'][d])+"\n")
                    except:
                        print("none")
            if 'curedCount' in  data[p]:
                for d in data[p]['curedCount']:
                    try:
                        altas.write(d+","+str(codi)+","+data[p]['ENGLISH']+","+str(data[p]['curedCount'][d])+"\n")
                    except:
                        print("none")
            if 'deadCount' in  data[p]:
                for d in data[p]['deadCount']:
                    try:
                        defun.write(d+","+str(codi)+","+data[p]['ENGLISH']+","+str(data[p]['deadCount'][d])+"\n")
                    except:
                        print("none")
            codi += 1

    casos.close()
    altas.close()
    defun.close()

def pull_datasets(base_directory="datasets/",data_directory="data/"):
    g = git.cmd.Git(base_directory)
    import_file_path = base_directory +"COVID 19/"
    g.pull()
    copy2(import_file_path + "ccaa_covid19_casos_long.csv", data_directory + "ccaa_covid19_casos_long.csv")
    copy2(import_file_path + "ccaa_covid19_altas_long.csv", data_directory + "ccaa_covid19_altas_long.csv")
    copy2(import_file_path + "ccaa_covid19_fallecidos_long.csv", data_directory + "ccaa_covid19_fallecidos_long.csv")


pull_datasets()
pull_global()

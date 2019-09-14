import subprocess

entornoGrafico = str()
for i in ["dolphin", "caja", "nautilus"]:
    ejecucion = subprocess.Popen("{} -h".format(i), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = ejecucion.communicate()
    if ejecucion.returncode == 0:
        entornoGrafico = i

if entornoGrafico is not None:
    print(entornoGrafico)

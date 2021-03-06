import os
import subprocess

OG_PATH = '/opt/opengnsys/'

def poweroff():
	if os.path.exists('/scripts/oginit'):
		subprocess.call('source ' + OG_SCRIPT_PATH + 'etc/preinit/loadenviron.sh; ' + OG_SCRIPT_PATH + 'scripts/poweroff', shell=True)
	else:
		subprocess.call(['/sbin/poweroff'])

def reboot():
	if os.path.exists('/scripts/oginit'):
		subprocess.call('source ' + OG_SCRIPT_PATH + 'etc/preinit/loadenviron.sh; ' + OG_SCRIPT_PATH + 'scripts/reboot', shell=True)
	else:
		subprocess.call(['/sbin/reboot'])

def execCMD(httpparser):
	cmd = httpparser.getCMD()
	cmds = cmd.split(" ")
	try:
		result = subprocess.check_output(cmds)
	except:
		raise ValueError('Error: Incorrect command value')

	return result.decode('utf-8')

def procsession(httpparser):
	disk = httpparser.getDisk()
	partition = httpparser.getPartition()

	try:
		result = subprocess.check_output([OG_PATH + 'interfaceAdm/IniciarSesion', disk, partition], shell=True)
	except:
		raise ValueError('Error: Incorrect command value')

	return result.decode('utf-8')

def procsoftware(httpparser, path):
	disk = httpparser.getDisk()
	partition = httpparser.getPartition()

	try:
		result = subprocess.check_output([OG_PATH + 'interfaceAdm/InventarioSoftware', disk, partition, path], shell=True)
	except:
		raise ValueError('Error: Incorrect command value')

	return result.decode('utf-8')

def prochardware(path):
	try:
		result = subprocess.check_output([OG_PATH + 'interfaceAdm/InventarioHardware', path], shell=True)
	except:
		raise ValueError('Error: Incorrect command value')

	return result.decode('utf-8')

def procsetup(httpparser):
	disk = httpparser.getDisk()
	cache = httpparser.getCache()
	cachesize = httpparser.getCacheSize()
	partlist = httpparser.getPartitionSetup()
	listConfigs = []

	for part in partlist:
		i = 0
		json = {}
		cfg = 'dis=' + disk + '*che=' + cache + '*tch=' + cachesize + '!par=' + part["partition"] + '*cpt='+part["code"] + '*sfi=' + part['filesystem'] + '*tam=' + part['size'] + '*ope=' + part['format'] + '%'
		try:
			subprocess.check_output([OG_PATH + 'interfaceAdm/Configurar', disk, cfg], shell=True)
		except:
			continue

		result = subprocess.check_output([OG_PATH + 'interfaceAdm/getConfiguration'], shell=True)
		val = result.decode('utf-8').rstrip().split('\t')
		while i < len(val):
			val[i] = val[i].split('=')[1]
			i += 1

		json['partition'] = val[1]
		json['code'] = val[4]
		json['filesystem'] = val[2]
		json['size'] = val[5]
		json['format'] = val[6]
		listConfigs.append(json)

	return listConfigs

def procirestore(httpparser):
	disk = httpparser.getDisk()
	partition = httpparser.getPartition()
	name = httpparser.getName()
	repo = httpparser.getRepo()
	ctype = httpparser.getType()
	profile = httpparser.getProfile()
	cid = httpparser.getId()

	try:
		result = subprocess.check_output([OG_PATH + 'interfaceAdm/RestaurarImagen', disk, partition, name, repo, ctype], shell=True)
	except:
		raise ValueError('Error: Incorrect command value')

	return result.decode('utf-8')

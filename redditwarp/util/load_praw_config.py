
import os
import configparser

def load_praw_config():
	inifile = 'praw.ini'
	locations = []
	if 'XDG_CONFIG_HOME' in os.environ:
		locations.append(os.path.join(os.environ['XDG_CONFIG_HOME'], inifile))
	if 'HOME' in os.environ:
		locations.append(os.path.join(os.environ['HOME'], '.config', inifile))
	if 'APPDATA' in os.environ:
		locations.append(os.path.join(os.environ['APPDATA'], inifile))
	locations.append(inifile)

	config = configparser.ConfigParser()
	config.read(locations)
	return config

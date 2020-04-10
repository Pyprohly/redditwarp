
import sys
from os import path as op
from os import getenv
import configparser

def get_praw_ini_potential_locations():
	inifile = 'praw.ini'

	tlp_dir = ''
	if __name__ != '__main__':
		top_level_package_name, _, _ = __name__.partition('.')
		tlp_module = sys.modules[top_level_package_name]
		tlp_dir = op.dirname(tlp_module.__file__)

	getenv2 = lambda key: getenv(key, '')
	location_components = [
		(tlp_dir,),  # Package default
		(getenv2('APPDATA'),),  # Windows
		(getenv2('HOME'), '.config',),  # Legacy Linux and macOS
		(getenv2('XDG_CONFIG_HOME'),),  # Modern Linux
		('.',),  # Current working directory
	]

	locations = [
		op.join(*comps, inifile)
		for comps in location_components
		if comps[0]
	]
	return locations

def load_praw_config():
	config = configparser.ConfigParser()
	config.read(get_praw_ini_potential_locations())
	return config

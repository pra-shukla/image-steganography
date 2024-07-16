import json
import os

path = os.getcwd().split('\\')
path = '\\'.join(path[:len(path) - path[: : -1].index('Steganography')])
dnt_path = path + '\\do-not-change.json'
set_path = path + '\\settings.json'
del path

class Settings:
	'''class Settings deals with ./do-not-change.json and ./settings.json'''

	@staticmethod
	def __OW(static, dynamic) -> None:
		for key, value in dynamic.items():
			if isinstance(value, dict) and key in static and isinstance(static[key], dict):
				Settings.__OW(static[key], value)
			else:
				static[key] = value
		return None

	@staticmethod
	def failsafe(func):
		def ret(*args, **kwargs):
			try:
				return func(*args, **kwargs)
			except:
				Settings.settings_ready = False
		return ret

	@failsafe
	def __init__(self) -> None:
		with open(dnt_path, 'r') as f:
			self.static = json.load(f)

		try:
			with open(set_path, 'r') as f:
				self.dynamic = json.load(f)
		except:
			with open('settings.json', 'w') as f:
				f.write(json.dumps(dict(), indent = 4))

		self.__overwrite()
		self.settings_ready = True
		return None

	@failsafe
	def get(self, path: str):
		val = self.static
		for obj in path.split('.'):
			val = val[obj]
		return val

	@failsafe
	def __overwrite(self) -> None:
		Settings.__OW(self.static, self.dynamic)
		return None

	@failsafe
	def update(self, path: str, value) -> None:
		temp = self.static
		objects = path.split('.')
		for obj in objects[:-1]:
			temp = temp[obj]
		temp[objects[-1]] = value
		self.__path_to_dict(path, value)
		with open('settings.json', 'w') as f:
			f.write(json.dumps(self.dynamic, indent = 4))
		return None

	@failsafe
	def __path_to_dict(self, path: str, VAL) -> None:
		updt = dict()
		temp = updt
		objects = path.split('.')
		for obj in objects[:-1]:
			temp[obj] = dict()
			temp = temp[obj]
		temp[objects[-1]] = VAL
		Settings.__OW(self.dynamic, updt)
		return None

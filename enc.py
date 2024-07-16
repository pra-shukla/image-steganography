from settings import Settings
import numpy as NP
from hashlib import sha256
import importlib
import sys

sys.path.insert(1, './enc')

class Encryption(Settings):
	'''class Encryption deals with all the available enccryption algorithms'''

	def __init__(self) -> None:

		Settings.__init__(self)

		self.enc_available = self.get('encryption.algos')
		self.default = self.get('encryption.default')
		self.key = None
		self.kdf = None
		self.options = list()
		for types in self.enc_available.values():
			for typ in types:
				self.options.append(typ)

		module = importlib.import_module(self.default)
		self.algo = getattr(module, self.default)()
		self.kdf = self.algo.kdf_cycles
		return None

	def set_algo(self, algo: str) -> None:

		for typ in self.enc_available:
			if algo in self.enc_available[typ]:
				mod = typ
				break

		module = importlib.import_module(typ)
		self.algo = getattr(module, typ)()
		self.algo.default = self.algo.types[algo]

		if self.key is not None:
			self.set_key(self.key, self.kdf)
		return None

	def set_key(self, key: str, kdf: int) -> None:
		self.key = key
		self.kdf = kdf
		self.algo.set_key(key, kdf)
		return None

	def encrypt(self, field: NP, do: bool) -> NP:

		hsh = NP.full(32, 0, dtype = 'uint8')
		for idx, value in enumerate(sha256(bytes(field)).digest()):
			hsh[idx] = int(value)

		if not do:
			meta = NP.array(0, dtype = 'uint8')
			ret = NP.append(meta, hsh)
			ret = NP.append(ret, field)
			return ret

		enc_data, meta = self.algo.do(field)
		meta = NP.array(meta, dtype = 'uint8')
		ret = NP.append(meta, hsh)
		ret = NP.append(ret, enc_data)
		return ret

	def decrypt(self, field: NP, kdf: int, key: str = None) -> NP:
		if key is None:
			key = self.key
		self.algo.set_key(key, kdf)

		meta = field[0]
		hsh_ref = list(field[1: 33])
		dec_data = self.algo.undo(field[33: ], meta)
		hsh = NP.full(32, 0, dtype = 'uint8')
		for idx, value in enumerate(sha256(bytes(dec_data)).digest()):
			hsh[idx] = int(value)
		hsh = list(hsh)

		self.algo.set_key(self.key, kdf)
		if hsh_ref != hsh:
			return None
		return dec_data

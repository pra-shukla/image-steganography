from settings import Settings
from PIL import Image
import numpy as NP
import importlib
import sys

sys.path.insert(1, './steg')

class Stegano(Settings):

	def __init__(self) -> None:

		Settings.__init__(self)

		self.steg_available = self.get('stego.algos')
		self.default = self.get('stego.default')
		self.options = list()
		self.cover = None
		self.depth = None
		for types in self.steg_available.values():
			for typ in types:
				self.options.append(typ)

		module = importlib.import_module(self.default)
		self.algo = getattr(module, self.default)()
		return None

	def set_algo(self, algo: str) -> None:

		for typ in self.steg_available:
			if algo in self.steg_available[typ]:
				mod = typ
				break

		module = importlib.import_module(typ)
		self.algo = getattr(module, typ)()
		self.algo.default = self.algo.types[algo]

		if self.cover is not None:
			self.algo.set_cover(self.cover)
			self.capacity = self.algo.capacity
		if self.depth is not None:
			self.set_depth(self.depth)
		return None

	def set_depth(self, depth: int):
		self.algo.set_depth(depth)
		self.depth = depth
		self.capacity = self.algo.capacity
		return None

	def set_cover(self, path: str) -> None:

		img = Image.open(path).convert('RGB')
		field = NP.array(img.getdata())
		self.cover = field
		self.dimensions = (img.height, img.width, 3)

		self.algo.set_cover(field)
		self.capacity = self.algo.capacity
		return None

	def hide(self, field: NP) -> None:
		self.algo.set_data(field)
		ret = self.algo.commit()
		ret = ret.reshape(self.dimensions)

		out = Image.fromarray(ret.astype('uint8'))
		out.save('./TEMP/OUT/new.png')
		return ret

	def read(self, path: str) -> NP:

		img = Image.open(path).convert('RGB')
		field = NP.array(img.getdata(), dtype = 'uint8')

		ret = self.algo.read(field)
		return ret

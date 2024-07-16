import numpy as NP
from random import randint, seed as SEED
from settings import Settings

class Dispersion(Settings):
	'''class Dispersion deals with dispersing and un-dispersing data'''

	@staticmethod
	def failsafe(func):
		def ret(*args, **kwargs):
			try:
				return func(*args, **kwargs)
			except:
				pass
		return ret

	@failsafe
	def __init__(self) -> None:
		super().__init__()
		self.cycles = self.get('dispersion.cycles')
		self.seed = self.get('dispersion.seed')
		self.dispersion_ready = True if isinstance(self.cycles, int) and isinstance(self.seed, int) else False
		self.dispersion_ready = True if self.settings_ready else False
		return None

	@failsafe
	def do(self, Field: NP) -> NP:
		field = Field.copy()
		size = len(field)
		self.set_seed()
		for _ in range(self.cycles):
			index = randint(1, size - 1)
			field[0], field[index] = field[index], field[0]
		return field

	@failsafe
	def undo(self, Field: NP, seed: int) -> NP:
		field = Field.copy()
		size = len(field)
		SEED(seed)
		args = [randint(1, size - 1) for _ in range(self.cycles)]
		args.reverse()
		args = NP.array(args)
		for index in args:
			field[0], field[index] = field[index], field[0]
		return field

	@failsafe
	def set_seed(self, seed: int = None) -> None:
		if seed is None:
			seed = self.seed
		else:
			pass
		if isinstance(seed, int):
			SEED(seed)
			self.dispersion_ready = True
			if seed != self.seed:
				self.update('dispersion.seed', seed)
				self.seed = seed
			else:
				pass
		else:
			pass
		return None

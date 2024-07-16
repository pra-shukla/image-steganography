from settings import Settings
import numpy as NP
from math import floor, ceil

class LSB(Settings):
	'''class LSB does LSB steganography on input int-8 cover array with int-8 data array'''

	@staticmethod
	def failsafe(func):
		def ret(*args, **kwargs):
			try:
				return func(*args, **kwargs)
			except:
				return None
		return ret

	@failsafe
	def __init__(self) -> None:
		super().__init__()
		self.depth = self.get('lsb.depth')
		self.types = {'LSB': 1}
		self.default = None
		self.__ter_seq = (0x00, 0xff, 0x7b, 0x67)
		self.__ter_len = len(self.__ter_seq) - 1
		return None

	@failsafe
	def set_depth(self, depth: int) -> None:
		if depth not in (1, 2, 4):
			return None
		self.depth = depth
		self.capacity = self.__info()
		self.update('lsb.depth', depth)
		return None

	@failsafe
	def set_cover(self, field: NP) -> None:
		self.__cover_type = field.shape
		self.__cover = field.copy().flatten()
		self.capacity = self.__info()
		self.__int8s = ceil(len(bin(self.__cover.size)[2:]) / 8)
		return None

	@failsafe
	def __info(self) -> int:
		ret = floor((self.__cover.size - 1) * self.depth / 8)
		ret -= ceil(len(bin(self.__cover.size)[2:]) / 8)
		ret -= len(self.__ter_seq)
		return ret

	@failsafe
	def set_data(self, field: NP) -> None:
		if field.size > self.capacity:
			return None
		self.__data = NP.append(field, NP.array(self.__ter_seq, dtype = 'uint8'))
		return None

	@failsafe
	def commit(self) -> NP:
		if self.__cover is None or self.__data is None:
			print(1)
			return None
		start, end, skip = self.__skip()
		temp = self.__mod_data(skip)
		steg = self.__cover.copy()

		temp_idx = 1
		steg[0] = ((steg[0] >> 2) << 2) | temp[0]
		for index in range(1, start):
			steg[index] = self.__hide(steg[index], temp[temp_idx])
			temp_idx += 1

		for index in range(start, end, skip):
			steg[index] = self.__hide(steg[index], temp[temp_idx])
			temp_idx += 1

		steg = steg.reshape(self.__cover_type)
		return steg

	@failsafe
	def __hide(self, parent, child):
		return ((parent >> self.depth) << self.depth) | child

	@failsafe
	def __skip(self) -> int:
		start = self.__int8s * 8 // self.depth + 1
		skip = (self.__cover.size - start - 1) // (self.__data.size * 8 // self.depth - 1)
		end = skip * (self.__data.size * 8 // self.depth - 1) + start + 1
		return (start, end, skip)

	@failsafe
	def __mod_data(self, skip) -> NP:
		const = self.__int8s
		size = (self.__data.size + const) * 8 // self.depth + 1
		ret = NP.full(size, 0, dtype = 'uint8')

		match self.depth:
			case 1:
				ret[0] = 0
			case 2:
				ret[0] = 1
			case 4:
				ret[0] = 2
			case 8:
				ret[0] = 3

		mod_idx = 1
		skip_data = list()
		and_val = 2 ** self.depth - 1
		for _ in range(const):
			skip_data.append(skip & 255)
			skip = skip >> 8
		for value in skip_data[: : -1]:
			for _ in range(8 // self.depth):
				ret[mod_idx] = value & (and_val)
				value = value >> self.depth
				mod_idx += 1

		for value in self.__data.copy():
			for _ in range(8 // self.depth):
				ret[mod_idx] = value & (and_val)
				value = value >> self.depth
				mod_idx += 1
		return ret

	@failsafe
	def read(self, field: NP) -> NP:
		cover = field.copy().flatten()
		self.__ter_seq = list(self.__ter_seq)
		match cover[0] & 3:
			case 0:
				depth = 1
			case 1:
				depth = 2
			case 2:
				depth = 4
			case 3:
				depth = 8
		int8s = ceil(len(bin(cover.size)[2:]) / 8) * 8 // depth
		skip = 0
		temp, val, and_val, i = 0, 8 // depth, 2 ** depth - 1, 0
		for index in range(1, int8s + 1):
			temp = ((cover[index] & and_val) << (i * depth)) | temp
			i += 1
			if i == val:
				skip = skip << 8
				skip = skip | temp
				temp, i = 0, 0
		size = cover.size * depth // 8
		data = NP.full(size, 0, dtype = 'uint8')

		temp, val, data_idx, and_val, i = 0, 8 // depth, 0, 2 ** depth - 1, 0
		seq = [0 for _ in range(len(self.__ter_seq))]
		for index in range(int8s + 1, cover.size, skip):
			temp = ((cover[index] & and_val) << (i * depth)) | temp
			i += 1
			if i == val:
				self.__ter_shift(seq, temp)
				if seq == self.__ter_seq:
					break
				data[data_idx] = temp
				data_idx += 1
				temp, i = 0, 0

		data = data[: data_idx - self.__ter_len]
		self.__ter_seq = tuple(self.__ter_seq)
		return data

	def __ter_shift(self, seq: list, temp: int) -> None:
		for i in range(len(seq) - 1):
			seq[i] = seq[i + 1]
		seq[len(seq) - 1] = temp
		return None

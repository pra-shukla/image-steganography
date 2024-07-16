import numpy as NP
import json
from hashlib import sha256
from settings import Settings

class AES(Settings):
	'''class AES converts input 'int-8' NumPy array into encrypted / decrypted 'int-8' NumPy array'''

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
		self.types = {'AES-128': 16, 'AES-192': 24, 'AES-256': 32}
		self.default = 16
		self.ready = False
		self.__get_ref()
		self.__consts = {
			16: (10, 4), 
			24: (12, 6), 
			32: (14, 8)
		}
		Settings.__init__(self)
		self.kdf_cycles = self.get('AES.kdf')
		return None

	@failsafe
	def __get_ref(self) -> None:
		with open('./enc/ref.json', 'r') as f:
			data = json.load(f)
		self.SBox = NP.array(data['SBox'], dtype = 'uint8')
		self.InvSBox = NP.array(data['InvSBox'], dtype = 'uint8')
		self.Mul_2 = NP.array(data['Mul2'], dtype = 'uint8')
		self.Mul_3 = NP.array(data['Mul3'], dtype = 'uint8')
		self.Mul_9 = NP.array(data['Mul9'], dtype = 'uint8')
		self.Mul_11 = NP.array(data['Mul11'], dtype = 'uint8')
		self.Mul_13 = NP.array(data['Mul13'], dtype = 'uint8')
		self.Mul_14 = NP.array(data['Mul14'], dtype = 'uint8')
		self.RCon = NP.array(data['RCon'], dtype = 'uint8')

	@failsafe
	def do(self, field: NP) -> NP:
		IP = self.__pad(field)
		length, stray = len(IP), len(IP) - len(field)
		self.__expand_key()
		for index in range(0, length, 16):
			IP[index: index + 16] = self.__encrypt(IP[index: index + 16])
		return (IP, stray)

	@failsafe
	def undo(self, field: NP, stray: int = 0) -> NP:
		OP = field.copy()
		self.__expand_key()
		self.__reverse_key()
		for index in range(0, len(OP), 16):
			OP[index: index + 16] = self.__decrypt(OP[index: index + 16])
		OP = self.__unpad(OP, stray)
		return OP

	@failsafe
	def set_key(self, key: str, kdf: int) -> None:
		self.kdf_cycles = kdf
		self.update('AES.kdf', kdf)
		self.key = NP.full(self.default, 0, dtype = 'uint8')
		key = key.encode()
		for _ in range(self.kdf_cycles):
			key = sha256(key).digest()
		for index, value in enumerate(key):
			if index >= self.default:
				break
			else:
				self.key[index] = int(value)
		self.__expand_key()
		self.ready = True if self.settings_ready else False
		return None

	@failsafe
	def __sub_bytes(self, inv: bool = False) -> None:
		if inv:
			for index in range(16):
				self.current[index] = self.InvSBox[self.current[index]]
		else:
			for index in range(16):
				self.current[index] = self.SBox[self.current[index]]
		return None

	@failsafe
	def __shift_rows(self, inv: bool = False) -> None:
		s = self.current
		if inv:
			s[1], s[5], s[9], s[13] = s[13], s[1], s[5], s[9]
			s[2], s[6], s[10], s[14] = s[10], s[14], s[2], s[6]
			s[3], s[7], s[11], s[15] = s[7], s[11], s[15], s[3]
		else:
			s[1], s[5], s[9], s[13] = s[5], s[9], s[13], s[1]
			s[2], s[6], s[10], s[14] = s[10], s[14], s[2], s[6]
			s[3], s[7], s[11], s[15] = s[15], s[3], s[7], s[11]
		return None

	@failsafe
	def __mix_colmumns(self, inv: bool = False) -> None:
		t = self.current
		s = NP.full(16, 0, dtype = 'uint8')
		if inv:
			for i in range(0, 13, 4):
				s[i] = self.Mul_14[t[i]] ^ self.Mul_11[t[i + 1]] ^ self.Mul_13[t[i + 2]] ^ self.Mul_9[t[i + 3]]
			for i in range(0, 13, 4):
				s[i + 1] = self.Mul_9[t[i]] ^ self.Mul_14[t[i + 1]] ^ self.Mul_11[t[i + 2]] ^ self.Mul_13[t[i + 3]]
			for i in range(0, 13, 4):
				s[i + 2] = self.Mul_13[t[i]] ^ self.Mul_9[t[i + 1]] ^ self.Mul_14[t[i + 2]] ^ self.Mul_11[t[i + 3]]
			for i in range(0, 13, 4):
				s[i + 3] = self.Mul_11[t[i]] ^ self.Mul_13[t[i + 1]] ^ self.Mul_9[t[i + 2]] ^ self.Mul_14[t[i + 3]]
		else:
			for i in range(0, 13, 4):
				s[i] = self.Mul_2[t[i]] ^ self.Mul_3[t[i + 1]] ^ t[i + 2] ^ t[i + 3]
			for i in range(0, 13, 4):
				s[i + 1] = t[i] ^ self.Mul_2[t[i + 1]] ^ self.Mul_3[t[i + 2]] ^ t[i + 3]
			for i in range(0, 13, 4):
				s[i + 2] = t[i] ^ t[i + 1] ^ self.Mul_2[t[i + 2]] ^ self.Mul_3[t[i + 3]]
			for i in range(0, 13, 4):
				s[i + 3] = self.Mul_3[t[i]] ^ t[i + 1] ^ t[i + 2] ^ self.Mul_2[t[i + 3]]
		self.current = s
		return None

	@failsafe
	def __add_rkey(self, *rkey) -> None:
		for index in range(0, 16, 4):
			self.current[index: index + 4] ^= rkey[index // 4]
		return None

	@failsafe
	def __G(self, Field: NP, rnd: int) -> NP:
		field = Field.copy()
		field[0], field[1], field[2], field[3] = field[1], field[2], field[3], field[0]
		for i in range(4):
			field[i] = self.SBox[field[i]]
		field ^= NP.array([self.RCon[rnd], 0, 0, 0], dtype = 'uint8')
		return field

	@failsafe
	def __expand_key(self) -> None:
		key_size = (self.__consts[self.default][0] + 1) * 4
		interval = self.__consts[self.default][1]
		rnd = 1
		self.exp_key = NP.full((key_size, 4), 0, dtype = 'uint8')
		for index in range(0, self.default, 4):
			self.exp_key[index // 4] = self.key[index: index + 4]

		for index in range(interval, key_size):
			if index % interval:
				self.exp_key[index] = self.exp_key[index - 1] ^ self.exp_key[index - interval]
			else:
				self.exp_key[index] = self.__G(self.exp_key[index - 1], rnd) ^ self.exp_key[index - interval]
				rnd += 1
		return None

	@failsafe
	def __reverse_key(self) -> None:
		length = len(self.exp_key)
		bridge = [list(item) for item in self.exp_key]

		for index in range(0, length // 2, 4):
			temp = bridge[index: index + 4]
			bridge[index: index + 4] = bridge[length - index - 4: length - index]
			bridge[length - index - 4: length - index] = temp
		self.exp_key = NP.array(bridge, dtype = 'uint8')
		return None

	@failsafe
	def __pad(self, field: NP) -> NP:
		size = (len(field) // 16 + 1) * 16 if len(field) % 16 else len(field)
		new = NP.full(size, 0, dtype = 'uint8')
		strt = size - len(field)
		for index in range(strt, size):
			new[index] = field[index - strt]
		return new

	@failsafe
	def __unpad(self, field: NP, stray: int) -> NP:
		return field[stray: ]

	@failsafe
	def __encrypt(self, field: NP) -> NP:
		self.current = field
		rounds = self.__consts[self.default][0]

		self.__add_rkey(*self.exp_key[0: 4])

		for rnd in range(1, rounds):
			self.__sub_bytes()
			self.__shift_rows()
			self.__mix_colmumns()
			self.__add_rkey(*self.exp_key[rnd * 4: rnd * 4 + 4])

		self.__sub_bytes()
		self.__shift_rows()
		self.__add_rkey(*self.exp_key[-4: ])
		return self.current

	@failsafe
	def __decrypt(self, field: NP) -> NP:
		self.current = field
		rounds = self.__consts[self.default][0]

		self.__add_rkey(*self.exp_key[0: 4])
		self.__shift_rows(inv = True)
		self.__sub_bytes(inv = True)

		for rnd in range(1, rounds):
			self.__add_rkey(*self.exp_key[rnd * 4: rnd * 4 + 4])
			self.__mix_colmumns(inv = True)
			self.__shift_rows(inv = True)
			self.__sub_bytes(inv = True)

		self.__add_rkey(*self.exp_key[-4: ])
		return self.current

import customtkinter as ctk
import numpy as NP
import webbrowser
import shutil
import threading
import zipfile
import os
from tkinter import filedialog
from PIL import Image, ImageTk
from settings import Settings
from enc import Encryption
from dispersion import Dispersion
from steg import Stegano
from random import randint, choice
from math import ceil
from hashlib import sha256

class Startup():
	'''class Startup deals with the startup screen'''

	def __init__(self):

		self.__clear('./TEMP')
		self.__welfare()

		self.root = ctk.CTk(fg_color = '#1F1F1F')
		self.root.geometry('900x500')
		self.root.title('  Steganography')
		self.root.resizable(0, 0)
		self.root.iconbitmap('./assets/icon.ico')

		self.top = ctk.CTkFrame(self.root, width = 50, fg_color = '#1A1B1C')
		self.top.pack(expand = True, fill = 'both')

		self.__add_widgets()
		self.root.mainloop()

	def __add_widgets(self) -> None:
		add_icon = ctk.CTkImage(Image.open('./assets/add-light.png'), size = (50, 50))
		self.add_button = ctk.CTkButton(self.top,
			image = add_icon,
			command = self.__open_main,
			fg_color = 'transparent',
			hover_color = '#2B2D2E',
			text = '',
			width = 70,
			height = 70,
			corner_radius = 30)
		self.add_button.place(relx = 0.5, rely = 0.479, anchor = 'center')

		self.read_button = ctk.CTkButton(self.top,
			command = self.__open_read,
			text = 'Read',
			fg_color = '#212C28',
			hover_color = '#2B2D2E',
			font = ('cascadia code', -13),
			width = 80)
		self.read_button.place(relx = 0.05, rely = 0.95, anchor = 'sw')

		self.learn_button = ctk.CTkButton(self.top,
			command = self.learn_more,
			text = 'Learn more',
			text_color = '#4D5654',
			fg_color = '#1A1B1C',
			hover_color = '#1A1B1C',
			width = 50)
		self.learn_button.place(relx = 0.96, rely = 0.95, anchor = 'se')
		return None

	def __open_read(self) -> None:
		path = filedialog.askopenfile(filetypes = [('Images', '*.png')])
		if path is None:
			return None

		Extract(path.name)
		return None

	@staticmethod
	def learn_more() -> None:
		webbrowser.open('https://en.wikipedia.org/wiki/Steganography')
		return None

	def __open_main(self) -> None:
		path = filedialog.askopenfile(filetypes = [('Images', '*.png')])
		if path is None:
			return None
		load_icon = ctk.CTkImage(Image.open('./assets/loading-light.png'), size = (50, 50))
		self.add_button.configure(image = load_icon)

		threading.Thread(target = Main, args = (self.root, self.top, path.name)).start()
		return None

	def __welfare(self) -> bool:
		pass

	@staticmethod	
	def __clear(Path: str) -> None:
		for file in os.listdir(Path):
			path = os.path.join(Path, file)
			if os.path.isfile(path):
				os.remove(path)
			elif os.path.isdir(path):
				Startup.__clear(path)
		return None

class Main():
	'''class Main deals with the main App screen'''

	def __init__(self, root: ctk, top_frame: ctk, cover_path: str) -> None:

		self.settings = Settings()
		self.encryption = Encryption()
		self.dispersion = Dispersion()
		self.steg = Stegano()
		self.files = list()

		self.error_e = False
		self.steg.set_cover(cover_path)
		self.display_image = 'old.png'
		self.cover_path = cover_path
		self.sz_files = 0
		self.sz_text = 0
		shutil.copy(cover_path, f'./TEMP/OUT/old.png')

		self.pass_gen_win = None
		self.text_edit_win = None
		self.view_files_win = None

		top_frame.pack_forget()
		self.root = root
		self.root.configure(fg_color = '#1F1F1F')
		path = cover_path.split('/')[-1]
		self.root.title(View_files.shorten_name(path) + ' - Steganography')
		del path

		self.bottom = ctk.CTkFrame(self.root, height = 20, fg_color = '#181818')
		self.bottom.pack(side = 'bottom', fill = 'x')
		self.steg_org = ctk.CTkLabel(self.bottom,
			text = 'Original',
			fg_color = 'transparent',
			font = ('cascadia code', 11),
			text_color = '#999999')
		self.steg_org.pack(side = 'right', padx = 20)

		self.left = ctk.CTkFrame(self.root, width = 50, fg_color = '#181818')
		self.left.pack(side = 'left', fill = 'y')

		self.side_panel = ctk.CTkFrame(self.root, fg_color = '#181818', width = 170)
		self.side_panel.pack(side = 'left', fill = 'y', padx = 5, pady = 5)

		self.top = ctk.CTkFrame(self.root, height = 50, fg_color = '#181818')
		self.top.pack(side = 'top', fill = 'x')

		self.mid = ctk.CTkFrame(self.root, fg_color = '#1F1F1F')
		self.mid.pack(side = 'top', expand = True, fill = 'both')
		self.img_label = ctk.CTkLabel(self.mid, text = '')

		self.files_side_panel = ctk.CTkFrame(self.side_panel, fg_color = 'transparent', width = 170)
		self.steg_side_panel = ctk.CTkFrame(self.side_panel, fg_color = 'transparent', width = 170)
		self.enc_side_panel = ctk.CTkFrame(self.side_panel, fg_color = 'transparent', width = 170)
		self.disp_side_panel = ctk.CTkFrame(self.side_panel, fg_color = 'transparent', width = 170)

		self.__add_main_buttons()

		self.__set_files_panel()
		self.__set_steg_panel()
		self.__set_enc_panel()
		self.__set_disp_panel()
		self.__add_main_image(cover_path)

		self.files_side_panel.pack(side = 'left', fill = 'y', padx = 5, pady = 5)
		self.current = (self.files_side_panel, self.files_button)
		self.files_button.configure(fg_color = '#37373C', hover_color = '#37373C')

	def __add_main_buttons(self) -> None:

		files_icon = ctk.CTkImage(Image.open('./assets/documents-light.png'), size = (32, 32))
		self.files_button = ctk.CTkButton(self.left,
			image = files_icon,
			command = lambda: self.__switch(self.files_side_panel),
			fg_color = 'transparent',
			text = '',
			hover_color = '#2B2D2E',
			width = 50,
			height = 50)
		self.files_button.pack(pady = 10)

		steg_icon = ctk.CTkImage(Image.open('./assets/binary-code-light.png'), size = (32, 32))
		self.steg_button = ctk.CTkButton(self.left,
			image = steg_icon,
			command = lambda: self.__switch(self.steg_side_panel),
			fg_color = 'transparent',
			text = '',
			hover_color = '#2B2D2E',
			width = 50,
			height = 50)
		self.steg_button.pack(pady = 10)

		padlock_icon = ctk.CTkImage(Image.open('./assets/encryption-light.png'), size = (32, 32))
		self.enc_button = ctk.CTkButton(self.left,
			image = padlock_icon,
			command = lambda: self.__switch(self.enc_side_panel),
			fg_color = 'transparent',
			text = '',
			hover_color = '#2B2D2E',
			width = 50,
			height = 50)
		self.enc_button.pack(pady = 10, padx = 5)

		disp_icon = ctk.CTkImage(Image.open('./assets/dispersion-light.png'), size = (32, 32))
		self.disp_button = ctk.CTkButton(self.left,
			image = disp_icon,
			command = lambda: self.__switch(self.disp_side_panel),
			fg_color = 'transparent',
			text = '',
			hover_color = '#2B2D2E',
			width = 50,
			height = 50)
		self.disp_button.pack(pady = 10)

		save_icon = ctk.CTkImage(Image.open('./assets/save2-light.png'), size = (20, 20))
		self.final_save_button = ctk.CTkButton(self.top,
			image = save_icon,
			command = self.__save_final,
			fg_color = 'transparent',
			text = '',
			hover_color = '#2B2D2E',
			corner_radius = 10,
			width = 30,
			height = 30,
			state = 'disabled')
		self.final_save_button.place(relx = 0.94, rely = 0.5, anchor = 'center')

		do_icon = ctk.CTkImage(Image.open('./assets/tick-light.png'), size = (20, 20))
		self.tick_button = ctk.CTkButton(self.top,
			image = do_icon,
			command = self.__do,
			fg_color = 'transparent',
			text = '',
			hover_color = '#2B2D2E',
			corner_radius = 10,
			width = 30,
			height = 30)
		self.tick_button.place(relx = 0.87, rely = 0.5, anchor = 'center')

		share_icon = ctk.CTkImage(Image.open('./assets/share-light.png'), size = (20, 20))
		self.open_button = ctk.CTkButton(self.top,
			image = share_icon,
			command = self.__display_image,
			fg_color = 'transparent',
			text = '',
			hover_color = '#2B2D2E',
			corner_radius = 10,
			width = 30,
			height = 30)
		self.open_button.place(relx = 0.795, rely = 0.5, anchor = 'center')

		flip_icon = ctk.CTkImage(Image.open('./assets/flip-light.png'), size = (20, 20))
		self.flip_button = ctk.CTkButton(self.top,
			image = flip_icon,
			command = self.__flip_image,
			fg_color = 'transparent',
			text = '',
			hover_color = '#2B2D2E',
			corner_radius = 10,
			width = 30,
			height = 30,
			state = 'disabled')
		self.flip_button.place(relx = 0.725, rely = 0.5, anchor = 'center')

	def __set_files_panel(self) -> None:
		
		self.file_names = list()

		self.files_label = ctk.CTkLabel(self.files_side_panel, text = 'Files', fg_color = 'transparent', font = ('Open Sans Medium', 18))

		self.text_label = ctk.CTkLabel(self.files_side_panel, text = 'Text to hide', fg_color = 'transparent', font = ('cascadia code', 10))
		self.text_entry = ctk.CTkTextbox(self.files_side_panel,
			font = ('cascadia code', 14),
			height = 130,
			width = 164)
		self.text_entry.bind('<Any-KeyPress>',
			lambda event: threading.Thread(target = self.__entered, args = (event,)).start())

		comp_icon = ctk.CTkImage(Image.open('./assets/share-light.png'), size = (15, 15))
		self.comp_button = ctk.CTkButton(self.files_side_panel,
			image = comp_icon,
			command = self.__open_text_edit,
			fg_color = 'transparent',
			text = '',
			width = 30,
			hover_color = '#37373C',
			corner_radius = 10)

		add_icon = ctk.CTkImage(Image.open('./assets/plus-light.png'), size = (15, 15))
		self.add_button = ctk.CTkButton(self.files_side_panel,
			image = add_icon,
			command = self.__add_file,
			fg_color = 'transparent',
			text = '',
			width = 30,
			hover_color = '#37373C',
			corner_radius = 10)

		more_icon = ctk.CTkImage(Image.open('./assets/more-light.png'), size = (15, 15))
		self.view_files_button = ctk.CTkButton(self.files_side_panel,
			image = more_icon,
			command = self.__open_view_files,
			fg_color = 'transparent',
			text = '',
			width = 30,
			hover_color = '#37373C',
			corner_radius = 10)

		self.text_size_label = ctk.CTkLabel(self.files_side_panel,
			text = 'Text size',
			fg_color = 'transparent',
			font = ('Open Sans Medium', 12))
		self.total_files_label = ctk.CTkLabel(self.files_side_panel,
			text = 'Total files',
			fg_color = 'transparent', 
			font = ('Open Sans Medium', 12))
		self.total_size_label = ctk.CTkLabel(self.files_side_panel,
			text = 'Total file size',
			fg_color = 'transparent',
			font = ('Open Sans Medium', 12))

		self.text_size = ctk.StringVar(value = '0B')
		self.text_size_label2 = ctk.CTkLabel(self.files_side_panel,
			textvariable = self.text_size,
			fg_color = 'transparent',
			font = ('cascadia code', 12))
		self.total_files = ctk.IntVar(value = 0)
		self.total_files_label2 = ctk.CTkLabel(self.files_side_panel,
			textvariable = self.total_files,
			fg_color = 'transparent', 
			font = ('cascadia code', 12))
		self.total_size = ctk.StringVar(value = '0KB')
		self.total_size_label2 = ctk.CTkLabel(self.files_side_panel,
			textvariable = self.total_size,
			fg_color = 'transparent',
			font = ('cascadia code', 12))

		self.capacity_left_var = ctk.StringVar(value = '0.00KB')
		self.capacity_left_label = ctk.CTkLabel(self.files_side_panel,
			textvariable = self.capacity_left_var,
			fg_color = 'transparent',
			font = ('cascadia code', 12))
		self.capacity_left_bar = ctk.CTkProgressBar(self.files_side_panel, orientation = 'horizontal', width = 163)

		self.files_label.place(x = 13, y = 5)

		self.text_label.place(x = 13, y = 40)
		self.text_entry.place(x = 3, y = 62)
		self.comp_button.place(x = 120, y = 198)

		self.text_size_label.place(x = 10, y = 240)
		self.text_size_label2.place(x = 120, y = 240)

		self.total_files_label.place(x = 10, y = 260)
		self.total_files_label2.place(x = 120, y = 260)

		self.total_size_label.place(x = 10, y = 280)
		self.total_size_label2.place(x = 120, y = 280)

		self.add_button.place(relx = 0.5, y = 330, anchor = 'center')
		self.view_files_button.place(x = 120, y = 316)

		self.capacity_left_label.place(relx = 0.188, rely = 0.9)
		self.capacity_left_bar.place(relx = 0.5, rely = 0.975, anchor = 'center')
		self.__update_cl_bar()

		return None

	def __set_steg_panel(self) -> None:

		self.steg_label = ctk.CTkLabel(self.steg_side_panel, text = 'Steganography', fg_color = 'transparent', font = ('Open Sans Medium', 18))

		self.steg_options = ctk.CTkComboBox(self.steg_side_panel,
			values = self.steg.options,
			width = 150,
			font = ('cascadia code', 14),
			dropdown_font = ('cascadia code', 10),
			command = lambda event: self.__set_steg_algo(event))

		self.depth_label = ctk.CTkLabel(self.steg_side_panel, text = 'Depth', fg_color = 'transparent', font = ('cascadia code', 10))
		self.steg_entry = ctk.CTkComboBox(self.steg_side_panel,
			values = ['1', '2', '4'],
			width = 150,
			font = ('cascadia code', 14),
			dropdown_font = ('cascadia code', 10),
			command = self.__set_steg_depth)
		self.steg_entry.set(str(self.steg.algo.depth))

		self.capacity_label = ctk.CTkLabel(self.steg_side_panel, text = 'Capacity', fg_color = 'transparent', font = ('Open Sans Medium', 14))
		self.capacity_length = ctk.StringVar(value = f'{self.steg.capacity // 1024}KB')
		self.length_label = ctk.CTkLabel(self.steg_side_panel,
			textvariable = self.capacity_length,
			fg_color = 'transparent',
			font = ('cascadia code', 12))

		self.steg_label.place(x = 13, y = 5)

		self.steg_options.place(x = 10, y = 70)

		self.depth_label.place(x = 13, y = 110)
		self.steg_entry.place(x = 10, y = 132)

		self.capacity_label.place(x = 11, y = 180)
		self.length_label.place(x = 110, y = 180)

		return None

	def __set_enc_panel(self) -> None:
		
		self.enc_label = ctk.CTkLabel(self.enc_side_panel,
			text = 'Encrypt',
			fg_color = 'transparent',
			font = ('Open Sans Medium', 14))
		self.enc_on = not False

		self.params = {
			'length': 16,
			'A-Z': True,
			'a-z': True,
			'0-9': True,
			'spcl': True,
			'min_num': 1,
			'min_spcl': 1
		}

		self.do_enc = ctk.IntVar(value = 0)
		self.enc_switch = ctk.CTkSwitch(self.enc_side_panel, text = '',
			onvalue = 1,
			offvalue = 0,
			width = 10,
			variable = self.do_enc,
			command = self.__enc_switch)

		self.enc_options = ctk.CTkComboBox(self.enc_side_panel,
			values = self.encryption.options,
			width = 150,
			font = ('cascadia code', 14),
			dropdown_font = ('cascadia code', 10),
			command = lambda event: self.__set_enc_algo(event))

		self.pass_label = ctk.CTkLabel(self.enc_side_panel,
			text = 'Password',
			fg_color = 'transparent',
			font = ('cascadia code', 10))
		self.password = ctk.StringVar(value = '')
		self.pass_entry = ctk.CTkEntry(self.enc_side_panel,
			placeholder_text = 'password',
			textvariable = self.password,
			font = ('cascadia code', 14),
			fg_color = 'transparent',
			height = 30,
			width = 150)
		self.pass_entry.bind('<Any-KeyPress>',
			lambda event: threading.Thread(target = self.__update_strength_mod,
												args = (event,)).start())

		self.pass_strength = ctk.CTkProgressBar(self.enc_side_panel,
			orientation = 'horizontal',
			width = 150)
		self.pass_strength.set(0.25)
		self.pass_strength.configure(progress_color = 'red')

		save_icon = ctk.CTkImage(Image.open('./assets/save-light.png'), size = (15, 15))
		self.save_button = ctk.CTkButton(self.enc_side_panel,
			image = save_icon,
			command = self.__download_pass,
			fg_color = 'transparent',
			text = '',
			width = 30,
			hover_color = '#37373C',
			corner_radius = 10)
		regen_icon = ctk.CTkImage(Image.open('./assets/redo-light.png'), size = (18, 18))
		self.regen_button = ctk.CTkButton(self.enc_side_panel,
			image = regen_icon,
			command = self.__enter_pass,
			fg_color = 'transparent',
			text = '',
			width = 30,
			hover_color = '#37373C',
			corner_radius = 10)
		more_icon = ctk.CTkImage(Image.open('./assets/more-light.png'), size = (15, 15))
		self.more_button = ctk.CTkButton(self.enc_side_panel,
			image = more_icon,
			command = self.__open_password_gen,
			fg_color = 'transparent',
			text = '',
			width = 30,
			hover_color = '#37373C',
			corner_radius = 10)

		self.kdf_label = ctk.CTkLabel(self.enc_side_panel,
			text = 'kdf-cycles',
			fg_color = 'transparent',
			font = ('cascadia code', 10))
		self.kdf = ctk.StringVar(value = self.encryption.kdf)
		self.kdf_entry = ctk.CTkEntry(self.enc_side_panel,
			placeholder_text = 'kdf cycles',
			textvariable = self.kdf,
			font = ('cascadia code', 14),
			fg_color = 'transparent',
			height = 30,
			width = 150)

		self.enc_label.place(x = 13, y = 5)
		self.enc_switch.place(x = 120, y = 9)

		self.enc_options.place(x = 10, y = 70)

		self.pass_label.place(x = 13, y = 110)
		self.pass_entry.place(x = 10, y = 132)
		self.pass_strength.place(x = 10, y = 167)
		self.more_button.place(x = 128, y = 180)
		self.regen_button.place(x = 88, y = 180)
		self.save_button.place(x = 51, y = 180)

		self.kdf_label.place(x = 13, y = 213)
		self.kdf_entry.place(x = 10, y = 235)
	
		self.__enc_switch()

		return None

	def __set_disp_panel(self) -> None:
		
		self.disp_label = ctk.CTkLabel(self.disp_side_panel,
			text = 'Disperse',
			fg_color = 'transparent',
			font = ('Open Sans Medium', 14))
		self.disp_on = not True

		self.do_disp = ctk.IntVar(value = 1)
		self.disp_switch = ctk.CTkSwitch(self.disp_side_panel, text = '',
			onvalue = 1,
			offvalue = 0,
			width = 10,
			variable = self.do_disp,
			command = self.__disp_switch)

		self.key_label = ctk.CTkLabel(self.disp_side_panel,
			text = 'Key',
			fg_color = 'transparent',
			font = ('cascadia code', 10))
		self.disp_key = ctk.StringVar(value = self.settings.get('dispersion.seed'))
		self.disp_key_entry = ctk.CTkEntry(self.disp_side_panel,
			placeholder_text = 'password',
			textvariable = self.disp_key,
			font = ('cascadia code', 14),
			fg_color = 'transparent',
			height = 30,
			width = 150)

		self.disp_label.place(x = 13, y = 5)
		self.disp_switch.place(x = 120, y = 9)

		self.key_label.place(x = 13, y = 48)
		self.disp_key_entry.place(x = 10, y = 70)

		self.__disp_switch()

		return None

	def __add_main_image(self, path: str) -> None:
		img = Image.open(path)
		if int(600 * img.height / img.width) > 370:
			size = (int(370 * img.width / img.height), 370)
		else:
			size = (600, int(600 * img.height / img.width))

		main = ctk.CTkImage(img, size = size)
		self.img_label.configure(image = main)

		self.img_label.place(relx = 0.5, rely = 0.5, anchor = 'center')
		return None

	def __switch(self, button: str) -> None:
		
		if button == self.current[0]:
			return None
		else:
			pass

		if button == self.files_side_panel:
			self.current[0].pack_forget()
			self.current[1].configure(fg_color = 'transparent', hover_color = '#2B2D2E')
			self.files_side_panel.pack(side = 'left', fill = 'y', padx = 5, pady = 5)
			self.current = (self.files_side_panel, self.files_button)
			self.files_button.configure(fg_color = '#37373C', hover_color = '#37373C')
		elif button == self.steg_side_panel:
			self.current[0].pack_forget()
			self.current[1].configure(fg_color = 'transparent', hover_color = '#2B2D2E')
			self.steg_side_panel.pack(side = 'left', fill = 'y', padx = 5, pady = 5)
			self.current = (self.steg_side_panel, self.steg_button)
			self.steg_button.configure(fg_color = '#37373C', hover_color = '#37373C')
		elif button == self.enc_side_panel:
			self.current[0].pack_forget()
			self.current[1].configure(fg_color = 'transparent', hover_color = '#2B2D2E')
			self.enc_side_panel.pack(side = 'left', fill = 'y', padx = 5, pady = 5)
			self.current = (self.enc_side_panel, self.enc_button)
			self.enc_button.configure(fg_color = '#37373C', hover_color = '#37373C')
		elif button == self.disp_side_panel:
			self.current[0].pack_forget()
			self.current[1].configure(fg_color = 'transparent', hover_color = '#2B2D2E')
			self.disp_side_panel.pack(side = 'left', fill = 'y', padx = 5, pady = 5)
			self.current = (self.disp_side_panel, self.disp_button)
			self.disp_button.configure(fg_color = '#37373C', hover_color = '#37373C')
		else:
			pass

		return None

	def __enc_switch(self) -> None:
		
		if self.enc_on:
			self.enc_on = False
			self.enc_options.configure(state = 'disabled')
			self.pass_entry.configure(text_color = '#737373')
			self.pass_entry.configure(state = 'disabled')
			self.save_button.configure(state = 'disabled')
			self.regen_button.configure(state = 'disabled')
			self.more_button.configure(state = 'disabled')
			self.kdf_entry.configure(text_color = '#737373')
			self.kdf_entry.configure(state = 'disabled')
		else:
			self.enc_on = True
			self.enc_options.configure(state = 'normal')
			self.pass_entry.configure(text_color = '#FFFFFF')
			self.pass_entry.configure(state = 'normal')
			self.save_button.configure(state = 'normal')
			self.regen_button.configure(state = 'normal')
			self.more_button.configure(state = 'normal')
			self.kdf_entry.configure(text_color = '#FFFFFF')
			self.kdf_entry.configure(state = 'normal')

		return None

	def __disp_switch(self) -> None:

		if self.disp_on:
			self.disp_on = False
			self.disp_key_entry.configure(text_color = '#737373')
			self.disp_key_entry.configure(state = 'disabled')
		else:
			self.disp_on = True
			self.disp_key_entry.configure(text_color = '#FFFFFF')
			self.disp_key_entry.configure(state = 'normal')

		return None

	def __update_strength_mod(self, event) -> None:

		strength = Password_gen.strength(self.password.get())

		match strength:
			case 0:
				self.pass_strength.set(0.25)
				self.pass_strength.configure(progress_color = 'red')
			case 1:
				self.pass_strength.set(0.75)
				self.pass_strength.configure(progress_color = 'orange')
			case 2:
				self.pass_strength.set(1.00)
				self.pass_strength.configure(progress_color = 'green')

		return None

	def __open_password_gen(self) -> None:
		temp = Password_gen(self.params, self.password)
		return None

	def __open_text_edit(self) -> None:
		limit = self.steg.capacity - self.sz_files - self.sz_text
		temp = Text_edit(self.text_entry.get('0.0', 'end')[:-1],
			self.text_entry,
			self.text_size, limit)
		return None

	def __open_view_files(self) -> None:

		args = (self.files, 
			self.total_files,
			self.total_size,
			self.capacity_left_var,
			self.capacity_left_bar,
			self.steg.capacity,
			self)
		temp = View_files(*args)
		return None

	def __error_message(self, message: str) -> None:

		if self.error_e:
			self.__close_error()

		self.error_frame = ctk.CTkFrame(self.mid,
			height = 50,
			width = 230,
			fg_color = '#9C2B2E',
			border_width = 1,
			border_color = '#E84E4F')

		cancel_icon = ctk.CTkImage(Image.open('./assets/cancel-light.png'), size = (25, 25))
		self.error_label_icon = ctk.CTkLabel(self.error_frame,
			fg_color = 'transparent',
			image = cancel_icon,
			text = '')
		self.error_label = ctk.CTkLabel(self.error_frame,
			fg_color = 'transparent',
			text = message,
			font = ('cascadia code', 13),
			justify = 'left')

		close_icon = ctk.CTkImage(Image.open('./assets/cross-light.png'), size = (15, 15))
		self.close_button = ctk.CTkButton(self.error_frame,
			image = close_icon,
			command = self.__close_error,
			fg_color = 'transparent',
			text = '',
			width = 30,
			hover_color = '#8D0000',
			corner_radius = 10)

		self.error_label_icon.pack(side = 'left', padx = 10)
		self.error_label.pack(side = 'left')
		self.close_button.pack(side = 'right', padx = 10)
		self.error_frame.pack_propagate(False)
		self.error_frame.place(relx = 0.985, rely = 0.98, anchor = 'se')
		self.error_e = True

		self.root.after(3000, self.__close_error)
		return None

	def __close_error(self) -> None:

		self.error_frame.place_forget()
		self.error_e = False
		return None

	def __entered(self, event) -> None:

		self.sz_text = len(self.text_entry.get('0.0', 'end').strip())
		if self.sz_text < 1000:
			self.text_size.set(f'{self.sz_text}B')
		else:
			self.text_size.set(f'{self.sz_text / 1024:.2f}KB')

		if self.sz_text > self.steg.capacity - self.sz_files:
			self.__error_message('Text limit\nreached')
			return None

		self.__update_cl_bar()
		return None

	def __add_file(self) -> None:
		path = filedialog.askopenfile()
		if path is None:
			return None

		path = path.name
		name = path.split('/')[-1]
		size = os.path.getsize(path)
		if path.split('/')[-1] in self.files:
			self.__error_message('Already\nIncluded')
			return None

		if size > self.steg.capacity - self.sz_files - self.sz_text:
			self.__error_message('File too\nlarge')
			return None

		shutil.copy(path, f'./TEMP/{name}')
		self.files.append(name)
		self.total_files.set(self.total_files.get() + 1)
		self.sz_files += size
		self.total_size.set(str(self.sz_files // 1024) + 'KB')

		self.__update_cl_bar()
		return None

	def __update_cl_bar(self) -> None:

		ratio = (self.sz_text + self.sz_files) / self.steg.capacity
		self.capacity_left_var.set(f'{(self.sz_text + self.sz_files) / 1024:.2f}KB / {self.steg.capacity / 1024:.2f}KB')
		if ratio <= 0.8:
			self.capacity_left_bar.set(ratio)
			self.capacity_left_bar.configure(progress_color = 'green')
		elif ratio > 0.8 and ratio <= 0.93:
			self.capacity_left_bar.set(ratio)
			self.capacity_left_bar.configure(progress_color = 'orange')
		elif ratio > 0.93:
			self.capacity_left_bar.set(ratio)
			self.capacity_left_bar.configure(progress_color = 'red')

		return None

	def __enter_pass(self) -> None:
		self.password.set(Password_gen.generator(**self.params))
		self.__update_strength_mod(None)
		return None

	def __download_pass(self) -> None:

		file_name = self.cover_path.split('/')[-1]
		password = self.password.get().strip()
		kdf = self.kdf.get().strip()
		disp_key = self.disp_key.get()
		data = f'NAME           : {file_name}\nPASSWORD       : {password}\n'
		data += f'KDF            : {kdf}\nDISPERSION KEY : {disp_key}'

		with open('./TEMP/password.txt', 'w') as f:
			f.write(data)

		path = filedialog.asksaveasfile(initialfile = 'password.txt',
			defaultextension = '.txt',
			filetypes = [('All Files', '*.*'), ('Text Documents', '*.txt')]).name
		shutil.move('./TEMP/password.txt', path)

		return None

	def __display_image(self) -> None:

		img = Image.open(f'./TEMP/OUT/{self.display_image}')
		img.show()
		return None

	def __flip_image(self) -> None:

		if self.display_image == 'old.png':
			self.display_image = 'new.png'
			self.flip_button.configure(fg_color = 'transparent')
			self.__add_main_image('./TEMP/OUT/new.png')
			self.steg_org.configure(text = 'Steg')
		else:
			self.display_image = 'old.png'
			self.flip_button.configure(fg_color = '#37373C')
			self.__add_main_image('./TEMP/OUT/old.png')
			self.steg_org.configure(text = 'Original')

		return None

	def __save_final(self) -> None:

		if not os.path.exists('./TEMP/OUT/new.png'):
			return None

		old_name = self.cover_path.split('/')[-1].split('.')[0]
		path = filedialog.asksaveasfile(initialfile = f'{old_name}-steg.png',
			defaultextension = '.txt',
			filetypes = [('All Files', '*.*'), ('Text Documents', '*.txt')]).name
		shutil.copy('./TEMP/OUT/new.png', path)
		return None

	def __set_steg_depth(self, event) -> None:

		depth = int(event)
		self.steg.set_depth(depth)
		self.__update_cl_bar()
		self.capacity_length.set(f'{self.steg.capacity // 1024}KB')

		return None

	def __set_steg_algo(self, event) -> None:

		self.steg.set_algo(event)
		self.__update_cl_bar()
		self.capacity_length.set(f'{self.steg.capacity // 1024}KB')
		return None

	def __set_enc_algo(self, event) -> None:

		self.encryption.set_algo(event)
		return None

	def __do(self) -> None:

		text = self.text_entry.get('0.0', 'end').strip()
		if text == '' and not len(self.files):
			self.__error_message('No data\nadded')
			return None

		with open('./TEMP/%TEMP%.txt', 'w') as f:
			f.write(text)

		self.files.append('%TEMP%.txt')
		for file in self.files:
			with zipfile.ZipFile('./TEMP/files.zip', 'a') as f:
					f.write(f'./TEMP/{file}')
		self.files.pop(-1)

		with open('./TEMP/files.zip', 'rb') as f:
			data = NP.frombuffer(f.read(), dtype = 'uint8')

		if self.do_disp.get():
			try:
				key = int(self.disp_key.get())
			except:
				self.__error_message('Invalid Dispersion\nkey')
				return None
			self.dispersion.set_seed(key)
			data = self.dispersion.do(data)

		if self.do_enc.get():
			if self.password.get() == '':
				self.__error_message('Set a\npassword')
				return None

			try:
				kdf = int(self.kdf.get())
			except:
				self.__error_message('Invalid\nKDF')
				return None

			self.encryption.set_key(self.password.get(), kdf)
			data = self.encryption.encrypt(data, True)
		else:
			data = self.encryption.encrypt(data, False)

		self.steg.hide(data)

		self.flip_button.configure(state = 'normal')
		self.final_save_button.configure(state = 'normal')
		self.__flip_image()
		return None

class Password_gen():
	'''class Password_gen deals with the generate password window'''

	def __init__(self, params: dict, password: ctk.StringVar = None) -> None:

		self.bg = '#181818'
		self.fg = '#1F1F1F'
		self.padx = 10
		self.pady = 2
		self.params = params
		self.password = password
		self.root = ctk.CTkToplevel(fg_color = self.bg)

		self.root.resizable(0, 0)
		self.root.title('')
		self.root.after(250, lambda: self.root.iconbitmap('./assets/favicon.ico'))

		self.frame0 = ctk.CTkFrame(self.root, fg_color = 'transparent', height = 6)
		self.frame0.pack_propagate(False)
		self.frame1 = ctk.CTkFrame(self.root, fg_color = self.fg, height = 40, width = 400)
		self.frame1.pack_propagate(False)
		self.frame2 = ctk.CTkFrame(self.root, fg_color = self.fg, height = 30, width = 400)
		self.frame2.pack_propagate(False)
		self.frame3 = ctk.CTkFrame(self.root, fg_color = self.fg, height = 30, width = 400)
		self.frame3.pack_propagate(False)
		self.frame4 = ctk.CTkFrame(self.root, fg_color = self.fg, height = 30, width = 400)
		self.frame4.pack_propagate(False)
		self.frame5 = ctk.CTkFrame(self.root, fg_color = self.fg, height = 30, width = 400)
		self.frame5.pack_propagate(False)
		self.frame6 = ctk.CTkFrame(self.root, fg_color = self.fg, height = 30, width = 400)
		self.frame6.pack_propagate(False)
		self.frame7 = ctk.CTkFrame(self.root, fg_color = self.fg, height = 30, width = 400)
		self.frame7.pack_propagate(False)
		self.frame8 = ctk.CTkFrame(self.root, fg_color = self.fg, height = 30, width = 400)
		self.frame8.pack_propagate(False)
		self.frame9 = ctk.CTkFrame(self.root, fg_color = 'transparent', height = 6)
		self.frame9.pack_propagate(False)

		self.__place_widgets()

		self.frame0.pack()
		self.frame1.pack(padx = 10, pady = 2)
		self.frame2.pack(padx = 10, pady = 2)
		self.frame3.pack(padx = 10, pady = 2)
		self.frame4.pack(padx = 10, pady = 2)
		self.frame5.pack(padx = 10, pady = 2)
		self.frame6.pack(padx = 10, pady = 2)
		self.frame7.pack(padx = 10, pady = 2)
		self.frame8.pack(padx = 10, pady = 2)
		self.frame9.pack()

		return None

	def __place_widgets(self) -> None:

		self.pass_entry = ctk.CTkEntry(self.frame1,
			placeholder_text = 'password',
			textvariable = self.password,
			font = ('cascadia code', 14),
			fg_color = 'transparent',
			height = 30,
			width = 280)

		redo_icon = ctk.CTkImage(Image.open('./assets/redo-light.png'), size = (25, 25))
		self.redo_button = ctk.CTkButton(self.frame1,
			image = redo_icon,
			command = lambda: self.on_press('redo'),
			fg_color = 'transparent',
			text = '',
			width = 50,
			hover_color = '#37373C',
			corner_radius = 10)
		self.num_plus_button = ctk.CTkButton(self.frame7,
			command = lambda: self.on_press('num_plus'),
			fg_color = 'transparent',
			text = ' + ',
			width = 50,
			hover_color = '#37373C',
			corner_radius = 10)
		self.num_minus_button = ctk.CTkButton(self.frame7,
			command = lambda: self.on_press('num_minus'),
			fg_color = 'transparent',
			text = ' - ',
			width = 50,
			hover_color = '#37373C',
			corner_radius = 10)
		self.spcl_plus_button = ctk.CTkButton(self.frame8,
			command = lambda: self.on_press('spcl_plus'),
			fg_color = 'transparent',
			text = ' + ',
			width = 50,
			hover_color = '#37373C',
			corner_radius = 10)
		self.spcl_minus_button = ctk.CTkButton(self.frame8,
			command = lambda: self.on_press('spcl_minus'),
			fg_color = 'transparent',
			text = ' - ',
			width = 50,
			hover_color = '#37373C',
			corner_radius = 10)

		self.len_label = ctk.CTkLabel(self.frame2, text = 'Length', fg_color = 'transparent', font = ('Open Sahgns Medium', 13))
		self.AZ_label = ctk.CTkLabel(self.frame3, text = 'A-Z', fg_color = 'transparent', font = ('Open Sans Medium', 13))
		self.az_label = ctk.CTkLabel(self.frame4, text = 'a-z', fg_color = 'transparent', font = ('Open Sahgns Medium', 13))
		self.num_label = ctk.CTkLabel(self.frame5, text = '0-9', fg_color = 'transparent', font = ('Open Sahgns Medium', 13))
		self.spcl_label = ctk.CTkLabel(self.frame6, text = '!@#$%^&*', fg_color = 'transparent', font = ('Open Sahgns Medium', 13))
		self.min_num_label = ctk.CTkLabel(self.frame7, text = 'Minimum numbers', fg_color = 'transparent', font = ('Open Sahgns Medium', 13))
		self.min_spcl_label = ctk.CTkLabel(self.frame8, text = 'Minimum special', fg_color = 'transparent', font = ('Open Sahgns Medium', 13))

		self.pass_length = ctk.IntVar(value = 16)
		self.length_label = ctk.CTkLabel(self.frame2,
			textvariable = self.pass_length,
			fg_color = 'transparent',
			font = ('cascadia code', 12))
		self.min_num = ctk.IntVar(value = 1)
		self.min_num_count_label = ctk.CTkLabel(self.frame7,
			textvariable = self.min_num,
			fg_color = 'transparent',
			font = ('cascadia code', 12))
		self.min_spcl = ctk.IntVar(value = 1)
		self.min_spcl_count_label = ctk.CTkLabel(self.frame8,
			textvariable = self.min_spcl,
			fg_color = 'transparent',
			font = ('cascadia code', 12))

		self.len_slider = ctk.CTkSlider(self.frame2,
			from_ = 8,
			to = 128,
			number_of_steps = 113,
			width = 300,
			variable = self.pass_length,
			command = lambda event: self.on_press('slider'))


		self.AZ = ctk.IntVar(value = 1)
		self.AZ_switch = ctk.CTkSwitch(self.frame3, text = '',
			onvalue = 1,
			offvalue = 0,
			width = 10,
			variable = self.AZ,
			command = lambda: self.on_press('AZ-Switch'))
		self.az = ctk.IntVar(value = 1)
		self.az_switch = ctk.CTkSwitch(self.frame4, text = '',
			onvalue = 1,
			offvalue = 0,
			width = 10,
			variable = self.az,
			command = lambda: self.on_press('az-Switch'))
		self.num = ctk.IntVar(value = 1)
		self.num_switch = ctk.CTkSwitch(self.frame5, text = '',
			onvalue = 1,
			offvalue = 0,
			width = 10,
			variable = self.num,
			command = lambda: self.on_press('09-Switch'))
		self.spcl = ctk.IntVar(value = 1)
		self.spcl_switch = ctk.CTkSwitch(self.frame6, text = '',
			onvalue = 1,
			offvalue = 0,
			width = 10,
			variable = self.spcl,
			command = lambda: self.on_press('spcl-Switch'))

		self.pass_entry.pack(side = 'left')
		self.redo_button.pack(side = 'right')

		self.len_label.pack(side = 'left', padx = self.padx, pady = self.pady)
		self.len_slider.pack(side = 'right', pady = self.pady)
		self.length_label.pack(side = 'right', padx = self.padx, pady = self.pady)

		self.AZ_label.pack(side = 'left', padx = self.padx, pady = self.pady)
		self.AZ_switch.pack(side = 'right', pady = self.pady)

		self.az_label.pack(side = 'left', padx = self.padx, pady = self.pady)
		self.az_switch.pack(side = 'right', pady = self.pady)

		self.num_label.pack(side = 'left', padx = self.padx, pady = self.pady)
		self.num_switch.pack(side = 'right', pady = self.pady)

		self.spcl_label.pack(side = 'left', padx = self.padx, pady = self.pady)
		self.spcl_switch.pack(side = 'right', pady = self.pady)

		self.min_num_label.pack(side = 'left', padx = self.padx, pady = self.pady)
		self.num_plus_button.pack(side = 'right', padx = self.padx, pady = self.pady)
		self.num_minus_button.pack(side = 'right', padx = self.padx, pady = self.pady)
		self.min_num_count_label.pack(side = 'right', padx = self.padx, pady = self.pady)

		self.min_spcl_label.pack(side = 'left', padx = self.padx, pady = self.pady)
		self.spcl_plus_button.pack(side = 'right', padx = self.padx, pady = self.pady)
		self.spcl_minus_button.pack(side = 'right', padx = self.padx, pady = self.pady)
		self.min_spcl_count_label.pack(side = 'right', padx = self.padx, pady = self.pady)

	@staticmethod
	def generator(**params) -> str:
		A_Z = 'ABCDEFGHIJLMNPQRSTUVWXYZ'
		a_z = 'abcdefghijmnopqrstuvwxyz'
		num = '123456789'
		spl = '!@#$%^&*'
		full = str()
		rng = params['length']

		out = list()
		if params['0-9']:
			for _ in range(params['min_num']):
				out.append(choice(num))
			full += num
			rng -= params['min_spcl']

		if params['spcl']:
			for _ in range(params['min_spcl']):
				out.append(choice(spl))
			full += spl
			rng -= params['min_num']

		if params['A-Z']:
			full += A_Z
		if params['a-z']:
			full += a_z

		if len(full):
			for _ in range(rng):
				out.append(choice(full))

		if len(out):
			for _ in range(256):
				idx = randint(0, params['length'] - 1)
				out[0], out[idx] = out[idx], out[0]

		return ''.join(out)

	def on_press(self, button) -> None:

		if button == 'redo':
			pass

		elif button == 'slider':
			self.params['length'] = self.pass_length.get()

		elif button == 'num_plus':
			if self.min_num.get() + self.min_spcl.get() < self.pass_length.get():
				self.min_num.set(self.min_num.get() + 1)
			self.params['min_num'] = self.min_num.get()

		elif button == 'num_minus':
			if self.min_num.get() > 0:
				self.min_num.set(self.min_num.get() - 1)
			self.params['min_num'] = self.min_num.get()

		elif button == 'spcl_plus':
			if self.min_num.get() + self.min_spcl.get() < self.pass_length.get():
				self.min_spcl.set(self.min_spcl.get() + 1)
			self.params['min_spcl'] = self.min_spcl.get()

		elif button == 'spcl_minus':
			if self.min_spcl.get() > 0:
				self.min_spcl.set(self.min_spcl.get() - 1)
			self.params['min_spcl'] = self.min_spcl.get()

		elif button == 'AZ-Switch':
			self.params['A-Z'] = bool(self.AZ.get())

		elif button == 'az-Switch':
			self.params['a-z'] = bool(self.az.get())

		elif button == '09-Switch':
			self.params['0-9'] = bool(self.num.get())

		elif button == 'spcl-Switch':
			self.params['spcl'] = bool(self.spcl.get())

		else:
			pass

		self.password.set(Password_gen.generator(**self.params))
		return None

	@staticmethod
	def strength(password: str) -> int:

		criteria1 = len(password) >= 8
		criteria2 = any([char.isupper() for char in password])
		criteria3 = any([char.islower() for char in password])
		criteria4 = any([char.isdigit() for char in password])
		criteria5 = any([char.isalnum() == False for char in password])

		score = 0
		if criteria1:
			score += 1
		if all((criteria2, criteria3, criteria4, criteria5)):
			score += 1

		return score

class Text_edit():
	'''class Text_edit deals with the text editing window'''

	def __init__(self, text: str, textvariable: ctk.CTkEntry, text_size: ctk.CTkLabel, char_size: int)  -> None:
		
		self.text = text
		self.textvariable = textvariable
		self.label = text_size
		self.char_size = char_size
		self.error_e = False

		self.root = ctk.CTkToplevel(fg_color = '#1F1F1F')
		self.root.geometry('500x300')
		self.root.minsize(500, 300)
		self.root.title('')
		self.root.after(250, lambda: self.root.iconbitmap('./assets/favicon.ico'))

		self.bottom = ctk.CTkFrame(self.root, height = 20, fg_color = '#181818')
		self.bottom.pack(side = 'bottom', fill = 'x')

		self.text_entry = ctk.CTkTextbox(self.root,
			font = ('cascadia code', 14))
		self.text_entry.pack(expand = True, fill = 'both', padx = 3, pady = 3)
		self.text_entry.insert('0.0', text)
		self.text_entry.bind('<Any-KeyPress>',
			lambda event: threading.Thread(target = self.__entered, args = (event,)).start())

		self.char_left_label = ctk.CTkLabel(self.bottom,
			text = f'{char_size - len(text)} characters left',
			fg_color = 'transparent',
			font = ('cascadia code', 11),
			text_color = '#AAAAAA')
		self.char_left_label.pack(side = 'right', padx = 20)

		self.destroy_label = ctk.CTkLabel(self.bottom,
			text = 'Alt-Enter to exit',
			fg_color = 'transparent',
			font = ('cascadia code', 11),
			text_color = '#AAAAAA')
		self.destroy_label.pack(side = 'left', padx = 20)

		self.root.bind('<Alt-Return>', lambda event: self.__close_window(event))

		self.root.mainloop()

	def __error_message(self) -> None:

		if self.error_e:
			self.__close_error()

		self.error_frame = ctk.CTkFrame(self.root,
			height = 37,
			width = 210,
			fg_color = '#9C2B2E')
		self.error_frame.pack_propagate(False)

		cancel_icon = ctk.CTkImage(Image.open('./assets/cancel-light.png'), size = (18, 18))
		self.error_label_icon = ctk.CTkLabel(self.error_frame,
			fg_color = 'transparent',
			image = cancel_icon,
			text = '')
		self.error_label = ctk.CTkLabel(self.error_frame,
			fg_color = 'transparent',
			text = 'Maximun character\nLimit Reached',
			font = ('cascadia code', 11),
			justify = 'left')

		close_icon = ctk.CTkImage(Image.open('./assets/cross-light.png'), size = (12, 12))
		self.save_button = ctk.CTkButton(self.error_frame,
			image = close_icon,
			command = self.__close_error,
			fg_color = 'transparent',
			text = '',
			width = 30,
			hover_color = '#8D0000',
			corner_radius = 10)

		self.error_label_icon.pack(side = 'left', padx = 10)
		self.error_label.pack(side = 'left')
		self.save_button.pack(side = 'right', padx = 10)
		self.error_frame.place(relx = 0.985, rely = 0.88, anchor = 'se')
		self.error_e = True

		self.root.after(3000, self.__close_error)
		return None

	def __close_error(self) -> None:

		self.error_frame.place_forget()
		self.error_e = False
		return None

	def __entered(self, event) -> None:
		
		try:
			if len(self.text_entry.get('0.0', 'end')) - 1 > self.char_size:
				self.__error_message()
			else:
				self.char_left_label.configure(text = str(self.char_size - len(self.text_entry.get('0.0', 'end')) + 1) + ' characters left')
		except:
			pass
		return None

	def __close_window(self, event) -> None:

		text = self.text_entry.get('0.0', 'end')[0: self.char_size].strip()
		self.textvariable.delete('0.0', 'end')
		self.textvariable.insert('0.0', text)
		if len(text) < 1000:
			self.label.set(f'{len(text)}B')
		else:
			self.label.set(f'{len(size) / 1024:.2f}KB')
		self.root.destroy()
		return

class View_files():
	'''class View_files deals with the file viewing window'''

	def __init__(self, *args) -> None:
		
		self.root = ctk.CTkToplevel(fg_color = '#1F1F1F')
		self.root.geometry('500x300')
		self.root.title('')
		self.root.minsize(500, 300)
		self.root.after(250, lambda: self.root.iconbitmap('./assets/favicon.ico'))

		self.files = args[0]
		self.files_label = args[1]
		self.size_label = args[2]
		self.capacity_label = args[3]
		self.bar = args[4]
		self.capacity = args[5]
		self.instance = args[6]

		self.frames = dict()

		self.bottom = ctk.CTkFrame(self.root, height = 20, fg_color = '#181818')
		self.bottom.pack(side = 'bottom', fill = 'x')

		ctk.CTkFrame(self.root, height = 5, fg_color = 'transparent').pack(side = 'bottom', fill = 'x')

		self.main_frame = ctk.CTkScrollableFrame(self.root, fg_color = 'transparent')
		self.main_frame.pack(expand = True, fill = 'both', padx = 5)

		self.no_f_label = ctk.CTkLabel(self.bottom,
			text = str(len(self.files)) + ' Files',
			fg_color = 'transparent',
			font = ('cascadia code', 11),
			text_color = '#AAAAAA')
		self.no_f_label.pack(side = 'right', padx = 20)

		for idx, file in enumerate(self.files, start = 1):
			self.__add_frame(file, idx)

		if not len(self.files):
			ctk.CTkLabel(self.main_frame,
				text = 'No files added.',
				fg_color = 'transparent',
				font = ('cascadia code', 13),
				text_color = '#AAAAAA').pack()

		self.root.mainloop()

	def __add_frame(self, name: str, idx: int) -> None:

		size = os.path.getsize(f'./TEMP/{name}')
		temp = ctk.CTkFrame(self.main_frame, height = 40, fg_color = '#181818')
		idx_label = ctk.CTkLabel(temp,
			text = f'{idx}.',
			font = ('cascadia code', 13))
		name_label = ctk.CTkLabel(temp,
			text = self.shorten_name(name),
			font = ('Open Sans Medium', 13))
		size_label = ctk.CTkLabel(temp,
			text = f'{size}B',
			font = ('cascadia code', 11))
		close_icon = ctk.CTkImage(Image.open('./assets/cross-light.png'), size = (15, 15))
		close_button = ctk.CTkButton(temp,
			image = close_icon,
			command = lambda: self.__remove(name),
			fg_color = 'transparent',
			text = '',
			width = 30,
			hover_color = '#37373C',
			corner_radius = 10)

		idx_label.pack(side = 'left', pady = 3, padx = 10)
		name_label.pack(side = 'left', pady = 3, padx = 5)
		size_label.place(y = 3, x = 350, anchor = 'ne')
		close_button.pack(side = 'right', pady = 3, padx = 5)
		temp.pack(side = 'top', fill = 'x', padx = 3, pady = 3)

		self.frames[name] = temp
		return None

	def __remove(self, name: str) -> None:
		
		size = os.path.getsize(f'./TEMP/{name}')
		self.frames[name].pack_forget()
		self.files.remove(name)
		self.frames.pop(name)
		os.remove(f'./TEMP/{name}')

		if not len(self.files):
			ctk.CTkLabel(self.main_frame,
				text = 'No files added.',
				fg_color = 'transparent',
				font = ('cascadia code', 13),
				text_color = '#AAAAAA').pack()

		self.files_label.set(self.files_label.get() - 1)
		new_size = 0
		for file in self.files:
			new_size += os.path.getsize(f'./TEMP/{file}')

		self.instance.sz_files = new_size
		self.size_label.set(f'{new_size // 1024}KB')
		old = self.capacity_label.get().split('.')[0] + '.' + self.capacity_label.get().split('.')[1][: 2]
		new_capacity_label = abs(float(old) - size / 1024)
		self.capacity_label.set(f'{new_capacity_label:.2f}KB / {self.capacity / 1024:.2f}KB')
		self.no_f_label.configure(text = str(self.files_label.get()) + ' Files')

		ratio = self.bar.get() - size / self.capacity
		if ratio <= 0.8:
			self.bar.set(ratio)
			self.bar.configure(progress_color = 'green')
		elif ratio > 0.8 and ratio <= 0.93:
			self.bar.set(ratio)
			self.bar.configure(progress_color = 'orange')
		elif ratio > 0.93:
			self.bar.set(ratio)
			self.bar.configure(progress_color = 'red')

		return None

	@staticmethod
	def shorten_name(name: str) -> str:

		if len(name.split('.')[0]) <= 13:
			return name

		start = name.split('.')[0][:8]
		mid = name.split('.')[0][-5:]
		end = name.split('.')[1]
		out = f'{start}...{mid}.{end}'
		return out

class Extract():
	'''class Extract deals with extracting data back from the steg file'''

	def __init__(self, path: str) -> None:

		self.encryption = Encryption()
		self.dispersion = Dispersion()
		self.steg = Stegano()

		self.root = ctk.CTkToplevel(fg_color = '#1F1F1F')
		self.root.geometry('300x450')
		self.root.title('')
		self.root.resizable(0, 0)
		self.root.after(250, lambda: self.root.iconbitmap('./assets/favicon.ico'))
		self.error_e = False

		self.data = self.steg.read(path)
		self.__add_widgets()

	def __add_widgets(self) -> None:

		hsh_ref = list(self.data[1: 33])
		hsh = NP.full(32, 0, dtype = 'uint8')
		for idx, value in enumerate(sha256(bytes(self.data[33: ])).digest()):
			hsh[idx] = int(value)
		hsh = list(hsh)
		if hsh_ref == hsh:
			title = 'Data is un-encrypted'
			self.is_enc = False
		else:
			title = 'Data is encrypted'
			self.is_enc = True

		self.main_label = ctk.CTkLabel(self.root,
			text = title,
			fg_color = 'transparent',
			font = ('cascadia code', 14))
		self.enc_options = ctk.CTkComboBox(self.root,
			values = self.encryption.options,
			width = 250,
			font = ('cascadia code', 14),
			dropdown_font = ('cascadia code', 10),
			command = lambda event: self.encryption.set_algo(event))
		self.pass_label = ctk.CTkLabel(self.root,
			text = 'Password',
			fg_color = 'transparent',
			font = ('cascadia code', 10))
		self.password = ctk.StringVar(value = '')
		self.pass_entry = ctk.CTkEntry(self.root,
			placeholder_text = 'password',
			textvariable = self.password,
			font = ('cascadia code', 14),
			fg_color = 'transparent',
			height = 30,
			width = 250)
		self.kdf_label = ctk.CTkLabel(self.root,
			text = 'kdf-cycles',
			fg_color = 'transparent',
			font = ('cascadia code', 10))
		self.kdf = ctk.StringVar(value = '1')
		self.kdf_entry = ctk.CTkEntry(self.root,
			placeholder_text = 'password',
			textvariable = self.kdf,
			font = ('cascadia code', 14),
			fg_color = 'transparent',
			height = 30,
			width = 250)

		self.disp_label = ctk.CTkLabel(self.root,
			text = 'Dispersion',
			fg_color = 'transparent',
			font = ('cascadia code', 14))
		self.disp_on = False

		self.do_disp = ctk.IntVar(value = 1)
		self.disp_switch = ctk.CTkSwitch(self.root, text = '',
			onvalue = 1,
			offvalue = 0,
			width = 10,
			variable = self.do_disp)

		self.key_label = ctk.CTkLabel(self.root,
			text = 'Key',
			fg_color = 'transparent',
			font = ('cascadia code', 10))
		self.disp_key = ctk.StringVar(value = '255')
		self.disp_key_entry = ctk.CTkEntry(self.root,
			placeholder_text = 'password',
			textvariable = self.disp_key,
			font = ('cascadia code', 14),
			fg_color = 'transparent',
			height = 30,
			width = 250)

		do_icon = ctk.CTkImage(Image.open('./assets/tick-light.png'), size = (20, 20))
		self.tick_button = ctk.CTkButton(self.root,
			image = do_icon,
			command = self.__do,
			fg_color = 'transparent',
			text = '',
			hover_color = '#2B2D2E',
			corner_radius = 10,
			width = 30,
			height = 30)
		save_icon = ctk.CTkImage(Image.open('./assets/save2-light.png'), size = (20, 20))
		self.save_button = ctk.CTkButton(self.root,
			image = save_icon,
			command = self.__save,
			fg_color = 'transparent',
			text = '',
			hover_color = '#2B2D2E',
			corner_radius = 10,
			width = 30,
			height = 30,
			state = 'normal')

		if hsh_ref == hsh:
			self.enc_options.configure(state = 'disabled')
			self.pass_entry.configure(state = 'disabled')
			self.kdf_entry.configure(state = 'disabled')
			self.password.set('password')
			self.pass_entry.configure(text_color = '#737373')
			self.kdf_entry.configure(text_color = '#737373')

		self.main_label.place(x = 17, y = 14)
		self.enc_options.place(x = 17, y = 55)
		self.pass_label.place(x = 19, y = 88)
		self.pass_entry.place(x = 17, y = 110)
		self.kdf_label.place(x = 19, y = 140)
		self.kdf_entry.place(x = 17, y = 162)

		self.disp_label.place(x = 17, y = 215)
		self.disp_switch.place(x = 150, y = 219)
		self.key_label.place(x = 19, y = 244)
		self.disp_key_entry.place(x = 17, y = 266)

		self.tick_button.place(x = 185, y = 395)
		self.save_button.place(x = 240, y = 395)

		return None

	def __do(self) -> None:

		data = self.data.copy()
		if self.is_enc:

			if self.password.get().strip() == '':
				self.__error_message('Enter a\npassword')
				return None
			try:
				kdf = int(self.kdf_entry.get().strip())
			except:
				self.__error_message('Invalid\nKDF')
				return None

			self.encryption.set_key(self.password.get().strip(), kdf)
			data = self.encryption.decrypt(data,
				int(self.kdf_entry.get()),
				self.password.get().strip())
			if data is None:
				self.__error_message('Wrong\npassword / KDF')
				return None

		else:
			data = data[33:]

		if self.disp_switch.get():

			try:
				key = int(self.disp_key_entry.get().strip())
			except:
				self.__error_message('Invalid\nkey')
				return None

			data = self.dispersion.undo(data, key)

		data = data.tobytes()
		with open('./TEMP/IN/file.zip', 'wb') as f:
			f.write(data)

		if not zipfile.is_zipfile('./TEMP/IN/file.zip'):
			self.__error_message('Incorrect\nKEY')
			return None

		with zipfile.ZipFile('./TEMP/IN/file.zip', 'r') as f:
			self.files = f.namelist()
			self.files.remove('TEMP/%TEMP%.txt')
			f.extract('TEMP/%TEMP%.txt')
		with open('TEMP/%TEMP%.txt', 'r') as f:
			self.text = f.read()
		os.remove('TEMP/%TEMP%.txt')

		self.__open_files()
		return None

	def __error_message(self, message: str) -> None:

		if self.error_e:
			self.__close_error()

		self.error_frame = ctk.CTkFrame(self.root,
			height = 40,
			width = 270,
			fg_color = '#9C2B2E',
			border_width = 1,
			border_color = '#E84E4F')

		cancel_icon = ctk.CTkImage(Image.open('./assets/cancel-light.png'), size = (20, 20))
		self.error_label_icon = ctk.CTkLabel(self.error_frame,
			fg_color = 'transparent',
			image = cancel_icon,
			text = '')
		self.error_label = ctk.CTkLabel(self.error_frame,
			fg_color = 'transparent',
			text = message,
			font = ('cascadia code', 11),
			justify = 'left')

		close_icon = ctk.CTkImage(Image.open('./assets/cross-light.png'), size = (12, 12))
		self.close_button = ctk.CTkButton(self.error_frame,
			image = close_icon,
			command = self.__close_error,
			fg_color = 'transparent',
			text = '',
			width = 30,
			hover_color = '#8D0000',
			corner_radius = 10)

		self.error_label_icon.pack(side = 'left', padx = 10)
		self.error_label.pack(side = 'left')
		self.close_button.pack(side = 'right', padx = 10)
		self.error_frame.pack_propagate(False)
		self.error_frame.place(relx = 0.5, rely = 0.76, anchor = 'center')
		self.error_e = True

		self.root.after(3000, self.__close_error)
		return None

	def __close_error(self) -> None:

		self.error_frame.place_forget()
		self.error_e = False
		return None

	def __open_files(self) -> None:
		
		temp = Out_files(self.files, self.text)
		return None

	def __save(self) -> None:

		path = filedialog.askdirectory()
		try:
			with zipfile.ZipFile('./TEMP/IN/file.zip', 'r') as f:
				f.extractall(path)
		except:
			return None
		return None

class Out_files():
	'''class View_files displays the hidden data'''

	def __init__(self, files: list, text: str):

		self.root = ctk.CTkToplevel(fg_color = '#1F1F1F')
		self.root.geometry('300x450')
		self.root.title('')
		self.root.resizable(0, 0)
		self.root.after(250, lambda: self.root.iconbitmap('./assets/favicon.ico'))

		self.text_label = ctk.CTkLabel(self.root,
			text = 'Hidden text',
			fg_color = 'transparent',
			font = ('cascadia code', 10),
			height = 8)
		self.text_entry = ctk.CTkTextbox(self.root,
			font = ('cascadia code', 14),
			height = 80,
			fg_color = '#181818')
		if text == '':
			self.text_entry.insert('0.0', 'No text')
			self.text_entry.configure(state = 'disabled')
			self.text_entry.configure(text_color = '#737373')
		else:
			self.text_entry.insert('0.0', text)
		self.files_label = ctk.CTkLabel(self.root,
			text = 'Hidden files',
			fg_color = 'transparent',
			font = ('cascadia code', 10),
			height = 8)
		self.main_frame = ctk.CTkScrollableFrame(self.root, fg_color = '#181818')

		if not len(files):
			ctk.CTkLabel(self.main_frame,
				text = 'No files added.',
				fg_color = 'transparent',
				font = ('cascadia code', 13),
				text_color = '#AAAAAA').pack()
		else:
			for idx, file in enumerate(files, start = 1):
				self.__add_frame(file.split('/')[-1], idx)

		self.text_label.pack(padx = 5, pady = 5, fill = 'x')
		self.text_entry.pack(padx = 5, pady = 5, expand = True, fill = 'both')
		self.files_label.pack(padx = 5, pady = 5, fill = 'x')
		self.main_frame.pack(padx = 5, pady = 5, expand = True, fill = 'both')

		return None

	def __add_frame(self, name, idx) -> None:

		temp = ctk.CTkFrame(self.main_frame, height = 30, fg_color = '#1F1F1F')
		idx_label = ctk.CTkLabel(temp,
			text = f'{idx}.',
			font = ('cascadia code', 13))
		name_label = ctk.CTkLabel(temp,
			text = View_files.shorten_name(name),
			font = ('Open Sans Medium', 13))

		idx_label.pack(side = 'left', pady = 3, padx = 10)
		name_label.pack(side = 'left', pady = 3, padx = 5)
		temp.pack(side = 'top', fill = 'x', padx = 3, pady = 3)

		return None

Startup()
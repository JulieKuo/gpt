import logging
import time
from datetime import datetime
from pathlib import Path


class ExecutionLog():
	def __init__(self, log_folder, level=logging.INFO):
		self.check_directory(log_folder)
		date = self.get_date()
		filepath = '{}/{}.txt'.format(log_folder, date)
		self._project_name = ''

		self._logger = logging.getLogger(filepath)
		self._logger.setLevel(level)

		log_format = logging.Formatter('[%(asctime)s][%(levelname)5s] %(message)s', datefmt='%Y/%m/%d %H:%M:%S')
		f_handler = logging.FileHandler(filepath, 'a')
		f_handler.setLevel(logging.INFO)
		f_handler.setFormatter(log_format)

		self._logger.addHandler(f_handler)
		print('\nlog save at: ', filepath, '\n')

	def update_project_name(self, project_name):
		self._project_name = f'[{project_name}] '

	def start_job(self, action):
		self._time_start = time.time()
		self._logger.info("{}--- {} ".format(self._project_name, action).ljust(50, '-'))
		return

	def complete_job(self):
		self._logger.info("{} Cost {:.2f} sec -----\n".format(self._project_name, time.time() - self._time_start).rjust(50, '-'))
		return

	def write_info(self, log_msg):
		self._logger.info(f'{self._project_name} {log_msg}')
		return

	def write_error(self, log_msg):
		self._logger.error(f'{self._project_name} {log_msg}\n')
		return

	@staticmethod
	def check_directory(log_folder):
		Path(log_folder).mkdir(parents=True, exist_ok=True)

	@staticmethod
	def get_date():
		return datetime.today().strftime('%Y%m%d')

	def write_exception(self, log_msg=''):
		self._logger.exception(f'{self._project_name} {log_msg}\n')
		return


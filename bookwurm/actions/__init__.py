# SPDX-License-Identifier: BSD-3-Clause
from abc       import ABCMeta, abstractmethod
from argparse  import ArgumentParser, Namespace

__all__ = (
	'BookwurmAction',
)

class BookwurmAction(metaclass = ABCMeta):
	'''
	bookwurm action base class

	This is the abstract base class that is used
	to implement any possible action for the bookwurm
	command line interface.

	Attributes
	----------
	pretty_name : str
		The pretty name of the action to show.

	short_help : str
		A short help string for the action.

	help : str
		A more comprehensive help string for the action.

	description : str
		The description of the action.

	'''
	@property
	@abstractmethod
	def pretty_name(self) -> str:
		''' The pretty name of the action  '''
		raise NotImplementedError('Actions must implement this property')

	@property
	@abstractmethod
	def short_help(self) -> str:
		''' A short help description for the action '''
		raise NotImplementedError('Actions must implement this property')

	@property
	def help(self) -> str:
		''' A longer help message for the action '''
		return '<HELP MISSING>'

	@property
	def description(self) -> str:
		''' A description for the action  '''
		return '<DESCRIPTION MISSING>'


	def __init__(self):
		pass

	@abstractmethod
	def register_args(self, parser: ArgumentParser) -> None:
		'''
		Register action arguments.

		When an action instance is initialized this method is
		called so when :py:func:`run` is called any needed
		arguments can be passed to the action.

		Parameters
		----------
		parser : argparse.ArgumentParser
			The argument parser to register commands with.

		Raises
		------
		NotImplementedError
			The abstract method must be implemented by the action.

		'''

		raise NotImplementedError('Actions must implement this method')

	@abstractmethod
	def run(self, args: Namespace, config: dict) -> int:
		'''
		Run the action.

		Run the action instance, passing the parsed
		arguments and the selected device if any.

		Parameters
		----------
		args : argsparse.Namespace
			Any command line arguments passed.

		config : dict
			The bookwurm configuration file.

		Returns
		-------
		int
			0 if run was successful, otherwise an error code.

		Raises
		------
		NotImplementedError
			The abstract method must be implemented by the action.

		'''

		raise NotImplementedError('Actions must implement this method')

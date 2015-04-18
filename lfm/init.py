import clip

import utils
from lambda_config import LambdaConfig


PROMPT = '''lfm init will help you create a .lambda.yml file. It only covers the
most common configuration, and tries to guess sane defaults. You may
skip any step that does not have a default by entering nothing.

Press ^C at any time to quit.
'''


def run():
	config = LambdaConfig().load_from_cwd()
	clip.echo(PROMPT)
	user_input = {
		'FunctionName': clip.prompt('Function name: ', skip=True),
		'Handler': clip.prompt('Handler: ', skip=True),
		'Description': clip.prompt('Description: ', skip=True),
		'Runtime': clip.prompt('Runtime', default='nodejs'),
		'Timeout': clip.prompt('Timeout: ', type=int, skip=True),
		'MemorySize': clip.prompt('Memory size: ', type=int, skip=True)
	}
	config.update_config({k: v for k, v in utils.iteritems(user_input) if v})
	install_task = clip.prompt('Install task: ', skip=True)
	if install_task is not None:
		config.update({
			'install': install_task
		})
	config.dump_to_cwd()

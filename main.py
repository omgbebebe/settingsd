import sys
import os

from settingsd import const
from settingsd import application
from settingsd import logger


if __name__ == "__main__" :
	app = application.Application()
	app.init()

	logger.message(const.LOG_LEVEL_INFO, "Initialized")
	try :
		app.run()
	except KeyboardInterrupt :
		app.close()
	logger.message(const.LOG_LEVEL_INFO, "Closed")
	

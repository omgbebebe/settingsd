import sys
import os

from settingsd import application


if __name__ == "__main__" :
	app = application.Application()
	app.init()

	print >> sys.stderr, "Initialized"
	try :
		app.run()
	except KeyboardInterrupt :
		app.close()
	print >> sys.stderr, "\nClosed"


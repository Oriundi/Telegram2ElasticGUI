import logging
# from datetime import datetime
#from utilities.load_config import config_key

# now = datetime.now()

# create logger
log = logging.getLogger('main_log')
logging.basicConfig(format='%(asctime)s :: %(levelname)s :: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
log.setLevel(logging.INFO)
# create file handler which logs even debug messages
fh = logging.FileHandler("run_log.log")
fh.setLevel(logging.INFO)
fmt = logging.Formatter(fmt='%(asctime)s :: %(levelname)s :: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
fh.setFormatter(fmt)
log.addHandler(fh)

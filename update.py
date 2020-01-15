import subprocess
import logging

log = logging.getLogger('RemoTV.update')

def checkLocalChanges():
   untracked = 0
   modified = 0

   try:
      output = subprocess.check_output(["git", "status", "--porcelain"])
   except subprocess.CalledProcessError as error:
      log.error(error)
      return False

   for item in output.splitlines():
      item = item.split()
      if item[0] == b'M':
         modified = modified + 1
      elif item[0] == b'??':
         untracked = untracked + 1

   log.info("{} modified, {} untracked files".format(modified, untracked))

   if modified != 0:
      log.error("Error: Modified core filed detected!")
      return False
   else:
      return True


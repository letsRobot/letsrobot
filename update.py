import subprocess
import logging
import sys
import re
import robot_util
import extended_command

log = logging.getLogger('RemoTV.update')

update_available = False

def checkForUpdates():
   global update_available
   isOod = subprocess.check_output('git fetch && git status -b -uno', shell=True)
   isOod = str(isOod)
   if "behind" in isOod:
      update_available = re.search(r'\d+(\scommits|\scommit)', isOod).group(0).split()[0]
      return True
   else:
      return False

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
      log.error("Error: Modified core files detected!")
      return False
   else:
      return True

def doUpdate():
   # get the old head so we can revert if something goes wrong.
   try:
      old_head = subprocess.check_output(["git", "rev-parse", "HEAD"]).rstrip()
   except subprocess.CalledProcessError as error:
      log.error(error)
      return False

   # run the update
   try:
      subprocess.check_output(["git", "pull"])
   except subprocess.CalledProcessError as error:
      log.error(error)
      # attempt to revert to old head
      subprocess.call(["git", "reset","--hard" ,old_head])
      return False

   # test the updated controller.
   try:
      subprocess.check_output([sys.executable, "controller.py", "--test"])
   except subprocess.CalledProcessError as error:
      log.error(error)
      # attempt to revert to old head
      subprocess.call(["git", "reset", "--hard", old_head])
      return False
   return True

def update_handler(command, args):
   global update_available
   if extended_command.is_authed(args['sender']) == 2:
      if len(command) == 1:  # just .update
         if not update_available:
            if checkForUpdates():
               robot_util.sendChatMessage(
                  "{} updates available. Send '.update yes' to apply updates.".format(update_available))
            else:
               robot_util.sendChatMessage(
                  "Robot is already up to date. Nothing to do!")
         else: 
            robot_util.sendChatMessage(
               "{} updates available. Send '.update yes' to apply updates.".format(update_available))
      else:
         if command[1] == "yes":
            if checkLocalChanges():
               if doUpdate():
                  update_fetched = False
                  robot_util.sendChatMessage(
                     'Update completed. Restart for changes to take effect.')
               else:
                  robot_util.sendChatMessage(
                    'Update Failed. run "git pull" locally to determine error.')
            else:
               robot_util.sendChatMessage(
                  'Automatic Update aborted, you have modified core files.')

def setup(config):
   extended_command.add_command('.update', update_handler)

if __name__ == "__main__":

   def sendChatDummy(*args):
      return True

   robot_util.sendChatMessage = sendChatDummy

   if checkForUpdates():
      print("Updates Available.")
      if (sys.version_info > (3, 0)):
         key = input('Apply updates (y/n)? ').rstrip()
      else:
         key = raw_input('Apply updates (y/n)? ').rstrip()
      key = str(key.lower())
      if key == "y":
         if checkLocalChanges():
            if doUpdate():
               print("Update completed successfully")
            else:
               print("Update failed, attempted revert")
         else:
            print("Local changes detected, update aborted")
      else:
         print("Exited without updating")
   else:
      print("Already up to date")



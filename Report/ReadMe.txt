Required Platforms:

PC Application:
    - Bluetooth-enabled hardware on the PC
    - Any modern stable Linux distribution (Mac OSX might work as well, but
      has not been tested)
    - Python 3.6
    - pip (Python package manager - Python 3 version)

Mobile Application:
    - Android minimum version 5.1 (SDK 21)
    - Bluetooth-enabled hardware on the phone
    - Camera hardware on the phone

Setup and Execution Instructions for PC:
    - Turn Bluetooth On
    - Open Terminal emulator
    - Go into the project's PC directory
    - Execute "./run.sh"

Setup and Execution Instructions for Phone:
    - Install provided APK in project root directory on Android phone with minimum version 5.1
    - Open the app and follow the PC program's instructions

Example usage:
- Create file "foo.txt" on your "/tmp" directory with contents "1NS3CUR3 F1L3"
- Follow setup and execution instructions for Phone
- Follow the computer's instructions until you have succesfully paired your
  device
- Execute command "status" and verify the output
- On the phone, select the "Connection" option and input your password
- On the computer, notice that the phone has been connected by executing the
  command "status" again
- Run the command "add /tmp/foo.txt" (note that this application supports tab
  completion on the command line)
- Check again with "status" that the file has been added to the protected file
  list
- On the phone, press "Done"
- On the computer, check the file (/tmp/foo.txt) and notice that its contents
  have been encrypted
- On the computer, run "exit"
- Execute the "run.sh" script once again
- Notice that the computer no longer shows the welcome screen, and input your
  previously selected password
- On the phone, press "Connection" once again
- On the computer, check that "/tmp/foo.txt" has been decrypted
- On the computer, execute the "remove /tmp/foo.txt" command
- On the phone, press done
- On the computer, verify that the "/tmp/foo.txt" file has remained decrypted
- On the phone, press "Connection"
- On the computer, execute "add /tmp/foo.txt", then crash the program (you
  may, for example, close your terminal window) and press "Done" on your
  phone
- Execute the program again and notice that after you input your password,
  your file will be encrypted even though the phone is not connected.
- Connect the phone once again, then run the "unpair" command on the computer
- Press "Unpair current device" on the phone and input your password

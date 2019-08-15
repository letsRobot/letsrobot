---
name: Bug report
about: Create a report to help us improve

---

**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Use this controller
2. Change this setting
3. do this command
4. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Screenshots**
Screenshots of the console are appreciated.

**Logs**
Always try to share logs if you can, or an output of the console.

**Configurations**
 - Sharing a pared down version of your `controller.conf` file could help. We obviously don't need things like your API key, username, etc.
 - We need to know what version of the controller you're running. Run the following in the repo directory:
    ```sh
    git log -1
    ```
    - Paste the output here. Should look similar to
        ```
        commit bb800be720a90aca11652495960f4eca6798cb1 (HEAD -> master, origin/master, origin/HEAD)
        Merge:  ee13305 5b68a0
        Author: Bryan Morrison <b.morrison4@students.clark.edu>
        Date:   Wed August 14 18:25:21 2019 -0700

            Merge pull request # 7 from remotv/amixer-usb-volume-fix

            Amixer usb volume fix
        ```

**Additional context**
Add any other context about the problem here.

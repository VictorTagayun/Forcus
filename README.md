# Focus Enforcer
Forcus Enforcer (a.k.a Forcus) is an application that lets Cozmo supervise your concentration on some jobs on desk, such as reading a book. Cozmo assumes your face wouldn’t move a lot if you fully concentrated on the job. He gets increasingly angry and reacts every time your face moved a large distance, meaning you’re not concentrating.

## Steps
1. Place cozmo in front of and about same height of your face
2. Change FOCUS_TIME in forcus.py to set your anticipated forcusing time (in seconds)
3. Run script forcus.py
4. Start your own task, for example reading the book

## Dependencies
The modules required in addition to the Cozmo module are:

* pygame
* Common

Common is a package included in the Git repo: https://github.com/Wizards-of-Coz/Common

The other modules can be installed via pip if not already present: 
`pip3 install pygame`

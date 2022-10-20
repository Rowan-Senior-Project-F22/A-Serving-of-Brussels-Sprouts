# A Serving of Brussels Sprouts
Senior project git repository.

## Project Description
The project's goal is to build a Web application that provides both music
recommendations and social features. The application will rely on resources
made available by Spotify and will be built using the Django Web framework.

The social concept of the system is to introduce its users to new people and
new music. By providing friend and music suggestions to the user, the system
will initiate conversations.

## Project Structure
This is a Django application broken out by application. Applications are specified in the primary
directory.

## Deployment
There is an Azure Web Application that is connected to the application thru a CI/CD pipeline via GitHub workflow automation.
This leverages the ```staging``` branch as the deployment code base. Merges to this branch require a pull request, which can come
from any of the three design teams' individual branches. Note that changes should only be pushed to ```staging``` if they are
ready for testing and review by other team members. Once code is tested, pull requests can be created to ```main```, pending a
successful deployment, which requires approval by a majority  of the group (5 members).

## Contributors
- Chris Rinaldi <rinald43@students.rowan.edu>
- Jeremy Juckett <jucket82@students.rowan.edu>
- Brandon Ngo <ngobra82@students.rowan.edu>
- Wasiu Biobaku <biobak96@students.rowan.edu>
- Tristan Toothaker <tootha53@students.rowan.edu>
- Nayef Alzurayer <alzura47@students.rowan.edu>
- Alex Deems <deemsa64@students.rowan.edu>
- Mura Babar <babart77@students.rowan.edu>

## Using GIT
- Cloning the repo: git clone https://github.com/Rowan-Senior-Project-F22/Senior-Project-F22
- Pulling updates: git pull
- Branching: git branch branchname
- Switching branches: git checkout branchname
- Adding changes: git add filenames...
- Committing changes: git commit
- Pushing committed changes: git push
- Merging: git merge branchname
 
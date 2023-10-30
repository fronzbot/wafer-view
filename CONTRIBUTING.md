# Contributing to Wafer View

Everybody is invited and welcome to contribute to Wafer View.

The process is straight-forward.

 - Read [How to get faster PR reviews](https://github.com/kubernetes/community/blob/master/contributors/guide/pull-requests.md#best-practices-for-faster-reviews) by Kubernetes (but skip step 0 and 1)
 - Fork Wafer View [git repository](https://github.com/fronzbot/wafer-view).
 - Write the code for your feature/improvement/bug fix
 - Ensure tests work.
 - Create a Pull Request against the [**dev**](https://github.com/fronzbot/wafer-view/tree/dev) branch of Wafer View.

## Feature suggestions

If you want to suggest a new feature for Home Assistant (e.g., new integrations), please open a thread in our [Community Forum: Feature Requests](https://community.home-assistant.io/c/feature-requests).
We use [GitHub for tracking issues](https://github.com/home-assistant/core/issues), not for tracking feature requests.

## Development Quick-Start

#### Setup Local Repository

```bash
git clone git@github.com:<github-username>/wafer-view.git
cd wafer-view
git remote add upstream https://github.com/fronzbot/wafer-view.git
```

#### Create a virtualenv and install dependencies

First: if on linux, it's possible you need to install GTK3 for the GUI to work. Run the following commands (commands shown for debian):

```bash
sudo apt-get update
sudo apt-get install build-essential libgtk-3-dev
```

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirement.txt
pip install -r requirements_test.txt
pip install tox
```

#### Create your feature branch

```bash
git checkout -b <branch-name>
```

#### Make changes

Now you can make changes to your code. Keep changes minimal (ie. if you're working on adding a new standard, don't also include GUI changes- make those separate PR's even if they're linked)

#### Test changes

To run all tests:

```bash
tox
```

On Debian, it can take a long time to install wxPython inside the tox venv. As such, here are the commands you can use that do not rely on tox:

For linting: 
```bash
ruff check waferview tests
black --check --diff waferview tests
rst-lint README.rst
```

For tests:
```bash
pytest --timeout=9 --durations=10 -cov=waferview --cov-report term-missing
```

For new features, please add tests to ensure the feature works as intended and that any future changes do not break the intended behavior.

#### Commit Changes

```bash
git add .
git commit
```

#### Catching up with dev

If your code is taking a while to develop, you may be behind the `dev` branch, in which case you need to catch up before creating your pull-request. To do this you can run `git rebase` as follows (running this on your local branch):

```bash
git fetch upstream dev
git rebase upstream/dev
```

If rebase detects conflicts, repeat the following process until all changes have been resolved:

1. git status shows you the filw with a conflict. You will need to edit that file and resolve the lines between `<<<< | >>>>`
2. Add the modified file: `git add <file>` or `git add .`
3. Continue rebase: `git rebase --continue`
4. Repeat until all conflicts resolved

#### Push and Submit PR

Once you're ready to submit your PR, go ahead and push your changes to your fork:

```bash
git push origin <branch-name>
```
1. On GitHub, navigate to the [wafer-view](https://github.com/fronzbot/wafer-view/tree/dev) repository.
2. In the "Branch" menu, choose the branch that contains your commits (from your fork).
3. To the right of the Branch menu, click New pull request.
4. The base branch dropdown menu should read `dev`. Use the compare branch drop-down menu to choose the branch you made your changes in.
5. Type a title and complete the provided description for your pull request.
6. Click Create pull request.
7. 
More detailed instructions can be found here: [Creating a Pull Request](https://help.github.com/articles/creating-a-pull-request)

- [Development Practices](#development-practices)
- [Version Control](#version-control)

# Development Practices
- [Git Templates](#git-templates)

## Git Templates
Use the general [git templates](https://github.com/NCI-GDC/git-templates) for NCI-GDC project. Follow the instruction [here](https://github.com/NCI-GDC/git-templates#setup-git-templates) to setup for global config or for this particular repo. It contains git hooks to do security scanning for each commit, as well as other type checkings to insure the consistency of coding format.

# Version Control
- [Branches](#branches)
- [Commits](#commits)
- [Code Review](#code-review)
- [Rebase](#rebase)
- [Merge Branch](#merge-branch)
- [Tags](#tags)
- [Signed Commits](#signed-commits)
- [Master Branch](#master-branch)
- [Release](#release)
- [Workflow](#workflow)

## Branches
All new development should happen on a supporting branch rather than directly on develop or master. Supporting branches should formatted as `<type>/##-couple-words` or `<type>/very-short-description`, where <type> denotes a change type as derived from the [AngularJS Git Commit Message Convention](https://gist.github.com/stephenparish/9941e89d80e2bc58a153 "AngularJS Git Commit Message Convention").

To create a supporting branch, type 'git checkout -b branch_name' e.g.: 

```
❯ git checkout -b feat/678-my-feature
```

Once development is complete for the scope defined by the supporting branch, a pull request can be made for the develop branch to code review the changes. Once the changes are reviewed and approved, they can be merged into the develop branch.

At an agreed upon point in each development sprint, a release branch will be created off of the develop branch. This signifies all new development for that repository is complete, and any new development occuring in support branches or the develop branch will not be available to merge into master until the next sprint. Any development occuring in this release branch should be only related to bug fixes for what has already been completed. Release branches should be formatted as 'release-vA.B.C.D', where A = major release, B = project phase, C = monthly milestone, D = sprint within the monthly milestone.

```
❯ git checkout -b release-v0.2.15.1 develop
```

It's important to note any changes going into this release branch need to also be merged back into the develop branch, as well.

```
❯ git checkout develop
❯ git merge --no-ff release-v0.2.15.1
```

At the end of each sprint, once a release branch is deemed stable, the release branch will be merged into master. At any given point, the current SHA in master should be able to be deployed to staging. Once this merge occurs, the master branch should be tagged with the release number used in the release branch naming convention.

```
❯ git checkout master
❯ git merge --no-ff release-v0.2.15.1
❯ git tag -s v0.2.15.1
```

This branch structure is essentially the [git flow](http://nvie.com/posts/a-successful-git-branching-model/ "Git Flow Overview") model, and is used  to allow for a clear delineation and sign off between each phase of development and testing.


*References*

- [Git Flow Overview](http://nvie.com/posts/a-successful-git-branching-model/ "Git Flow Overview")
- [AngularJS Git Commit Message Convention](https://gist.github.com/stephenparish/9941e89d80e2bc58a153 "AngularJS Git Commit Message Convention").

## Commits

Commit messages follow a combination of guidelines set by Angular and Tim Pope.

Examples of valid commits:
 
```
type(scope): one line description (50 char or less)
```

```
type(scope): one line description (50 char or less)

Longer description (70 or less)
- list of changes
- one more thing
```

```
type(scope): one line description (50 char or less)

Closes ##
```

```
type(scope): one line description (50 char or less)

Longer description (70 or less)
- list of changes
- one more thing

Closes ##, ##
Closes ##
```

This format is automatically checked by a pre commit git hook.

*References*

- http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html
- http://addamhardy.com/blog/2013/06/05/good-commit-messages-and-enforcing-them-with-git-hooks/
- https://docs.google.com/document/d/1QrDFcIiPjSLDn3EL15IJygNPiHORgU1_OOAqWjiDU5Y/edit#

## Code Review

All branches should be code reviewed prior to merge back into develop. The process for this is straightforward - submit a pull request to develop, tag the relevant users that you desire review from, and wait for comment. Once your reviewers have signed off on your changes, then you may merge the changes into develop and delete your supporting branch. 

Any branches containing significant work need to be reviewed and signed-off before they can be considered complete.

## Rebase


*References*

```
❯ git checkout develop
❯ git pull origin develop
❯ git checkout <feature_branch>
❯ git rebase -i develop // Squash and rework commits here
❯ git push <feature_branch> --force-with-lease
```

- https://www.atlassian.com/git/tutorials/rewriting-history/git-rebase-i

## Merge Branch

Branches can only be merged after the following is completed:

0. Rebased
0. Signed Off
0. Tested by CI

Make sure your branch is up to date with develop by [rebasing](#rebase) before merging.

```
❯ git checkout develop
❯ git merge <feature_branch>
❯ git push origin develop
```

## Tags

```
❯ git tag -s 1.2.3
```

*References*

- http://git-scm.com/book/en/Git-Basics-Tagging

## Signed Commits

Tags should be signed.

### Generating a PGP Key
```
❯ brew install gpg 
❯ gpg --gen-key
❯ gpg --list-secret-keys | grep "^sec"
[gpg-key-id]
❯ git config user.signingkey [gpg-key-id]
```

### Adding a maintainer key
```
❯ gpg -a --export [gpg-key-id] | git hash-object -w --stdin
[object SHA]
❯ git tag -a [object SHA] maintainer-pgp-pub
```

*References*

- http://mikegerwitz.com/papers/git-horror-story
- https://fedoraproject.org/wiki/Creating_GPG_Keys
- http://www.javacodegeeks.com/2013/10/signing-git-tags.html
- https://coderwall.com/p/d3uo3w
- http://git.661346.n2.nabble.com/GPG-signing-for-git-commit-td2582986.html

## Master Branch

No development should happen on the master branch and tests should never be broken.

## Release

TODO - describe the release process since it is no longer automated.

## Workflow

0. clone the repo, git init with [template](#git-templates)
0. create a new [branch](#branches)
0. do some [work](#development-practices)
0. [commit](#commits) your changes
0. push changes to Github for [review](#code-review)
0. repeat 3-5 as necessary
0. [rebase](#rebase) develop into your branch and deal with any conflicts.
0. push feature changes to Github using `--force-with-lease`
0. get someone to [review and sign-off](#code-review) on your branch
0. wait for the CI system to test your branch
0. have your branch [merged](#merge-branch) into develop
0. repeat 2-11 until sprint work complete
0. create the release branch from develop
0. implement bug fixes directly into the release branch
0. update CHANGELOG and documentation for new release
0. [tag](#tags) release
0. merge the release branch into develop and master
0. run [release](#release) process

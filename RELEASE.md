# RELEASE INSTRUCTIONS

Headfake follows [semver](https://semver.org/) for versioning which means that only major point releases will be
breaking changes. It uses a version of [gitflow](https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow)

## Preparing a patch release
* The starting point for a patch/fix for a minor (non-breaking) version should be the `releases/X.Y.0` branch
* IF the release branch has been closed, a new branch `hotfixes/X.Y.Z` should be created from the nearest tag
(e.g. if the fix is for 1.2.x, and the latest tag is v1.2.3, then the branch should be called `hotfixes/1.2.3`.
* Add information on the release into the HISTORY.md file, this should include the date and version number.
* Create a new tag corresponding to the version number (e.g. v1.2.4).

## Preparing a minor or major release
* At the point of release preparation
* Create a new branch `releases/X.Y.0` from `develop` e.g. `releases/2.4.x`.
* Additional changes to the release should be made to the release branch at this point and later merged into `develop`.
* Whether the release is minor or major will be depend on whether it is a breaking change or additional
functionality/non-critical bug fixes.
* Add information on the release into the HISTORY.md file, this should include the date and version number.
* Create a new tag corresponding to the version number (e.g. v2.4.0).

## Making the release
Once work in the release branch
is complete, a new tag should be created.
* Run `make version` command and confirm that the version is as expected (setup_scm will produce a
 'dirty' version if files have changed and have not been committed)
* Run `make upload` command and confirm that the build and upload have worked correctly.

## Final merging of branches
* Whether patches are merged into the main branches depends on whether they affect later releases.
* Minor and major releases should be merged into `develop` and then `master`
* Old release branches should be closed

## New features
* For very minor fixes/changes commits can be made to `develop` although this is not recommended.
* Direct commits should not be made to `master`
* New features should be built within a feature branch derived from the `develop` branch.
* Feature branch
* It is recommended that a feature branch contains a single feature, although this will not always be possible
(particularly for a major refactoring).
* Feature branches should be named something like `features/add-new-item`
* Feature branches should be merged into `develop` or a release branch as soon as possible and closed

# cinderblock

Scenario: You are using CircleCI and GitHub. You have some product that is made
of several components. Each component has its own git repository and project on
CircleCI.  Separately, there's a git repository and associated CircleCI project
which runs integration tests for all the components. When a commit is made to a
component, you want to:

  1. build the component,
  2. run the integration tests, then
  3. see the results of the integration tests from the triggering commit.

`cinderblock` uses the CircleCI and GitHub APIs to accomplish this workflow
with a minimum of fuss.

## Install

Put something like this in circle.yml:

    dependencies:
      pre:
        - pip install --user git+https://github.com/paperg/cinderblock.git

## Usage

### Triggering Integration Tests

Scenario: CircleCI is building your project. It's just run your unit tests and
they have passed. Now you want integration tests to run.

      cinderblock trigger paperg/integration/master

A CircleCI API token which has privileges to trigger a build on the projects
involved must be set in `$CINDERBLOCK_CIRCLE_API_TOKEN`.  This token gets passed
as an environment variable between the projects.  This can be used for the 
receiving project to use CircleCI API to grab artifacts from the triggering 
projects.

A build of the master branch of the paperg/integration project will be started.
In that build, cinderblock will set `$CINDERBLOCK_SOURCE_COMMIT` and
`$CINDERBLOCK_SOURCE_BUILD` environment variables so the integration tests can
know where the trigger came from.

### Updating Commit Status from the Integration Tests

Scenario: Some other project has triggered integration tests. As the
integration tests, you need to update the commit status of the commit that
initiated the tests, based on the success or failure of integration tests.

    cinderblock update pending
    if run_the_tests; then
      cinderblock update success
    else
      cinderblock update failure
      exit 1
    fi

Replace `run_the_tests` with the appropriate test command.

cinderblock knows which commit to update because `cinderblock trigger` sets
`$CINDERBLOCK_SOURCE_COMMIT` with that information.

If `$CINDERBLOCK_SOURCE_COMMIT` isn't set or is empty, then cinderblock infers
that this build wasn't triggered by another project and so there is no commit
status to update. In this case `cinderblock update` will exit, successfully
having done nothing.

## Test

    tox

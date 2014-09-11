[![Build Status](https://travis-ci.org/KeepSafe/android-resource-remover.svg?branch=master)](https://travis-ci.org/KeepSafe/android-resource-remover)

android-resource-remover
========================

android-resource-remover is utility that removes unused resources reported by [Android Lint](http://developer.android.com/tools/help/lint.html) from your project. The goal is to reduce your APK size and keep the app clean from unused stuff.


## Getting started
Requirements:

* Python >= 2.7.*
* ADT >= 16

To install run:

    pip install android-resource-remover

## Usage - general
Open the directory where your app is located and run

```
android-resource-remover
```

Android resources have dependencies to each other. This means that after running resource-remover the first time, it will clean up unused resources file that hold a reference to other resources. You can run this resource remover multiple times until there is no more unused resources to be removed. We've been running it up to 4 times in a row.


### Use with gradle
`android-resource-remover` is build on top of android lint. If you have a gradle project you have to run lint within your gradle build scripts and then use the `lint-result.xml` as the input file for `android-resource-remover`

e.g.

    ./gradlew clean build :lint && android-resource-remover --xml build/lint-results.xml


### Options

#### --help
Prints help message.

#### --lint
Full path to the lint tool like: `d:\Dev\Android SDK\tools\lint`

This will be executed as the lint command. If not provided it assumes the lint command in available and runs: `lint`

#### --app
Full path to the android app like: `d:\Dev\My_Android_App`

If not provided it assumes the current directory is the app's root directory.

#### --xml

Use existing lint result. If provided lint won't be run.

#### --ignore-layouts

Ignore layout directory

## Expected behavior
### Resource ID in code not found
If you have references to elements in an old layout that you're not using anymore, you will get a compile error that the ID (`R.id.<something>`) can not be found. The reason is that the resource file that contained `R.id.<something>` has been removed as it was not used any more. Time to clean up your code.

## FAQ
**Q:  installing dependency lxml failed** with `clang: error: unknown argument: '-mno-fused-madd' [-Wunused-command-line-argument-hard-error-in-future]`
*A: [http://stackoverflow.com/a/22322645](http://stackoverflow.com/a/22322645)*

## Release History
* 2014-09-11   v0.1.1   Fixes bugs
* 2014-02-14   v0.1.0   Initial release

## Licence
Apache version 2.0


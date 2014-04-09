android-resource-remover
========================

A script which removes unused resources reported by [Android Lint](http://developer.android.com/tools/help/lint.html)

## Getting started
Requirements:

* Python >= 2.7.*
* ADT >= 16

## Usage
Run the script from console.

```
python clean_app.py
```

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

## Release History
* 2014-02-14   v0.1.0   Initial release

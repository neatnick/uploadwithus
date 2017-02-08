# uploadwithus

`uploadwithus` is a python package and a command line tool which seeks to solve the problems that arise when attempting to use sendwithus with in a large production environment.  The tool give you the ability to:

- easily separate production and development code
- keep your templates and snippets in version control
- provide an easy to use point to allow you to deploy your local changes

To do this, the tool interacts with a local repository holding snippet and template code.  It duplicates the code in this repository on sendwithus, creating development copies for you.  You can then modify and test the development copies without affecting code in production.

## Installation

The tool requires python 3.  Once you have python 3 set up, installation is easy, just run: `pip install uploadwithus`.

## Project Setup

In order to use the `uploadwithus` tool, the project containing your templates and snippets should have the following structure:

```
├── snippets
│   ├── snippet1.html
│   └── snippet2.html
├── templates
│   ├── template1
│   │   ├── general.html
│   │   └── version2.html
│   └── template2
│       └── general.html
├── snippet_info.yaml
└── template_info.yaml
```

#### Snippets

Snippets are all contained within the `snippets` folder.  For a snippet to get uploaded to sendwithus it must be present in the `snippets` folder and also listed in the `snippet_info.yaml` file.  For the example project shown above the `snippet_info.yaml` file would look like this:

```yaml
- snippet1
- snippet2
```

#### Templates

Templates are contained within the `templates` folder.  Each sendwithus template is represented by a directory containing `html` files for each version on the template.  Every template folder must at least contain a `general.html` file which is the default version for the template.  As with snippets, in order for a template and its versions to be uploaded to sendwithus, the template must have an entry in the `template_info.yaml` file.  This file also serves to hold any additional information for the templates (i.e. subjects).  For the example project the `template_info.yaml` file might look like this:

```yaml
template1:
  name: template1
  subject: example default subject for template 1
  versions:
      - name: general
        subject: null
      - name: version2
        subject: override subject for version 2

template2:
  name: template2
  subject: default subject for template 2
  versions:
    - name: general
      subject: null
```

#### API Key

The script requires access to your api key in order to upload to sendwithus.  In order to provide this, create an environmental variable called `SENDWITHUS_API_KEY` and set it to one of your sendwithus api keys.

## Usage

To view usage run `uploadwithus --help`.

# uploadwithus

`uploadwithus` is a python package and a command line tool which seeks to solve the problems that arise when attempting to use sendwithus with in a large production environment.  The tool give you the ability to:

- easily separate production and development code
- keep your templates and snippets in version control
- provide an easy to use point to allow you to deploy your local changes

To do this, the tool interacts with a local repository holding snippet and template code.  It duplicates the code in this repository on sendwithus, creating development copies for you.  You can then modify and test the development copies without affecting code in production.

## Installation

The tool requires can run with `python 2.7` or `python 3`.  To install, just run: `pip install uploadwithus`.

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
├── template_info.yaml
└── config.yaml (optional)
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

#### Config

The script takes an optional `config.yaml` file.  This file allows you a place to declare your sendwithus api key and list snippets that you would like to be expanded before your templates get uploaded to sendwithus.  A sample config file is shown below:

```yaml
api_key: test_123
expand:
  - snippet1
```

Templates containing snippets listed under the `expand` key will have those snippets expanded to their `html` equivalent before they get uploaded to sendwithus.  This is valuable for a couple of reasons:  
- One reason is that sendwithus performs HTML validation for any templates that get uploaded through their api.  So, if your templates break validation (e.g. one of your snippets contains the templates `<head>` tag), a solution could be to add that snippet to the `expand` key so that the template will pass validation at the time it is uploaded.  
- Another use case arrises because sendwithus does not track clicked links in snippets during an A/B test.  Expanding snippets would allow you to see links that get clicked in these snippets.

#### API Key

The script requires access to your api key in order to upload to sendwithus.  If you don't want to provide this in the config file, you can create an environmental variable called `SENDWITHUS_API_KEY` and set it to one of your sendwithus api keys.

## Usage

To view usage run `uploadwithus --help`.

---

###### Questions? Comments? Suggestions? Concerns?
###### Email me at `nbalboni2@gmail.com`.

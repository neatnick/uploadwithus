"""
Uploadwithus is a command line tool to facilitate keeping sendwithus templates
and snippets code up to date with an emails repository.  The tool allows you to
maintain your email templates and snippets under a version control system, and
also allows separation of testing and production emails.  For more in depth
information on its usage and features, check out the README.

Copyright (c) 2017, Nick Balboni.
License: MIT (see LICENSE for details)
"""

# python 2 support
from __future__ import print_function, unicode_literals
from builtins import input
import errno

import os
import re
import sys
import yaml
from cached_property import cached_property
from sendwithus import api as sendwithus_api
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

__author__ = 'Nick Balboni'
__version__ = '0.2.0'
__license__ = 'MIT'


### Constants ##################################################################
DEFAULT_TPL_VER = 'general'
DEV_NAME_TPL    = lambda name: 'test_{}'.format(name)
DEV_SUBJECT_TPL = lambda subject: '[DEV] {}'.format(subject)
TPL_CREATE_MSG  = 'created new template < {} >'
TPL_CREATE_ERR  = 'unable to create template < {} > :\n\t{}'
TPL_UPDATE_MSG  = 'updated template < {} >'
TPL_UPDATE_ERR  = 'unable to update template < {} > :\n\t{}'
VER_CREATE_MSG  = 'created new version < {} > for template < {} >'
VER_CREATE_ERR  = 'unable to create version < {} > on template < {} > :\n\t{}'
VER_UPDATE_MSG  = 'updated version < {} > on template < {} >'
VER_UPDATE_ERR  = 'unable to update version < {} > on template < {} > :\n\t{}'
SNP_CREATE_MSG  = 'created new snippet < {} >'
SNP_CREATE_ERR  = 'unable to create snippet < {} > :\n\t{}'
SNP_UPDATE_MSG  = 'updated snippet < {} >'
SNP_UPDATE_ERR  = 'unable to update snippet < {} > :\n\t{}'
TPL_NOT_FOUND_ERR = 'template < {} > not found'
VER_NOT_FOUND_ERR = 'version < {} > on template < {} > not found'
SNP_NOT_FOUND_ERR = 'snippet < {} > not found'


### Helpers ####################################################################
def log(template, *args, **kwargs):
    status = 'ERROR' if 'error' in kwargs and kwargs['error'] else 'DEBUG'
    print(status, ':', template.format(*args))

def snippet_replace(content, snippet):
    reg = r'{%\s+snippet\s+[\'\"]{1}' + snippet + '[\'\"]{1}\s+%}'
    return re.sub(reg, get_content(snippet, snippet=True), content)

def get_content(name, version=None, snippet=False):
    """ throws FileNotFoundError """
    if snippet:
        fp = os.path.join('snippets', name + '.html')
    elif version is None:
        fp = os.path.join('templates', name + '.html')
    else:
        fp = os.path.join('templates', name, version + '.html')
    try:
        with open(fp) as fs:
            return fs.read()
    except FileNotFoundError as e:
        if snippet:
            log(SNP_NOT_FOUND_ERR, name, error=True)
        elif version is None:
            log(TPL_NOT_FOUND_ERR, name, error=True)
        else:
            log(VER_NOT_FOUND_ERR, name, version, error=True)


### The Meat and Potatos #######################################################
class API:
    def __init__(self, key, expands):
        self.api = sendwithus_api(api_key=key)
        self.expands = expands

    def parse_content(self, content):
        # expand snippets before uploading
        for snippet in self.expands:
            content = snippet_replace(content, snippet)
        # regex replace
        ptn = re.compile(r'{%\s+snippet\s+[\'\"]{1}(.*?)[\'\"]{1}\s+%}')
        for match in ptn.finditer(content):
            new_name = 'test_' + match.group(1)
            new_snippet = match.group(0).replace(match.group(1), new_name)
            content = content.replace(match.group(0), new_snippet)
        return content

    ### TEMPLATES ##############################################################
    @cached_property
    def sendwithus_templates(self):
        templates_data = {}
        for tpl in self.api.templates().json():
            templates_data[tpl['name']] = {
                'id': tpl['id'],
                'versions': { v['name']: v['id'] for v in tpl['versions'] }
            }
        return templates_data

    @cached_property
    def local_templates(self):
        templates_data = {}
        with open('template_info.yaml', 'r') as f:
            templates_data = yaml.load(f)
        return templates_data

    def create_template(self, template, development=True):
        """ create new templates with the general version
            returns template id and array of created versions """
        try:
            html = get_content(template, version=DEFAULT_TPL_VER)
            subject = self.local_templates[template]['subject']
            if development:
                html = self.parse_content(html)
                subject = DEV_SUBJECT_TPL(subject)
                template = DEV_NAME_TPL(template)
            # create new template
            resp = self.api.create_template(template, subject, html)
            resp.raise_for_status()
            tid = resp.json()['id']
            # get id of the new version
            resp = self.api.get_template(tid)
            resp.raise_for_status()
            vid = list(resp.json()['versions'])[0]['id']
            # rename template to DEFAULT_TPL_VER
            # NOTE: template can potentially be created but not renamed: add cleanup?
            self.api.update_template_version(
                DEFAULT_TPL_VER, subject, tid, vid, html=html
            ).raise_for_status()
        except Exception as e:
            log(TPL_CREATE_ERR, template, e, error=True)
        else:
            log(TPL_CREATE_MSG, template)
            return ( tid, [ DEFAULT_TPL_VER ] )

    def create_template_version(self, template, tid, version, development=True):
        """ adds a new template version to an existing template
            returns boolean """
        try:
            html = get_content(template, version=version['name'])
            subject = version['subject']
            if subject is None:
                subject = self.local_templates[template]['subject']
            if development:
                html = self.parse_content(html)
                subject = DEV_SUBJECT_TPL(subject)
                template = DEV_NAME_TPL(template)
            self.api.create_new_version(
                version['name'], subject, template_id=tid, html=html
            ).raise_for_status()
        except Exception as e:
            log(VER_CREATE_ERR, version['name'], template, e, error=True)
            return False
        else:
            log(VER_CREATE_MSG, version['name'], template)
            return True

    def add_new_templates(self, development=True):
        """ creates new templates for any local templates that don't have
            sendwithus copies; throws FileNotFoundError """
        created_templates = {}
        for key, value in self.local_templates.items():
            name = DEV_NAME_TPL(key) if development else key
            tid = None
            # if local template is not on sendwithus
            if not name in self.sendwithus_templates:
                content = self.create_template(key, development)
                if not content is None:
                    tid, versions = content
                    created_templates[name] = versions
            else:
                tid = self.sendwithus_templates[name]['id']
            # search local versions for ones not already on sendwithus
            for version in value['versions']:
                v = version['name']
                if v == DEFAULT_TPL_VER or (name in self.sendwithus_templates and \
                v in self.sendwithus_templates[name]['versions']):
                    continue
                if self.create_template_version(key, tid, version, development):
                    if name in created_templates:
                        created_templates[name].append(v)
                    else:
                        created_templates[name] = [v]
        return created_templates

    def update_templates(self, development=True):
        """ updates the templates copies on sendwithus
            throws KeyError and FileNotFoundError """
        created_templates = self.add_new_templates(development=development)
        for key, value in self.local_templates.items():
            name = DEV_NAME_TPL(key) if development else key
            versions = [ (v['name'], v['subject']) for v in value['versions'] ]
            for version, subject in versions:
                if name in created_templates and version in created_templates[name]:
                    continue # don't re-add templates or versions
                try:
                    html = get_content(key, version)
                    if subject is None:
                        subject = value['subject']
                    template_id = self.sendwithus_templates[name]['id']
                    version_id = self.sendwithus_templates[name]['versions'][version]
                    if development:
                        html = self.parse_content(html)
                        subject = DEV_SUBJECT_TPL(subject)
                    self.api.update_template_version(
                        version, subject, template_id, version_id, html=html
                    ).raise_for_status()
                except Exception as e: # KeyError, requests Error
                    log(VER_UPDATE_ERR, version, name, e, error=True)
                else:
                    log(VER_UPDATE_MSG, version, name)

    def get_sendwithus_ids(self):
        for key, value in self.sendwithus_templates.items():
            print(key, ':', value['id'])

    ### SNIPPETS ###############################################################
    @cached_property
    def sendwithus_snippets(self):
        return { s['name']: s['id'] for s in self.api.snippets().json() }

    @cached_property
    def local_snippets(self):
        snippets_data = []
        with open('snippet_info.yaml', 'r') as f:
            snippets_data = yaml.load(f)
        return snippets_data

    def add_new_snippets(self, development=True):
        """ creates new snippets for any local snippets that don't have
            sendwithus copies """
        created_snippets = {}
        for snippet in self.local_snippets:
            name = DEV_NAME_TPL(snippet) if development else snippet
            if not name in self.sendwithus_snippets:
                try:
                    html = get_content(snippet, snippet=True)
                    if development:
                        html = self.parse_content(html)
                    resp = self.api.create_snippet(name, html)
                    resp.raise_for_status()
                except Exception as e:
                    log(SNP_CREATE_ERR, name, e, error=True)
                else:
                    log(SNP_CREATE_MSG, name)
                    created_snippets[name] = resp.json()['snippet']['id']
        return created_snippets

    def update_snippets(self, snippets=[], development=True):
        """ overwrites sendwithus snippet copies with locally held snippets """
        if len(snippets) == 0:
            snippets = self.local_snippets
        created_snippets = self.add_new_snippets(development=development)
        for snippet in snippets:
            name = DEV_NAME_TPL(snippet) if development else snippet
            if name in created_snippets:
                continue
            try:
                html = get_content(snippet, snippet=True)
                if development:
                    html = self.parse_content(html)
                snippet_id = self.sendwithus_snippets[name]
                resp = self.api.update_snippet(snippet_id, name, html)
                resp.raise_for_status()
            except Exception as e: # KeyError, requests exception
                log(SNP_UPDATE_ERR, name, e, error=True)
            else:
                log(SNP_UPDATE_MSG, name)


### Command Line Interface #####################################################
def parse_args():
    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        description=__doc__ )
    parser.add_argument('-v', '--version', action='store_true',
        help='print out version string and exit')
    parser.add_argument('-i', '--info', action='store_true',
        help='print out the sendwithus ids and names of the templates and '
        'snippets included in the templates yaml file')
    parser.add_argument('--update-dev', action='store_true',
        help='update the sendwithus development templates and snippets')
    parser.add_argument('--update-prod', action='store_true',
        help='update the sendwithus production templates and snippets')
    # parser.add_argument('templates', metavar='T', type=str, nargs='*',
    #     help='the list of templates to upload')
    # parser.add_argument('-s', '--snippets', action="store_true",
    #     help='provide this flag to upload all local snippets.'
    #     '  Any new snippets will be created')
    return parser.parse_args()


### Main #######################################################################
def main():
    options = parse_args()
    if options.version:
        print('uploadwithus', __version__)
        sys.exit(0)
    config = {}
    try: # read config file
        with open('config.yaml', 'r') as f:
            config = yaml.load(f)
    except IOError as e:
        if e.errno == errno.ENOENT: # FileNotFoundError
            log('config file not found')
        else:
            raise
    if not 'api_key' in config:
        try: # initiate api key from environmental variable
            config['api_key'] = os.environ['SENDWITHUS_API_KEY']
        except KeyError as e:
            log('SENDWITHUS_API_KEY environmental variable not found.', error=True)
            sys.exit(1)
    if not 'expand' in config:
        config['expand'] = []
    _api = API(config['api_key'], config['expand'])
    if options.info:
        _api.get_sendwithus_ids()
    if options.update_dev:
        _api.update_snippets(development=True)
        _api.update_templates(development=True)
    if options.update_prod:
        resp = input(
            'NOTE: this option modifies production emails, use only when '
            'deploying development code.  Type `I understand` to continue.'
            '\n-->  '
        )
        if resp == 'I understand':
            _api.update_snippets(development=False)
            _api.update_templates(development=False)

if __name__ == '__main__':
    main()

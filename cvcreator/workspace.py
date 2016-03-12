"""
"""
import tempfile
import shutil
import inspect
import glob
import os
import yaml

import cvcreator

__all__ = ["open", "get_template_names", "get_yaml_example"]

builtin_open = open # because override


def get_template_names():
    """
Get available template names

Faster then creating a full Workspace and retriving it from there.
    """
    templatedir = os.path.dirname(inspect.getfile(cvcreator))
    templatedir = templatedir + os.path.sep + "templates" + os.path.sep
    templates = glob.glob(templatedir + "*.yaml")
    templates = [os.path.basename(t)[:-5] for t in templates]
    return templates

def get_yaml_example():
    """
Get YAML example filename
    """
    templatedir = os.path.dirname(inspect.getfile(cvcreator))
    templatedir = templatedir + os.path.sep + "templates" + os.path.sep
    yamlfile = templatedir + "example"
    return yamlfile


class open(object):

    def __init__(self, filename, template=None):

        assert os.path.isfile(filename)
        self.path = tempfile.mkdtemp() + os.path.sep

        self.filename = os.path.basename(filename)

        # get template dir
        templatedir = os.path.dirname(inspect.getfile(cvcreator))
        templatedir = templatedir + os.path.sep + "templates" + os.path.sep
        assert os.path.isdir(templatedir)

        # copy everything over
        for name in glob.glob(templatedir + "*"):
            shutil.copy(name, self.path)
        shutil.copy(filename, self.path + "_content")

        # process template name
        if not template:
            template = "default"
        template = template
        if not os.path.isfile(self.path + template + ".yaml"):
            self.template_mot_found(template)
        self.template = template


    def __enter__(self):
        return self

    def __exit__(self, ty, va, tb):
        self.close()

    def close(self):
        shutil.rmtree(self.path)

    def template_mot_found(self, template):
        raise ValueError("""\
Template '%s' not found in available templates:
%s""" % (template, get_template_names()))

    def get_template(self, template=None):

        if not template:
            template = self.template

        if not os.path.isfile(self.path + template + ".yaml"):
            self.template_not_found(template)

        with builtin_open(self.path + template + ".yaml") as f:
            return yaml.load(f)


    def get_content(self):
        with builtin_open(self.path + "_content") as f:
            return yaml.load(f)

    def compile(self, textxt):

        texname = self.path + self.filename[:-4] + "tex"
        with builtin_open(texname, "w") as f:
            f.write(textxt)

        os.system("cd %s; latexmk %s -pdf -latexoption=\"-interaction=nonstopmode\"" % (self.path, texname))

        pdfname = self.path + self.filename[:-4] + "pdf"
        return pdfname




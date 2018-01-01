from os import path, listdir, walk
from lxml import etree
import lxml.builder as lb
import zipfile


class ModuleGen:
    """This helps create Modules (.mod) files for Fantasy Grounds.

    This should decrease the amount of time needed to organize maps by
    allowing users to create modules with the map categories already existing.
    Encounters follow the same categorical format as maps. (soon)
    """

    def __init__(self, name='MyModule', ruleset='Any', author='Me',
                 xmlout='.', libdir=None, version=None):
        """
        Args:
            name (str): Name of the module.
            ruleset (str): Restricted ruleset for mod.
            author (str): Author to stamp on the mod.
            xmlout (str): The output storage location for the necessary
                definition and db xml files.
            libdir (str): The location of the files to use for the mod.
            version (str): Versioning override, leave None for auto-numbering.
        """
        if not libdir:
            libdir = '.'
        if not path.isdir(libdir):
            raise Exception('Library directory (libdir) does not exist.')
        if not path.isdir(xmlout):
            raise Exception('Out directory (xmlout) does not exist.')
        self.name = name
        self.ruleset = ruleset
        self.author = author
        self.out = xmlout
        self.libdir = libdir
        self.version = self.getVersion(version)

    def getVersion(self, version=None, inc=0.1):
        """Gets the version from the definition.xml file and increments it;
        allows override to manual versioning.

        Args:
            version (str): Versioning override, leave None for auto-numbering.
            inc (float): Number to increment the version by per build.
        """
        indef = self.out + '/definition.xml'
        if not version:
            version = 0
            if path.isfile(indef):
                doc = etree.parse(indef)
                version = float(doc.getroot().get('version'))
            version = version + inc
        return str(round(version, 1))

    def genXML(self):
        """ Calls the XML generators and saves them out to the output location."""
        dbxml = self._getDB()
        defxml = self._getDefinition()
        dbxml.write(self.out + '/' + 'db.xml', xml_declaration=True, encoding='iso-8859-1', pretty_print=True)
        defxml.write(self.out + '/' + 'definition.xml', xml_declaration=True, encoding='iso-8859-1', pretty_print=True)
        return {'dbxml': dbxml, 'defxml': defxml}

    def zip(self, loc=None):
        """ Zips the data in the `out` file as a *.mod file at the defined location.
        Useful for compiling the data and installing into the FG Module folder.
        Args:
            loc (str): Location to save the zipped mod file.mod
        """
        if not loc:
            loc = '.'
        zf = zipfile.ZipFile('{}/{}.mod'.format(loc, self.name), 'w', zipfile.ZIP_DEFLATED)
        print('Zipping to {}/{}.mod'.format(loc, self.name))
        abs_src = path.abspath(self.out)
        for dirname, subdirs, files in walk(self.out):
            for filename in files:
                absname = path.abspath(path.join(dirname, filename))
                arcname = absname[len(abs_src) + 1:]
                zf.write(absname, arcname)
        zf.close()

    def _getDB(self):
        """ Grabs, and outputs xml, the information needed for the db.xml, this includes files in the libdir
        as well as other information needed for building categories. Currently this only 
        works for images, though it will be expanded for other data points."""
        imgId = 1
        root = lb.E.root(lb.E.image(lb.E.category(name="", mergeid="", baseicon="1", decalicon="1")), version=self.version)
        images = []
        for filename in listdir(self.libdir):
            ext = filename.split('.')[-1]
            if ext == 'jpg' or ext == 'png':
                relpath = path.relpath(self.libdir, self.out)
                img = getattr(lb.E, "id-%05d"%imgId)(
                    lb.E.image(lb.E.bitmap(relpath+'/'+filename), type="image"),
                    lb.E.name(filename, type="string")
                )
                images.append(img)
                imgId += 1

        cat = root.find(".//category")
        for img in images:
            cat.append(img)

        return etree.ElementTree(root)

    def _getDefinition(self):
        """ Builds the definition.xml structure with the data passed in to init.
        Includes versioning, ruleset, author and name."""
        root = etree.Element('root')
        root.set('version', self.version)
        elements = ['name', 'ruleset', 'author']
        for e in elements:
            child = etree.Element(e)
            child.text = getattr(self, e)
            root.append(child)
        return etree.ElementTree(root)


x = ModuleGen('HMaps', author='Hooker', xmlout='hookermaps', libdir='hookermaps/maps')
x.genXML()
x.zip()
x.zip('S:\Fantasy Grounds\Data\modules')

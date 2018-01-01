from os import path, listdir, walk
import shutil
from lxml import etree
import lxml.builder as lb
import zipfile


class ModuleGen:

    def __init__(self, name='MyModule', ruleset='Any', author='Me',
                 out='.', libdir=None, version=None):
        if not libdir:
            libdir = '.'
        if not path.isdir(libdir):
            raise Exception('Library directory (libdir) does not exist.')
        if not path.isdir(out):
            raise Exception('Out directory (out) does not exist.')
        self.name = name
        self.ruleset = ruleset
        self.author = author
        self.out = out
        self.libdir = libdir
        self.version = self.getVersion(version)

    def getVersion(self, version=None, inc=0.1):
        indef = self.out + '/definition.xml'
        if not version:
            version = 0
            if path.isfile(indef):
                doc = etree.parse(indef)
                version = float(doc.getroot().get('version'))
            version = version + inc
        return str(round(version, 1))

    def genXML(self, version=None):
        dbxml = self._getDB()
        defxml = self._getDefinition()
        dbxml.write(self.out + '/' + 'db.xml', xml_declaration=True, encoding='iso-8859-1', pretty_print=True)
        defxml.write(self.out + '/' + 'definition.xml', xml_declaration=True, encoding='iso-8859-1', pretty_print=True)
        return {'dbxml': dbxml, 'defxml': defxml}


    def zip(self):
        zf = zipfile.ZipFile("{}.mod".format(self.name), 'w', zipfile.ZIP_DEFLATED)
        abs_src = path.abspath(self.out)
        for dirname, subdirs, files in walk(self.out):
            for filename in files:
                absname = path.abspath(path.join(dirname, filename))
                arcname = absname[len(abs_src) + 1:]
                zf.write(absname, arcname)
        zf.close()

    def install(self, dir):
        shutil.move('T:\projects\FGMods\HMaps.mod',fgdir+'\HMaps.mod')
    """
    img = getattr(lb.E, "id-%05d"%imgId)(
        lb.E.image(lb.E.bitmap(filename), type="image"),
        lb.E.name(filename, type="string"))
    """
    def _getDB(self):
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
        root = etree.Element('root')
        root.set('version', self.version)
        elements = ['name', 'ruleset', 'author']
        for e in elements:
            child = etree.Element(e)
            child.text = getattr(self, e)
            root.append(child)
        return etree.ElementTree(root)


x = ModuleGen('HMaps', author='Hooker', out='hookermaps', libdir='hookermaps/maps')
x.zip()
x.install('S:\Fantasy Grounds\Data\modules')
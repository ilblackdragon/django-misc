import re
import os
from BeautifulSoup import BeautifulSoup

class Tree(object):
    
    def __init__(self, name):
        self.childs = []
        self.parent = None
        self.current = self
        self.indent = -2
        self.name = name

    def __str__(self):
        res = (" " * self.indent if self.indent >= 0 else "") + self.name + " " + str(self.__class__) + "\n"
        for child in self.childs:
            res += str(child)
        return res

    def copy(self):
        n = type(self)(self.name)
        n.__dict__ = self.__dict__
        n.childs = self.copyChilds()
        return n

    def copyChilds(self):
        childs = []
        for child in self.childs:
            childs.append(child.copy())
        return childs

    def addNode(self, node):
        for child in self.childs:
            if child.name == node.name:
                child.addNodes(node.copyChilds())
                return child
        self.childs.append(node)
        node.parent = self
        return node

    def addNodes(self, nodes):
        for node in nodes:
            self.addNode(node)
        return nodes

    def removeNode(self, node):
        node.parent = None
        self.childs.remove(node)

    def addChild(self, str):
        node = Node(str)
        return self.addNode(node)

    def findChild(self, name):
        for child in self.childs:
            if child.name == name:
                return child
        return None

    def getAllChilds(self, split = '|'):
        res = ''
        for child in self.childs:
            if res != '':
                res += split
            res += child.name
        return res

    def addString(self, str):
        indent = len(str) - len(str.lstrip())
        if self.current.indent == indent:
            thisnode = self.current.parent.addChild(str.lstrip())
        if self.current.indent < indent:
            thisnode = self.current.addChild(str.lstrip())
        if self.current.indent > indent:
            while self.current.indent > indent:
                self.current = self.current.parent
            thisnode = self.current.parent.addChild(str.lstrip())
        self.current = thisnode
        self.current.indent = indent
        self.current.current = self.current
        return thisnode

    def applyToAll(self, toall):
        self.removeNode(toall)
        for child in self.childs:
            child.addNodes(toall.copyChilds())

    def fixNodes(self):
        toall = None
        for child in self.childs[:]:
            if child.name == ".*":
                toall = child
                continue
            snchilds = child.name.split('|')
            if (len(snchilds) > 1):
                for snchild in snchilds:
                    schild = self.findChild(snchild)
                    if schild == None:
                        schild = self.addChild(snchild)
                    schild.addNodes(child.copyChilds())
                self.removeNode(child)
        if toall != None:
            self.applyToAll(toall)
        for child in self.childs:
            child.fixNodes()

class Node(Tree):

    def addChild(self, str):
        if str == "style":
            node = Style(str)
        else:
            node = Attr(str)
        return self.addNode(node)

class Attr(Node):

    def addChild(self, str):
        node = AttrValue(str)
        return self.addNode(node)

    def applyToAll(self, toall):
        pass

class Style(Attr):
    pass

class AttrValue(Attr):
    pass

def generate_code(fileName, outputFileName = None):
    lines = open(fileName, 'r').read().splitlines()
    code = ""
    r_tags = {'.*': {}}
    tags = {}
    current_tag = '.*'
    current_attr = ''
    tree = Tree("Tree")
    for line in lines:
        if len(line) == 0 or line.startswith('#'):
            continue
        tree.addString(line)
    tree.fixNodes()
    #print str(tree)

    code = """
###
### This file generates automaticly
### Do not change anything at it
### Generated from '""" + fileName + """'
###

import re
from BeautifulSoup import BeautifulSoup

tag_check = re.compile(r'^(""" + tree.getAllChilds() + """)$', re.IGNORECASE)
attr_check = {}
attr_value_check = {}
style_check = {}
style_value_check = {}
"""
    
    for child in tree.childs:
        code += "attr_check['" + child.name + "'] = re.compile(r'^(" + child.getAllChilds() + ")$', re.IGNORECASE)\n"
        code += "attr_value_check['" + child.name + "'] = {}\n"
        for ch in child.childs:
            code += "attr_value_check['" + child.name + "']['" + ch.name + "'] = re.compile(r'^(" + ch.getAllChilds() + ")$', re.IGNORECASE)\n"

    for child in tree.childs:
        child_style = child.findChild('style')
        if not child_style:
            continue
        code += "style_check['" + child.name + "'] = re.compile(r'^(" + child_style.getAllChilds() + ")$', re.IGNORECASE)\n"
        code += "style_value_check['" + child.name + "'] = {}\n"
        for ch in child_style.childs:
            code += "style_value_check['" + child.name + "']['" + ch.name + "'] = re.compile(r'^(" + ch.getAllChilds() + ")$', re.IGNORECASE)\n"

    code += """

def clear_html_code(text):
    soup = BeautifulSoup(text)
    tags = soup.findAll()
    for tag in tags:
        if not tag_check.match(tag.name):
            tag.extract()
        else:
            for attr in tag.attrs[:]:
                if not attr_check[tag.name].match(attr[0]):
                    tag.attrs.remove(attr)
                else:
                    if (attr[0].lower() == "style"):
                        list = attr[1].split(';')
                        res = ""
                        for x in list:
                            if x.find(':') > 0:
                                keys = x.split(':')
                                if style_check[tag.name].match(keys[0]) and (keys[0] not in style_value_check[tag.name] or style_value_check[tag.name][keys[0]].match(keys[1])):
                                    res += x + ';'
                        tag.attrs.remove(attr)
                        tag.attrs.append(("style", res))
                    else:
                        if not attr_value_check[tag.name][attr[0]].match(attr[1]):
                            tag.attrs.remove(attr)
    return unicode(soup)

"""
    if outputFileName != None:
        f = file(outputFileName, 'w')
        f.write(code)
        f.close()
    return code


if __name__ == "__main__":
    code = generate_code("needs.cfg", 'clear.py')
    import clear
    text = """
        <div>
            </div>
        <table q="ww" width=10>qqq
            <table style="margin:10;color:10;width:50" width=10>www
            </div>eee
            <hr class="editor_cut"/>
        <p>rrr  
            <table>tt
<p>
	<span class="Apple-style-span" style="color: rgb(68, 68, 68); font-family: Tahoma, 'Trebuchet MS', 'Arial Narrow'; line-height: 20px; "><img alt="asdad" width="12a0" height=130 src="http://dl.dropbox.com/u/116385/Screenshots/pzu3w~8_dtjp.png" style="border-top-width: 0px; border-right-width: 0px; border-bottom-width: 0px; border-left-width: 0px; border-style: initial; border-color: initial; "></span>
</p>
<iframe title="YouTube video player" class="youtube-player" type="text/html" width="480" height="390" src="http://www.youtube.com/embed/mK8Rnqch08c" frameborder="0"></iframe>
<iframe src="http://player.vimeo.com/video/17644530" width="400" height="225" frameborder="0"></iframe><p><a href="http://vimeo.com/17644530">Health</a> from <a href="http://vimeo.com/hayleymorris">Hayley Morris</a> on <a href="http://vimeo.com">Vimeo</a>.</p>
<object width="480" height="385"><param name="movie" value="http://wwwpyoutube.com/e/vvmqCXR-tiA"></param><param name="allowFullScreen" value="true"></param><param name="allowscriptaccess" value="always"></param><embed src="http://www.youtube.com/e/vvmqCXR-tiA" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="480" height="385"></embed></object>
<iframe src="http://vkontakte.ru/video_ext.php?oid=14071319&id=156556674&hash=2a4233a33890ef11&hd=1" width="607" height="360" frameborder="0"></iframe>
Text1 <div style="text-align: center">Some text</div> Text2
<a style="text-align:center;">Link</a>
<div align='center'>qwe</div>
<center>ad</center>
    """
    #clear.clear_html_code('<a style="text-align: center">Link</a>')
    print clear.clear_html_code(text)

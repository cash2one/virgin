__author__ = 'hcy'

datatype= ["String", "FormattedString", "Url", "DateTime", "Float",
               "Integer", "Arbitrary", "Nested", "List", "Raw", "Boolean",
               "Fixed", "Price"]

datatypedict={
        "type": "",
        "description":"",
        "default":""
    }

class fields:
    def String(self,**args):
        s=datatypedict
        datatypedict["type"]="string"
        if args.get('default'):
            datatypedict["description"]=""
        else:
            datatypedict["description"]=args.get('description')
        if args.get('default'):
            datatypedict["default"]=""
        else:
            datatypedict["default"]=args.get('default')
        return s


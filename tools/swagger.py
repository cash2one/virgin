# coding=utf-8

datatype= ["String", "FormattedString", "Url", "DateTime", "Float",
               "Integer", "Arbitrary", "Nested", "List", "Raw", "Boolean",
               "Fixed", "Price"]

datatypedict={
    "type": "",
    "description":"",
    "default":""
}



class swagger:

    __parameters=[]
    __tab=""
    __explain=""

    def __init__(self,tab,explain):
        self.__tab=tab
        self.__explain=explain


    def add_parameter(self,**attrs):
        para={}
        para["name"]=attrs.get('name')
        para["parametertype"]=attrs.get('parametertype')
        para["type"]=attrs.get('type')
        if attrs.get('required'):
            para["required"]='true'
        else:
            para["required"]='false'
        para["description"]=attrs.get('description')
        para["default"]=attrs.get('default')
        print para
        self.__parameters.append(para)
        print self.__parameters


    def result(self,resultjson):
        print resultjson

    def mylpath(self,schemaid="",result={}):
        # print schemaid
        # print result
        # out=self.__tab+"\n" \
        #                "---\n" \
        #                "tags:\n" \
        #                "  - "+self.__explain+"\n" \
        #                "parameters:\n"
        # for a in self.__parameters:
        #           out+="  - name: "+a["name"]+"\n"\
        #                "    in: "+a["parametertype"]+"\n"\
        #                "    type: "+a["type"]+"\n"\
        #                "    required: "+a["required"]+"\n"\
        #                "    description: "+a["description"]+"\n"\
        #                "    default: "+a["default"]+"\n"
        # out+="responses:"
        #
        # print out
        # return "/www/site/foodmap/virgin/virgin/ml/orderbypreset.yml"
        return ""



    def String(self,**args):
        s=datatypedict
        datatypedict["type"]="string"
        if args.get('description')==None:
            datatypedict["description"]=""
        else:
            datatypedict["description"]=args.get('description')
        if args.get('default') ==None:
            datatypedict["default"]=""
        else:
            datatypedict["default"]=args.get('default')
        return s


    def Integer(self,**args):
        s=datatypedict
        datatypedict["type"]="int"
        if args.get('description')==None:
            datatypedict["description"]=""
        else:
            datatypedict["description"]=args.get('description')
        if args.get('default') ==None:
            datatypedict["default"]=""
        else:
            datatypedict["default"]=args.get('default')
        return s


    def Float(self,**args):
        s=datatypedict
        datatypedict["type"]="float"
        if args.get('description')==None:
            datatypedict["description"]=""
        else:
            datatypedict["description"]=args.get('description')
        if args.get('default') ==None:
            datatypedict["default"]=""
        else:
            datatypedict["default"]=args.get('default')
        return s


    def Boolean(self,**args):
        s=datatypedict
        datatypedict["type"]="boolean"
        if args.get('description')==None:
            datatypedict["description"]=""
        else:
            datatypedict["description"]=args.get('description')
        if args.get('default') ==None:
            datatypedict["default"]=""
        else:
            datatypedict["default"]=args.get('default')
        return s




if __name__ == '__main__':
    a =swagger("订单","餐位管理")
    a.add_parameter(name='restaurant_id',parametertype='formData',type='string',required=True,description='饭店id',default='57329b1f0c1d9b2f4c85f8e3')
    a.add_parameter(name='preset_time',parametertype='formData',type='string',required= True,description='预定时间',default='2015-6-16')
    # json=a.String(description='nihao')
    # print json
    # json=a.Integer(description='nihao')
    # print json
    ccc=a.mylpath(schemaid="aa",result={})
    print ccc


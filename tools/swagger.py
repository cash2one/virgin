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
        self.__parameters=[]


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
        para["default"]="'"+attrs.get('default')+"'"
        # print para
        # l.append(para)
        # self.__parameters=l
        self.__parameters.append(para)
        # print self.__parameters




    def mylpath(self,schemaid="",result={}):
        global fire
        fire=[]
        out=self.__explain+"\n" \
                       "---\n" \
                       "tags:\n" \
                       "  - "+self.__tab+"\n" \
                       "parameters:\n"

        for a in self.__parameters:
                  out+="  - name: "+a["name"]+"\n"\
                       "    in: "+a["parametertype"]+"\n"\
                       "    type: "+a["type"]+"\n"\
                       "    required: "+a["required"]+"\n"\
                       "    description: "+a["description"]+"\n"\
                       "    default: "+a["default"]+"\n"
        out+="responses:\n" \
             "    500:\n"\
             "      description: 服务器错误\n"\
             "    400:\n"\
             "      description: 无效的参数\n"\
             "    200:\n"\
             "      description: 返回格式\n"\
             "      schema:\n"\
             "        id: "+schemaid+"\n"\
             "        properties:\n"\


        for k in result.keys():
            print_dict(k, result[k],1,type(result))

        for a in fire:
            # print a
            # print totype(a["zjlx"])
            n=""
            for p in range(int(a['n'])*6+8):
                n+=' '
            if totype(a["zjlx"])=="string" :
              bb = str(a['nr']).split('|||')
              if len(bb)>=3:
               out+=""+n+""+str(a["k"])+":\n" \
                    ""+n+"  type: "+bb[0]+"\n" \
                    ""+n+"  description: '"+bb[1]+"'\n" \
                    ""+n+"  default: \""+bb[2]+"\"\n"
            if totype(a["zjlx"])=="object":
              out+= ""+n+""+str(a["k"])+":\n" \
                    ""+n+"  type: object\n" \
                    ""+n+"  description: ''\n" \
                    ""+n+"  properties:\n"
            if totype(a["zjlx"])=="array":
              out+= ""+n+""+str(a["k"])+":\n" \
                    ""+n+"  type: array\n" \
                    ""+n+"  description: ''\n" \
                    ""+n+"  items:\n" \
                    ""+n+"    type: "+totype(a['xjlx'])+"\n"\
                    ""+n+"    description: ''"+"\n"\
                    ""+n+"    properties: "+"\n"
              if totype(a['xjlx'])!="object":
               out+=""+n+"  default: "+str(a['nr'])+"\n"
              else:
               out+=""+n+"\n"

        import os
        path = os.path.dirname(__file__).replace("tools","")+"ml/"+schemaid+".yml"
        fp = open(path,'w+')
        fp.write(out)
        self.__parameters = []
        return path
        # return out

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
        return str(datatypedict["type"]+"|||"+datatypedict["description"]+"|||"+datatypedict["default"])


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
        return str(datatypedict["type"])+"|||"+str(datatypedict["description"])+"|||"+str(datatypedict["default"])


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
        return str(datatypedict["type"])+"|||"+str(datatypedict["description"])+"|||"+str(datatypedict["default"])


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
        return str(datatypedict["type"])+"|||"+str(datatypedict["description"])+"|||"+str(datatypedict["default"])


fire=[]
def print_dict(k, v,n,sjlx):
    if isinstance(v, dict):
        cc=sjlx
        if str(sjlx) != "<type 'list'>":
            i={
                "n":n,
                "sjlx":sjlx,
                "k":k,
                "zjlx":type(v),
                "xjlx":"",
                "nr":""
            }
            fire.append(i)
            # print n,sjlx,k,type(v)
            cc=type(v)
        for kk in v.keys():
            print_dict(kk, v[kk],n+1,cc)
    if isinstance(v,list):
         if len(v)==0:
            xjlx="<type 'str'>"
         else:
            xjlx=type(v[0])
         i={
                "n":n,
                "sjlx":sjlx,
                "k":k,
                "zjlx":type(v),
                "xjlx":xjlx,
                "nr":v
            }
         fire.append(i)
         # print n,sjlx,k,type(v),xjlx


         for cc in v:
            print_dict(cc,cc,n,type(v))
    if isinstance(v,str):
        i={
                "n":n,
                "sjlx":sjlx,
                "k":k,
                "zjlx":type(v),
                "xjlx":"",
                "nr":v
         }
        fire.append(i)
        # print n,sjlx,k,type(v), v


def totype(t):
    str1=""
    if str(t)=="<type 'dict'>":
        str1="object"
    if str(t)=="<type 'list'>":
        str1="array"
    if str(t)=="<type 'str'>":
        str1="string"
    return str1



# if __name__ == '__main__':
    # ab =swagger("订单","餐位管理")
    # ab.add_parameter(name='restaurant_id',parametertype='formData',type='string',required=True,description='饭店id',default='57329b1f0c1d9b2f4c85f8e3')
    # ab.add_parameter(name='preset_time',parametertype='formData',type='string',required= True,description='预定时间',default='2015-6-16')
    # # json=a.String(description='nihao')
    # # print json
    # # json=a.Integer(description='nihao')
    # # print json
    #
    #
    # rjson={
    #       "auto": ab.String(description='验证是否成功'),
    #       "code": ab.Integer(description='',default=0),
    #       "date": {
    #         "list111":["1","2","3"],
    #         "list": [
    #           {
    #             "room_count": [
    #               {
    #                 "orderinfo": [
    #                   {
    #                     "id": ab.String(description='',default="572ff4f6ed222e1e28b56056"),
    #                     "numpeople": ab.Integer(description='',default=8),
    #                     "preset_time": ab.String(description='',default="10:10"),
    #                   }
    #                 ],
    #                 "room_id": ab.String(description='',default="201605111054507163"),
    #                 "room_name": ab.String(description='',default="中包(1间)"),
    #               }
    #             ],
    #             "room_people_num": ab.String(description='',default="10-12人包房"),
    #           }
    #         ]
    #       },
    #       "message": ab.String(description='',default="")
    # }
    # ccc=ab.mylpath(schemaid="aa",result=rjson)
    # print ccc
    #



    # print fire
    # out=""
    # for a in fire:
    #     print a
    #     print totype(a["zjlx"])
    #     n=""
    #     for p in range(int(a['n'])*6):
    #         n+=' '
    #     if totype(a["zjlx"])=="string" :
    #       bb = str(a['nr']).split('|||')
    #       if len(bb)>=3:
    #        out+=""+n+""+str(a["k"])+":\n" \
    #             ""+n+"  type: "+bb[0]+"\n" \
    #             ""+n+"  description: '"+bb[1]+"'\n" \
    #             ""+n+"  default: "+bb[2]+"\n"
    #     if totype(a["zjlx"])=="object":
    #       out+= ""+n+""+str(a["k"])+":\n" \
    #             ""+n+"  type: object\n" \
    #             ""+n+"  description: ''\n" \
    #             ""+n+"  properties:\n"
    #     if totype(a["zjlx"])=="array":
    #       out+= ""+n+""+str(a["k"])+":\n" \
    #             ""+n+"  type: array\n" \
    #             ""+n+"  description: ''\n" \
    #             ""+n+"  items:\n" \
    #             ""+n+"    type: "+totype(a['xjlx'])+"\n"
    #       if totype(a['xjlx'])!="object":
    #        out+=""+n+"  default: "+str(a['nr'])+"\n"
    #       else:
    #        out+=""+n+"    properties:\n"


    # print out

    # message:
    #   type: string
    #   description: 接口调用成功
    #   default: ""
    # auto:
    #   type: boolean
    #   description: jwt验证  true 成功 false 失败
    #   default: false
    # code:
    #   type: int
    #   description: 接口状态码
    #   default: 0
    # date:
    #   type: object
    #   description: 接口状态码
    #   properties:
    #     list:
    #       type: array
    #       description: 包房列表
    #       items:
    #         type: object
    #         properties:
    #           room_people_num:
    #             type: string
    #             default: "10-12人包房"
    #           room_count:
    #              type: array
    #              description: 接口调用成功
    #              items:
    #                type: object
    #                properties:
    #                    room_id:
    #                       type: string
    #                       default: "201605111054507163"
    #                    room_name:
    #                      type: string
    #                      description: 接口调用成功
    #                      default: 中包(1间)
    #                    orderinfo:
    #                           type: array
    #                           description: 接口调用成功
    #                           items:
    #                              type: object
    #                              properties:
    #                                 id:
    #                                   type: string
    #                                   default: "572ff4f6ed222e1e28b56056"
    #                                 preset_time:
    #                                   type: string
    #                                   default: "10:10"
    #                                 numpeople:
    #                                   type: int
    #                                   default: 8"





from xml.etree.ElementTree import Element,SubElement,ElementTree
import xml.etree.cElementTree as ET
import logging

module_logger = logging.getLogger("main.sub")

def ReadInXML(p):
    """
    Read in XML content
    :param p: string path
    :return: XML File
    """
    f=ET.parse(p)
    return f

def prettyXml(element, indent, newline, level = 0):
    """
    Beautify the output of XML
    :param element: XML Content
    :param indent: \t
    :param newline: \n
    :param level:
    :return:
    """
    if element:
        if element.text == None or element.text.isspace():
            element.text = newline + indent * (level + 1)
        else:
            element.text = newline + indent * (level + 1) + element.text.strip() + newline + indent * (level + 1)
    temp = list(element)
    if(len(temp)!=0):
        for subelement in range(len(temp)):
            if temp.index(temp[subelement]) < (len(temp) - 1):
                temp[subelement].tail = newline + indent * (level + 1)
            else:
                temp[subelement].tail = newline + indent * level
            prettyXml(temp[subelement], indent, newline, level = level + 1)
    else:
        return

    return element

def SaveXML(x,p):
    """
    Save XML File according to the path
    :param x: XML root
    :param p: path to save
    :return:
    """
    with open(p,'wb') as f:
        f.write('<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE eagle SYSTEM "eagle.dtd">\n'.encode('utf8'))
        ET.ElementTree(x).write(f,'utf-8')
        f.close()
        pass
    pass

def GetVersion(x1,x2):
    """
    Get the version of XML
    :param x1:
    :param x2:
    :return:
    """
    module_logger = logging.getLogger("main.GetVersion")

    tag1=x1.items()
    tag2=x2.items()

    retMsg=""
    if ("version" in tag1[0]) and ("version" in tag2[0]) :
        v1=x1.get('version')
        v2=x2.get('version')
        if(v1>v2):
            retMsg=v1
            module_logger.warning("version is not agreed")
        elif(v1<v2):
            retMsg=v2
            module_logger.warning("version is not agreed")
        else:
            retMsg=v2
        pass
    else:
        module_logger.warning("version is not specified")
        retMsg="9.4.2"

    return retMsg

def GetLayers(x1,x2):
    """
    Extract layer data from two files and return dict
    :param x1:
    :param x2:
    :return:
    """
    x1_layer = x1.findall("layer")
    x2_layer = x2.findall("layer")

    x_dict=[]
    x2_dict=[]
    max_number=0

    x2_ret=[]


    index_1=0
    index_2=0
    # Loop and get new layers
    while(index_1<len(x1_layer) and index_2<len(x2_layer) ):
        x1_number=int(x1_layer[index_1].get("number"))
        x2_number = int(x2_layer[index_2].get("number"))
        max_number=max(max_number,x1_number,x2_number)
        if(x1_number<x2_number):
            x_dict.append(x1_layer[index_1])
            index_1=index_1+1
            pass
        elif(x1_number>x2_number):
            x_dict.append(x2_layer[index_2])
            index_2 = index_2 + 1
            pass
        else:
            if (x1_layer[index_1].get("name") == x2_layer[index_2].get("name")):
                x_dict.append(x1_layer[index_1])
                index_1 = index_1 + 1
                index_2 = index_2 + 1
                pass
            else:
                module_logger.warning(
                    "layer {0} has same number {1} with layer {2}".format(x1_layer[index_1].get("name"), x1_number,
                                                                          x2_layer[index_2].get("name")))
                x_dict.append(x1_layer[index_1])
                index_1 = index_1 + 1
                x2_dict.append(x2_layer[index_2])
                index_2 = index_2 + 1
        pass

    if(len(x2_dict)!=0):
        index_2=0
        while(index_2<len(x2_dict)):
            temp=x2_dict[index_2]
            x2_ret.append({"old":temp.get("number"),"new":str(max_number+1)})
            temp.set("number",str(max_number+1))
            x_dict.append(temp)
            max_number=max_number+1
            index_2=index_2+1

    x_root=Element("layers")
    for i in range(len(x_dict)):
        x_root.append(x_dict[i])

    return x_root,[],x2_ret

def GetLibraries(x1,x2):
    """
    Extract libraries data from two files and return dict
    :param x1:
    :param x2:
    :return:
    """
    # TODO: Library could be different though they have same name
    x1_lib = x1.findall("library")
    x2_lib = x2.findall("library")
    if(len(x1_lib)==0 and len(x2_lib)==0):
        x_root=Element("libraries")
        x_root.text=" "
        return x_root

    x_root=Element("libraries")
    if not (len(x1_lib)==0):
        for i in range(len(x1_lib)):
            x_root.append(x1_lib[i])
            pass
        pass

    if(len(x1_lib)==0):
        for i in range(len(x2_lib)):
            x_root.append(x2_lib[i])
            pass
        pass
    else:
        x_lib=x_root.getchildren()
        for i in range(len(x2_lib)):
            x2_name=x2_lib[i].get("name")
            x2_in=True
            for j in range(len(x_lib)):
                if(x2_name==x_lib[j].get("name")):
                    x2_in=False
                    module_logger.warning("Library:{0} has appeared".format(x2_name))

                    x_sublib=x_lib[j]
                    x2_sublib=x2_lib[i]


                    x_packages=x_sublib.find('packages')
                    x2_packages=x2_sublib.find('packages')

                    x_package=x_packages.getchildren()
                    x2_package=x2_packages.getchildren()

                    for m in range(len(x2_package)):
                        is_same=False
                        for n in range(len(x_package)):
                            if(x_package[n].get('name')==x2_package[m].get('name')):
                                is_same=True
                                pass
                            pass
                        if not is_same:
                            x_packages.append(x2_package[m])
                            pass
                        pass


                    x_symbols=x_sublib.find('symbols')
                    x2_symbols=x2_sublib.find('symbols')

                    x_symbol=x_symbols.getchildren()
                    x2_symbol=x2_symbols.getchildren()

                    for m in range(len(x2_symbol)):
                        is_same=False
                        for n in range(len(x_symbol)):
                            if(x_symbol[n].get('name')==x2_symbol[m].get('name')):
                                is_same=True
                                pass
                            pass
                        if not is_same:
                            x_symbols.append(x2_symbol[m])
                            pass
                        pass


                    x_devicesets = x_sublib.find('devicesets')
                    x2_devicesets = x2_sublib.find('devicesets')

                    x_device=x_devicesets.getchildren()
                    x2_device = x2_devicesets.getchildren()

                    for m in range(len(x2_device)):
                        is_same=False
                        for n in range(len(x_device)):
                            if(x_device[n].get('name')==x2_device[m].get('name')):
                                is_same=True
                                pass
                            pass
                        if not is_same:
                            x_devicesets.append(x2_device[m])
                            pass
                        pass
                    break
            if(x2_in):
                x_root.append(x2[i])
                pass
            pass
        pass
    return x_root

def GetClasses(x1,x2):
    """
    Extract classes data from two files and return dict
    :param x1:
    :param x2:
    :return:
    """
    x1_class = x1.findall("class")
    x2_class = x2.findall("class")
    if (len(x1_class) == 0 and len(x2_class) == 0):
        return '<classes>\n<class number="0" name="default" width="0" drill="0">\n</class>\n</classes>'

    max_number=-1
    x_root = Element("classes")
    x2_ret=[]
    if not (len(x1_class) == 0):
        for i in range(len(x1_class)):
            x_root.append(x1_class[i])
            max_number=max(max_number,int(x1_class[i].get('number')))
            pass
        pass

    if (len(x1_class) == 0):
        for i in range(len(x2_class)):
            x_root.append(x2_class[i])
            pass
        pass
    else:
        for i in range(len(x2_class)):
            is_same=False
            x_item=x2_class[i]
            for j in range(len(x1_class)):
                if(x1_class[j].get('number')==x2_class[i].get('number')):
                    if(x1_class[j].get('name')==x2_class[i].get('name')):
                        is_same=True
                        break
                    else:
                        max_number=max_number+1
                        x2_ret.append({'old':x_item.get('number'),'new':str(max_number)})
                        module_logger.warning("class {0} and {1} share the same number".format(x1_class[j].get('name'),x_item.get('name')))
                        x_item.set('number',str(max_number))
                        x_root.append(x_item)
                        is_same=True
                    pass
                pass
            if not is_same:
                x_root.append(x_item)

    return x_root,[],x2_ret

def GetParts_Number(x):
    """
    Input string name and extract name and id
    :param x: SUPPLY12
    :return: SUPPLY,12
    """
    index=len(x)-1
    num=""
    while(ord(x[index])>=48 and ord(x[index])<=57):
        num=x[index]+num
        index=index-1
        pass
    if(num==""):
        module_logger.error("parts {0} has error. Cannot parse the name".format(x))
        return x,0
    return x[0:index+1],int(num)

def GetParts(x1,x2):
    """
    Extract parts data from two files and return dict
    :param x1:
    :param x2:
    :return:
    """
    x1_parts = x1.findall("part")
    x2_parts = x2.findall("part")
    if (len(x1_parts) == 0 and len(x2_parts) == 0):
        x_root = Element("parts")
        x_root.text = " "
        return x_root,[],[]

    x_root = Element("parts")
    x_name={}
    x2_ret=[]
    if not (len(x1_parts) == 0):
        for i in range(len(x1_parts)):
            x_root.append(x1_parts[i])
            name,id=GetParts_Number(x1_parts[i].get("name"))
            if not (name in x_name):
                x_name[name]=id
            else:
                x_name[name]=max(x_name[name],id)
            pass
        pass

    if (len(x1_parts) == 0):
        for i in range(len(x2_parts)):
            x_root.append(x2_parts[i])
            pass
        pass
    else:
        for i in range(len(x2_parts)):
            name,id=GetParts_Number(x2_parts[i].get("name"))
            if not name in x_name:
                x_root.append(x2_parts[i])
                pass
            else:
                x_name[name]=x_name[name]+1
                x2_ret.append({"old":x2_parts[i].get("name"),"new":name+str(x_name[name])})
                x2_parts[i].set("name",name+str(x_name[name]))
                x_root.append(x2_parts[i])
                pass

    return x_root,[],x2_ret

def GetPlain(x1,x2,x2_layers_dict):
    """
    Extract plain data from two files and return dict
    :param x1:
    :param x2:
    :param x2_layers_dict:
    :return:
    """
    x1_subplain = x1.getchildren()
    x2_subplain = x2.getchildren()

    if(len(x1_subplain)==0 and len(x2_subplain)==0):
        x_root = Element("plain")
        x_root.text = " "
        return x_root

    x_root=Element("plain")

    if not (len(x1_subplain) == 0):
        for i in range(len(x1_subplain)):
            x_root.append(x1_subplain[i])
            pass
        pass

    for i in range(len(x2_subplain)):
        x_item=x2_subplain[i]

        is_same=False
        for j in range(len(x2_layers_dict)):
            s1=x_item.get("layer")
            s2=x2_layers_dict[j]['old']
            if(int(x_item.get('layer'))==int(x2_layers_dict[j]['old'])):
                x_item.set("layer",x2_layers_dict[j]['new'])
                x_root.append(x_item)
                is_same=True
                pass
            pass

        if not is_same:
            x_root.append(x_item)
            pass
        pass
    return x_root

def GetInstances(x1,x2,x2_parts_dict):
    """
    Extract instances data from two files and return dict
    :param x1:
    :param x2:
    :param x2_parts_dict:
    :return:
    """
    x1_instance = x1.getchildren()
    x2_instance = x2.getchildren()

    if (len(x1_instance) == 0 and len(x2_instance) == 0):
        x_root = Element("instances")
        x_root.text = " "
        return x_root

    x_root = Element("instances")

    if not (len(x1_instance) == 0):
        for i in range(len(x1_instance)):
            x_root.append(x1_instance[i])
            pass
        pass

    for i in range(len(x2_instance)):
        x_item = x2_instance[i]

        is_same = False
        for j in range(len(x2_parts_dict)):
            if not is_same:
                s1 = x_item.get("part")
                s2 = x2_parts_dict[j]['old']
                if (x_item.get('part') == x2_parts_dict[j]['old']):
                    x_item.set("part", x2_parts_dict[j]['new'])
                    x_root.append(x_item)
                    is_same = True
                    pass
                pass

        if not is_same:
            x_root.append(x_item)
            pass
        pass
    return x_root

def GetBusses(x1,x2,x2_layers_dict):
    """
    Extract busses data from two files and return dict
    :param x1:
    :param x2:
    :return:
    """
    x1_bus = x1.getchildren()
    x2_bus = x2.getchildren()

    if (len(x1_bus) == 0 and len(x2_bus) == 0):
        x_root = Element("busses")
        x_root.text = " "
        return x_root

    x_root = Element("busses")

    if not (len(x1_bus) == 0):
        for i in range(len(x1_bus)):
            x_root.append(x1_bus[i])
            pass
        pass

    if not (len(x2_bus) == 0):
        for i in range(len(x2_bus)):
            x_bus=Element('bus')
            x_bus.set('name',x2_bus[i].get('name'))

            x2_segment=x2_bus[i].find("segment")
            x2_wire=x2_segment.getchildren()

            x_segment=Element('segment')

            for j in range(len(x2_wire)):
                x_item=x2_wire[j]
                is_same=False
                for k in range(len(x2_layers_dict)):
                    if(int(x_item.get('layer'))==int(x2_layers_dict[k]['old'])):
                        x_item.set('layer',x2_layers_dict[k]['new'])
                        is_same=True
                        x_segment.append(x_item)
                        break
                    pass

                if not is_same:
                    x_segment.append(x_item)
                    pass
                pass

            x_bus.append(x_segment)
            pass
        x_root.append(x_bus)
        pass

    return x_root
def GetNet_Number(x):
    """
    Input string name and extract name and id
    :param x: SUPPLY
    :return: SUPPLY,0
    """
    index=len(x)-1
    num=""
    while(ord(x[index])>=48 and ord(x[index])<=57):
        num=x[index]+num
        index=index-1
        pass
    if(num==""):
        return x,0
    return x[0:index+1],int(num)

def GetSegment(x,x2_layers_dict,x2_parts_dict,x2_net_dict):
    """
    Extract segment data from two files and return dict
    :param x:
    :param x2_layers_dict:
    :param x2_net_dict:
    :return:
    """
    x_root=Element("segment")

    x2_wire = x.findall('wire')
    x2_pinref = x.findall('pinref')
    x2_junction = x.findall('junction')
    x2_label = x.findall('label')

    if not (len(x2_wire)==0):
        for i in range(len(x2_wire)):
            x_item=x2_wire[i]
            is_same=False
            for j in range(len(x2_layers_dict)):
                if(x_item.get('layer')==x2_layers_dict[j]['old']):
                    x_item.set('layer',x2_layers_dict[j]['new'])
                    x_root.append(x_item)
                    is_same=True
                    pass
                pass

            if not is_same:
                x_root.append(x_item)
                pass
            pass
        pass

    if not (len(x2_pinref)==0):
        for i in range(len(x2_pinref)):
            x_item=x2_pinref[i]
            is_same=False
            for j in range(len(x2_parts_dict)):
                if(x_item.get('part')==x2_parts_dict[j]['old']):
                    x_item.set('part',x2_parts_dict[j]['new'])
                    pass
                pass

            # for j in range(len(x2_net_dict)):
            #     if(x_item.get('pin')==x2_net_dict[j]['old']):
            #         x_item.set('pin',x2_net_dict[j]['new'])
            #         x_root.append(x_item)
            #         is_same=True
            #         pass
            #     pass

            if not is_same:
                x_root.append(x_item)
                pass
            pass
        pass

    if not (len(x2_junction)==0):
        for i in range(len(x2_junction)):
            x_root.append(x2_junction[i])
        pass

    if not (len(x2_label)==0):
        for i in range(len(x2_label)):
            x_root.append(x2_label[i])
        pass

    return x_root


def GetSubNet(x,x2_layers_dict,x2_parts_dict,x2_classes_dict,x2_net_dict):
    """
    Extract Nets data from two files and return dict
    :param x:
    :param x2_layers_dict:
    :param x2_classes_dict:
    :return:
    """
    for i in range(len(x2_classes_dict)):
        if(x.get("class")==x2_classes_dict[i]['old']):
            x.set('class',x2_classes_dict[i]['new'])
            pass
        pass

    x_root=Element('net')
    x_root.set('name',x.get('name'))
    x_root.set('class', x.get('class'))

    x_segment=x.findall('segment')
    for i in range(len(x_segment)):
        x_new_segment=GetSegment(x_segment[i],x2_layers_dict,x2_parts_dict,x2_net_dict)
        x_root.append(x_new_segment)
        pass

    return x_root


def GetNets(x1,x2,x2_layers_dict,x2_parts_dict,x2_classes_dict):
    """
    Extract Nets data from two files and return dict
    :param x1:
    :param x2:
    :param x2_layers_dict:
    :param x2_classes_dict:
    :return:
    """
    x1_net = x1.findall('net')
    x2_net = x2.findall('net')
    x_name={}
    x2_net_dict=[]
    if (len(x1_net) == 0 and len(x2_net) == 0):
        return "<nets> </nets>"

    x_root = Element("nets")

    if not (len(x1_net) == 0):
        for i in range(len(x1_net)):
            x_root.append(x1_net[i])
            name,id=GetNet_Number(x1_net[i].get('name'))
            if not (name in x_name):
                x_name[name]=id
            else:
                x_name[name]=max(x_name[name],id)
            pass
        pass

    if not (len(x2_net)==0):
        for i in range(len(x2_net)):
            name,id=GetNet_Number(x2_net[i].get('name'))
            if not (name in x_name):
                x_name[name]=id
            else:
                x2_net_dict.append({'old':x2_net[i].get('name'),'new':name+str(x_name[name]+1)})
                x2_net[i].set('name',name+str(x_name[name]+1))
                x_name[name]=x_name[name]+1

    if not (len(x2_net) == 0):
        for i in range(len(x2_net)):
            x_net=GetSubNet(x2_net[i],x2_layers_dict,x2_parts_dict,x2_classes_dict,x2_net_dict)
            x_root.append(x_net)

    return x_root

def PlainBox(x,x1,y1,x2,y2):
    """
    Get smallest surrounding box for plain
    :param x:
    :param x1:
    :param y1:
    :param x2:
    :param y2:
    :return:
    """
    x_list=x.getchildren()
    for i in range(len(x_list)):
        if (x_list[i].tag == "text"):
            x1 = min(x1, float(x_list[i].get('x')))
            y1 = min(y1, float(x_list[i].get('y')))
            x2 = max(x2, float(x_list[i].get('x')))
            y2 = max(y2, float(x_list[i].get('y')))
            pass
        if (x_list[i].tag == "wire"):
            x1 = min(x1, float(x_list[i].get('x1')))
            y1 = min(y1, float(x_list[i].get('y1')))
            x2 = max(x2, float(x_list[i].get('x1')))
            y2 = max(y2, float(x_list[i].get('y1')))
            x1 = min(x1, float(x_list[i].get('x2')))
            y1 = min(y1, float(x_list[i].get('y2')))
            x2 = max(x2, float(x_list[i].get('x2')))
            y2 = max(y2, float(x_list[i].get('y2')))
            pass
        if (x_list[i].tag == "circle"):
            x1 = min(x1, float(x_list[i].get('x')))
            y1 = min(y1, float(x_list[i].get('y')))
            x2 = max(x2, float(x_list[i].get('x')))
            y2 = max(y2, float(x_list[i].get('y')))
            pass
        if (x_list[i].tag == "rectangle"):
            x1 = min(x1, float(x_list[i].get('x1')))
            y1 = min(y1, float(x_list[i].get('y1')))
            x2 = max(x2, float(x_list[i].get('x1')))
            y2 = max(y2, float(x_list[i].get('y1')))
            x1 = min(x1, float(x_list[i].get('x2')))
            y1 = min(y1, float(x_list[i].get('y2')))
            x2 = max(x2, float(x_list[i].get('x2')))
            y2 = max(y2, float(x_list[i].get('y2')))
            pass

    return x1,y1,x2,y2

def InstancesBox(x,x1,y1,x2,y2):
    """
    Get smallest surrounding box for instances
    :param x:
    :param x1:
    :param y1:
    :param x2:
    :param y2:
    :return:
    """
    x_list=x.getchildren()
    for i in range(len(x_list)):
        x1 = min(x1, float(x_list[i].get('x')))
        y1 = min(y1, float(x_list[i].get('y')))
        x2 = max(x2, float(x_list[i].get('x')))
        y2 = max(y2, float(x_list[i].get('y')))

        x_attribute=x_list[i].getchildren()
        for j in range(len(x_attribute)):
            x1 = min(x1, float(x_attribute[j].get('x')))
            y1 = min(y1, float(x_attribute[j].get('y')))
            x2 = max(x2, float(x_attribute[j].get('x')))
            y2 = max(y2, float(x_attribute[j].get('y')))

    return x1,y1,x2,y2

def BussesBox(x,x1,y1,x2,y2):
    """
    Get smallest surrounding box for instances
    :param x:
    :param x1:
    :param y1:
    :param x2:
    :param y2:
    :return:
    """
    x_list=x.getchildren()
    for i in range(len(x_list)):
        x_segment=x_list[i].getchildren()
        for j in range(len(x_segment)):
            x_wire=x_segment[j].getchildren()
            for k in range(len(x_wire)):
                x1 = min(x1, float(x_wire[k].get('x1')))
                y1 = min(y1, float(x_wire[k].get('y1')))
                x2 = max(x2, float(x_wire[k].get('x1')))
                y2 = max(y2, float(x_wire[k].get('y1')))
                x1 = min(x1, float(x_wire[k].get('x2')))
                y1 = min(y1, float(x_wire[k].get('y2')))
                x2 = max(x2, float(x_wire[k].get('x2')))
                y2 = max(y2, float(x_wire[k].get('y2')))
                pass
            pass
        pass
    return x1,y1,x2,y2

def NetsBox(x,x1,y1,x2,y2):
    """
    Get smallest nets box for instances
    :param x:
    :param x1:
    :param y1:
    :param x2:
    :param y2:
    :return:
    """
    x_list=x.getchildren()
    for i in range(len(x_list)):
        x_segment=x_list[i].getchildren()
        for j in range(len(x_segment)):
            x_items=x_segment[j].getchildren()
            for k in range(len(x_items)):
                if (x_items[k].tag == "wire"):
                    x1 = min(x1, float(x_items[k].get('x1')))
                    y1 = min(y1, float(x_items[k].get('y1')))
                    x2 = max(x2, float(x_items[k].get('x1')))
                    y2 = max(y2, float(x_items[k].get('y1')))
                    x1 = min(x1, float(x_items[k].get('x2')))
                    y1 = min(y1, float(x_items[k].get('y2')))
                    x2 = max(x2, float(x_items[k].get('x2')))
                    y2 = max(y2, float(x_items[k].get('y2')))
                    pass
                if (x_items[k].tag == "junction"):
                    x1 = min(x1, float(x_items[k].get('x')))
                    y1 = min(y1, float(x_items[k].get('y')))
                    x2 = max(x2, float(x_items[k].get('x')))
                    y2 = max(y2, float(x_items[k].get('y')))
                    pass
    return x1,y1,x2,y2

def GetSurroundingBox(x):
    """
    Get smallest surrounding box
    :param x:
    :return:
    """
    x1=1000
    y1=1000
    x2=0
    y2=0

    x1_plain=x.find('plain')
    x1, y1, x2, y2 = PlainBox(x1_plain, x1, y1, x2, y2)

    x1_instances=x.find('instances')
    x1, y1, x2, y2 = InstancesBox(x1_instances, x1, y1, x2, y2)

    x1_busses=x.find('busses')
    x1, y1, x2, y2 = BussesBox(x1_busses, x1, y1, x2, y2)

    x1_nets=x.find('nets')
    x1, y1, x2, y2 = NetsBox(x1_nets, x1, y1, x2, y2)

    return x1,y1,x2,y2

def OffsetPlain(x,offset_x,offset_y):
    """
    Offset the x and y for plain
    :param x:
    :param offset_x:
    :param offset_y:
    :return:
    """
    x_list = x.getchildren()
    for i in range(len(x_list)):
        if (x_list[i].tag == "text"):
            x_list[i].set('x', str(offset_x + float(x_list[i].get('x'))))
            x_list[i].set('y', str(offset_y + float(x_list[i].get('y'))))
            pass
        if (x_list[i].tag == "wire"):
            x_list[i].set('x1', str(offset_x + float(x_list[i].get('x1'))))
            x_list[i].set('y1', str(offset_y + float(x_list[i].get('y1'))))
            x_list[i].set('x2', str(offset_x + float(x_list[i].get('x2'))))
            x_list[i].set('y2', str(offset_y + float(x_list[i].get('y2'))))
            pass
        if (x_list[i].tag == "circle"):
            x_list[i].set('x', str(offset_x + float(x_list[i].get('x'))))
            x_list[i].set('y', str(offset_y + float(x_list[i].get('y'))))
            pass
        if (x_list[i].tag == "rectangle"):
            x_list[i].set('x1', str(offset_x + float(x_list[i].get('x1'))))
            x_list[i].set('y1', str(offset_y + float(x_list[i].get('y1'))))
            x_list[i].set('x2', str(offset_x + float(x_list[i].get('x2'))))
            x_list[i].set('y2', str(offset_y + float(x_list[i].get('y2'))))
            pass
    pass

def OffsetInstances(x,offset_x,offset_y):
    """
    Offset the x and y for instances
    :param x:
    :param offset_x:
    :param offset_y:
    :return:
    """
    x_list = x.getchildren()
    for i in range(len(x_list)):
        x_list[i].set('x', str(offset_x + float(x_list[i].get('x'))))
        x_list[i].set('y', str(offset_y + float(x_list[i].get('y'))))

        x_attribute = x_list[i].getchildren()
        for j in range(len(x_attribute)):
            x_attribute[j].set('x', str(offset_x + float(x_attribute[j].get('x'))))
            x_attribute[j].set('y', str(offset_y + float(x_attribute[j].get('y'))))
    pass

def OffsetBusses(x,offset_x,offset_y):
    """
    Offset the x and y for busses
    :param x:
    :param offset_x:
    :param offset_y:
    :return:
    """
    x_list = x.getchildren()
    for i in range(len(x_list)):
        x_segment = x_list[i].getchildren()
        for j in range(len(x_segment)):
            x_wire = x_segment[j].getchildren()
            for k in range(len(x_wire)):
                x_wire[k].set('x1', str(offset_x + float(x_wire[k].get('x1'))))
                x_wire[k].set('y1', str(offset_y + float(x_wire[k].get('y1'))))
                x_wire[k].set('x2', str(offset_x + float(x_wire[k].get('x2'))))
                x_wire[k].set('y2', str(offset_y + float(x_wire[k].get('y2'))))
                pass
            pass
        pass
    pass

def OffsetNets(x,offset_x,offset_y):
    """
    Offset the x and y for nets
    :param x:
    :param offset_x:
    :param offset_y:
    :return:
    """
    x_list = x.getchildren()
    for i in range(len(x_list)):
        x_segment = x_list[i].getchildren()
        for j in range(len(x_segment)):
            x_items = x_segment[j].getchildren()
            for k in range(len(x_items)):
                if (x_items[k].tag == "wire"):
                    x_items[k].set('x1', str(offset_x + float(x_items[k].get('x1'))))
                    x_items[k].set('y1', str(offset_y + float(x_items[k].get('y1'))))
                    x_items[k].set('x2', str(offset_x + float(x_items[k].get('x2'))))
                    x_items[k].set('y2', str(offset_y + float(x_items[k].get('y2'))))
                    pass
                if (x_items[k].tag == "junction"):
                    x_items[k].set('x', str(offset_x + float(x_items[k].get('x'))))
                    x_items[k].set('y', str(offset_y + float(x_items[k].get('y'))))
                    pass
    pass

def GetOffset(x,offset_x,offset_y):
    x_plain = x.find('plain')
    OffsetPlain(x_plain,offset_x,offset_y)

    x_instances = x.find('instances')
    OffsetInstances(x_instances, offset_x,offset_y)

    x_busses = x.find('busses')
    OffsetBusses(x_busses, offset_x,offset_y)

    x_nets = x.find('nets')
    OffsetNets(x_nets, offset_x,offset_y)

def GetSheet(x1,x2,x2_layers_dict,x2_parts_dict,x2_classes_dict):
    """
    Extract sheet data from two files and return dict
    :param x1:
    :param x2:
    :return:
    """
    x_sheet=Element("sheet")

    x1_x1, x1_y1, x1_x2, x1_y2 = GetSurroundingBox(x1)
    x2_x1, x2_y1, x2_x2, x2_y2 = GetSurroundingBox(x2)
    offset_x=(abs(x2_x1-x1_x2))*1.2
    offset_y=0

    GetOffset(x2,offset_x,offset_y)

    x1_plain=x1.find("plain")
    x2_plain=x2.find("plain")
    x_plain=GetPlain(x1_plain,x2_plain,x2_layers_dict)
    x_sheet.append(x_plain)

    x1_instances = x1.find("instances")
    x2_instances = x2.find("instances")
    x_instances=GetInstances(x1_instances,x2_instances,x2_parts_dict)
    x_sheet.append(x_instances)

    x1_busses = x1.find("busses")
    x2_busses = x2.find("busses")
    x_busses=GetBusses(x1_busses,x2_busses,x2_layers_dict)
    x_sheet.append(x_busses)

    x1_nets = x1.find('nets')
    x2_nets = x2.find('nets')
    x_nets=GetNets(x1_nets,x2_nets,x2_layers_dict,x2_parts_dict,x2_classes_dict)
    x_sheet.append(x_nets)

    return x_sheet


def GetSheets(x1,x2,x2_layers_dict,x2_parts_dict,x2_classes_dict):
    """
    Extract sheets data from two files and return dict
    :param x1:
    :param x2:
    :return:
    """
    if(x1 and x2):
        x_sheets=Element("sheets")
        x1_sheet=x1.find("sheet")
        x2_sheet=x2.find("sheet")
        x_sheet=GetSheet(x1_sheet,x2_sheet,x2_layers_dict,x2_parts_dict,x2_classes_dict)
        x_sheets.append(x_sheet)
        return x_sheets
    else:
        module_logger.error("No sheets existed in either files")
        return Element("sheets")

def MergeXML(x1,x2):
    """
    Merge 2 Files
    :param x1: xml-file-1
    :param x2: xml-file-2
    :return: xml file
    """

    # # # eagle
    x1_eagle=x1.getroot()
    x2_eagle=x2.getroot()
    x_eagle=Element('eagle')

    x_version=GetVersion(x1_eagle,x2_eagle)
    x_eagle.set('version',x_version)

    # # #   drawing
    x1_drawing = x1_eagle.find("drawing")
    x2_drawing = x2_eagle.find("drawing")
    x_drawing=Element("drawing")
    x_eagle.append(x_drawing)

    # # #   settings
    x_settings=Element("settings")
    x_setting_1=ET.XML("<setting alwaysvectorfont=\"no\"/>")
    x_setting_2=ET.XML("<setting verticaltext=\"up\"/>")
    x_settings.append(x_setting_1)
    x_settings.append(x_setting_2)
    x_drawing.append(x_settings)

    # # #   grid
    x_grid = ET.XML('<grid distance="0.1" unitdist="inch" unit="inch" style="lines" multiple="1" display="no" altdistance="0.01" altunitdist="inch" altunit="inch"/>')
    x_drawing.append(x_grid)

    # # #   layers
    x1_layers = x1_drawing.find("layers")
    x2_layers = x2_drawing.find("layers")
    x_layers,x1_layers_dict,x2_layers_dict=GetLayers(x1_layers,x2_layers)
    x_drawing.append(x_layers)

    # # #   schematic
    x1_schematic = x1_drawing.find("schematic")
    x2_schematic = x2_drawing.find("schematic")
    x_schematic=Element("schematic")
    x_schematic.set("xreflabel","%F%N/%S.%C%R")
    x_schematic.set("xrefpart", "/%S.%C%R")
    x_drawing.append(x_schematic)

    # # #   library
    x1_libraries = x1_schematic.find("libraries")
    x2_libraries = x2_schematic.find("libraries")
    x_libraries=GetLibraries(x1_libraries,x2_libraries)
    x_schematic.append(x_libraries)

    # # #   attributes
    x_attributes = Element("attributes")
    x_attributes.text = " "
    x_schematic.append(x_attributes)

    # # #   variantdefs
    x_variantdefs = Element("variantdefs")
    x_variantdefs.text = " "
    x_schematic.append(x_variantdefs)

    # # #   classes
    x1_classes = x1_schematic.find('classes')
    x2_classes = x2_schematic.find('classes')
    x_classes,x1_classes_dict,x2_classes_dict=GetClasses(x1_classes,x2_classes)
    x_schematic.append(x_classes)

    # # #   parts
    x1_parts = x1_schematic.find("parts")
    x2_parts = x2_schematic.find("parts")
    x_parts,x1_parts_dict,x2_parts_dict=GetParts(x1_parts,x2_parts)
    x_schematic.append(x_parts)

    # # #   sheets
    x1_sheets = x1_schematic.find("sheets")
    x2_sheets = x2_schematic.find("sheets")
    x_sheets = GetSheets(x1_sheets,x2_sheets,x2_layers_dict,x2_parts_dict,x2_classes_dict)
    x_schematic.append(x_sheets)

    return x_eagle
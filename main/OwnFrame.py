# Qt5 version 5.15.2
# PyQt5 version 5.15.2
# python version 3.8

from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5 import QtGui
import numpy as np


class OwnFrame:
    __inputValidatorSetted = False

    def __init__(self, parent, width=None, height=None):
        self.__frame = QFrame(parent)
        if width is not None:
            self.__frame.setFixedWidth(width)
        if height is not None:
            self.__frame.setFixedHeight(height)

        self._setup()

    def getFrame(self):
        return self.__frame

    def _setup(self):
        self._setupTextInputRestrict()  # 这是这个类所有的
        self._setupDataInWidgets()

    @classmethod
    def _setupTextInputRestrict(cls):
        if cls.__inputValidatorSetted:  # 已经设置过了
            return
        cls.__inputValidatorSetted = True

        ncRegx = QtCore.QRegExp(r"[a-zA-Z\d]+")  # 匹配数字和字母的组合
        cls.ncRegxValidator = QtGui.QRegExpValidator(ncRegx)

        intRegx = QtCore.QRegExp(r"-?[1-9]\d+|0")  # 不以0开头除非是0，包含负数
        cls.intRegxValidator = QtGui.QRegExpValidator(intRegx)

        npRegx = QtCore.QRegExp(r"(^(?!0)\d+)|0")  # 不以0开头除非是0，不包含负数
        cls.npRegxValidator = QtGui.QRegExpValidator(npRegx)

        # .123或123.或123.123或0.123或0，其实0可以不单独写出来，但如果要在别的地方用还是要的
        # 有一种特殊情况要排除，就是只有一个'.'，这样是不能转换为浮点数的，要么默认这个为0，要么为非法输入
        # 单个'.'就认为是0了
        floatRegx = QtCore.QRegExp(r"(^(?!0)\-?\d*\.?\d*)|(^\-?(0\.)\d*)|0")
        cls.floatRegxValidator = QtGui.QRegExpValidator(floatRegx)
        # float;float;...
        # 是基于floatRegx改过来的，也有单个'.'的情况
        floatListRegx = QtCore.QRegExp(
            r"^(?!;)(((\-?(?!0)\d*\.?\d*)|(\-?(0\.)\d*)|0);(?!;))*((\-?(?!0)\d*\.?\d*)|(\-?(0\.)\d*)|0)")
        cls.floatListRegxValidator = QtGui.QRegExpValidator(floatListRegx)

        floatlistRegx = QtCore.QRegExp(
            r"^(?!:)(((\-?(?!0)\d*\.?\d*)|(\-?(0\.)\d*)|0):(?!:))*((\-?(?!0)\d*\.?\d*)|(\-?(0\.)\d*)|0)")
        cls.floatlistRegxValidator = QtGui.QRegExpValidator(floatlistRegx)  # floatlist与floatList不同,一个是用:分隔,一个是用;分隔

        # 两个浮点数，float-float
        twoFloatRegx = QtCore.QRegExp(
            r"^(?!;)(((\-?(?!0)\d*\.?\d*)|(\-?(0\.)\d*)|0);(?!;))?((\-?(?!0)\d*\.?\d*)|(\-?(0\.)\d*)|0)")
        cls.twoFloatRegxValidator = QtGui.QRegExpValidator(twoFloatRegx)

        # to do list:怎么写出更好的复数正则表达式？？主要问题在于实部和虚部都有的复数,纯虚数和纯实数比较容易,以下有三个版本
        # complexRegx = QtCore.QRegExp(r'(\-?\d+\.?\d+[(\-|\+)]{1}\d+\.?\d+[j])|'
        #                              r'(((^(?!0)\-?\d*\.?\d*)|(^\-?(0\.)\d*)|0)[j])|'
        #                              r'((^(?!0)\-?\d*\.?\d*)|(^\-?(0\.)\d*)|0)')
        # complexRegx = QtCore.QRegExp(r"(((^(?!0)\-?\d*\.?\d*)|(^\-?(0\.)\d*)|0)(\-|\+)((^(?!0)\d*\.?\d*)|((0\.)\d*)|0))[j]|"
        #                              r"(((^(?!0)\-?\d*\.?\d*)|(^\-?(0\.)\d*)|0)[j])|"
        #                              r"((^(?!0)\-?\d*\.?\d*)|(^\-?(0\.)\d*)|0)")  实数和纯虚数没问题,复数输入时虚部只能为0.xxxj
        complexRegx = QtCore.QRegExp(r"(((^(?!0)\-?\d*\.?\d*)|(^\-?(0\.)\d*)|0)(\-|\+)[\d]+\.?[\d]+)[j]|"
                                     r"(((^(?!0)\-?\d*\.?\d*)|(^\-?(0\.)\d*)|0)[j])|"
                                     r"((^(?!0)\-?\d*\.?\d*)|(^\-?(0\.)\d*)|0)")
        cls.complexRegxValidator = QtGui.QRegExpValidator(complexRegx)

    # 将用户输入的字符串转换为相应的数据格式
    # 转换为复数或实数或整数的必须返回该数据格式,不要返回None,因为在后面计算时可能会出错
    @classmethod
    def _toSimpleStrFromText(cls, text: str or QLineEdit) -> str:
        if text == None:
            return ""
        if type(text) is not str:
            text = text.text()
        return "" if len(text) == 0 else text

    @classmethod
    def _toIntFromText(cls, text: str or QLineEdit) -> int or None:
        if text == None:
            return None
        if type(text) is not str:
            text = text.text()
        try:
            res = None if len(text) == 0 else int(text)
        except ValueError:
            cls.informMsg("数据格式有错误:on to int")
            res = None
        return res

    @classmethod
    def _toFloatFromText(cls, text: str or QLineEdit) -> float:
        # 数据格式错误的情形(可能有遗漏):None/""/"."
        if text == None:
            return 0.0
        if type(text) is not str:
            text = text.text()
        try:
            res = 0.0 if len(text) == 0 else (0.0 if text == "." else float(text))
        except ValueError:
            cls.informMsg("数据格式有错误:on to float,已架设为0.0")
            res = 0.0
        return res

    @classmethod
    def _toComplexFromText(cls, text: str or QLineEdit) -> complex:
        # 格式错误的几种情况(可能有遗漏):None/""/"."/".+x.xj"
        if text == None:
            return 0j
        if type(text) is not str:
            text = text.text()
        if len(text) == 0:
            return 0j
        if text == ".":
            return 0j
        try:
            res = complex(text)  # 若text中含有空格, 则无法转换为复数, 例如1+ 0.123j,但我们已经用正则表达式进行了限制
        except ValueError:
            cls.informMsg("数据格式有错误:on to complex,已假定为0.0")
            res = 0j
        return res

    @classmethod
    def _toFloatListByStrFromText(cls, text: str or QLineEdit) -> list or None:
        # 用于Fx_vv这一类参数和v_soc这一类参数
        if text is None:
            return None
        if type(text) is not str:
            text = text.text()
        if len(text) > 0:
            str_list = text.split(";") # 如果text的最后一个字符是";",那么str_list的最后一个元素是空字符串""
            res = []
            for ele in str_list:  # ele有可能为空字符串""
                temp = cls._toFloatFromText(ele)
                res.append(temp)
        else:
            res = None
        return res

    @classmethod
    # 得到等差数列
    def _tofloatlistByStrFromText(cls, text: str or QLineEdit) -> list or None:
        if text == None:
            return None
        if type(text) is not str:
            text = text.text()
        str_list = text.split(":")
        float_list = []
        if len(str_list) == 3:
            for ele in str_list:
                float_list.append(cls._toFloatFromText(ele))
            float_array = cls._tofloatarrayFromfloatlist(float_list)
            if float_array == None:
                cls.informMsg("无法形成等差数列")
                return None
            res = float_array
        else:
            cls.informMsg("数据格式有问题:请输入三个浮点数")
            res = None
        return res

    def _tofloatarrayFromfloatlist(float_list:list):  # 用cls._tofloatarrayFromfloatlist来调用
        head = float_list[0]
        end = float_list[1]
        step = float_list[2]
        N = int(np.floor((end - head) / step))
        if N < 0:
            return None
        float_array = [head]
        for i in range(N):
            float_array.append(head + (i + 1) * step)
        return float_array

    @classmethod
    def _toFloatListByWidgets_1DFromText(cls, widgets: list) -> list:
        res = []
        for ele in widgets:
            item = cls._toFloatFromText(ele.text())
            res.append(item)  # 可能得到None的元素，代表这个框没有输入，一些情况下没有输入默认为0，一些情况下有其他默认值
        return res

    @classmethod
    def _toComplexListByWidgets_1DFromText(cls, widgets: list) -> list:
        res = []
        for ele in widgets:
            item = cls._toComplexFromText(ele.text())
            if item == None:
                item = 0.0
            res.append(item)  # 可能得到None的元素，代表这个框没有输入，一些情况下没有输入默认为0，一些情况下有其他默认值
        return res

    @classmethod
    def _toFloatListByWidgets_2DFromText(cls, widgets: [[]]) -> [[]]:
        res = []
        for ele in widgets:
            temp = cls._toFloatListByWidgets_1DFromText(ele)
            res.append(temp)
        return res

    @classmethod
    def _toComplexListByWidgets_2DFromText(cls, widgets: [[]]) -> [[]]:
        res = []
        for ele in widgets:
            temp = cls._toComplexListByWidgets_1DFromText(ele)
            res.append(temp)
        return res

    def _setupDataInWidgets(self):
        # 在各个页面都设置好之后调用这个,把各个需要获取输入的控件(或其上数据)加入字典中，同时指定解析方式,方便之后从界面获取输入
        self.widgetsWithData = {}  # key是代表名字的str，value是一个元组(widget, method to parse)

    def _bindDataWithWidgets(self, name: str, widget, parser):
        self.widgetsWithData[name] = (widget, parser)

    def _getDataFromInupt(self, dataName: str):
        # 根据数据名从界面相应组件获取数据，用个字典来存下各个组件吧
        if dataName not in self.widgetsWithData.keys():
            self.informMsg(f"从widgetsWithData中获取数据时出错，错误的数据名:{dataName}")
            return None
        data_with_processor = self.widgetsWithData[dataName]
        return data_with_processor[1](data_with_processor[0])

    @classmethod
    def informMsg(cls, msg: str):
        msgBox = QMessageBox()
        msgBox.setWindowTitle("inform")
        msgBox.setText(msg)
        msgBox.exec_()  # 模态

    @classmethod
    def questionMsg(cls, msg: str):
        msgBox = QMessageBox()
        msgBox.setWindowTitle("确认框")
        reply = QMessageBox.information(msgBox,  # 使用infomation信息框
                                        "标题",
                                        msg,
                                        QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            return True
        if reply == QMessageBox.No:
            return False
        msgBox.exec_()  # 模态


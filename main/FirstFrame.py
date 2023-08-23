# Qt5 version 5.15.2
# PyQt5 version 5.15.2
# python version 3.8

from OwnFrame import *
from DataManager import *
import re
import json
import numpy as np
from edrixs.solvers import *
from edrixs.angular_momentum import *
from edrixs.coulomb_utensor import *
from edrixs.utils import *
import matplotlib.pyplot as plt
import matplotlib as mpl
import sys

shell_name_to_edge = {
    '1s': 'K',
    '2s': 'L1',
    '2p12': 'L2',
    '2p32': 'L3',
    '2p': 'L23',
    '3s': 'M1',
    '3p12': 'M2',
    '3p32': 'M3',
    '3p': 'M23',
    '3d32': 'M4',
    '3d52': 'M5',
    '3d': 'M45',
    '4s': 'N1',
    '4p12': 'N2',
    '4p32': 'N3',
    '4p': 'N23',
    '4d32': 'N4',
    '4d52': 'N5',
    '4d': 'N45',
    '4f52': 'N6',
    '4f72': 'N7',
    '4f': 'N67',
    '5s': 'O1',
    '5p12': 'O2',
    '5p32': 'O3',
    '5p': 'O23',
    '5d32': 'O4',
    '5d52': 'O5',
    '5d': 'O45',
    '6s': 'P1',
    '6p12': 'P2',
    '6p32': 'P3',
    '6p': 'P23'
}


class FirstFrame(OwnFrame):
    def __init__(self, parent=None, width=1280, height=840):
        OwnFrame.__init__(self, parent, width, height)
        self.frame = super().getFrame()
        self.frame.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        # self.frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.frame.setMinimumHeight(height - 20)
        self.frame.setMinimumWidth(width - 36)
        self.needToSaveStyleSheet = 'color:rgb(160,60,60)'
        self.font = QtGui.QFont()
        self.font.setFamily("Arial")
        self.font.setPointSize(8)
        self._setupDataVariable()
        self._arrangeUI()
        self._retranslateAll()

        self._textInputRestrict()
        self._arrangeDataInWidgets()

    def _setupDataVariable(self):
        self.dataManager = DataManager_atom()
        self.eval_i_present = None
        self.eval_n_present = None
        self.trans_op_present = None
        self.gs_list_present = [0]
        self.atom_name_present = ""
        self.AtomDataKeys = ['atom_name', 'v_name', 'v_noccu', 'c_name', 'c_noccu',
                             'slater_Fx_vv_initial', 'slater_Fx_vc_initial', 'slater_Gx_vc_initial',
                             'slater_Fx_cc_initial',
                             'slater_Fx_vv_intermediate', 'slater_Fx_vc_intermediate',
                             'slater_Gx_vc_intermediate', 'slater_Fx_cc_intermediate',
                             'v_soc', 'c_soc', 'shell_level_v', 'shell_level_c', 'gamma_c', 'gamma_f', 'v1_ext_B',
                             'v1_on_which', 'v_cmft', 'v_othermat', 'local_axis', 'ed']
        self.current_index = 1

    def _arrangeUI(self):
        # 创建QStack
        if "stack":
            self.stack_box = QGroupBox(self.frame)
            self.stack_box.setFixedSize(980, 605)
            self.stack = QStackedWidget(self.stack_box)
            self.stack.setFixedSize(970, 605)
            # 创建十多个stack
            self.stack_simple_parameters = QWidget(self.stack)
            # self.stack_external_crystal_field = QWidget(self.stack)
            self.stack_no_shell = QWidget(self.stack)
            self.stack_s_shell = QWidget(self.stack)
            self.stack_p_or_t2g_shell = QWidget(self.stack)
            self.stack_d_shell = QWidget(self.stack)
            self.stack_f_shell = QWidget(self.stack)
            self.stack_other_matrix = QWidget(self.stack)
            # 每个stack分别调用
            self.create_stack_simple_paramters()
            self.create_stack_no_shell()
            self.create_stack_s_shell()
            self.create_stack_p_or_t2g_shell()
            self.create_stack_d_shell()
            self.create_stack_f_shell()
            self.create_stack_other_matrixs()
            # 添加到QStackedWidget
            self.stack.addWidget(self.stack_simple_parameters)  # index=0
            # self.stack.addWidget(self.stack_external_crystal_field)
            self.stack.addWidget(self.stack_no_shell)  # 一定要把所有页面都加上,否则界面可能会有脏东西
            self.stack.addWidget(self.stack_s_shell)  # 一定要把所有页面都加上,否则界面可能会有脏东西
            self.stack.addWidget(self.stack_p_or_t2g_shell)  # 一定要把所有页面都加上,否则界面可能会有脏东西
            self.stack.addWidget(self.stack_d_shell)  # 一定要把所有页面都加上,否则界面可能会有脏东西
            self.stack.addWidget(self.stack_f_shell)  # 一定要把所有页面都加上,否则界面可能会有脏东西
            self.stack.addWidget(self.stack_other_matrix)  # 一定要把所有页面都加上,否则界面可能会有脏东西

        # 创建选择栏
        if "stack_list":
            self.stack_list = QListWidget(self.frame)
            self.stack_list.setGeometry(0, 0, 200, 160)
            self.stack_list.setFixedSize(200, 180)
            self.stack_list.insertItem(0, 'internal_parameters')
            self.stack_list.insertItem(1, 'external_crystal_field')
            self.stack_list.insertItem(2, 'other_matrix')
            self.stack_list.currentRowChanged.connect(self.stack_display)

        # 文件栏
        if "atom_list":
            self.boxAtomList = QGroupBox(self.frame)
            self.boxAtomList.setGeometry(0, 170, 200, 605)
            self.boxAtomList.setFixedSize(200, 605)

            self.buttonAddToAtomList = QPushButton(self.boxAtomList)
            self.buttonAddToAtomList.setStyleSheet(self.needToSaveStyleSheet)
            self.buttonAddToAtomList.setFixedSize(80, 32)
            self.buttonAddToAtomList.clicked.connect(self._handleOnAddToAtomList)

            self.buttonCheckInput = QPushButton(self.boxAtomList)
            self.buttonCheckInput.setStyleSheet(self.needToSaveStyleSheet)
            self.buttonCheckInput.setFixedSize(80, 32)
            self.buttonCheckInput.clicked.connect(self._handleOnCheckInput)

            self.atom_list = QListWidget(self.boxAtomList)  # 一个列表，包含各个电子的情况
            self.atom_list.setFixedSize(180, 480)
            # 给list设置一个右键菜单，可以右键删除
            # 然后双击事件的话是打开进行修改
            self.atom_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            atom_list_menu = QMenu(self.atom_list)
            self.atom_list_menu_import_action = QAction(atom_list_menu)

            def atom_list_import_action():  # 这个action不能直接接handleOnImport，这个Import是带参数item的
                # 如果能打开menu的话肯定是选中item了的
                self._handleOnImportAtomFromList(self.atom_list.currentItem())

            self.atom_list_menu_import_action.triggered.connect(atom_list_import_action)
            self.atom_list_menu_delete_action = QAction(atom_list_menu)
            self.atom_list_menu_delete_action.triggered.connect(self._handleOnDeleteFromAtomList)

            atom_list_menu.addAction(self.atom_list_menu_import_action)
            atom_list_menu.addAction(self.atom_list_menu_delete_action)

            def atom_list_menu_show():
                # 还要判断一下是否选中item
                if self.atom_list.currentItem() is None:
                    return
                atom_list_menu.exec_(QtGui.QCursor.pos())

            self.atom_list.customContextMenuRequested.connect(atom_list_menu_show)
            self.atom_list.itemDoubleClicked.connect(self._handleOnImportAtomFromList)

            self.atom_list_save_button = QPushButton(self.atom_list)
            self.atom_list_save_button.setFixedSize(80, 32)
            self.atom_list_save_button.clicked.connect(self._handleOnSaveAtomList)

            self.atom_list_load_button = QPushButton(self.atom_list)
            self.atom_list_load_button.setFixedSize(80, 32)
            self.atom_list_load_button.clicked.connect(self._handleOnLoadAtomList)

            self.boxAtomListLayout = QGridLayout(self.boxAtomList)
            self.boxAtomListLayout.setAlignment(QtCore.Qt.AlignTop)
            self.boxAtomListLayout.addWidget(self.buttonAddToAtomList, 0, 0, 1, 1, QtCore.Qt.AlignTop)
            self.boxAtomListLayout.addWidget(self.buttonCheckInput, 0, 1, 1, 1, QtCore.Qt.AlignTop)
            self.boxAtomListLayout.addWidget(self.atom_list, 1, 0, 2, 2, QtCore.Qt.AlignTop)
            self.boxAtomListLayout.addWidget(self.atom_list_save_button, 3, 0, 1, 1, QtCore.Qt.AlignTop)
            self.boxAtomListLayout.addWidget(self.atom_list_load_button, 3, 1, 1, 1, QtCore.Qt.AlignTop)

            self.boxAtomList.setLayout(self.boxAtomListLayout)

        # local axis
        if "local axis":
            self.Box_Local_Axis = QGroupBox(self.frame)
            self.Box_Local_Axis.setFixedSize(250, 180)
            # 3*3的矩阵
            self.local_axis_texts = [[QLineEdit(self.Box_Local_Axis) for _ in range(3)] for _ in range(3)]
            for row in self.local_axis_texts:
                for LineEdit in row:
                    LineEdit.setFixedSize(60, 42)

            Box_Local_Axis_Layout_Layout = QGridLayout(self.Box_Local_Axis)
            Box_Local_Axis_Layout_Layout.setAlignment(QtCore.Qt.AlignTop)
            self.arrange_matrix_on_box(Box_Local_Axis_Layout_Layout, self.local_axis_texts)
            self.Box_Local_Axis.setLayout(Box_Local_Axis_Layout_Layout)

        # 精确对角化
        if "exact_diagonalization":
            self.exact_diag_box = QGroupBox(self.frame)
            self.exact_diag_box.setFixedSize(700, 180)
            # 文件是否写入
            self.verbose_label = QLabel(self.exact_diag_box)
            self.verbose_label.setAlignment(QtCore.Qt.AlignCenter)
            self.verbose_label.setFixedSize(60, 32)
            self.verbose_text = QLineEdit(self.exact_diag_box)
            self.verbose_text.setFixedSize(100, 32)
            # 精确对角化的频道选择
            self.ed_combo = QComboBox(self.exact_diag_box)
            self.ed_combo.setFixedSize(170, 32)
            self.ed_combo.addItem("ed_1v1c_python")  # 当选用某些频道但没有实现进行精确对角化则会报错,让用户先去进行相应的精确对角化
            self.ed_combo.addItem("ed_1v1c_fortan")
            self.ed_combo.addItem("ed_2v1c_fortan")

            self.ed_calculation_button = QPushButton(self.exact_diag_box)
            self.ed_calculation_button.setFixedSize(60, 32)
            self.ed_calculation_button.clicked.connect(self._handleOnEdCalculation)

            HBox_ed = QHBoxLayout()
            HBox_ed.addWidget(self.verbose_label)
            HBox_ed.addWidget(self.verbose_text)
            HBox_ed.addWidget(self.ed_combo)
            HBox_ed.addWidget(self.ed_calculation_button)
            # 显示精确对角化的结果
            self.firstPageOutputBox = QGroupBox(self.exact_diag_box)
            self.ed_show_button = QPushButton(self.firstPageOutputBox)
            self.ed_show_button.setFixedSize(120, 32)
            self.ed_show_button.clicked.connect(self._handleOnEdShow)
            self.gs_list_label = QLabel(self.exact_diag_box)
            self.gs_list_label.setAlignment(QtCore.Qt.AlignCenter)
            self.gs_list_label.setFixedSize(100, 32)
            self.gs_list_text = QLineEdit(self.frame)
            self.gs_list_text.setFixedSize(60, 32)
            self.gs_list_text.editingFinished.connect(self._handleOn_Refresh_gs_list)
            firstPageOutputBoxLayout = QHBoxLayout(self.firstPageOutputBox)
            firstPageOutputBoxLayout.setAlignment(QtCore.Qt.AlignTop)
            firstPageOutputBoxLayout.addWidget(self.ed_show_button)
            firstPageOutputBoxLayout.addWidget(self.gs_list_label)
            firstPageOutputBoxLayout.addWidget(self.gs_list_text)
            self.firstPageOutputBox.setLayout(firstPageOutputBoxLayout)

            exact_diag_box_layout = QVBoxLayout(self.exact_diag_box)
            exact_diag_box_layout.setAlignment(QtCore.Qt.AlignTop)
            exact_diag_box_layout.addLayout(HBox_ed)
            exact_diag_box_layout.addWidget(self.firstPageOutputBox)
            self.exact_diag_box.setLayout(exact_diag_box_layout)

        if "frame_layout":
            HBox_1 = QHBoxLayout()
            HBox_1.addWidget(self.Box_Local_Axis)
            HBox_1.addWidget(self.exact_diag_box)
            # 垂直布局
            VBox_1 = QVBoxLayout()
            VBox_1.addWidget(self.boxAtomList)
            VBox_1.addWidget(self.stack_list)
            VBox_2 = QVBoxLayout()
            VBox_2.addWidget(self.stack_box)
            VBox_2.addLayout(HBox_1)

            # 水平布局，添加部件到布局中
            HBox = QHBoxLayout(self.frame)
            HBox.addLayout(VBox_1)
            HBox.addLayout(VBox_2)
            self.frame.setLayout(HBox)

            self.scrollForFirstFrame = QScrollArea(self.frame.parent())
            self.scrollForFirstFrame.setWidget(self.frame)

    def arrange_matrix_on_box(self, grid_layout, widgets):
        for row_i in range(len(widgets)):
            one_row = widgets[row_i]
            for col_j in range(len(one_row)):
                grid_layout.addWidget(one_row[col_j], row_i, col_j, QtCore.Qt.AlignTop)

    def create_stack_simple_paramters(self):
        try:
            if "valence and core >> stack_simple_parameters":
                self.Box_Atom_Information = QGroupBox(self.stack_simple_parameters)
                self.atom_name_label = QLabel(self.Box_Atom_Information)
                self.atom_name_label.setAlignment(QtCore.Qt.AlignCenter)
                self.atom_name_label.setStyleSheet(self.needToSaveStyleSheet)
                self.atom_name_label.setFixedSize(145, 32)
                self.atom_name_text = QLineEdit(self.Box_Atom_Information)
                self.atom_name_text.setFixedSize(60, 32)
                self.atom_name_text.setStyleSheet(self.needToSaveStyleSheet)

                self.v_name_label = QLabel(self.Box_Atom_Information)
                self.v_name_label.setAlignment(QtCore.Qt.AlignCenter)
                self.v_name_label.setStyleSheet(self.needToSaveStyleSheet)
                self.v_name_label.setFixedSize(145, 32)
                self.v_name_text = QLineEdit(self.Box_Atom_Information)  # str
                self.v_name_text.setStyleSheet(self.needToSaveStyleSheet)
                self.v_name_text.setFixedSize(60, 32)

                self.v_noccu_label = QLabel(self.Box_Atom_Information)
                self.v_noccu_label.setAlignment(QtCore.Qt.AlignCenter)
                self.v_noccu_label.setStyleSheet(self.needToSaveStyleSheet)
                self.v_noccu_label.setFixedSize(145, 32)
                self.v_noccu_text = QLineEdit(self.Box_Atom_Information)  # int
                self.v_noccu_text.setStyleSheet(self.needToSaveStyleSheet)
                self.v_noccu_text.setFixedSize(60, 32)

                self.c_name_label = QLabel(self.Box_Atom_Information)
                self.c_name_label.setAlignment(QtCore.Qt.AlignCenter)
                self.c_name_label.setStyleSheet(self.needToSaveStyleSheet)
                self.c_name_label.setFixedSize(145, 32)
                self.c_name_text = QLineEdit(self.Box_Atom_Information)  # str
                self.c_name_text.setStyleSheet(self.needToSaveStyleSheet)
                self.c_name_text.setFixedSize(60, 32)

                self.c_noccu_label = QLabel(self.Box_Atom_Information)
                self.c_noccu_label.setAlignment(QtCore.Qt.AlignCenter)
                self.c_noccu_label.setStyleSheet(self.needToSaveStyleSheet)
                self.c_noccu_label.setFixedSize(145, 32)
                self.c_noccu_text = QLineEdit(self.Box_Atom_Information)  # int
                self.c_noccu_text.setStyleSheet(self.needToSaveStyleSheet)

                self.shell_level_v_label = QLabel(self.Box_Atom_Information)
                self.shell_level_v_label.setAlignment(QtCore.Qt.AlignCenter)
                self.shell_level_v_label.setStyleSheet(self.needToSaveStyleSheet)
                self.shell_level_v_label.setFixedSize(135, 32)
                self.shell_level_v_text = QLineEdit(self.Box_Atom_Information)  # float
                self.shell_level_v_text.setStyleSheet(self.needToSaveStyleSheet)
                self.shell_level_v_text.setFixedSize(60, 32)

                self.shell_level_c_label = QLabel(self.Box_Atom_Information)
                self.shell_level_c_label.setAlignment(QtCore.Qt.AlignCenter)
                self.shell_level_c_label.setStyleSheet(self.needToSaveStyleSheet)
                self.shell_level_c_label.setFixedSize(135, 32)
                self.shell_level_c_text = QLineEdit(self.Box_Atom_Information)  # float
                self.shell_level_c_text.setStyleSheet(self.needToSaveStyleSheet)
                self.shell_level_c_text.setFixedSize(60, 32)
                self.c_noccu_text.setFixedSize(60, 32)

                self.v_soc_label = QLabel(self.Box_Atom_Information)
                self.v_soc_label.setAlignment(QtCore.Qt.AlignCenter)
                self.v_soc_label.setStyleSheet(self.needToSaveStyleSheet)
                self.v_soc_label.setFixedSize(145, 32)
                self.v_soc_text = QLineEdit(self.Box_Atom_Information)  # float-float
                self.v_soc_text.setStyleSheet(self.needToSaveStyleSheet)
                self.v_soc_text.setFixedSize(100, 32)

                self.c_soc_label = QLabel(self.Box_Atom_Information)
                self.c_soc_label.setAlignment(QtCore.Qt.AlignCenter)
                self.c_soc_label.setStyleSheet(self.needToSaveStyleSheet)
                self.c_soc_label.setFixedSize(145, 32)
                self.c_soc_text = QLineEdit(self.Box_Atom_Information)  # float
                self.c_soc_text.setStyleSheet(self.needToSaveStyleSheet)
                self.c_soc_text.setFixedSize(60, 32)

                self.gamma_c_label = QLabel(self.Box_Atom_Information)
                self.gamma_c_label.setAlignment(QtCore.Qt.AlignCenter)
                self.gamma_c_label.setFixedSize(145, 32)

                self.gamma_c_text = QLineEdit(self.Box_Atom_Information)
                self.gamma_c_text.setFixedSize(62, 32)

                self.gamma_f_label = QLabel(self.Box_Atom_Information)
                self.gamma_f_label.setAlignment(QtCore.Qt.AlignCenter)
                self.gamma_f_label.setFixedSize(145, 32)

                self.gamma_f_text = QLineEdit(self.Box_Atom_Information)
                self.gamma_f_text.setFixedSize(62, 32)

                if "self.Box_Atom_Information_Layout":
                    self.Box_Atom_Information_Layout = QGridLayout(self.Box_Atom_Information)
                    self.Box_Atom_Information_Layout.setAlignment(QtCore.Qt.AlignTop)
                    self.Box_Atom_Information_Layout.addWidget(self.atom_name_label, 0, 0, 1, 1, QtCore.Qt.AlignTop)
                    self.Box_Atom_Information_Layout.addWidget(self.atom_name_text, 0, 1, 1, 1, QtCore.Qt.AlignTop)
                    self.Box_Atom_Information_Layout.addWidget(self.v_name_label, 1, 0, 1, 1, QtCore.Qt.AlignTop)
                    self.Box_Atom_Information_Layout.addWidget(self.v_name_text, 1, 1, 1, 1, QtCore.Qt.AlignTop)
                    self.Box_Atom_Information_Layout.addWidget(self.v_noccu_label, 1, 2, 1, 1, QtCore.Qt.AlignTop)
                    self.Box_Atom_Information_Layout.addWidget(self.v_noccu_text, 1, 3, 1, 1, QtCore.Qt.AlignTop)
                    self.Box_Atom_Information_Layout.addWidget(self.c_name_label, 1, 4, 1, 1, QtCore.Qt.AlignTop)
                    self.Box_Atom_Information_Layout.addWidget(self.c_name_text, 1, 5, 1, 1, QtCore.Qt.AlignTop)
                    self.Box_Atom_Information_Layout.addWidget(self.c_noccu_label, 1, 6, 1, 1, QtCore.Qt.AlignTop)
                    self.Box_Atom_Information_Layout.addWidget(self.c_noccu_text, 1, 7, 1, 1, QtCore.Qt.AlignTop)

                    self.Box_Atom_Information_Layout.addWidget(self.shell_level_v_label, 2, 0, QtCore.Qt.AlignTop)
                    self.Box_Atom_Information_Layout.addWidget(self.shell_level_v_text, 2, 1, QtCore.Qt.AlignTop)
                    self.Box_Atom_Information_Layout.addWidget(self.shell_level_c_label, 2, 2, QtCore.Qt.AlignTop)
                    self.Box_Atom_Information_Layout.addWidget(self.shell_level_c_text, 2, 3, QtCore.Qt.AlignTop)
                    self.Box_Atom_Information_Layout.addWidget(self.gamma_c_label, 2, 4, QtCore.Qt.AlignTop)
                    self.Box_Atom_Information_Layout.addWidget(self.gamma_c_text, 2, 5, QtCore.Qt.AlignTop)
                    self.Box_Atom_Information_Layout.addWidget(self.gamma_f_label, 2, 6, QtCore.Qt.AlignTop)
                    self.Box_Atom_Information_Layout.addWidget(self.gamma_f_text, 2, 7, QtCore.Qt.AlignTop)

                    self.Box_Atom_Information_Layout.addWidget(self.v_soc_label, 3, 0, QtCore.Qt.AlignTop)
                    self.Box_Atom_Information_Layout.addWidget(self.v_soc_text, 3, 1, QtCore.Qt.AlignTop)
                    self.Box_Atom_Information_Layout.addWidget(self.c_soc_label, 3, 2, QtCore.Qt.AlignTop)
                    self.Box_Atom_Information_Layout.addWidget(self.c_soc_text, 3, 3, QtCore.Qt.AlignTop)
                    self.Box_Atom_Information.setLayout(self.Box_Atom_Information_Layout)

            if "slater_initial >> stack_simple_parameters":
                self.slater_initial_box = QGroupBox(self.stack_simple_parameters)
                self.slater_initial_box.setStyleSheet(self.needToSaveStyleSheet)
                self.slater_initial_box.setFixedSize(475, 215)

                self.slater_initial_Fx_vv_label = QLabel(self.slater_initial_box)
                self.slater_initial_Fx_vv_label.setAlignment(QtCore.Qt.AlignCenter)
                self.slater_initial_Fx_vv_label.setFixedSize(80, 32)
                self.slater_initial_Fx_vv_text = QLineEdit(self.slater_initial_box)
                self.slater_initial_Fx_vv_text.setFixedSize(350, 32)

                self.slater_initial_Fx_vc_label = QLabel(self.slater_initial_box)
                self.slater_initial_Fx_vc_label.setAlignment(QtCore.Qt.AlignCenter)
                self.slater_initial_Fx_vc_label.setFixedSize(80, 32)
                self.slater_initial_Fx_vc_text = QLineEdit(self.slater_initial_box)
                self.slater_initial_Fx_vc_text.setFixedSize(350, 32)

                self.slater_initial_Gx_vc_label = QLabel(self.slater_initial_box)
                self.slater_initial_Gx_vc_label.setAlignment(QtCore.Qt.AlignCenter)
                self.slater_initial_Gx_vc_label.setFixedSize(80, 32)
                self.slater_initial_Gx_vc_text = QLineEdit(self.slater_initial_box)
                self.slater_initial_Gx_vc_text.setFixedSize(350, 32)

                self.slater_initial_Fx_cc_label = QLabel(self.slater_initial_box)
                self.slater_initial_Fx_cc_label.setAlignment(QtCore.Qt.AlignCenter)
                self.slater_initial_Fx_cc_label.setFixedSize(80, 32)
                self.slater_initial_Fx_cc_text = QLineEdit(self.slater_initial_box)
                self.slater_initial_Fx_cc_text.setFixedSize(350, 32)

                slaterInitialBoxLayout = QGridLayout(self.slater_initial_box)
                slaterInitialBoxLayout.setAlignment(QtCore.Qt.AlignTop)
                slaterInitialBoxLayout.addWidget(self.slater_initial_Fx_vv_label, 0, 0, QtCore.Qt.AlignTop)
                slaterInitialBoxLayout.addWidget(self.slater_initial_Fx_vv_text, 0, 1, 1, 3, QtCore.Qt.AlignTop)
                slaterInitialBoxLayout.addWidget(self.slater_initial_Fx_vc_label, 1, 0, QtCore.Qt.AlignTop)
                slaterInitialBoxLayout.addWidget(self.slater_initial_Fx_vc_text, 1, 1, 1, 3, QtCore.Qt.AlignTop)
                slaterInitialBoxLayout.addWidget(self.slater_initial_Gx_vc_label, 2, 0, QtCore.Qt.AlignTop)
                slaterInitialBoxLayout.addWidget(self.slater_initial_Gx_vc_text, 2, 1, 1, 3, QtCore.Qt.AlignTop)
                slaterInitialBoxLayout.addWidget(self.slater_initial_Fx_cc_label, 3, 0, QtCore.Qt.AlignTop)
                slaterInitialBoxLayout.addWidget(self.slater_initial_Fx_cc_text, 3, 1, 1, 3, QtCore.Qt.AlignTop)
                self.slater_initial_box.setLayout(slaterInitialBoxLayout)

            if "slater_intermediate >> stack_simple_parameters":
                self.slater_intermediate_box = QGroupBox(self.stack_simple_parameters)
                self.slater_intermediate_box.setStyleSheet(self.needToSaveStyleSheet)
                self.slater_intermediate_box.setFixedSize(475, 215)

                self.slater_intermediate_Fx_vv_label = QLabel(self.slater_intermediate_box)
                self.slater_intermediate_Fx_vv_label.setAlignment(QtCore.Qt.AlignCenter)
                self.slater_intermediate_Fx_vv_label.setFixedSize(80, 32)
                self.slater_intermediate_Fx_vv_text = QLineEdit(self.slater_intermediate_box)
                self.slater_intermediate_Fx_vv_text.setFixedSize(350, 32)

                self.slater_intermediate_Fx_vc_label = QLabel(self.slater_intermediate_box)
                self.slater_intermediate_Fx_vc_label.setAlignment(QtCore.Qt.AlignCenter)
                self.slater_intermediate_Fx_vc_label.setFixedSize(80, 32)
                self.slater_intermediate_Fx_vc_text = QLineEdit(self.slater_intermediate_box)
                self.slater_intermediate_Fx_vc_text.setFixedSize(350, 32)

                self.slater_intermediate_Gx_vc_label = QLabel(self.slater_intermediate_box)
                self.slater_intermediate_Gx_vc_label.setAlignment(QtCore.Qt.AlignCenter)
                self.slater_intermediate_Gx_vc_label.setFixedSize(80, 32)
                self.slater_intermediate_Gx_vc_text = QLineEdit(self.slater_intermediate_box)
                self.slater_intermediate_Gx_vc_text.setFixedSize(350, 32)

                self.slater_intermediate_Fx_cc_label = QLabel(self.slater_intermediate_box)
                self.slater_intermediate_Fx_cc_label.setAlignment(QtCore.Qt.AlignCenter)
                self.slater_intermediate_Fx_cc_label.setFixedSize(80, 32)
                self.slater_intermediate_Fx_cc_text = QLineEdit(self.slater_intermediate_box)
                self.slater_intermediate_Fx_cc_text.setFixedSize(350, 32)

                slaterIntermediateBoxLayout = QGridLayout(self.slater_intermediate_box)
                slaterIntermediateBoxLayout.setAlignment(QtCore.Qt.AlignTop)
                slaterIntermediateBoxLayout.addWidget(self.slater_intermediate_Fx_vv_label, 0, 0, QtCore.Qt.AlignTop)
                slaterIntermediateBoxLayout.addWidget(self.slater_intermediate_Fx_vv_text, 0, 1, 1, 3,
                                                      QtCore.Qt.AlignTop)
                slaterIntermediateBoxLayout.addWidget(self.slater_intermediate_Fx_vc_label, 1, 0, QtCore.Qt.AlignTop)
                slaterIntermediateBoxLayout.addWidget(self.slater_intermediate_Fx_vc_text, 1, 1, 1, 3,
                                                      QtCore.Qt.AlignTop)
                slaterIntermediateBoxLayout.addWidget(self.slater_intermediate_Gx_vc_label, 2, 0, QtCore.Qt.AlignTop)
                slaterIntermediateBoxLayout.addWidget(self.slater_intermediate_Gx_vc_text, 2, 1, 1, 3,
                                                      QtCore.Qt.AlignTop)
                slaterIntermediateBoxLayout.addWidget(self.slater_intermediate_Fx_cc_label, 3, 0, QtCore.Qt.AlignTop)
                slaterIntermediateBoxLayout.addWidget(self.slater_intermediate_Fx_cc_text, 3, 1, 1, 3,
                                                      QtCore.Qt.AlignTop)

                self.slater_intermediate_box.setLayout(slaterIntermediateBoxLayout)

            if "external magnetic field >> stack_simple_parameters":
                self.Box_External_Magnetic_Field = QGroupBox(self.stack_simple_parameters)

                self.v1_ext_B_label = QLabel(self.Box_External_Magnetic_Field)
                self.v1_ext_B_label.setAlignment(QtCore.Qt.AlignCenter)
                self.v1_ext_B_label.setFixedSize(80, 42)

                self.v1_ext_B_texts = [QLineEdit(self.Box_External_Magnetic_Field),
                                       QLineEdit(self.Box_External_Magnetic_Field),
                                       QLineEdit(self.Box_External_Magnetic_Field)]
                for text in self.v1_ext_B_texts:
                    text.setFixedSize(70, 42)

                self.v1_on_which_label = QLabel(self.Box_External_Magnetic_Field)
                self.v1_on_which_label.setAlignment(QtCore.Qt.AlignCenter)
                self.v1_on_which_label.setFixedSize(160, 42)

                # self.v1_on_which_text = QLineEdit(self.Box_External_Magnetic_Field)
                # self.v1_on_which_text.setFixedSize(120,42)
                self.v1_on_which_combo = QComboBox(self.Box_External_Magnetic_Field)
                self.v1_on_which_combo.setFixedSize(100, 42)
                self.v1_on_which_combo.addItem("spin")  # 当选用某些频道但没有实现进行精确对角化则会报错,让用户先去进行相应的精确对角化
                self.v1_on_which_combo.addItem("orbital")
                self.v1_on_which_combo.addItem("both")
                self.v1_on_which_combo.setCurrentIndex(0)

                Box_External_Magnetic_Field_Layout = QHBoxLayout(self.Box_External_Magnetic_Field)
                Box_External_Magnetic_Field_Layout.setAlignment(QtCore.Qt.AlignTop)
                Box_External_Magnetic_Field_Layout.addWidget(self.v1_ext_B_label)
                for i in range(3):
                    Box_External_Magnetic_Field_Layout.addWidget(self.v1_ext_B_texts[i])
                Box_External_Magnetic_Field_Layout.addWidget(self.v1_on_which_label)
                # Box_External_Magnetic_Field_Layout.addWidget(self.v1_on_which_text)
                Box_External_Magnetic_Field_Layout.addWidget(self.v1_on_which_combo)

                self.Box_External_Magnetic_Field.setLayout(Box_External_Magnetic_Field_Layout)

            self.slater_parameter_tip_btn = QPushButton(self.stack_simple_parameters)
            # self.slater_parameter_tip_btn.setAlignment(QtCore.Qt.AlignCenter) # 按钮不能加这句否则会报错
            self.slater_parameter_tip_btn.setFixedHeight(42)
            self.slater_parameter_tip_btn.clicked.connect(self._handleOn_ShowTip_of_SlaterParameters)

            self.default_parameters_btn = QPushButton(self.stack_simple_parameters)
            # self.slater_parameter_tip_btn.setAlignment(QtCore.Qt.AlignCenter) # 按钮不能加这句否则会报错
            self.default_parameters_btn.setFixedHeight(42)
            self.default_parameters_btn.clicked.connect(self._handleOn_Set_Default_Parameters)
            self.reset_parameters_btn = QPushButton(self.stack_simple_parameters)
            self.reset_parameters_btn.setFixedHeight(42)
            self.reset_parameters_btn.clicked.connect(self._handleOn_ReSet_Parameters)
        except:
            self.informMsg("stack_simple_parameters的布局出现问题")

        HBOX = QHBoxLayout()
        HBOX.addWidget(self.slater_parameter_tip_btn)
        HBOX.addWidget(self.default_parameters_btn)
        HBOX.addWidget(self.reset_parameters_btn)

        stack_simple_parameters_Layout = QGridLayout(self.stack_simple_parameters)
        stack_simple_parameters_Layout.addWidget(self.Box_Atom_Information, 0, 0, 1, 2, QtCore.Qt.AlignTop)
        stack_simple_parameters_Layout.addLayout(HBOX, 1, 0, 1, 2, QtCore.Qt.AlignTop)
        stack_simple_parameters_Layout.addWidget(self.slater_initial_box, 2, 0, 1, 1, QtCore.Qt.AlignTop)
        stack_simple_parameters_Layout.addWidget(self.slater_intermediate_box, 2, 1, 1, 1, QtCore.Qt.AlignTop)
        stack_simple_parameters_Layout.addWidget(self.Box_External_Magnetic_Field, 3, 0, 1, 2, QtCore.Qt.AlignTop)
        self.stack_simple_parameters.setLayout(stack_simple_parameters_Layout)

    def create_stack_no_shell(self):
        # 水平布局
        layout = QHBoxLayout(self.stack_no_shell)
        # 添加控件到布局中
        layout.addWidget(QLabel('无内容显示'))
        self.stack_no_shell.setLayout(layout)

    def create_stack_s_shell(self):
        # 添加控件到布局中
        # 2*2的矩阵
        self.Box_s_matrix = QGroupBox(self.stack_s_shell)
        self.s_shell_texts = [[QLineEdit(self.Box_s_matrix) for _ in range(2)] for _ in range(2)]
        for row in self.s_shell_texts:
            for LineEdit in row:
                LineEdit.setFixedSize(60, 42)
        # 水平布局
        layout = QGridLayout(self.Box_s_matrix)
        layout.setAlignment(QtCore.Qt.AlignTop)
        self.arrange_matrix_on_box(layout, self.s_shell_texts)
        #
        stack_s_shell_layout = QHBoxLayout(self.stack_s_shell)
        stack_s_shell_layout.setAlignment(QtCore.Qt.AlignCenter)
        stack_s_shell_layout.addWidget(self.Box_s_matrix)
        self.stack_s_shell.setLayout(stack_s_shell_layout)

    def create_stack_p_or_t2g_shell(self):
        # 添加控件到布局中
        # 晶体场对称性选择
        if "point symmetry":
            self.Box_Point_Symmetry_p_or_t2g = QGroupBox(self.stack_p_or_t2g_shell)
            self.generate_cf_trigonal_t2g_btn = QPushButton(self.Box_Point_Symmetry_p_or_t2g)
            self.generate_cf_trigonal_t2g_btn.setFixedSize(150, 32)
            self.generate_cf_trigonal_t2g_btn.clicked.connect(self._handleOnGenerate_cf_trigonal_t2g)
            self.cf_trigonal_t2g_delta_label = QLabel(self.Box_Point_Symmetry_p_or_t2g)
            self.cf_trigonal_t2g_delta_label.setAlignment(QtCore.Qt.AlignCenter)
            self.cf_trigonal_t2g_delta_label.setFixedSize(80, 32)
            self.cf_trigonal_t2g_delta_text = QLineEdit(self.Box_Point_Symmetry_p_or_t2g)
            self.cf_trigonal_t2g_delta_text.setFixedSize(80, 32)

            self.generate_cf_tetragonal_t2g_btn = QPushButton(self.Box_Point_Symmetry_p_or_t2g)
            self.generate_cf_tetragonal_t2g_btn.setFixedSize(150, 32)
            self.generate_cf_tetragonal_t2g_btn.clicked.connect(self._handleOnGenerate_cf_tetragonal_t2g)
            self.cf_tetragonal_t2g_ten_dq_label = QLabel(self.Box_Point_Symmetry_p_or_t2g)
            self.cf_tetragonal_t2g_ten_dq_label.setAlignment(QtCore.Qt.AlignCenter)
            self.cf_tetragonal_t2g_ten_dq_label.setFixedSize(80, 32)
            self.cf_tetragonal_t2g_ten_dq_text = QLineEdit(self.Box_Point_Symmetry_p_or_t2g)
            self.cf_tetragonal_t2g_ten_dq_text.setFixedSize(80, 32)
            self.cf_tetragonal_t2g_d1_label = QLabel(self.Box_Point_Symmetry_p_or_t2g)
            self.cf_tetragonal_t2g_d1_label.setAlignment(QtCore.Qt.AlignCenter)
            self.cf_tetragonal_t2g_d1_label.setFixedSize(80, 32)
            self.cf_tetragonal_t2g_d1_text = QLineEdit(self.Box_Point_Symmetry_p_or_t2g)
            self.cf_tetragonal_t2g_d1_text.setFixedSize(80, 32)
            self.cf_tetragonal_t2g_d3_label = QLabel(self.Box_Point_Symmetry_p_or_t2g)
            self.cf_tetragonal_t2g_d3_label.setAlignment(QtCore.Qt.AlignCenter)
            self.cf_tetragonal_t2g_d3_label.setFixedSize(80, 32)
            self.cf_tetragonal_t2g_d3_text = QLineEdit(self.Box_Point_Symmetry_p_or_t2g)
            self.cf_tetragonal_t2g_d3_text.setFixedSize(80, 32)

            Box_Point_Symmetry_p_or_t2g_Layout = QGridLayout(self.Box_Point_Symmetry_p_or_t2g)
            Box_Point_Symmetry_p_or_t2g_Layout.addWidget(self.generate_cf_trigonal_t2g_btn, 0, 0, 1, 1,
                                                         QtCore.Qt.AlignTop)
            Box_Point_Symmetry_p_or_t2g_Layout.addWidget(self.cf_trigonal_t2g_delta_label, 0, 1, 1, 1,
                                                         QtCore.Qt.AlignTop)
            Box_Point_Symmetry_p_or_t2g_Layout.addWidget(self.cf_trigonal_t2g_delta_text, 0, 2, 1, 1,
                                                         QtCore.Qt.AlignTop)

            Box_Point_Symmetry_p_or_t2g_Layout.addWidget(self.generate_cf_tetragonal_t2g_btn, 1, 0, 1, 1,
                                                         QtCore.Qt.AlignTop)
            Box_Point_Symmetry_p_or_t2g_Layout.addWidget(self.cf_tetragonal_t2g_ten_dq_label, 1, 1, 1, 1,
                                                         QtCore.Qt.AlignTop)
            Box_Point_Symmetry_p_or_t2g_Layout.addWidget(self.cf_tetragonal_t2g_ten_dq_text, 1, 2, 1, 1,
                                                         QtCore.Qt.AlignTop)
            Box_Point_Symmetry_p_or_t2g_Layout.addWidget(self.cf_tetragonal_t2g_d1_label, 1, 3, 1, 1,
                                                         QtCore.Qt.AlignTop)
            Box_Point_Symmetry_p_or_t2g_Layout.addWidget(self.cf_tetragonal_t2g_d1_text, 1, 4, 1, 1, QtCore.Qt.AlignTop)
            Box_Point_Symmetry_p_or_t2g_Layout.addWidget(self.cf_tetragonal_t2g_d3_label, 1, 5, 1, 1,
                                                         QtCore.Qt.AlignTop)
            Box_Point_Symmetry_p_or_t2g_Layout.addWidget(self.cf_tetragonal_t2g_d3_text, 1, 6, 1, 1, QtCore.Qt.AlignTop)
            self.Box_Point_Symmetry_p_or_t2g.setLayout(Box_Point_Symmetry_p_or_t2g_Layout)

        # 6*6的矩阵
        if "matrix":
            self.Box_p_or_t2g_matrix = QGroupBox(self.stack_p_or_t2g_shell)
            self.p_or_t2g_shell_matrix_texts = [[QLineEdit(self.Box_p_or_t2g_matrix)
                                                 for _ in range(6)]
                                                for _ in range(6)]
            for row in self.p_or_t2g_shell_matrix_texts:
                for LineEdit in row:
                    LineEdit.setFixedSize(120, 42)
            Box_p_or_t2g_matrix_layout = QGridLayout(self.Box_p_or_t2g_matrix)
            self.arrange_matrix_on_box(Box_p_or_t2g_matrix_layout, self.p_or_t2g_shell_matrix_texts)

        # 垂直布局
        if "layout":
            layout = QVBoxLayout(self.stack_p_or_t2g_shell)
            layout.setAlignment(QtCore.Qt.AlignTop)
            layout.addWidget(self.Box_Point_Symmetry_p_or_t2g)
            layout.addWidget(self.Box_p_or_t2g_matrix)
            self.stack_p_or_t2g_shell.setLayout(layout)

    def create_stack_d_shell(self):
        # 添加控件到布局中
        # 晶体场对称性选择
        if "point symmetry":
            self.Box_Point_Symmetry_d = QGroupBox(self.stack_d_shell)
            self.generate_cf_cubic_d_btn = QPushButton(self.Box_Point_Symmetry_d)
            self.generate_cf_cubic_d_btn.setFixedSize(150, 32)
            self.generate_cf_cubic_d_btn.clicked.connect(self._handleOnGenerate_cf_cubic_d)
            self.cf_cubic_d_ten_dq_label = QLabel(self.Box_Point_Symmetry_d)
            self.cf_cubic_d_ten_dq_label.setAlignment(QtCore.Qt.AlignCenter)
            self.cf_cubic_d_ten_dq_label.setFixedSize(80, 32)
            self.cf_cubic_d_ten_dq_text = QLineEdit(self.Box_Point_Symmetry_d)
            self.cf_cubic_d_ten_dq_text.setFixedSize(80, 32)

            self.generate_cf_tetragonal_d_btn = QPushButton(self.Box_Point_Symmetry_d)
            self.generate_cf_tetragonal_d_btn.setFixedSize(150, 32)
            self.generate_cf_tetragonal_d_btn.clicked.connect(self._handleOnGenerate_cf_tetragonal_d)
            self.cf_tetragonal_d_ten_dq_label = QLabel(self.Box_Point_Symmetry_d)
            self.cf_tetragonal_d_ten_dq_label.setAlignment(QtCore.Qt.AlignCenter)
            self.cf_tetragonal_d_ten_dq_label.setFixedSize(80, 32)
            self.cf_tetragonal_d_ten_dq_text = QLineEdit(self.Box_Point_Symmetry_d)
            self.cf_tetragonal_d_ten_dq_text.setFixedSize(80, 32)
            self.cf_tetragonal_d_d1_label = QLabel(self.Box_Point_Symmetry_d)
            self.cf_tetragonal_d_d1_label.setAlignment(QtCore.Qt.AlignCenter)
            self.cf_tetragonal_d_d1_label.setFixedSize(80, 32)
            self.cf_tetragonal_d_d1_text = QLineEdit(self.Box_Point_Symmetry_d)
            self.cf_tetragonal_d_d1_text.setFixedSize(80, 32)
            self.cf_tetragonal_d_d3_label = QLabel(self.Box_Point_Symmetry_d)
            self.cf_tetragonal_d_d3_label.setAlignment(QtCore.Qt.AlignCenter)
            self.cf_tetragonal_d_d3_label.setFixedSize(80, 32)
            self.cf_tetragonal_d_d3_text = QLineEdit(self.Box_Point_Symmetry_d)
            self.cf_tetragonal_d_d3_text.setFixedSize(80, 32)

            self.generate_cf_square_planar_d_btn = QPushButton(self.Box_Point_Symmetry_d)
            self.generate_cf_square_planar_d_btn.setFixedSize(150, 32)
            self.generate_cf_square_planar_d_btn.clicked.connect(self._handleOnGenerate_cf_square_planar_d)
            self.cf_square_planar_d_ten_dq_label = QLabel(self.Box_Point_Symmetry_d)
            self.cf_square_planar_d_ten_dq_label.setAlignment(QtCore.Qt.AlignCenter)
            self.cf_square_planar_d_ten_dq_label.setFixedSize(80, 32)
            self.cf_square_planar_d_ten_dq_text = QLineEdit(self.Box_Point_Symmetry_d)
            self.cf_square_planar_d_ten_dq_text.setFixedSize(80, 32)
            self.cf_square_planar_d_ds_label = QLabel(self.Box_Point_Symmetry_d)
            self.cf_square_planar_d_ds_label.setAlignment(QtCore.Qt.AlignCenter)
            self.cf_square_planar_d_ds_label.setFixedSize(80, 32)
            self.cf_square_planar_d_ds_text = QLineEdit(self.Box_Point_Symmetry_d)
            self.cf_square_planar_d_ds_text.setFixedSize(80, 32)

            Box_Point_Symmetry_d_Layout = QGridLayout(self.Box_Point_Symmetry_d)
            Box_Point_Symmetry_d_Layout.addWidget(self.generate_cf_cubic_d_btn, 0, 0, 1, 1, QtCore.Qt.AlignTop)
            Box_Point_Symmetry_d_Layout.addWidget(self.cf_cubic_d_ten_dq_label, 0, 1, 1, 1, QtCore.Qt.AlignTop)
            Box_Point_Symmetry_d_Layout.addWidget(self.cf_cubic_d_ten_dq_text, 0, 2, 1, 1, QtCore.Qt.AlignTop)

            Box_Point_Symmetry_d_Layout.addWidget(self.generate_cf_tetragonal_d_btn, 1, 0, 1, 1, QtCore.Qt.AlignTop)
            Box_Point_Symmetry_d_Layout.addWidget(self.cf_tetragonal_d_ten_dq_label, 1, 1, 1, 1, QtCore.Qt.AlignTop)
            Box_Point_Symmetry_d_Layout.addWidget(self.cf_tetragonal_d_ten_dq_text, 1, 2, 1, 1, QtCore.Qt.AlignTop)
            Box_Point_Symmetry_d_Layout.addWidget(self.cf_tetragonal_d_d1_label, 1, 3, 1, 1, QtCore.Qt.AlignTop)
            Box_Point_Symmetry_d_Layout.addWidget(self.cf_tetragonal_d_d1_text, 1, 4, 1, 1, QtCore.Qt.AlignTop)
            Box_Point_Symmetry_d_Layout.addWidget(self.cf_tetragonal_d_d3_label, 1, 5, 1, 1, QtCore.Qt.AlignTop)
            Box_Point_Symmetry_d_Layout.addWidget(self.cf_tetragonal_d_d3_text, 1, 6, 1, 1, QtCore.Qt.AlignTop)

            Box_Point_Symmetry_d_Layout.addWidget(self.generate_cf_square_planar_d_btn, 2, 0, 1, 1, QtCore.Qt.AlignTop)
            Box_Point_Symmetry_d_Layout.addWidget(self.cf_square_planar_d_ten_dq_label, 2, 1, 1, 1, QtCore.Qt.AlignTop)
            Box_Point_Symmetry_d_Layout.addWidget(self.cf_square_planar_d_ten_dq_text, 2, 2, 1, 1, QtCore.Qt.AlignTop)
            Box_Point_Symmetry_d_Layout.addWidget(self.cf_square_planar_d_ds_label, 2, 3, 1, 1, QtCore.Qt.AlignTop)
            Box_Point_Symmetry_d_Layout.addWidget(self.cf_square_planar_d_ds_text, 2, 4, 1, 1, QtCore.Qt.AlignTop)
            self.Box_Point_Symmetry_p_or_t2g.setLayout(Box_Point_Symmetry_d_Layout)

        # 10*10的矩阵
        if "matrixs":
            self.Box_d_matrix = QGroupBox(self.stack_d_shell)
            self.d_shell_matrix_texts = [[QLineEdit(self.stack_d_shell)
                                          for _ in range(10)]
                                         for _ in range(10)]
            for row in self.d_shell_matrix_texts:
                for LineEdit in row:
                    LineEdit.setFixedSize(65, 25)
            # 网格布局
            Box_d_matrix_layout = QGridLayout(self.Box_d_matrix)
            self.arrange_matrix_on_box(Box_d_matrix_layout, self.d_shell_matrix_texts)

        # 垂直布局
        if "layout":
            layout = QVBoxLayout(self.stack_d_shell)
            layout.setAlignment(QtCore.Qt.AlignTop)
            layout.addWidget(self.Box_Point_Symmetry_d)
            layout.addWidget(self.Box_d_matrix)
            self.stack_d_shell.setLayout(layout)

    def create_stack_f_shell(self):
        # 添加控件到布局中
        # 晶体场对称性选择
        self.Box_Point_Symmetry_f = QGroupBox(self.stack_f_shell)
        # to do list:f轨道的点群对称性
        Box_Point_Symmetry_d_Layout = QGridLayout(self.Box_Point_Symmetry_d)

        self.Box_Point_Symmetry_p_or_t2g.setLayout(Box_Point_Symmetry_d_Layout)

        # 14*14的矩阵
        self.Box_f_matrix = QGroupBox(self.stack_f_shell)
        self.f_shell_matrix_texts = [[QLineEdit(self.stack_f_shell)
                                      for _ in range(14)]
                                     for _ in range(14)]
        for row in self.f_shell_matrix_texts:
            for LineEdit in row:
                LineEdit.setFixedSize(50, 36)

        # 水平布局
        Box_f_matrix_layout = QGridLayout(self.Box_f_matrix)
        self.arrange_matrix_on_box(Box_f_matrix_layout, self.f_shell_matrix_texts)

        # 垂直布局
        layout = QVBoxLayout(self.stack_f_shell)
        layout.setAlignment(QtCore.Qt.AlignTop)
        layout.addWidget(self.Box_Point_Symmetry_f)
        layout.addWidget(self.Box_f_matrix)
        self.stack_f_shell.setLayout(layout)

    def return_stack_index_of_crystal_field(self) -> int:
        v_name = super()._getDataFromInupt("v_name")
        if v_name == None:
            print(v_name)
            self.informMsg("请先输入正确的价电子壳层名称")
            return 1

        shell_name_v_list = re.findall(r'(s|p|t2g|d|f)', v_name)
        if shell_name_v_list == []:
            print(v_name)
            self.informMsg("请先输入正确的价电子壳层名称")
            return 1
        else:
            shell_name_v = shell_name_v_list[0]
            if shell_name_v == "s":
                return 2
            if shell_name_v == "p" or shell_name_v == "t2g":
                return 3
            if shell_name_v == "d":
                return 4
            if shell_name_v == "f":
                return 5

    def create_stack_other_matrixs(self):
        # 水平布局
        layout = QHBoxLayout(self.stack_other_matrix)
        # 添加控件到布局中
        layout.addWidget(QLabel('无内容显示'))
        self.stack_other_matrix.setLayout(layout)

    def stack_display(self, i):  # i是QStackedWidget的当前的Index,必须在函数中加上这个形参
        # 设置当前可见的选项卡的索引
        if i == 0:
            self.stack.setCurrentIndex(0)
        elif i == 1:  # 当用户想去写晶体场矩阵时
            k = self.return_stack_index_of_crystal_field()
            self.stack.setCurrentIndex(k)
            self.current_index = k
        elif i == 2:
            self.stack.setCurrentIndex(6)
            self.informMsg("not implemented yet")

    def _retranslateAll(self):
        self._retranslateTips()
        self._retranslateNames()

    def _retranslateTips(self):
        _translate = QtCore.QCoreApplication.translate
        if "atom_simple_parameters":
            self.atom_name_text.setToolTip(
                _translate("FirstFrame_atom_name_text_tip", "请输入元素名称"))
            self.atom_name_text.setPlaceholderText(
                _translate("FirstFrame_atom_name_text_sample", "例:Cu"))
            self.atom_name_text.setText(
                _translate("FirstFrame_atom_name_text", ""))
            self.v_name_text.setToolTip(
                _translate("FirstFrame_v_name_text_tip", "请输入价电子壳层的名称"))
            self.v_name_text.setPlaceholderText(
                _translate("FirstFrame_v_name_text_sample", "例:3d"))
            self.v_name_text.setText(
                _translate("FirstFrame_v_name_text", ""))
            self.v_noccu_text.setToolTip(
                _translate("FirstFrame_v_noccu_text_tip", "请输入价电子壳层的电子数目"))
            self.v_noccu_text.setPlaceholderText(
                _translate("FirstFrame_v_noccu_text_sample", "例:10"))
            self.v_noccu_text.setText(
                _translate("FirstFrame_v_noccu_text", ""))
            self.c_name_text.setToolTip(
                _translate("FirstFrame_c_name_text_tip", "请输入芯电子壳层的名称"))
            self.c_name_text.setPlaceholderText(
                _translate("FirstFrame_c_name_text_sample", "例:1s"))
            self.c_name_text.setText(
                _translate("FirstFrame_c_name_text", ""))
            self.c_noccu_text.setToolTip(
                _translate("FirstFrame_c_noccu_text_tip", "请输入芯电子壳层的电子数目"))
            self.c_noccu_text.setText(
                _translate("FirstFrame_c_noccu_text", ""))
            self.c_noccu_text.setPlaceholderText(
                _translate("FirstFrame_c_noccu_text_sample", "例:1"))
            self.v_soc_text.setToolTip(
                _translate("FirstFrame_v_soc_text_tip", "请分别输入价电子初始态和中间态的SOC(initial, intermediate)"))
            self.v_soc_text.setPlaceholderText(
                _translate("FirstFrame_v_soc_text_sample", "例:0.1;0.1"))
            self.v_soc_text.setText(
                _translate("FirstFrame_v_soc_text", ""))
            self.c_soc_text.setToolTip(
                _translate("FirstFrame_c_soc_text_tip", "请输入芯电子的SOC"))
            self.c_soc_text.setPlaceholderText(
                _translate("FirstFrame_c_soc_text_sample", "例:0.0"))
            self.c_soc_text.setText(
                _translate("FirstFrame_c_soc_text", ""))
            self.gamma_c_text.setToolTip(_translate("SecondFrame_gamma_c", "core-hole lifetime"))
            self.gamma_c_text.setPlaceholderText(_translate("SecondFrame_gamma_c", "例:0.1"))
            self.gamma_c_text.setText(_translate("SecondFrame_gamma_c_text", ""))
            self.gamma_f_text.setToolTip(_translate("SecondFrame_gamma_f", "final-state lifetime"))
            self.gamma_f_text.setText(_translate("SecondFrame_gamma_f", "例:0.1"))
            self.gamma_f_text.setText(_translate("SecondFrame_gamma_f_text", ""))

            self.shell_level_v_text.setToolTip(
                _translate("FirstFrame_shell_level_v_text_tip", "请输入价电子能级"))
            self.shell_level_v_text.setPlaceholderText(
                _translate("FirstFrame_shell_level_v_text_sample", "例:0.1"))
            self.shell_level_v_text.setText(
                _translate("FirstFrame_shell_level_v_text", ""))
            self.shell_level_c_text.setToolTip(
                _translate("FirstFrame_shell_level_c_text_tip", "请输入芯电子能级"))
            self.shell_level_c_text.setPlaceholderText(
                _translate("FirstFrame_shell_level_c_text_sample", "例:0.1"))
            self.shell_level_c_text.setText(
                _translate("FirstFrame_shell_level_c_text", ""))

            self.slater_initial_Fx_vv_text.setToolTip(
                _translate("FirstFrame_slater_initial_Fx_vv_text_tip", "两个价电子之间的Slater_integrals"))
            self.slater_initial_Fx_vv_text.setPlaceholderText(
                _translate("FirstFrame_slater_initial_Fx_vv_text_sample", "例:1.2;1.2;..."))
            self.slater_initial_Fx_vv_text.setText(
                _translate("FirstFrame_slater_initial_Fx_vv_text", ""))
            self.slater_initial_Fx_vc_text.setToolTip(
                _translate("FirstFrame_slater_initial_Fx_vc_text_tip", "价电子与芯电子之间的Slater_integrals"))
            self.slater_initial_Fx_vc_text.setPlaceholderText(
                _translate("FirstFrame_slater_initial_Fx_vc_text_sample", "例:1.2;1.2;..."))
            self.slater_initial_Fx_vc_text.setText(
                _translate("FirstFrame_slater_initial_Fx_vc_text", ""))
            self.slater_initial_Gx_vc_text.setToolTip(
                _translate("FirstFrame_slater_initial_Gx_vc_text_tip", "价电子与芯电子之间的Slater_integrals(exchange)"))
            self.slater_initial_Gx_vc_text.setPlaceholderText(
                _translate("FirstFrame_slater_initial_Gx_vc_text_sample", "例:1.2;1.2;..."))
            self.slater_initial_Gx_vc_text.setText(
                _translate("FirstFrame_slater_initial_Gx_vc_text", ""))
            self.slater_initial_Fx_cc_text.setToolTip(
                _translate("FirstFrame_slater_initial_Fx_cc_text_tip", "两个芯电子之间的Slater_integrals"))
            self.slater_initial_Fx_cc_text.setPlaceholderText(
                _translate("FirstFrame_slater_initial_Fx_cc_text_sample", "例:1.2;1.2-..."))
            self.slater_initial_Fx_cc_text.setText(
                _translate("FirstFrame_slater_initial_Fx_cc_text", ""))

            self.slater_intermediate_Fx_vv_text.setToolTip(
                _translate("FirstFrame_slater_intermediate_Fx_vv_text_tip", ""))
            self.slater_intermediate_Fx_vv_text.setPlaceholderText(
                _translate("FirstFrame_slater_intermediate_Fx_vv_text_sample", "例:1.2;1.2-..."))
            self.slater_intermediate_Fx_vv_text.setText(
                _translate("FirstFrame_slater_intermediate_Fx_vv_text", ""))
            self.slater_intermediate_Fx_vc_text.setToolTip(
                _translate("FirstFrame_slater_intermediate_Fx_vc_text_tip", ""))
            self.slater_intermediate_Fx_vc_text.setPlaceholderText(
                _translate("FirstFrame_slater_intermediate_Fx_vc_text_sample", "例:1.2;1.2-..."))
            self.slater_intermediate_Fx_vc_text.setText(
                _translate("FirstFrame_slater_intermediate_Fx_vc_text", ""))
            self.slater_intermediate_Gx_vc_text.setToolTip(
                _translate("FirstFrame_slater_intermediate_Gx_vc_text_tip", ""))
            self.slater_intermediate_Gx_vc_text.setPlaceholderText(
                _translate("FirstFrame_slater_intermediate_Gx_vc_text_sample", "例:1.2;1.2-..."))
            self.slater_intermediate_Gx_vc_text.setText(
                _translate("FirstFrame_slater_intermediate_Gx_vc_text", ""))
            self.slater_intermediate_Fx_cc_text.setToolTip(
                _translate("FirstFrame_slater_intermediate_Fx_cc_text_tip", ""))
            self.slater_intermediate_Fx_cc_text.setPlaceholderText(
                _translate("FirstFrame_slater_intermediate_Fx_cc_text_sample", "例:1.2;1.2;..."))
            self.slater_intermediate_Fx_cc_text.setText(
                _translate("FirstFrame_slater_intermediate_Fx_cc_text", ""))

            self.default_parameters_btn.setToolTip(
                _translate("FirstFrame_default_parameters_btn_sample", "设置默认值"))
            self.reset_parameters_btn.setToolTip(
                _translate("FirstFrame_default_parameters_btn_sample", "重置"))
            self.slater_parameter_tip_btn.setToolTip(
                _translate("FirstFrame_slater_parameter_tip_btn_sample", "告诉用户应该每种类型的Slater参数应该输入几个"))

            for text in self.v1_ext_B_texts:
                text.setToolTip(
                    _translate("FirstFrame_v1_ext_B_texts_tip", ""))
                text.setPlaceholderText(
                    _translate("FirstFrame_v1_ext_B_texts_sample", "例:1.0"))
                text.setText(
                    _translate("FirstFrame_v1_ext_B_texts", ""))

            self.v1_on_which_combo.setToolTip(
                _translate("FirstFrame_v1_on_which_text_tip", "请选择外磁场作用的自由度"))
            self.v1_on_which_combo.setCurrentIndex(0)
            for row in self.local_axis_texts:
                for lineEdit in row:
                    lineEdit.setToolTip(
                        _translate("FirstFrame_local_axis_texts_tip", ""))
                    lineEdit.setPlaceholderText(
                        _translate("FirstFrame_local_axis_texts_sample", "例:1.0"))
                    lineEdit.setText(
                        _translate("FirstFrame_local_axis_texts", ""))

        if "add to list":
            self.buttonAddToAtomList.setToolTip(
                _translate("FirstFrame_add_to_atom_list_button_tip", "添加到列表中"))

            self.atom_list_menu_import_action.setToolTip(  # 这个好像没用
                _translate("FirstFrame_atom_list_menu_import_action_tip", "导入选中元素"))
            self.atom_list_menu_delete_action.setToolTip(  # 这个好像没用
                _translate("FirstFrame_atom_list_menu_delete_action_tip", "删除选中元素"))

            self.atom_list_save_button.setToolTip(
                _translate("FirstFrame_atom_list_save_button_tip", "保存列表"))
            self.atom_list_load_button.setToolTip(
                _translate("FirstFrame_atom_list_load_button_tip", "加载列表"))

        if "s_shell":
            self.Box_s_matrix.setToolTip(
                _translate("FirstFrame_Box_s_matrix_tip", "请输入一个具有自旋简并度的厄米矩阵:其实s_轨道没有必要写,只是能级的整体平移"))
            for row in self.s_shell_texts:
                for text in row:
                    text.setText("")

        if "p_or_t2g_shell":
            self.Box_Point_Symmetry_p_or_t2g.setToolTip(
                _translate("FirstFrame_Box_Point_Symmetry_p_or_t2g_tip", "可以选择某种点群对称性,"))
            self.generate_cf_trigonal_t2g_btn.setToolTip(
                _translate("FirstFrame_generate_cf_trigonal_t2g_btn_tip", "点击按钮生成相应的矩阵"))
            self.cf_trigonal_t2g_delta_text.setToolTip(
                _translate("FirstFrame_cf_trigonal_t2g_delta_text_tip", "请输入参数delta"))

            self.generate_cf_tetragonal_t2g_btn.setToolTip(
                _translate("FirstFrame_generate_cf_tetragonal_t2g_btn_tip", "点击按钮生成相应的矩阵"))
            self.cf_tetragonal_t2g_ten_dq_text.setToolTip(
                _translate("FirstFrame_cf_tetragonal_t2g_ten_dq_label", "请输入参数ten_dq"))
            self.cf_tetragonal_t2g_d1_text.setToolTip(
                _translate("FirstFrame_cf_tetragonal_t2g_d1_label", "请输入参数d1"))
            self.cf_tetragonal_t2g_d3_text.setToolTip(
                _translate("FirstFrame_cf_tetragonal_t2g_d3_label", "请输入参数d3"))
            self.Box_p_or_t2g_matrix.setToolTip(
                _translate("FirstFrame_Box_p_or_t2g_matrix_tip", "请输入一个具有自旋简并度的厄米矩阵"))
            for row in self.p_or_t2g_shell_matrix_texts:
                for text in row:
                    text.setText("")

        if "d_shell":
            self.Box_Point_Symmetry_d.setToolTip(
                _translate("FirstFrame_Box_Point_Symmetry_d_tip", "可以选择某种点群对称性,"))
            self.generate_cf_cubic_d_btn.setToolTip(
                _translate("FirstFrame_generate_cf_cubic_d_btn_tip", "点击按钮生成相应的矩阵"))
            self.cf_cubic_d_ten_dq_text.setToolTip(
                _translate("FirstFrame_cf_cubic_d_ten_dq_text_tip", "请输入参数ten_dq"))

            self.generate_cf_tetragonal_d_btn.setToolTip(
                _translate("FirstFrame_generate_cf_tetragonal_d_btn_tip", "点击按钮生成相应的矩阵"))
            self.cf_tetragonal_d_ten_dq_text.setToolTip(
                _translate("FirstFrame_cf_tetragonal_d_ten_dq_text", "请输入参数ten_dq"))
            self.cf_tetragonal_d_d1_text.setToolTip(
                _translate("FirstFrame_cf_tetragonal_d_d1_text", "请输入参数d1"))
            self.cf_tetragonal_d_d3_text.setToolTip(
                _translate("FirstFrame_cf_tetragonal_d_d3_text", "请输入参数d3"))

            self.generate_cf_square_planar_d_btn.setToolTip(
                _translate("FirstFrame_generate_cf_tetragonal_d_btn_tip", "点击按钮生成相应的矩阵"))
            self.cf_square_planar_d_ten_dq_text.setToolTip(
                _translate("FirstFrame_cf_square_planar_d_ten_dq_text", "请输入参数ten_dq"))
            self.cf_square_planar_d_ds_text.setToolTip(
                _translate("FirstFrame_cf_square_planar_d_ds_text", "请输入参数d1"))
            self.Box_d_matrix.setToolTip(
                _translate("FirstFrame_Box_d_matrix_tip", "请输入一个具有自旋简并度的厄米矩阵"))
            for row in self.d_shell_matrix_texts:
                for text in row:
                    text.setText("")

        if "f_shell":
            self.Box_f_matrix.setToolTip(
                _translate("FirstFrame_Box_f_matrix_tip", "请输入一个具有自旋简并度的厄米矩阵"))
            for row in self.f_shell_matrix_texts:
                for text in row:
                    text.setText("")

        if "exact diagonalization":
            self.verbose_text.setToolTip(
                _translate("FirstFrame_verbose_text_tip", "是否将哈密顿量写入文件"))
            self.verbose_text.setPlaceholderText(
                _translate("FirstFrame_verbose_text_sample", "请输入0或1"))

            self.ed_combo.setToolTip(
                _translate("FirstFrame_ed_combo_tip", "选择精确对角化的工具"))
            self.ed_calculation_button.setToolTip(
                _translate("FirstFrame_ed_calculation_button_tip", "进行精确对角化计算"))
            self.ed_show_button.setToolTip(
                _translate("FirstFrame_ed_show_button_tip", "显示精确对角化的结果图"))
            self.gs_list_text.setToolTip(
                _translate("FirstFrame_gs_list_text_tip", "请输入初始态的截断指标"))
            self.gs_list_text.setPlaceholderText(
                _translate("FirstFrame_gs_list_text_sample", "例如:2"))

    def _retranslateNames(self):
        _translate = QtCore.QCoreApplication.translate
        if "atom_simple_paramters":
            self.Box_Atom_Information.setTitle(
                _translate("FirstFrame_atom_information_box", "atom_basic_info"))
            self.atom_name_label.setText(
                _translate("FirstFrame_atom_name_label", "atom_name"))
            self.v_name_label.setText(
                _translate("FirstFrame_v_name_label", "v_name"))
            self.v_noccu_label.setText(
                _translate("FirstFrame_v_noccu_label", "v_noccu"))
            self.c_name_label.setText(
                _translate("FirstFrame_c_name_label", "c_name"))
            self.c_noccu_label.setText(
                _translate("FirstFrame_c_noccu_label", "c_noccu"))
            self.v_soc_label.setText(
                _translate("FirstFrame_v_soc_label", "v_soc"))
            self.c_soc_label.setText(
                _translate("FirstFrame_c_soc_label", "c_soc"))
            self.shell_level_v_label.setText(
                _translate("FirstFrame_shell_level_v_label", "shell_level_v"))
            self.shell_level_c_label.setText(
                _translate("FirstFrame_shell_level_c_label", "shell_level_c"))
            self.gamma_c_label.setText(_translate("FirstFrame_gamma_c_label", "gamma_c"))
            self.gamma_f_label.setText(_translate("FirstFrame_gamma_f_label", "gamma_f"))

            self.slater_initial_box.setTitle(
                _translate("FirstFrame_slater_initial_box_title", "vc_slater_integrals_initial"))
            self.slater_initial_Fx_vv_label.setText(
                _translate("FirstFrame_slater_initial_Fx_vv_label", "Fx_vv"))
            self.slater_initial_Fx_vc_label.setText(
                _translate("FirstFrame_slater_initial_Fx_vc_label", "Fx_vc"))
            self.slater_initial_Gx_vc_label.setText(
                _translate("FirstFrame_slater_initial_Gx_vc_label", "Gx_vc"))
            self.slater_initial_Fx_cc_label.setText(
                _translate("FirstFrame_slater_initial_Fx_cc_label", "Fx_cc"))

            self.slater_intermediate_box.setTitle(
                _translate("FirstFrame_slater_intermediate_box_title", "vc_slater_integrals_intermediate"))
            self.slater_intermediate_Fx_vv_label.setText(
                _translate("FirstFrame_slater_intermediate_Fx_vv_label", "Fx_vv"))
            self.slater_intermediate_Fx_vc_label.setText(
                _translate("FirstFrame_slater_intermediate_Fx_vc_label", "Fx_vc"))
            self.slater_intermediate_Gx_vc_label.setText(
                _translate("FirstFrame_slater_intermediate_Gx_vc_label", "Gx_vc"))
            self.slater_intermediate_Fx_cc_label.setText(
                _translate("FirstFrame_slater_intermediate_Fx_cc_label", "Fx_cc"))

            self.slater_parameter_tip_btn.setText(
                _translate("FirstFrame_slater_parameter_tip_btn_text", "Tips on How to enter slater parameters"))
            self.default_parameters_btn.setText(
                _translate("FirstFrame_default_parameters_btn_text", "SET Default Parameters"))
            self.reset_parameters_btn.setText(
                _translate("FirstFrame_default_parameters_btn_text", "RESET Parameters"))

        if "local_axis":
            self.Box_Local_Axis.setTitle(
                _translate("FirstFrame_Box_Local_Axis_title", "local_axis"))
            self.Box_External_Magnetic_Field.setTitle(
                _translate("FirstFrame_Box_Local_Axis_title", "external_magnetic_field"))
            self.v1_ext_B_label.setText(
                _translate("FirstFrame_v1_ext_B_label", "Field"))
            self.v1_on_which_label.setText(
                _translate("FirstFrame_v1_on_which_label", "v1_on_which"))

        if "atom_list":
            self.buttonAddToAtomList.setText(
                _translate("FirstFrame_add_to_atom_list_button_label", "Add"))
            self.buttonCheckInput.setText(
                _translate("FirstFrame_add_to_atom_list_button_label", "Check"))
            self.atom_list_menu_import_action.setText(
                _translate("FirstFrame_atom_list_menu_import_action_name", "import"))
            self.atom_list_menu_delete_action.setText(
                _translate("FirstFrame_atom_list_menu_delete_action_name", "delete"))
            self.atom_list_save_button.setText(
                _translate("FirstFrame_atom_list_save_button_label", "save"))
            self.atom_list_load_button.setText(
                _translate("FirstFrame_atom_list_load_button_label", "load"))

        if "s_shell":
            self.Box_s_matrix.setTitle(
                _translate("FirstFrame_Box_s_matrix_title", "s_shell_crystal_field_matrix"))

        if "p_or_t2g_shell":
            self.Box_Point_Symmetry_p_or_t2g.setTitle(
                _translate("FirstFrame_Box_Point_Symmetry_p_or_t2g_title", "point symmetry"))
            self.generate_cf_trigonal_t2g_btn.setText(
                _translate("FirstFrame_generate_p_or_t2g_matrix_btn_text", 'trigonal_t2g'))
            self.cf_trigonal_t2g_delta_label.setText(
                _translate("FirstFrame_cf_trigonal_t2g_delta_label", "delta"))

            self.generate_cf_tetragonal_t2g_btn.setText(
                _translate("FirstFrame_cf_tetragonal_t2g_checkbox_text", "tetragonal_t2g"))
            self.cf_tetragonal_t2g_ten_dq_label.setText(
                _translate("FirstFrame_cf_tetragonal_t2g_ten_dq_label", "ten_dq"))
            self.cf_tetragonal_t2g_d1_label.setText(
                _translate("FirstFrame_cf_tetragonal_t2g_d1_label", "d1"))
            self.cf_tetragonal_t2g_d3_label.setText(
                _translate("FirstFrame_cf_tetragonal_t2g_d3_label", "d1"))
            self.Box_p_or_t2g_matrix.setTitle(
                _translate("FirstFrame_Box_p_or_t2g_matrix_title", "p_or_t2g_shell_crystal_field_matrix"))

        if "d_shell":
            self.Box_Point_Symmetry_d.setTitle(
                _translate("FirstFrame_Box_Point_Symmetry_d_title", "point symmetry"))
            self.generate_cf_cubic_d_btn.setText(
                _translate("FirstFrame_generate_d_matrix_btn_text", "cubic_d"))
            self.cf_cubic_d_ten_dq_label.setText(
                _translate("FirstFrame_cf_cubic_d_ten_dq_label", "ten_dq"))

            self.generate_cf_tetragonal_d_btn.setText(
                _translate("FirstFrame_generate_cf_tetragonal_d_btn_text", "tetragonal_d"))
            self.cf_tetragonal_d_ten_dq_label.setText(
                _translate("FirstFrame_cf_tetragonal_d_ten_dq_label", "ten_dq"))
            self.cf_tetragonal_d_d1_label.setText(
                _translate("FirstFrame_cf_tetragonal_d_d1_label", "d1"))
            self.cf_tetragonal_d_d3_label.setText(
                _translate("FirstFrame_cf_tetragonal_d_d3_label", "d3"))

            self.generate_cf_square_planar_d_btn.setText(
                _translate("FirstFrame_generate_cf_square_planar_d_btn_text", "square_planar_d"))
            self.cf_square_planar_d_ten_dq_label.setText(
                _translate("FirstFrame_cf_square_planar_d_ten_dq_label", "ten_dq"))
            self.cf_square_planar_d_ds_label.setText(
                _translate("FirstFrame_cf_square_planar_d_ds_label", "ds"))
            self.Box_d_matrix.setTitle(
                _translate("FirstFrame_Box_d_matrix_title", "d_shell_crystal_field_matrix"))

        if "exact diagonalization":
            self.exact_diag_box.setTitle(
                _translate("FirstFrame_exact_diag_box", "exact_diagonalization"))
            self.verbose_label.setText(
                _translate("FirstFrame_verbose_label", "verbose"))

            # self.channel_box.setTitle(
            #     _translate("FirstFrame_channel_box_title", "diagonalize and compute"))

            self.ed_calculation_button.setText(
                _translate("FirstFrame_ed_calculation_button_label", "RUN"))

            self.firstPageOutputBox.setTitle(
                _translate("FirstFrame_firstPageOutputBox_title", "ed_output"))
            self.ed_show_button.setText(
                _translate("FirstFrame_ed_show_button_text", "ed_show"))
            self.gs_list_label.setText(
                _translate("FirstFrame_gs_list_label", "gs_list"))

    def _textInputRestrict(self):
        if "stack_simple_parameters":
            self.atom_name_text.setValidator(self.ncRegxValidator)  # 元素名也用这个吧
            v_nameRegx = QtCore.QRegExp(r'([1-9]{1}s|[2-9]{1}p|[3-9]{1}t2g|[3-9]{1}d|[4-9]{1}f)')
            v_nameRegValidator = QtGui.QRegExpValidator(v_nameRegx, self.frame)
            c_nameRegx = QtCore.QRegExp(
                r'([1-9]s|[2-9]p12|[2-9]p32|[2-9]p|[3-9]d32|[3-9]d52|[3-9]d|[4-9]f72|[4-9]f52|[4-9]f)')
            c_nameRegValidator = QtGui.QRegExpValidator(c_nameRegx, self.frame)

            self.v_name_text.setValidator(v_nameRegValidator)
            self.c_name_text.setValidator(c_nameRegValidator)

            v_noccuRegx = QtCore.QRegExp(r"1[0-4]|[0-9]")
            v_noccuRegxValidator = QtGui.QRegExpValidator(v_noccuRegx, self.frame)
            self.v_noccu_text.setValidator(v_noccuRegxValidator)
            self.c_noccu_text.setValidator(v_noccuRegxValidator)

            self.v_soc_text.setValidator(self.twoFloatRegxValidator)
            self.c_soc_text.setValidator(self.floatRegxValidator)
            self.shell_level_v_text.setValidator(self.floatRegxValidator)
            self.shell_level_c_text.setValidator(self.floatRegxValidator)
            self.gamma_c_text.setValidator(self.floatRegxValidator)
            self.gamma_f_text.setValidator(self.floatRegxValidator)

            self.slater_initial_Fx_vv_text.setValidator(self.floatListRegxValidator)
            self.slater_initial_Fx_vc_text.setValidator(self.floatListRegxValidator)
            self.slater_initial_Gx_vc_text.setValidator(self.floatListRegxValidator)
            self.slater_initial_Fx_cc_text.setValidator(self.floatListRegxValidator)
            self.slater_intermediate_Fx_vv_text.setValidator(self.floatListRegxValidator)
            self.slater_intermediate_Fx_vc_text.setValidator(self.floatListRegxValidator)
            self.slater_intermediate_Gx_vc_text.setValidator(self.floatListRegxValidator)
            self.slater_intermediate_Fx_cc_text.setValidator(self.floatListRegxValidator)

            for text in self.v1_ext_B_texts:
                text.setValidator(self.floatRegxValidator)
            # forOnWhichRegx = QtCore.QRegExp(r"spin|orbital|both")
            # forOnWhichRegxValidator = QtGui.QRegExpValidator(forOnWhichRegx, self.frame)

        if "s_shell":
            for row in self.s_shell_texts:  # 这里只是初始化，后续如果更新矩阵的话要重新设置一遍
                for lineEdit in row:
                    lineEdit.setValidator(self.complexRegxValidator)

        if "p_or_t2g_shell":
            self.cf_trigonal_t2g_delta_text.setValidator(self.floatRegxValidator)
            self.cf_tetragonal_t2g_ten_dq_text.setValidator(self.floatRegxValidator)
            self.cf_tetragonal_t2g_d1_text.setValidator(self.floatRegxValidator)
            self.cf_tetragonal_t2g_d3_text.setValidator(self.floatRegxValidator)
            for row in self.p_or_t2g_shell_matrix_texts:  # 这里只是初始化，后续如果更新矩阵的话要重新设置一遍
                for lineEdit in row:
                    lineEdit.setValidator(self.complexRegxValidator)

        if "d_shell":
            self.cf_cubic_d_ten_dq_text.setValidator(self.floatRegxValidator)
            self.cf_tetragonal_d_ten_dq_text.setValidator(self.floatRegxValidator)
            self.cf_tetragonal_d_d1_text.setValidator(self.floatRegxValidator)
            self.cf_tetragonal_d_d3_text.setValidator(self.floatRegxValidator)
            self.cf_square_planar_d_ten_dq_text.setValidator(self.floatRegxValidator)
            self.cf_square_planar_d_ds_text.setValidator(self.floatRegxValidator)
            for row in self.d_shell_matrix_texts:  # 这里只是初始化，后续如果更新矩阵的话要重新设置一遍
                for lineEdit in row:
                    lineEdit.setValidator(self.complexRegxValidator)

        if "f_shell":
            for row in self.f_shell_matrix_texts:  # 这里只是初始化，后续如果更新矩阵的话要重新设置一遍
                for lineEdit in row:
                    lineEdit.setValidator(self.complexRegxValidator)

        if "local_axis":
            for row in self.local_axis_texts:
                for lineEdit in row:
                    lineEdit.setValidator(self.floatRegxValidator)

        if "exact_diagonalization":
            verboseRegx = QtCore.QRegExp(r"0|1")
            verboseRegxValidator = QtGui.QRegExpValidator(verboseRegx, self.frame)
            self.verbose_text.setValidator(verboseRegxValidator)
            self.gs_list_text.setValidator(self.npRegxValidator)

    def _arrangeDataInWidgets(self):
        # 在各个页面都设置好之后调用这个,把各个需要获取输入的控件(或其上数据)加入字典中，同时指定解析方式,方便之后从界面获取输入
        # 由于每个输入都被正则表达式所限制
        if "stack_simple_parameters":
            super()._bindDataWithWidgets("atom_name", self.atom_name_text, self._toSimpleStrFromText)
            super()._bindDataWithWidgets("v_name", self.v_name_text, self._toSimpleStrFromText)
            super()._bindDataWithWidgets("v_noccu", self.v_noccu_text, self._toIntFromText)
            super()._bindDataWithWidgets("c_name", self.c_name_text, self._toSimpleStrFromText)
            super()._bindDataWithWidgets("c_noccu", self.c_noccu_text, self._toIntFromText)
            super()._bindDataWithWidgets("v_soc", self.v_soc_text,
                                         self._toFloatListByStrFromText)  # float-float, (initial, optional[imtermediate])
            super()._bindDataWithWidgets("c_soc", self.c_soc_text, self._toFloatFromText)
            super()._bindDataWithWidgets("shell_level_v", self.shell_level_v_text, self._toFloatFromText)
            super()._bindDataWithWidgets("shell_level_c", self.shell_level_c_text, self._toFloatFromText)
            super()._bindDataWithWidgets("atom_name", self.atom_name_text, self._toSimpleStrFromText)
            super()._bindDataWithWidgets("gamma_c", self.gamma_c_text, self._toFloatFromText)
            super()._bindDataWithWidgets("gamma_f", self.gamma_f_text, self._toFloatFromText)
            # slater:返回list或None
            super()._bindDataWithWidgets("slater_Fx_vv_initial", self.slater_initial_Fx_vv_text,
                                         self._toFloatListByStrFromText)
            super()._bindDataWithWidgets("slater_Fx_vc_initial", self.slater_initial_Fx_vc_text,
                                         self._toFloatListByStrFromText)
            super()._bindDataWithWidgets("slater_Gx_vc_initial", self.slater_initial_Gx_vc_text,
                                         self._toFloatListByStrFromText)
            super()._bindDataWithWidgets("slater_Fx_cc_initial", self.slater_initial_Fx_cc_text,
                                         self._toFloatListByStrFromText)
            super()._bindDataWithWidgets("slater_Fx_vv_intermediate", self.slater_intermediate_Fx_vv_text,
                                         self._toFloatListByStrFromText)
            super()._bindDataWithWidgets("slater_Fx_vc_intermediate", self.slater_intermediate_Fx_vc_text,
                                         self._toFloatListByStrFromText)
            super()._bindDataWithWidgets("slater_Gx_vc_intermediate", self.slater_intermediate_Gx_vc_text,
                                         self._toFloatListByStrFromText)
            super()._bindDataWithWidgets("slater_Fx_cc_intermediate", self.slater_intermediate_Fx_cc_text,
                                         self._toFloatListByStrFromText)

            super()._bindDataWithWidgets("v1_ext_B", self.v1_ext_B_texts, self._toFloatListByWidgets_1DFromText)
            # super()._bindDataWithWidgets("v1_on_which", self.v1_on_which_text, self._toSimpleStrFromText)

        if "s_shell":
            super()._bindDataWithWidgets("s_matrix", self.s_shell_texts, self._toComplexListByWidgets_2DFromText)

        if "p_or_t2g_shell":
            super()._bindDataWithWidgets("p_or_t2g_matrix", self.p_or_t2g_shell_matrix_texts,
                                         self._toComplexListByWidgets_2DFromText)
            super()._bindDataWithWidgets("trigonal_t2g_delta", self.cf_trigonal_t2g_delta_text, self._toFloatFromText)
            super()._bindDataWithWidgets("tetragonal_t2g_ten_dq", self.cf_tetragonal_t2g_ten_dq_text,
                                         self._toFloatFromText)
            super()._bindDataWithWidgets("tetragonal_t2g_d1", self.cf_tetragonal_t2g_d1_text, self._toFloatFromText)
            super()._bindDataWithWidgets("tetragonal_t2g_d3", self.cf_tetragonal_t2g_d3_text, self._toFloatFromText)

        if "d_shell":
            super()._bindDataWithWidgets("d_matrix", self.d_shell_matrix_texts, self._toComplexListByWidgets_2DFromText)
            super()._bindDataWithWidgets("cubic_d_ten_dq", self.cf_cubic_d_ten_dq_text, self._toFloatFromText)
            super()._bindDataWithWidgets("tetragonal_d_ten_dq", self.cf_tetragonal_d_ten_dq_text, self._toFloatFromText)
            super()._bindDataWithWidgets("tetragonal_d_d1", self.cf_tetragonal_d_d1_text, self._toFloatFromText)
            super()._bindDataWithWidgets("tetragonal_d_d3", self.cf_tetragonal_d_d3_text, self._toFloatFromText)
            super()._bindDataWithWidgets("square_planar_d_ten_dq", self.cf_square_planar_d_ten_dq_text,
                                         self._toFloatFromText)
            super()._bindDataWithWidgets("square_planar_d_ds", self.cf_square_planar_d_ds_text, self._toFloatFromText)

        if "f_shell":
            super()._bindDataWithWidgets("f_matrix", self.f_shell_matrix_texts, self._toComplexListByWidgets_2DFromText)

        super()._bindDataWithWidgets("local_axis", self.local_axis_texts, self._toFloatListByWidgets_2DFromText)
        super()._bindDataWithWidgets("gs_list", self.gs_list_text, self._toIntFromText)
        super()._bindDataWithWidgets("verbose", self.verbose_text, self._toIntFromText)

    def _handleOn_ShowTip_of_SlaterParameters(self):
        v_name = super()._getDataFromInupt("v_name")
        c_name = super()._getDataFromInupt("c_name")
        if v_name == "":
            self.informMsg("请先输入价电子壳层的名称")
            return
        else:
            shell_name_v_list = re.findall(r'(s|p|t2g|d|f)', v_name)
            if shell_name_v_list == []:
                self.informMsg("请输入正确的价电子壳层名称")
                return
            else:
                shell_name_v = shell_name_v_list[0]
                if c_name == "":
                    shell_name = (shell_name_v,)
                    res = slater_integrals_name(shell_name=shell_name, label=("v",))
                    tip = ""
                    for item in res:
                        tip = tip + item + "  "
                    self.informMsg(tip)

                else:
                    shell_name_c_list = re.findall(r'(s|p32|p12|p|d52|d32|d|f72|f52|f)', c_name)
                    if shell_name_c_list == []:
                        self.informMsg("请输入正确的芯电子壳层名称")
                        return
                    else:
                        shell_name_c = shell_name_c_list[0]
                        shell_name = (shell_name_v, shell_name_c)
                        res = slater_integrals_name(shell_name=shell_name, label=("v", "c"))
                        tip = ""
                        for item in res:
                            tip = tip + item + "  "
                        self.informMsg(tip)

    def _handleOn_Set_Default_Parameters(self):
        if "get atom data":
            # 电子参数:原子名称和壳层需要用户输入,设置默认值的参数有soc/slater/gamma_c(会设置到第二个界面)
            atom_name = super()._getDataFromInupt("atom_name")
            v_name = super()._getDataFromInupt("v_name")
            c_name = super()._getDataFromInupt("c_name")
            v_noccu = super()._getDataFromInupt("v_noccu")
            shell_name_v_list = re.findall(r'(s|p|t2g|d|f)', v_name)
            if shell_name_v_list == []:
                self.informMsg("请输入正确的价电子壳层名称")
                return
            else:
                shell_name_v = shell_name_v_list[0]
                shell_name_c_list = re.findall(r'(s|p32|p12|p|d52|d32|d|f72|f52|f)', c_name)
                if shell_name_c_list == []:
                    self.informMsg("请输入正确的芯电子壳层名称")
                    return
                else:
                    shell_name_c = shell_name_c_list[0]
            shell_name = (shell_name_v, shell_name_c)
            edge = shell_name_to_edge[c_name]
            print(edge)

            res = get_atom_data(atom_name, v_name=v_name, v_noccu=v_noccu, edge=edge)
            name_i, slat_i = [list(i) for i in
                              zip(*res['slater_i'])]  # Slater integrals for initial Hamiltonian without core-hole
            name_n, slat_n = [list(i) for i in
                              zip(*res['slater_n'])]  # Slater integrals for intermediate Hamiltonian with core-hole

        if "set default parameters":
            # Spin-orbit coupling strengths
            v_soc_i = res['v_soc_i'][0]  # valence 3d electron without core-hole
            v_soc_n = res['v_soc_n'][0]  # valence 3d electron with core-hole
            # E_{L2} - E_{L3} = (2l+1) * zeta_p
            if shell_name_c == 'p' or "p32" or "p12":
                l = 1
            elif shell_name_c == "s":
                l = 0
            elif shell_name_c == "d" or "d52" or "d32":
                l = 2
            elif shell_name_c == "f" or "f52" or "f72":
                l = 3

            c_soc_n = (res['edge_ene'][0] - res['edge_ene'][1]) / (l + 0.5)  # core 2p electron
            print(res['edge_ene'][0])
            print(res['edge_ene'][1])
            print(c_soc_n)
            gamma_c = res['gamma_c'][1]  # core hole
            self.v_soc_text.setText(str(v_soc_i) + ";" + str(v_soc_n))
            self.c_soc_text.setText(str(c_soc_n))
            self.gamma_c_text.setText(str(gamma_c))
            # 将slater_i,slater_n的值分为Fx_vv,Fx_vc,Gx_vc,Fx_cc
            # slat_i与slat_n的vv部分可以是不一样的,因为这里用的是Hatree-Fock平均场去计算得到的轨道,不是严格意义上的原子轨道,因此core-hole出现之后求得的轨道会有不同
            slater = {"Fx_vv": "", "Fx_vc": "", "Gx_vc": "", "Fx_cc": ""}
            slater_init = ""
            try:
                for i in range(len(slat_n)):
                    if re.search(r"[F][0-9]+[_][1]{2}", name_n[i]):
                        slater["Fx_vv"] += str(slat_n[i]) + ";"
                        slater_init += str(slat_i[i]) + ";"
                    if re.search(r"[F][0-9]+[_][1][2]", name_n[i]):
                        slater["Fx_vc"] += str(slat_n[i]) + ";"
                    if re.search(r"[G][0-9]+[_][1][2]", name_n[i]):
                        slater["Gx_vc"] += str(slat_n[i]) + ";"
                    if re.search(r"[F][0-9]+[_][2]{2}", name_n[i]):
                        slater["Fx_cc"] += str(slat_n[i]) + ";"
                self.slater_initial_Fx_vv_text.setText(slater_init)
                self.slater_intermediate_Fx_vv_text.setText(slater["Fx_vv"])
                self.slater_intermediate_Fx_vc_text.setText(slater["Fx_vc"])
                self.slater_intermediate_Gx_vc_text.setText(slater["Gx_vc"])
                self.slater_intermediate_Fx_cc_text.setText(slater["Fx_cc"])
            except Exception as e:
                print(e)
                self.informMsg("默认数据设置失败")

    def _handleOn_ReSet_Parameters(self):
        self._retranslateTips()
        self.informMsg("已经重置")

    def _handleOnGenerate_cf_trigonal_t2g(self):
        # 即使用户不输入也有值
        delta = super()._getDataFromInupt("trigonal_t2g_delta")
        v1_cmft = cf_trigonal_t2g(delta=delta)
        for row in range(6):
            for column in range(6):
                self.p_or_t2g_shell_matrix_texts[row][column].setText(str(v1_cmft[row][column]))

    def _handleOnGenerate_cf_tetragonal_t2g(self):
        ten_dq = super()._getDataFromInupt("tetragonal_t2g_ten_dq")
        d1 = super()._getDataFromInupt("tetragonal_t2g_d1")
        d3 = super()._getDataFromInupt("tetragonal_t2g_d3")
        v1_cmft = cf_tetragonal_t2g(ten_dq=ten_dq, d1=d1, d3=d3)
        for row in range(6):
            for column in range(6):
                self.p_or_t2g_shell_matrix_texts[row][column].setText(str(v1_cmft[row][column]))

    def _handleOnGenerate_cf_cubic_d(self):
        ten_dq = super()._getDataFromInupt("cubic_d_ten_dq")
        v1_cmft = cf_cubic_d(ten_dq=ten_dq)
        for row in range(10):
            for column in range(10):
                self.d_shell_matrix_texts[row][column].setText(str(v1_cmft[row][column]))

    def _handleOnGenerate_cf_tetragonal_d(self):
        ten_dq = super()._getDataFromInupt("tetragonal_d_ten_dq")
        d1 = super()._getDataFromInupt("tetragonal_d_d1")
        d3 = super()._getDataFromInupt("tetragonal_d_d3")
        v1_cmft = cf_tetragonal_d(ten_dq=ten_dq, d1=d1, d3=d3)
        for row in range(10):
            for column in range(10):
                self.d_shell_matrix_texts[row][column].setText(str(v1_cmft[row][column]))

    def _handleOnGenerate_cf_square_planar_d(self):
        ten_dq = super()._getDataFromInupt("square_planar_d_ten_dq")
        ds = super()._getDataFromInupt("square_planar_d_ds")
        v1_cmft = cf_square_planar_d(ten_dq=ten_dq, ds=ds)
        for row in range(10):
            for column in range(10):
                self.d_shell_matrix_texts[row][column].setText(str(v1_cmft[row][column]))

    def _handleOnCheckInput(self):  # 写这个函数的主要目的担心Check_input按钮直接调用_verify...会出错
        self._verifyValid_and_getAtomDataFromInput()

    def _handleOnAddToAtomList(self) -> bool:
        atomData = self._verifyValid_and_getAtomDataFromInput()
        if atomData is None:  # 获取失败
            self.informMsg("add to fail")
            return False
        else:  # 此时atomData是AtomBasicData这个类
            print("数据获取成功")  # 用来检查
            name = DataManager_atom.getNameFromAtomData(atomData)  # 此时name不可能是"",因为getAtomDataFromInput中已经检查过了
            print(name)  # 用来检查
            if name in self.dataManager.atomBasicDataList.keys():
                reply = self.questionMsg("atom_list中已经存在同名item，是否要覆盖?")
                if reply == False:
                    return False
        atomData.ed["eval_i"] = self.eval_i_present
        atomData.ed["eval_n"] = self.eval_n_present
        atomData.ed["trans_op"] = self.trans_op_present
        atomData.ed["gs_list"] = self.gs_list_present
        print("hello")
        if self.dataManager.addAtomData(atomData) == False:
            self.informMsg("数据添加失败")
            return False
        # 新建一个item
        print("准备创建item")
        item = self._getItemFromAtomData(self.atom_list, atomData)
        # 遍历atom_list看有没有同名的，有的话直接删除,因为上面已经问过了
        row = 0
        while row < self.atom_list.count():
            if self.atom_list.item(row).text() == item.text():
                break
            row += 1
        if row != self.atom_list.count():
            # 已经存在同名的，先删除旧的
            self.atom_list.takeItem(row)
        print("准备创建item")
        self.atom_list.addItem(item)
        self.atom_list.sortItems()
        self.atom_list.setCurrentItem(item)  # 排过序之后可能不是原先的位置了，重新设置一下
        self.atom_name_present = name
        return True

    def _verifyValid_and_getAtomDataFromInput(self) -> AtomBasicData or None:
        # 获取页面上除verbose之外的参数,即atomdata.需要检验必要参数是否完整，如完整，进行保存，可能还要查重，不完整则返回None
        # 第一步:从界面上获取数据
        if "get parameters from first page":
            atom_name = super()._getDataFromInupt("atom_name")
            v_name = super()._getDataFromInupt("v_name")
            v_noccu = super()._getDataFromInupt("v_noccu")  # int
            c_name = super()._getDataFromInupt("c_name")
            c_noccu = super()._getDataFromInupt("c_noccu")  # int
            v_soc = super()._getDataFromInupt("v_soc")  # float-float, take the first
            c_soc = super()._getDataFromInupt("c_soc")  # float
            slater_Fx_vv_initial = super()._getDataFromInupt("slater_Fx_vv_initial")  # float-float-...
            slater_Fx_vc_initial = super()._getDataFromInupt("slater_Fx_vc_initial")  # float-float-...
            slater_Gx_vc_initial = super()._getDataFromInupt("slater_Gx_vc_initial")  # float-float-...
            slater_Fx_cc_initial = super()._getDataFromInupt("slater_Fx_cc_initial")  # float-float-...
            slater_Fx_vv_intermediate = super()._getDataFromInupt("slater_Fx_vv_intermediate")  # float-float-...
            slater_Fx_vc_intermediate = super()._getDataFromInupt("slater_Fx_vc_intermediate")  # float-float-...
            slater_Gx_vc_intermediate = super()._getDataFromInupt("slater_Gx_vc_intermediate")  # float-float-...
            slater_Fx_cc_intermediate = super()._getDataFromInupt("slater_Fx_cc_intermediate")  # float-float-...
            shell_level_v = super()._getDataFromInupt("shell_level_v")  # float
            shell_level_c = super()._getDataFromInupt("shell_level_c")  # float
            gamma_c = super()._getDataFromInupt("gamma_c")  # float
            gamma_f = super()._getDataFromInupt("gamma_f")  # float
            v1_ext_B = super()._getDataFromInupt("v1_ext_B")  # float list
            # v1_on_which = super()._getDataFromInupt("v1_on_which")  # str
            v1_on_which = self.v1_on_which_combo.currentText()  # str
            local_axis = super()._getDataFromInupt("local_axis")  # 2d float array

            self.current_index = self.return_stack_index_of_crystal_field()
            print(self.current_index)
            if self.current_index == 1:
                v1_cmft = None
                v1_othermat = None
            else:
                if self.current_index == 2:
                    v1_cmft = super()._getDataFromInupt("s_matrix")
                elif self.current_index == 3:
                    v1_cmft = super()._getDataFromInupt("p_or_t2g_matrix")
                elif self.current_index == 4:
                    v1_cmft = super()._getDataFromInupt("d_matrix")
                else:
                    v1_cmft = super()._getDataFromInupt("f_matrix")
                v1_othermat = np.zeros(np.array(v1_cmft).shape)

        # 第二步:检验数据的合法性
        if "check valid":
            if atom_name == "":
                self.informMsg("请输入规范格式的atom_name")
                return None
            if v_name == "":
                self.informMsg("请输入规范格式的v_name")
                return None
            if v_noccu is None:
                self.informMsg("请输入规范格式的v_noccu")
                return None
            if v_soc is None:
                self.informMsg("请输入规范格式的v_soc")
                return None
            if len(v_soc) == 1:  # 只输了一个
                v_soc = [v_soc[0], v_soc[0]]
            if c_name == "":
                self.informMsg("请输入规范格式的c_name")
                return None
            if c_noccu is None:
                self.informMsg("请输入规范格式的c_noccu")
                return None
            if c_soc == 0.0:
                self.informMsg("请输入规范格式的c_soc,已假设其为0.0")
            if gamma_c == 0.0:
                self.informMsg("请输入规范格式的gamma_c,已假设其为0.0")
            if gamma_f == 0.0:
                self.informMsg("请输入规范格式的gamma_f,已假设其为0.0")

            if local_axis == [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]:
                local_axis = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
            mat = np.array(local_axis)
            if np.all(np.dot(mat.T, mat) - np.diag([1] * 3)) != 0:
                self.informMsg("请输入实幺正矩阵local_axis")
                return None

        try:
            atomData = AtomBasicData(
                atom_name=atom_name,
                v_name=v_name,
                v_noccu=v_noccu,
                c_name=c_name,
                c_noccu=c_noccu,
                slater_Fx_vv_initial=slater_Fx_vv_initial,
                slater_Fx_vc_initial=slater_Fx_vc_initial,
                slater_Gx_vc_initial=slater_Gx_vc_initial,
                slater_Fx_cc_initial=slater_Fx_cc_initial,
                slater_Fx_vv_intermediate=slater_Fx_vv_intermediate,
                slater_Fx_vc_intermediate=slater_Fx_vc_intermediate,
                slater_Gx_vc_intermediate=slater_Gx_vc_intermediate,
                slater_Fx_cc_intermediate=slater_Fx_cc_intermediate,
                v_soc=v_soc,  # 只存initial
                c_soc=c_soc,
                shell_level_v=shell_level_v,
                shell_level_c=shell_level_c,
                gamma_c=gamma_c,
                gamma_f=gamma_f,
                v1_ext_B=v1_ext_B,
                v1_on_which=v1_on_which,
                v_cmft=v1_cmft,
                v_othermat=v1_othermat,
                local_axis=local_axis,
                ed={"eval_i": self.eval_i_present,
                    "eval_n": self.eval_n_present,
                    "trans_op": self.trans_op_present,
                    "gs_list": self.gs_list_present}
            )
        except Exception as e:
            self.informMsg("创建atomData失败: " + str(e))
            atomData = None

        return atomData

    def _getItemFromAtomData(self, parent, atomData: AtomBasicData) -> QListWidgetItem:
        item = QListWidgetItem(parent)
        itemName = DataManager_atom.getNameFromAtomData(atomData)
        item.setText(itemName)  # 默认这个name非空，需要在获取item前自行检查
        # 之后就根据这个name去数据中找相应的数据
        return item

    # menu上的删除键
    def _handleOnDeleteFromAtomList(self):
        # 如果要执行删除item的操作,意味着atom_list上必至少有一个item,因为需要右键点击item,选择delete
        item = self.atom_list.currentItem()
        row = self.atom_list.row(item)
        # 判断item对应的名字是否为self.atom_name_present
        if item.text() == self.atom_name_present:
            reply = self.questionMsg("确定要删除当前界面上的参数吗？？")
            if reply == True:
                self.atom_name_present = ""
                self.eval_i_present = None
                self.eval_n_present = None
                self.trans_op_present = None
                self.gs_list_present = [0]
                self._retranslateNames()  # 刷新界面

            else:
                return
        self.atom_list.takeItem(row)
        del self.dataManager.atomBasicDataList[item.text()]
        self.informMsg("已经删除")

    def _handleOnImportAtomFromList(self, item: QListWidgetItem):
        # 将atom_list中的某个item的数据导入到界面上称为当前的数据
        print(item.text())
        data = self.dataManager.getAtomDataByName(item.text())
        if data is None:  # 应该不会到这里，加入列表的时候存在，这个选择又只能选择列表中的，应该不会不存在
            self.informMsg(f"导入数据失败，未找到:{item.text()}")
            return
        # 根据数据设置界面
        self._setInterfaceByAtomData(data)
        self.informMsg("成功导入数据")
        # 这里只考虑了python_ed的情况,对于fortran的情形先不考虑
        self.atom_name_present = item.text()
        try:
            # to do list:需要将eval_i_present等的复数改成实数
            self.eval_i_present = self.dataManager.atomBasicDataList[item.text()].ed["eval_i"]
            self.eval_i_present = np.array(self.eval_i_present)
            self.eval_n_present = self.dataManager.atomBasicDataList[item.text()].ed["eval_n"]
            self.eval_n_present = np.array(self.eval_n_present)
            self.trans_op_present = self.dataManager.atomBasicDataList[item.text()].ed["trans_op"]
            self.gs_list_present = self.dataManager.atomBasicDataList[item.text()].ed["gs_list"]
        except Exception as e:
            print(e)
            self.informMsg("something wrong")

    def _setInterfaceByAtomData(self, data: AtomBasicData):
        # data来自于atom_list上的item的数据,其必然是非空的,且其数据格式必然是正确的,因此无需再检验
        try:
            self.atom_name_text.setText(data.atom_name)
            self.v_name_text.setText(data.v_name)
            self.v_noccu_text.setText(str(data.v_noccu))
            self.c_name_text.setText(data.c_name)
            self.c_noccu_text.setText(str(data.c_noccu))
            self.v_soc_text.setText(str(data.v_soc[0]) + ";" + str(data.v_soc[1]))
            self.c_soc_text.setText(str(data.c_soc))
            self.shell_level_c_text.setText(str(data.shell_level_c))
            self.shell_level_v_text.setText(str(data.shell_level_v))
            self.gamma_c_text.setText(str(data.gamma_c))
            self.gamma_f_text.setText(str(data.gamma_f))
            for index in range(self.v1_on_which_combo.count()):
                if self.v1_on_which_combo.itemText(index) == data.v1_on_which:
                    self.v1_on_which_combo.setCurrentIndex(index)

            temp = ""
            if data.slater_Fx_vv_initial is not None:
                for i in range(len(data.slater_Fx_vv_initial)):
                    if i > 0:
                        temp += ";"
                    temp += str(data.slater_Fx_vv_initial[i])
            self.slater_initial_Fx_vv_text.setText(temp)

            temp = ""
            if data.slater_Fx_vc_initial is not None:
                for i in range(len(data.slater_Fx_vc_initial)):
                    if i > 0:
                        temp += ";"
                    temp += str(data.slater_Fx_vc_initial[i])
            self.slater_initial_Fx_vc_text.setText(temp)

            temp = ""
            if data.slater_Gx_vc_initial is not None:
                for i in range(len(data.slater_Gx_vc_initial)):
                    if i > 0:
                        temp += ";"
                    temp += str(data.slater_Gx_vc_initial[i])
            self.slater_initial_Gx_vc_text.setText(temp)
            temp = ""
            if data.slater_Fx_cc_initial is not None:
                for i in range(len(data.slater_Fx_cc_initial)):
                    if i > 0:
                        temp += ";"
                    temp += str(data.slater_Fx_cc_initial[i])
            self.slater_intermediate_Fx_cc_text.setText(temp)

            temp = ""
            if data.slater_Fx_vv_intermediate is not None:
                for i in range(len(data.slater_Fx_vv_intermediate)):
                    if i > 0:
                        temp += ";"
                    temp += str(data.slater_Fx_vv_intermediate[i])
            self.slater_intermediate_Fx_vv_text.setText(temp)

            temp = ""
            if data.slater_Fx_vc_intermediate is not None:
                for i in range(len(data.slater_Fx_vc_intermediate)):
                    if i > 0:
                        temp += ";"
                    temp += str(data.slater_Fx_vc_intermediate[i])
            self.slater_intermediate_Fx_vc_text.setText(temp)

            temp = ""
            if data.slater_Gx_vc_intermediate is not None:
                for i in range(len(data.slater_Gx_vc_intermediate)):
                    if i > 0:
                        temp += ";"
                    temp += str(data.slater_Gx_vc_intermediate[i])
            self.slater_intermediate_Gx_vc_text.setText(temp)

            temp = ""
            if data.slater_Fx_cc_intermediate is not None:
                for i in range(len(data.slater_Fx_cc_intermediate)):
                    if i > 0:
                        temp += ";"
                    temp += str(data.slater_Fx_cc_intermediate[i])
            self.slater_intermediate_Fx_cc_text.setText(temp)

            i = 0
            for lineEdit in self.v1_ext_B_texts:
                lineEdit.setText(str(data.v1_ext_B[i]))
                i += 1

            for i in range(3):
                for j in range(3):
                    self.local_axis_texts[i][j].setText(str(data.local_axis[i][j]))

            self.gs_list_text.setText(str(data.ed["gs_list"][0]))

            if data.v_cmft != None:
                index = self.return_stack_index_of_crystal_field()
                if index == 2:
                    for i in range(2):
                        for j in range(2):
                            self.s_shell_texts[i][j].setText(str(data.v_cmft[i][j]))
                elif index == 3:
                    for i in range(6):
                        for j in range(6):
                            self.p_or_t2g_shell_matrix_texts[i][j].setText(str(data.v_cmft[i][j]))
                elif index == 4:
                    for i in range(10):
                        for j in range(10):
                            self.d_shell_matrix_texts[i][j].setText(str(data.v_cmft[i][j]))
                elif index == 5:
                    for i in range(14):
                        for j in range(14):
                            self.f_shell_matrix_texts[i][j].setText(str(data.v_cmft[i][j]))
        except:
            self.informMsg("无法将数据导入到界面,原因不明")

    # 保存文件按钮
    def _handleOnSaveAtomList(self):
        if "first step:check current item":
            item = self.atom_list.currentItem()
            if item is None:
                self.informMsg("未选中atom_list中的item")
                return

        if "second step:find path and fix file ame":
            fileName = item.text() + ".json"
            print(fileName)
            atomData = self.dataManager.atomBasicDataList[item.text()]
            fileName_choose, filetype = QFileDialog.getSaveFileName(self.scrollForFirstFrame,
                                                                    "文件保存",
                                                                    "./" + fileName,  # 起始路径
                                                                    "Json Files (*.json)")
            # PyQt【控件】：QFileDialog.getSaveFileName()的使用
            # 控件作用：打开文件资源管理器，获得你需要保存的文件名，注意：它不会帮你创建文件，只一个返回元组，元组第一项为你的文件路径。
            print(fileName_choose)
            str_list = fileName_choose.split("/")
            print(str_list[-1])
            if str_list[-1] != fileName:
                self.informMsg("文件名不是atom_name,请重新保存")
                return

        if "third step:data type transform and write a json file and save":
            # 将其中的复数相关的数据转化为字符串list,否则无法被保存
            atom_data_dict = DataManager_atom.saveAtomDatatoJsonFile(atomData)
            with open(fileName_choose, 'w') as f:
                json.dump(atom_data_dict, f, indent=4)  # 若已存在该文件,就覆盖之前

    # 上传文件按钮
    def _handleOnLoadAtomList(self):
        fileName, fileType = QFileDialog.getOpenFileName(self.frame, r'Load json',
                                                         r'.', r'json Files(*.json)')  # 打开程序文件所在目录是将路径换为.即可
        with open(fileName, "r") as f:
            atom_data = json.loads(f.read())  # temp是存放spectra data的数据类
        AtomData = DataManager_atom.getAtomDataFromJsonFile(atom_data)
        if AtomData == None:
            self.informMsg("读取文件数据发生错误")
            return

        if "check and add to dataManager":
            AtomName = DataManager_atom.getNameFromAtomData(AtomData)
            if AtomName in self.dataManager.atomBasicDataList.keys():
                reply = self.questionMsg("List中已经存在相同名称,是否进行覆盖？")
                if reply == False:
                    return None
            self.dataManager.addAtomData(AtomData)

        if "添加到atom_list中":
            item = self._getItemFromAtomData(self.atom_list, AtomData)
            row = 0
            while row < self.atom_list.count():
                if self.atom_list.item(row).text() == item.text():
                    break
                row += 1
            if row != self.atom_list.count():
                self.atom_list.takeItem(row)
            self.atom_list.addItem(item)
            self.atom_list.sortItems()
            self.atom_list.setCurrentItem(item)

    def _getAtomDataFromAtomList(self, item: QListWidgetItem) -> AtomBasicData or None:
        return self.dataManager.getAtomDataByName(item.text())

        # 生成self.eval_i/eval_n/trans_op/...

    def _handleOnEdCalculation(self) -> bool:
        atomData = self._verifyValid_and_getAtomDataFromInput()
        if atomData is None:
            return False

        # 第一句已经检验过数据的合法性,因此下面直接可以来用
        if self.ed_combo.currentText() == "ed_1v1c_python":
            shell_name_v = re.findall(r'(s|p|t2g|d|f)', atomData.v_name)[0]
            shell_name_c = re.findall(r'(s|p32|p12|p|d52|d32|d|f72|f52|f)', atomData.c_name)[0]
            shell_name = (shell_name_v, shell_name_c)

            shell_level = (atomData.shell_level_v, atomData.shell_level_c)

            v_soc = (atomData.v_soc[0], atomData.v_soc[1])
            c_soc = atomData.c_soc
            v_noccu = atomData.v_noccu
            slater_initial = atomData.slater_Fx_vv_initial  # list直接相加即可
            slater_initial += atomData.slater_Fx_vc_initial
            slater_initial += atomData.slater_Gx_vc_initial
            slater_initial += atomData.slater_Fx_cc_initial
            slater_intermediate = atomData.slater_Fx_vv_intermediate
            slater_intermediate += atomData.slater_Fx_vc_intermediate
            slater_intermediate += atomData.slater_Gx_vc_intermediate
            slater_intermediate += atomData.slater_Fx_cc_intermediate
            slater = (slater_initial, slater_intermediate)
            ext_B = (atomData.v1_ext_B[0], atomData.v1_ext_B[1], atomData.v1_ext_B[2])
            on_which = atomData.v1_on_which
            local_axis = np.array(atomData.local_axis)

            if atomData.v_cmft == None:
                v_cmft = None
            else:
                v_cmft = np.array(atomData.v_cmft)
            v_othermat = atomData.v_othermat  # v_othermat已经是ndarray了，即使它是零矩阵
            verbose = super()._getDataFromInupt("verbose")
            if verbose == None:
                verbose = 0
            print(shell_name, shell_level, v_soc, c_soc, v_noccu, slater, ext_B, on_which, v_cmft, v_othermat,
                  local_axis, verbose)
            self.eval_i_present, self.eval_n_present, self.trans_op_present = ed_1v1c_py(shell_name=shell_name,
                                                                                         shell_level=shell_level,
                                                                                         v_soc=v_soc, c_soc=c_soc,
                                                                                         v_noccu=v_noccu, slater=slater,
                                                                                         ext_B=ext_B, on_which=on_which,
                                                                                         v_cfmat=v_cmft,
                                                                                         v_othermat=v_othermat,
                                                                                         loc_axis=local_axis,
                                                                                         verbose=verbose)
            self.informMsg("精确对角化完成")  # 不同的电子构型得到的trans_op的维数也不同,可能会相差很大,因为Fock state的数目不同
            try:
                atomData = self._verifyValid_and_getAtomDataFromInput()
                self.atom_name_present = DataManager_atom.getNameFromAtomData(atomData)
                if self.atom_name_present not in self.dataManager.atomBasicDataList.keys():
                    self.dataManager.atomBasicDataList[self.atom_name_present] = atomData
                else:
                    self.dataManager.atomBasicDataList[self.atom_name_present].ed["eval_i"] = self.eval_i_present
                    self.dataManager.atomBasicDataList[self.atom_name_present].ed["eval_n"] = self.eval_n_present
                    self.dataManager.atomBasicDataList[self.atom_name_present].ed["trans_op"] = self.trans_op_present
            except Exception as e:
                print(str(e))
                self.informMsg("数据更新失败")
                return False
            return True

        if self.ed_combo.currentText() == "ed_1v1c_fortan":
            self.informMsg("not implemented yet")
            return False
        if self.ed_combo.currentText() == "ed_2v1c_fortan":
            self.informMsg("not implemented yet")
            return False

    def _handleOnEdShow(self):
        if self.eval_i_present is None:
            self.informMsg("请先进行精确对角化计算")
            return
        if self.eval_n_present is None:
            self.informMsg("请先进行精确对角化计算")
            return
        if self.trans_op_present is None:
            self.informMsg("请先进行精确对角化计算")
            return
        try:
            fig = plt.figure(figsize=(16, 14))
            mpl.rcParams['font.size'] = 20

            ax1 = plt.subplot(1, 1, 1)
            plt.grid()
            print(self.eval_i_present - min(self.eval_i_present))
            plt.plot(range(len(self.eval_i_present)), self.eval_i_present - min(self.eval_i_present), '-o')
            plt.xlabel(r'Multiplets')
            plt.ylabel(r'Energy (eV)')
            plt.title(r'(a) Energy of multiplets')
            plt.show()
        except Exception as e:
            print(e)
            self.informMsg("作图失败")

    def _handleOn_Refresh_gs_list(self):
        gs_max = super()._getDataFromInupt("gs_list")
        self.gs_list_present = [i for i in range(gs_max)]
        self.dataManager.atomBasicDataList[self.atom_name_present].ed["gs_list"] = self.gs_list_present
        print(self.gs_list_present)


if __name__ == '__main__':
    app=QApplication(sys.argv)
    demo=FirstFrame()
    demo.scrollForFirstFrame.show()
    sys.exit(app.exec_())

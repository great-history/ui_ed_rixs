# python version 3.8
import json
import re
from edrixs.utils import *
import numpy as np
# 基本数据，保存slater,soc这些
shell_name = {
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
AtomDataKeys = ['atom_name', 'v_name', 'v_noccu', 'c_name', 'c_noccu',
                             'slater_Fx_vv_initial', 'slater_Fx_vc_initial', 'slater_Gx_vc_initial',
                             'slater_Fx_cc_initial',
                             'slater_Fx_vv_intermediate', 'slater_Fx_vc_intermediate',
                             'slater_Gx_vc_intermediate', 'slater_Fx_cc_intermediate',
                             'v_soc', 'c_soc', 'shell_level_v', 'shell_level_c', 'gamma_c', 'gamma_f', 'v1_ext_B',
                             'v1_on_which', 'v_cmft', 'v_othermat', 'local_axis', 'ed']
SpectraDataKeys = ["atomdata","spectra_type", "poltype", "thin", "thout", "phi", "ominc", "eloss", "scattering_axis",
                    "temperature", "gamma_f", "spectra"]

class AtomBasicData:
    def __init__(self,
                 atom_name=None,
                 v_name=None,
                 v_noccu=None,
                 c_name=None,
                 c_noccu=None,
                 slater_Fx_vv_initial=None,
                 slater_Fx_vc_initial=None,
                 slater_Gx_vc_initial=None,
                 slater_Fx_cc_initial=None,
                 slater_Fx_vv_intermediate=None,
                 slater_Fx_vc_intermediate=None,
                 slater_Gx_vc_intermediate=None,
                 slater_Fx_cc_intermediate=None,
                 v_soc=None,  # 只存initial
                 c_soc=None,
                 shell_level_v=None,
                 shell_level_c=None,
                 gamma_c = None,
                 gamma_f = None,
                 v1_ext_B=None,
                 v1_on_which=None,
                 v_cmft=None,
                 v_othermat=None,
                 local_axis=None,
                 ed=None):
        self.atom_name = atom_name if atom_name is not None else ""
        self.v_name = v_name if v_name is not None else ""  # str
        self.v_noccu = v_noccu  # int
        self.c_name = c_name if c_name is not None else ""  # str
        self.c_noccu = c_noccu  # int
        self.slater_Fx_vv_initial = slater_Fx_vv_initial if slater_Fx_vv_initial is not None else []  # list of float
        self.slater_Fx_vc_initial = slater_Fx_vc_initial if slater_Fx_vc_initial is not None else []  # list of float
        self.slater_Gx_vc_initial = slater_Gx_vc_initial if slater_Gx_vc_initial is not None else []  # list of float
        self.slater_Fx_cc_initial = slater_Fx_cc_initial if slater_Fx_cc_initial is not None else []  # list of float
        self.slater_Fx_vv_intermediate = slater_Fx_vv_intermediate if slater_Fx_vv_intermediate is not None else []  # list of float
        self.slater_Fx_vc_intermediate = slater_Fx_vc_intermediate if slater_Fx_vc_intermediate is not None else []  # list of float
        self.slater_Gx_vc_intermediate = slater_Gx_vc_intermediate if slater_Gx_vc_intermediate is not None else []  # list of float
        self.slater_Fx_cc_intermediate = slater_Fx_cc_intermediate if slater_Fx_cc_intermediate is not None else []  # list of float
        self.v_soc = v_soc if v_soc is not None else [0.0, 0.0]# float-float
        self.c_soc = c_soc if c_soc is not None else 0.0# float
        self.shell_level_v = shell_level_v if shell_level_v is not None else 0.0 # float-float
        self.shell_level_c = shell_level_c if shell_level_c is not None else 0.0# float
        self.gamma_c = gamma_c if gamma_c is not None else 0.1  # list of float
        self.gamma_f = gamma_f if gamma_f is not None else 0.1  # list of float
        self.v1_ext_B = v1_ext_B  if v1_ext_B is not None else [0, 0, 0]# float
        self.v1_on_which = v1_on_which if v1_on_which is not None else "spin" # float
        self.v_cmft = v_cmft # float or None
        self.v_othermat = v_othermat # float or None
        self.local_axis = local_axis if local_axis is not None else [[1,0,0],[0,1,0],[0,0,1]]# float
        self.ed = ed  if ed is not None else {"eval_i":[],"eval_n":[],"trans_op":[[]],"gs_list":[0]} # float

class DataManager_atom:
    def __init__(self):
        # 存放一组AtomBasicData，也就是放在列表里的实际数据，用v_name+v_noccu+'_'+c_name+c_noccu作为key
        self.atomBasicDataList = {}

    def getNameFromAtomData(atomData: AtomBasicData) -> str:
        if atomData.atom_name is None or len(atomData.atom_name) == 0:
            return ""
        if atomData.v_name is None or len(atomData.v_name) == 0:
            return ""
        name = atomData.atom_name + "_" + atomData.v_name
        if atomData.v_noccu is not None:
            name = name + str(atomData.v_noccu)
        if len(atomData.c_name) > 0:
            name = name + "_" + atomData.c_name
            if atomData.c_noccu is not None:
                name = name + str(atomData.c_noccu)
        edge = shell_name[atomData.c_name]
        name = name + "_" + edge
        return name

    def getAtomNameByName(name:str) -> str:
        str_list = name.split("_")
        return str_list[0]

    def addAtomData(self, atomData: AtomBasicData) -> bool:
        dictKey = DataManager_atom.getNameFromAtomData(atomData)
        if len(dictKey) == 0:
            return False
        self.atomBasicDataList[dictKey] = atomData  # 已经存在的话直接覆盖
        return True

    def getAtomDataByName(self, name: str) -> AtomBasicData or None:
        if name in self.atomBasicDataList.keys():
            return self.atomBasicDataList[name]
        else:
            return None

    def getAtomDataFromJsonFile(atom_data:dict) -> AtomBasicData or None:
        if AtomDataKeys != list(atom_data.keys()):
            return None
        # 需要将AtomData转换为AtomBasicData类型
        try:
            v_cmft = [[complex(c_num) for c_num in row] for row in atom_data["v_cmft"]]
            v_othermat = [[complex(c_num) for c_num in row] for row in atom_data["v_othermat"]]
            ed = {"eval_i":None, "eval_n":None, "trans_op":None, "gs_list":None}
            ed["eval_i"] = [float(c_num) for c_num in atom_data["ed"]["eval_i"]]  # "eval_i"是一个数组,不是矩阵
            ed["eval_i"] = np.array(ed["eval_i"])
            ed["eval_n"] = [float(c_num) for c_num in atom_data["ed"]["eval_n"]]
            ed["eval_n"] = np.array(ed["eval_n"])
            # print(len(atom_data["ed"]["trans_op"]))
            # print(len(atom_data["ed"]["trans_op"][0]))
            # print(len(atom_data["ed"]["trans_op"][0][0]))
            ed["trans_op"] = [[[complex(c_num) for c_num in column]for column in row] for row in atom_data["ed"]["trans_op"]]
            ed["trans_op"] = np.array(ed["trans_op"])
            # print(ed["trans_op"].shape)
            ed["gs_list"] = atom_data["ed"]["gs_list"]
            AtomData = AtomBasicData(atom_name=atom_data["atom_name"],
                                     v_name=atom_data["v_name"],
                                     v_noccu=atom_data["v_noccu"],
                                     c_name=atom_data["c_name"],
                                     c_noccu=atom_data["c_noccu"],
                                     slater_Fx_vv_initial=atom_data["slater_Fx_vv_initial"],
                                     slater_Fx_vc_initial=atom_data["slater_Fx_vc_initial"],
                                     slater_Gx_vc_initial=atom_data["slater_Gx_vc_initial"],
                                     slater_Fx_cc_initial=atom_data["slater_Fx_cc_initial"],
                                     slater_Fx_vv_intermediate=atom_data["slater_Fx_vv_intermediate"],
                                     slater_Fx_vc_intermediate=atom_data["slater_Fx_vc_intermediate"],
                                     slater_Gx_vc_intermediate=atom_data["slater_Gx_vc_intermediate"],
                                     slater_Fx_cc_intermediate=atom_data["slater_Fx_cc_intermediate"],
                                     v_soc=atom_data["v_soc"],  # 只存initial
                                     c_soc=atom_data["c_soc"],
                                     shell_level_v=atom_data["shell_level_v"],
                                     shell_level_c=atom_data["shell_level_c"],
                                     gamma_c=atom_data["gamma_c"],
                                     gamma_f=atom_data["gamma_f"],
                                     v1_ext_B=atom_data["v1_ext_B"],
                                     v1_on_which=atom_data["v1_on_which"],
                                     v_cmft=v_cmft,
                                     v_othermat=v_othermat,
                                     local_axis=atom_data["local_axis"],
                                     ed=ed)
            return AtomData
        except Exception as e:
            print(e)
            return None

    def saveAtomDatatoJsonFile(atomData:AtomBasicData) -> dict:
        atom_data_dict = atomData.__dict__
        new_array = [[str(c_num) for c_num in row] for row in atom_data_dict["v_cmft"]]
        atom_data_dict["v_cmft"] = new_array
        new_array = [[str(c_num) for c_num in row] for row in atom_data_dict["v_othermat"]]
        atom_data_dict["v_othermat"] = new_array
        new_array = [str(c_num) for c_num in atom_data_dict["ed"]["eval_i"]]  # "eval_i"是一个数组,不是矩阵
        atom_data_dict["ed"]["eval_i"] = new_array
        new_array = [str(c_num) for c_num in atom_data_dict["ed"]["eval_n"]]
        atom_data_dict["ed"]["eval_n"] = new_array
        # 注意trans_op是有三个维度的张量,即trans_op.shape = npol,m,n
        atom_data_dict["ed"]["trans_op"] = [[[str(c_num) for c_num in column] for column in row] for row in atomData.ed["trans_op"]]
        return atom_data_dict

class SpectraBasicData:
    def __init__(self,
                 atomdata=None,
                 spectra_type=None,
                 poltype=None,
                 thin=None,
                 thout=None,
                 phi=None,
                 ominc=None,
                 eloss=None,
                 scattering_axis=None,
                 temperature=None,
                 gamma_f=None,
                 spectra=None):
        self.atomdata = atomdata if atomdata is not None else AtomBasicData()  # 存放当前体系的原子结构信息
        self.spectra_type = spectra_type if spectra_type is not None else []  # 存放极化状态,a list of tuples
        self.poltype = poltype if poltype is not None else []  # [(str,float, str, float),(...)]
        self.thin = thin  if thin is not None else 0.0 # float
        self.thout = thout if thout is not None else 0.0 # float
        self.phi = phi  if phi is not None else 0.0 # float
        self.ominc = ominc if ominc is not None else []  # list of float
        self.eloss = eloss if eloss is not None else []  # list of float
        self.scattering_axis = scattering_axis if scattering_axis is not None else [[]]  # list of list
        self.temperature = temperature if temperature is not None else "" # float
        self.gamma_f = gamma_f if gamma_f is not None else 0.0 # float
        self.spectra = spectra if spectra is not None else {}

class DataManager_spectra:
    def __init__(self):
        # 存放一组AtomBasicData，也就是放在列表里的实际数据，用v_name+v_noccu+'_'+c_name+c_noccu作为key
        self.spectraBasicDataList = {}

    def getNameFromSpectraData(spectraData: SpectraBasicData) -> str:
        if spectraData.atomdata is AtomBasicData():
            return ""
        else:
            Name = DataManager_atom.getNameFromAtomData(spectraData.atomdata) + "_" + spectraData.spectra_type +\
                   "_" + str(spectraData.temperature) + "K"
            print(Name)
            return Name

    def addSpectraData(self, spectraData: SpectraBasicData) -> bool:
        dictKey = DataManager_spectra.getNameFromSpectraData(spectraData)
        if len(dictKey) == 0:
            return False
        self.spectraBasicDataList[dictKey] = spectraData  # 已经存在的话直接覆盖
        return True

    def getSpectraDataByName(self, name: str) -> SpectraBasicData or None:
        if name in self.spectraBasicDataList.keys():
            return self.spectraBasicDataList[name]
        else:
            return None

    def getSpectraDataFromJsonFile(fileName: str) -> SpectraBasicData or None:
        with open(fileName, "r") as f:
            spectra_data = json.loads(f.read())  # temp是存放spectra data的数据类
        if SpectraDataKeys != list(spectra_data.keys()):
            return None
        # 需要将SpectraData转换为SpectraBasicData类型
        atom_data = spectra_data["atomdata"]
        AtomData = DataManager_atom.getAtomDataFromJsonFile(atom_data)
        if AtomData is None:
            return None
        thin = float(spectra_data["thin"]),
        thout = float(spectra_data["thout"]),
        phi = float(spectra_data["phi"]),
        ominc = [float(c_num) for c_num in spectra_data["ominc"]]
        ominc = (np.array(ominc)).flatten()
        eloss = [float(c_num) for c_num in spectra_data["eloss"]]
        eloss = (np.array(eloss)).flatten()
        scattering_axis = [[float(c_num) for c_num in row] for row in spectra_data["scattering_axis"]]
        scattering_axis = np.array(scattering_axis)
        temperature = float(spectra_data["temperature"])
        gamma_f = float(spectra_data["gamma_f"])
        if spectra_data["spectra_type"] == "rixs":
            alpha = float(spectra_data["poltype"][0][1])  # poltype is a list of tuples,and this list only have one tuple
            beta = float(spectra_data["poltype"][0][3])
            poltype = [(spectra_data["poltype"][0][0], alpha, spectra_data["poltype"][0][2], beta)]
            print(poltype)
            if "rixs_1v1c_python_ed" in spectra_data["spectra"].keys():
                spectra_rixs = [[float(str) for str in row] for row in spectra_data["spectra"]["rixs_1v1c_python_ed"]]
                spectra_data["spectra"]["rixs_1v1c_python_ed"] = np.array(spectra_rixs)
        else:
            alpha = float(spectra_data["poltype"][0][1])
            poltype = [(spectra_data["poltype"][0][0], alpha)]
            print(poltype)
            if "xas_1v1c_python_ed" in spectra_data["spectra"].keys():
                spectra_xas = [float(str) for str in spectra_data["spectra"]["xas_1v1c_python_ed"]]
                spectra_data["spectra"]["xas_1v1c_python_ed"] = np.array(spectra_xas)
        try:
            SpectraData = SpectraBasicData(atomdata=AtomData,
                                           spectra_type=spectra_data["spectra_type"],
                                           poltype=poltype,
                                           thin=thin,
                                           thout=thout,
                                           phi=phi,
                                           ominc=ominc,
                                           eloss=eloss,
                                           scattering_axis=scattering_axis,
                                           temperature=temperature,
                                           gamma_f=gamma_f,
                                           spectra=spectra_data["spectra"])  # spectra应该装的都是实数
            return SpectraData
        except Exception as e:
            print(e)
            return None

    def saveSpectraDatatoJsonFile(SpectraData:SpectraBasicData) -> dict:
        spectra_data_dict = SpectraData.__dict__
        AtomData = SpectraData.atomdata
        spectra_data_dict["atomdata"] = DataManager_atom.saveAtomDatatoJsonFile(AtomData)
        spectra_data_dict["ominc"] = [str(c_num) for c_num in spectra_data_dict["ominc"]]
        spectra_data_dict["eloss"] = [str(c_num) for c_num in spectra_data_dict["eloss"]]
        spectra_data_dict["scattering_axis"] = [[str(c_num) for c_num in row] for row in spectra_data_dict["scattering_axis"]]
        try:
            if "xas_1v1c_python_ed" in spectra_data_dict["spectra"].keys():
                spectra_data = spectra_data_dict["spectra"]["xas_1v1c_python_ed"]
                spectra_data_dict["spectra"]["xas_1v1c_python_ed"] = [str(c_num).strip("[]") for c_num in spectra_data]
                print(spectra_data_dict["spectra"]["xas_1v1c_python_ed"])  # 转换为浮点数时会有[]加入
            if "rixs_1v1c_python_ed" in spectra_data_dict["spectra"].keys():
                # print(spectra_data_dict["spectra"]["rixs_1v1c_python_ed"].shape) # 发现是一个三维矩阵,比如(1000,1000,1),因此需要先提取
                spectra_data = spectra_data_dict["spectra"]["rixs_1v1c_python_ed"][:,:,0]
                spectra_data_dict["spectra"]["rixs_1v1c_python_ed"] = [[str(c_num) for c_num in row] for row in spectra_data]
        except Exception as e:
            print(e)
        # to do list:之后可以加其他类型的谱
        print("success save file")
        return spectra_data_dict

if __name__ == "__main__":
    pass

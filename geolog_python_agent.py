#!/usr/bin/env python3
# Geolog Python智能体
# 用于分析、开发和修改Geolog Python脚本
# 基于loglan_09_python_hc.pdf规范开发

import os
import re
from typing import Dict, List

class GeologPythonAgent:
    def __init__(self, project_dir: str):
        """初始化Geolog Python智能体"""
        self.project_dir = project_dir
        self.info_files = []
        self.pysh_files = []
        self.pdf_knowledge = self._load_pdf_knowledge()
        self.analyze_project()
    
    def _load_pdf_knowledge(self) -> Dict:
        """加载PDF文档中的关键知识点"""
        return {
            'python_version': 'Python 3.8 (64-bit)',
            'file_convention': {
                'pysh': 'Geolog Python脚本',
                'info': '参数/IO描述文件'
            },
            'core_functions': {
                'gettable': '读取整个表，创建Numpy数组变量',
                'puttable': '将Numpy数组和标量变量写入输出日志',
                'getrow': '从表中逐行读取数据，创建Numpy变量',
                'putrow': '将Numpy变量逐行写入输出'
            },
            'pygg_functions': {
                'init': '初始化Geolog项目',
                'term': '终止Geolog会话',
                'open': '打开井/集/曲线（WELL/SET/LOG）',
                'close': '关闭井/集/曲线',
                'read': '从打开的曲线读取一帧数据',
                'write': '向打开的曲线写入一帧数据',
                'pos': '在曲线中移动位置',
                'getc': '获取字符串值（常量或曲线）',
                'getn': '获取数值值（常量或曲线）',
                'putc': '设置字符串值（常量或曲线）',
                'putn': '设置数值值（常量或曲线）',
                'delete': '删除井/集/曲线',
                'audit': '初始化数据写入审计'
            },
            'pygg_constants': {
                'MISS_INT': '缺失值（整数）：-1000000000',
                'MISS_FLOAT': '缺失值（浮点数）：-1.0e30',
                'MISS_DOUBLE': '缺失值（双精度）：-1.0e30',
                'MISS_STRING': '缺失值（字符串）：空字符串',
                'STATUS_OLD': '状态：读取（只读）',
                'STATUS_NEW': '状态：写入（新建/更新）'
            },
            'pygg_types': {
                'WELL': '井',
                'HOLE': '井眼',
                'SET': '数据集',
                'LOG': '曲线',
                'CONSTANT': '常量',
                'COMMENT': '注释',
                'ATTRIBUTE': '属性'
            },
            'pygg_macros': {
                'IS_MISS_INT(value)': '检查整数是否为缺失值',
                'IS_MISS_FLOAT(value)': '检查浮点数是否为缺失值',
                'IS_MISS_DOUBLE(value)': '检查双精度数是否为缺失值',
                'IS_MISS_STRING(value)': '检查字符串是否为缺失值（空字符串）'
            },
            'coding_tips': [
                'Geolog变量名必须始终为小写',
                'Python Loglan参数在import geolog之后、gettable()调用之前可用',
                '当没有输入时，移除(getrow()/gettable())循环',
                '当没有输出时，移除(putrow()/puttable())循环',
                '使用math.isnan检查缺失值',
                '使用numpy的nansum, nanmean, nanmedium处理NaN',
                'Python缩进为4个空格',
                '对于整数数组，指定numpy dtype=int64'
            ],
            'common_packages': {
                'core': ['numpy', 'pandas', 'matplotlib', 'scipy'],
                'description': {
                    'numpy': '数值计算、数组处理（必需）',
                    'pandas': '数据分析、数据框操作',
                    'matplotlib': '数据可视化（2D/3D图表）',
                    'scipy': '科学计算、信号处理、卷积、插值',
                    'seaborn': '统计可视化',
                    'sklearn': '机器学习算法（scikit-learn）',
                    'cv2': '图像处理（OpenCV，用于成像测井）',
                    'PIL': '图像处理（Pillow）',
                    'skimage': '科学图像处理（scikit-image）',
                    'h5py': 'HDF5文件处理',
                    'openpyxl': 'Excel文件读写',
                    'requests': 'HTTP请求',
                    'bs4': 'HTML解析（BeautifulSoup4）',
                    'pywt': '小波变换（PyWavelets）',
                    'torch': '深度学习（PyTorch）',
                    'tensorflow': '深度学习（TensorFlow）'
                },
                'application_scenarios': {
                    'scipy': ['曲线滤波', '信号去噪', '小波变换', '卷积运算', '插值', 'FFT'],
                    'sklearn': ['测井相分类', '聚类分析', '异常检测', '回归分析', '降维'],
                    'pandas': ['多井数据分析', '统计报表', '数据清洗', '分层统计', '数据聚合'],
                    'cv2': ['成像测井处理', '边缘检测', '图像增强', '形态学操作', '降噪'],
                    'matplotlib': ['综合测井图', 'T2谱热图', '交叉图分析', '多子图布局', '3D可视化'],
                    'torch/tensorflow': ['深度学习预测', '岩相识别', '智能解释', '序列分析']
                }
            },
            'missing_value': 'math.nan',
            'encoding': 'UTF-8'
        }
    
    def analyze_project(self):
        """分析项目结构"""
        for root, _, files in os.walk(self.project_dir):
            for file in files:
                if file.endswith('.info'):
                    self.info_files.append(os.path.join(root, file))
                elif file.endswith('.pysh'):
                    self.pysh_files.append(os.path.join(root, file))
    
    def parse_info_file(self, info_path: str) -> Dict:
        """解析.info文件"""
        params = {
            'inputs': [],
            'outputs': [],
            'constants': [],
            'metadata': {}
        }
        
        try:
            with open(info_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # 解析元数据行
                if line.startswith('LANGUAGE =') or line.startswith('TABS_LABEL_ORDER ='):
                    key_value = line.split('=', 1)
                    if len(key_value) == 2:
                        params['metadata'][key_value[0].strip()] = key_value[1].strip()
                    continue
                
                parts = line.split()
                if len(parts) < 10:
                    continue
                
                mode = parts[0]
                arg = parts[1]
                var = parts[2]
                type_ = parts[3]
                repeat = parts[4] if len(parts) > 4 else ''
                default = parts[5] if len(parts) > 5 else ''
                validation = parts[6] if len(parts) > 6 else ''
                location = parts[7] if len(parts) > 7 else ''
                unit = parts[8] if len(parts) > 8 else ''
                visible = parts[9] == 'TRUE' if len(parts) > 9 else True
                tab_label = parts[10] if len(parts) > 10 else ''
                comment = ' '.join(parts[11:]) if len(parts) > 11 else ''
                
                param_info = {
                    'arg': arg,
                    'var': var,
                    'type': type_,
                    'repeat': repeat,
                    'default': default,
                    'validation': validation,
                    'location': location,
                    'unit': unit,
                    'visible': visible,
                    'tab_label': tab_label,
                    'comment': comment
                }
                
                if mode == 'INPUT':
                    if location == 'CONSTANT':
                        params['constants'].append(param_info)
                    else:
                        params['inputs'].append(param_info)
                elif mode == 'OUTPUT':
                    params['outputs'].append(param_info)
                    
        except Exception as e:
            print(f"解析.info文件时出错: {e}")
        
        return params
    
    def analyze_pysh_file(self, pysh_path: str) -> Dict:
        """分析.pysh文件"""
        analysis = {
            'imports': [],
            'variables_used': [],
            'functions_defined': [],
            'geolog_usage': [],
            'calculations': [],
            'data_mode': None,  # 'row' or 'table'
            'missing_value_handling': [],
            'encoding_issues': []
        }
        
        try:
            with open(pysh_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查文件头
            if '# python loglan' in content or '#!/usr/bin/env python3' in content:
                analysis['has_header'] = True
            
            # 分析导入
            import_pattern = r'^import\s+([\w\.]+)|^from\s+([\w\.]+)\s+import'
            for match in re.finditer(import_pattern, content, re.MULTILINE):
                imports = [m for m in match.groups() if m]
                analysis['imports'].extend(imports)
            
            # 分析Geolog使用
            geolog_pattern = r'geolog\.(\w+)'
            geolog_calls = re.findall(geolog_pattern, content)
            analysis['geolog_usage'] = geolog_calls
            
            # 确定数据模式
            if 'geolog.getrow()' in content:
                analysis['data_mode'] = 'row'
            elif 'geolog.gettable()' in content:
                analysis['data_mode'] = 'table'
            
            # 分析变量使用（改进模式）
            var_pattern = r'\b([a-z_][a-z0-9_]*)\b(?=\s*[=+\-*/(\[])'
            variables = re.findall(var_pattern, content, re.IGNORECASE)
            # 过滤掉Python关键字和内置函数
            keywords = {'import', 'from', 'def', 'if', 'elif', 'else', 'for', 'while', 
                       'with', 'as', 'return', 'break', 'continue', 'in', 'not', 'and', 'or',
                       'try', 'except', 'finally', 'raise', 'pass', 'class', 'global', 'lambda'}
            builtins = {'print', 'range', 'len', 'abs', 'min', 'max', 'sum', 'type', 
                       'int', 'float', 'str', 'list', 'dict', 'set', 'tuple'}
            variables = [v for v in variables if v not in keywords and v not in builtins and v.islower()]
            analysis['variables_used'] = list(set(variables))
            
            # 分析函数定义
            func_pattern = r'def\s+(\w+)\s*\('
            analysis['functions_defined'] = re.findall(func_pattern, content)
            
            # 分析缺失值处理
            if 'math.isnan' in content:
                analysis['missing_value_handling'].append('math.isnan')
            if any(x in content for x in ['nansum', 'nanmean', 'nanmedium']):
                analysis['missing_value_handling'].append('numpy_nan_functions')
            
            # 检查编码相关
            if 'encoding=' in content:
                analysis['encoding_issues'].append('explicit_encoding')
            
        except Exception as e:
            print(f"分析.pysh文件时出错: {e}")
        
        return analysis
    
    def generate_variable_mapping(self, pysh_path: str, info_path: str) -> Dict:
        """生成变量映射表"""
        info_params = self.parse_info_file(info_path)
        pysh_analysis = self.analyze_pysh_file(pysh_path)
        
        mapping = {
            'input_variables': [],
            'output_variables': [],
            'constants': [],
            'unmatched_info_vars': [],
            'unmatched_pysh_vars': [],
            'consistency_issues': []
        }
        
        # 匹配输入变量
        for input_param in info_params['inputs']:
            if input_param['var'] in pysh_analysis['variables_used']:
                mapping['input_variables'].append(input_param)
            else:
                mapping['unmatched_info_vars'].append(
                    f"输入变量 {input_param['var']} (.info) 未在 .pysh 中使用")
        
        # 匹配输出变量
        for output_param in info_params['outputs']:
            if output_param['var'] in pysh_analysis['variables_used']:
                mapping['output_variables'].append(output_param)
            else:
                mapping['unmatched_info_vars'].append(
                    f"输出变量 {output_param['var']} (.info) 未在 .pysh 中使用")
        
        # 匹配常量
        for const_param in info_params['constants']:
            if const_param['var'] in pysh_analysis['variables_used']:
                mapping['constants'].append(const_param)
            else:
                mapping['unmatched_info_vars'].append(
                    f"常量 {const_param['var']} (.info) 未在 .pysh 中使用")
        
        # 找出未在.info中定义的.pysh变量
        all_info_vars = [p['var'].lower() for p in 
                         info_params['inputs'] + info_params['outputs'] + info_params['constants']]
        unmatched = [v for v in pysh_analysis['variables_used'] if v.lower() not in all_info_vars]
        mapping['unmatched_pysh_vars'] = unmatched
        
        # 检查一致性问题
        if pysh_analysis['data_mode'] == 'row' and 'geolog.gettable()' in open(pysh_path, 'r', encoding='utf-8').read():
            mapping['consistency_issues'].append('同时使用了row和table模式')
        
        return mapping
    
    def generate_summary(self) -> str:
        """生成项目摘要"""
        summary = f"# Geolog Python 项目分析\n\n"
        summary += f"## 项目概览\n"
        summary += f"- **项目目录**: {self.project_dir}\n"
        summary += f"- **.info 文件数量**: {len(self.info_files)}\n"
        summary += f"- **.pysh 文件数量**: {len(self.pysh_files)}\n"
        summary += f"- **基于规范**: loglan_09_python_hc.pdf\n"
        summary += f"- **推荐Python版本**: {self.pdf_knowledge['python_version']}\n\n"
        
        if self.info_files:
            summary += "## .info 文件分析\n"
            for info_file in self.info_files:
                summary += f"### {os.path.basename(info_file)}\n"
                params = self.parse_info_file(info_file)
                summary += f"- **输入日志**: {len(params['inputs'])} 个\n"
                summary += f"- **输出日志**: {len(params['outputs'])} 个\n"
                summary += f"- **常量参数**: {len(params['constants'])} 个\n"
                if params['metadata']:
                    summary += f"- **元数据**: {params['metadata']}\n"
                summary += "\n"
        
        if self.pysh_files:
            summary += "## .pysh 文件分析\n"
            for pysh_file in self.pysh_files:
                summary += f"### {os.path.basename(pysh_file)}\n"
                analysis = self.analyze_pysh_file(pysh_file)
                summary += f"- **导入模块**: {', '.join(set(analysis['imports']))}\n"
                summary += f"- **数据模式**: {analysis['data_mode'] or '未检测到'}\n"
                summary += f"- **Geolog函数**: {', '.join(set(analysis['geolog_usage']))}\n"
                summary += f"- **变量使用**: {len(analysis['variables_used'])} 个\n"
                if analysis['functions_defined']:
                    summary += f"- **自定义函数**: {', '.join(analysis['functions_defined'])}\n"
                if analysis['missing_value_handling']:
                    summary += f"- **缺失值处理**: {', '.join(analysis['missing_value_handling'])}\n"
                summary += "\n"
        
        return summary
    
    def generate_code_template(self, template_name: str) -> str:
        """生成代码模板"""
        templates = {
            'basic': """#!/usr/bin/env python3
# python loglan
# 基础模板 - 逐行处理模式

# 导入必需的模块
import geolog
import numpy as np
import math

# 从Geolog逐行读取数据
while geolog.getrow():
    # 在这里添加您的处理代码
    # 示例：简单的数学计算
    # result = input_value * 2

    # 处理缺失值
    # if not math.isnan(input_value):
    #     result = input_value * 2

    # 将数据存储回Geolog
    geolog.putrow()
""",
            'table': """#!/usr/bin/env python3
# python loglan
# 表格处理模板 - 批量处理模式

# 导入必需的模块
import geolog
import numpy as np
import pandas as pd

# 从Geolog读取整个表
if geolog.gettable():
    # 在这里添加您的处理代码
    # 所有输入数据现在都是numpy数组

    # 示例：创建DataFrame进行数据分析
    # df = pd.DataFrame({
    #     'depth': depth,
    #     'value1': value1,
    #     'value2': value2
    # })

    # 示例：批量计算
    # output_log = input_log1 + input_log2

    # 示例：处理缺失值
    # result = np.nanmean(input_log)

    # 将数据存储回Geolog
    geolog.puttable()
""",
            'advanced': """#!/usr/bin/env python3
# python loglan
# 高级模板 - 包含参数和复杂处理

# 导入必需的模块
import geolog
import numpy as np
import math
import pandas as pd

# 参数在gettable/getrow之前可用
# 在这里可以访问和处理常量参数

# 从Geolog读取数据（选择适合的模式）
while geolog.getrow():
    # 复杂计算示例
    # temp_c = (temp_f - 32) * 5/9
    # pressure = depth * 0.433

    # 条件处理
    # if value > threshold:
    #     result = value * factor1
    # else:
    #     result = value * factor2

    # 缺失值处理
    # if not math.isnan(input1) and not math.isnan(input2):
    #     result = input1 + input2
    # else:
    #     result = math.nan

    # 将数据存储回Geolog
    geolog.putrow()
""",
            'matplotlib': """#!/usr/bin/env python3
# python loglan
# 可视化模板 - 包含matplotlib绘图

# 导入必需的模块
import geolog
import numpy as np
import pandas as pd

# 对于Intel发行版，设置matplotlib后端
try:
    import matplotlib
    matplotlib.use('TKAgg', warn=False, force=True)
    import matplotlib.pyplot as plt
except ImportError:
    print("matplotlib未安装，跳过绘图")

# 从Geolog读取数据
if geolog.gettable():
    # 数据处理
    # processed_data = input_data * conversion_factor

    # 可视化（如果matplotlib可用）
    try:
        plt.figure(figsize=(10, 6))
        plt.plot(depth, input_value, label='Input')
        plt.plot(depth, output_value, label='Output')
        plt.xlabel('Depth')
        plt.ylabel('Value')
        plt.title('Log Data Visualization')
        plt.legend()
        plt.grid(True)
        plt.show()
    except:
        print("绘图跳过")

    # 将数据存储回Geolog
    geolog.puttable()
""",
            'waxman_smits': """#!/usr/bin/env python3
# python loglan
# Waxman-Smits水饱和度计算模板

# 导入必需的模块
import geolog
import numpy as np
import math

# 逐行处理测井数据
while geolog.getrow():
    # 温度转换
    # tc = (tf - 32) / 1.8
    # tk = tc + 273.15

    # 计算地层水电阻率
    # rw_at_temp = rw * (rwt + 6.77) / (tf + 6.77)

    # 计算黏土束缚水饱和度
    # swb = vsh * cbw_int

    # 计算Qv（阳离子交换容量）
    # qv = swb / (0.6425 / ((rho_f * sal) ** 0.5) + 0.22)

    # Waxman-Smits B参数计算
    # b = calculate_b_factor(tc, rw_at_temp)

    # 水饱和度计算（迭代方法）
    # for i in range(100):
    #     sw_guess = i / 100.0
    #     sw_calc = ((rw / (rt * phit ** m)) / (1 + rw * b * qv / sw_guess)) ** (1/n)
    #     if sw_calc <= sw_guess:
    #         break

    # 或使用Crain非迭代方法
    # term1 = b * qv * rw75
    # term2 = (term1 ** 2 + 4 * (1 / phit ** m) * rw / rt) ** 0.5
    # sw = 0.5 * (-term1 + term2)

    # 限制饱和度在合理范围内
    # sw = max(0.0001, min(1.0, sw))

    # 将结果存储回Geolog
    geolog.putrow()
""",
            'scipy_filtering': """#!/usr/bin/env python3
# python loglan
# SciPy滤波和信号处理模板

# 导入必需的模块
import geolog
import numpy as np
import math
from scipy import signal
from scipy.ndimage import gaussian_filter, median_filter
from scipy.signal import savgol_filter, butter, lfilter

# 从Geolog读取数据
if geolog.gettable():
    # 1. 高斯滤波（平滑）
    gr_smooth = gaussian_filter(gr, sigma=2.0)

    # 2. 中值滤波（去除脉冲噪声）
    gr_median = median_filter(gr, size=5)

    # 3. Savitzky-Golay滤波（保留特征）
    window_length = 51  # 必须是奇数
    polyorder = 3
    gr_savgol = savgol_filter(gr, window_length, polyorder)

    # 4. 巴特沃斯低通滤波
    def butter_lowpass(cutoff, fs, order=5):
        nyquist = 0.5 * fs
        normal_cutoff = cutoff / nyquist
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        return b, a

    def butter_lowpass_filter(data, cutoff, fs, order=5):
        b, a = butter_lowpass(cutoff, fs, order=order)
        y = lfilter(b, a, data)
        return y

    # 应用巴特沃斯滤波
    gr_butter = butter_lowpass_filter(gr, cutoff=0.1, fs=1.0, order=5)

    # 5. 小波去噪
    try:
        import pywt
        coeffs = pywt.wavedec(gr, 'db4', level=3)
        threshold = 0.1 * np.max(coeffs[0])
        coeffs_thresh = [pywt.threshold(c, threshold) for c in coeffs]
        gr_denoised = pywt.waverec(coeffs_thresh, 'db4')
    except ImportError:
        print("PyWavelets未安装，跳过小波去噪")
        gr_denoised = gr.copy()

    # 选择最佳结果
    gr_filtered = gr_savgol.copy()

    # 将数据存储回Geolog
    geolog.puttable()
""",
            'sklearn_clustering': """#!/usr/bin/env python3
# python loglan
# Scikit-learn聚类和机器学习模板

# 导入必需的模块
import geolog
import numpy as np
import math
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA

# 从Geolog读取数据
if geolog.gettable():
    # 1. 提取测井参数特征
    features = np.column_stack([
        gr,
        rhob,
        nphi,
        resistivity
    ])

    # 2. 数据标准化
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)

    # 3. 处理缺失值
    valid_mask = ~np.isnan(features_scaled).any(axis=1)
    features_valid = features_scaled[valid_mask]

    # 4. K-Means聚类
    n_clusters = 5
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(features_valid)

    # 5. 主成分分析（PCA）- 可选
    pca = PCA(n_components=2)
    features_pca = pca.fit_transform(features_valid)

    # 6. 创建输出数组
    facies = np.full_like(depth, math.nan)
    facies[valid_mask] = clusters.astype(float)

    # 7. 可选：PCA结果
    pca1 = np.full_like(depth, math.nan)
    pca2 = np.full_like(depth, math.nan)
    pca1[valid_mask] = features_pca[:, 0]
    pca2[valid_mask] = features_pca[:, 1]

    # 将数据存储回Geolog
    geolog.puttable()
""",
            'opencv_imaging': """#!/usr/bin/env python3
# python loglan
# OpenCV成像测井处理模板

# 导入必需的模块
import geolog
import numpy as np
import math
import cv2

# 从Geolog读取数据
if geolog.gettable():
    # 假设image_log是成像数据（深度 x 方位）
    if image_log is not None and len(image_log) > 0:

        # 1. 归一化到0-255
        img_norm = cv2.normalize(
            image_log,
            None,
            0,
            255,
            cv2.NORM_MINMAX
        ).astype(np.uint8)

        # 2. 边缘检测（Canny）
        edges = cv2.Canny(img_norm, 50, 150)

        # 3. 形态学操作
        kernel = np.ones((3, 3), np.uint8)
        opened = cv2.morphologyEx(img_norm, cv2.MORPH_OPEN, kernel)
        closed = cv2.morphologyEx(img_norm, cv2.MORPH_CLOSE, kernel)

        # 4. 降噪
        denoised = cv2.fastNlMeansDenoising(img_norm, h=10, templateWindowSize=7, searchWindowSize=21)

        # 5. 直方图均衡化
        equ = cv2.equalizeHist(img_norm)

        # 6. 锐化
        kernel_sharp = np.array([[-1,-1,-1],
                               [-1, 9,-1],
                               [-1,-1,-1]])
        sharpened = cv2.filter2D(img_norm, -1, kernel_sharp)

        # 7. 创建输出（转回原始类型）
        image_processed = np.full_like(image_log, math.nan)
        image_edges = np.full_like(image_log, math.nan)
        image_denoised = np.full_like(image_log, math.nan)

        valid_mask = ~np.isnan(image_log)
        if np.sum(valid_mask) > 0:
            image_processed[valid_mask] = denoised[valid_mask].astype(np.float32)
            image_edges[valid_mask] = edges[valid_mask].astype(np.float32)
            image_denoised[valid_mask] = equ[valid_mask].astype(np.float32)

    # 将数据存储回Geolog
    geolog.puttable()
""",
            'advanced_visualization': """#!/usr/bin/env python3
# python loglan
# 高级matplotlib可视化模板

# 导入必需的模块
import geolog
import numpy as np
import pandas as pd
import math

# 设置matplotlib后端
try:
    import matplotlib
    matplotlib.use('TKAgg', warn=False, force=True)
    import matplotlib.pyplot as plt
    import matplotlib.gridspec as gridspec
    from matplotlib import cm
    matplotlib_available = True
except ImportError:
    print("matplotlib未安装，跳过绘图")
    matplotlib_available = False

# 从Geolog读取数据
if geolog.gettable():
    # 数据处理
    # processed_data = input_data * conversion_factor

    # 高级可视化（如果matplotlib可用）
    if matplotlib_available:
        # 创建多子图布局
        fig = plt.figure(figsize=(15, 10))
        gs = gridspec.GridSpec(3, 4, figure=fig)

        # 轨迹1: GR和SP
        ax1 = fig.add_subplot(gs[0:3, 0])
        ax1.plot(gr, depth, 'g', label='GR', linewidth=0.5)
        ax1.plot(sp, depth, 'r', label='SP', linewidth=0.5)
        ax1.set_xlabel('GR (API) / SP (mV)')
        ax1.set_ylabel('Depth (m)')
        ax1.invert_yaxis()
        ax1.legend(loc='upper right')
        ax1.grid(True, alpha=0.3)

        # 轨迹2: 电阻率（对数坐标）
        ax2 = fig.add_subplot(gs[0:3, 1], sharey=ax1)
        ax2.semilogx(rt, depth, 'b', label='RT', linewidth=0.5)
        ax2.semilogx(ri, depth, 'orange', label='RI', linewidth=0.5)
        ax2.set_xlabel('Resistivity (Ω·m)')
        ax2.legend(loc='upper right')
        ax2.grid(True, alpha=0.3)
        plt.setp(ax2.get_yticklabels(), visible=False)

        # 轨迹3: 密度和中子
        ax3 = fig.add_subplot(gs[0:3, 2], sharey=ax1)
        ax3.plot(rhob, depth, 'r', label='RHOB', linewidth=0.5)
        ax3.plot(nphi * 100, depth, 'b', label='NPHI (PU)', linewidth=0.5)
        ax3.set_xlabel('RHOB (g/cc) / NPHI (PU)')
        ax3.legend(loc='upper right')
        ax3.grid(True, alpha=0.3)
        plt.setp(ax3.get_yticklabels(), visible=False)

        # 轨迹4: 岩相饼图
        ax4 = fig.add_subplot(gs[0, 3])
        facies_counts = pd.Series(facies).value_counts()
        colors = plt.cm.Set3(np.linspace(0, 1, len(facies_counts)))
        ax4.pie(facies_counts.values, labels=facies_counts.index, autopct='%1.1f%%',
                colors=colors, startangle=90)
        ax4.set_title('Facies Distribution')

        # 轨迹5: T2谱热图
        ax5 = fig.add_subplot(gs[1, 3])
        if t2_spectrum is not None:
            im = ax5.imshow(t2_spectrum.T, aspect='auto', cmap='viridis')
            ax5.set_xlabel('Depth Index')
            ax5.set_ylabel('T2 Bins')
            plt.colorbar(im, ax=ax5, label='T2 Spectrum')
        else:
            ax5.text(0.5, 0.5, 'No T2 Data', ha='center', va='center',
                    transform=ax5.transAxes, fontsize=12)

        # 轨迹6: 交叉图（带颜色编码）
        ax6 = fig.add_subplot(gs[2, 3])
        scatter = ax6.scatter(rhob, nphi * 100, c=depth, cmap='jet',
                           s=10, alpha=0.5, edgecolors='none')
        ax6.set_xlabel('RHOB (g/cc)')
        ax6.set_ylabel('NPHI (PU)')
        ax6.set_title('Neutron-Density Crossplot')
        plt.colorbar(scatter, ax=ax6, label='Depth (m)')

        plt.tight_layout()
        plt.savefig('well_log_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("图表已保存: well_log_analysis.png")

    # 将数据存储回Geolog
    geolog.puttable()
""",
            'pygg_basic': """#!/usr/bin/env python3
# Python GG 模板 - 数据库直接访问
# 使用 pygg 模块直接访问 Geolog 数据库

# 导入 pygg 模块
import pygg

# 初始化项目
status = pygg.init("MY_PROJECT")
if status <= 0:
    print("项目�失败")
    exit(1)

# 可选：启动审计
# pygg.audit("my_script", "数据批处理")

# 打开井（读取）
well_name = "PARADIGM"
status = pygg.open("WELL", "STATUS_OLD", well_name)
if status <= 0:
    print(f"打开井失败: {well_name}")
    pygg.term()
    exit(1)

# 打开集（读取）
set_name = "WIRE"
status = pygg.open("SET", "STATUS_OLD", set_name)
if status <= 0:
    print(f"打开集失败: {set_name}")
    pygg.term()
    exit(1)

# 打开曲线（读取）
log_names = ["GR", "RT", "DEPTH"]
for log_name in log_names:
    status = pygg.open("LOG", "STATUS_OLD", log_name)
    if status <= 0:
        print(f"打开曲线失败: {log_name}")
        pygg.term()
        exit(1)

# 读取数据
while pygg.read():
    # 获取曲线值
    gr_val = pygg.getn("LOG", "GR")
    rt_val = pygg.getn("LOG", "RT")
    depth_val = pygg.getn("LOG", "DEPTH")
    
    # 检查缺失值
    if not pygg.IS_MISS_FLOAT(gr_val) and not pygg.IS_MISS_FLOAT(rt_val):
        # 处理数据
        # 例如：计算
        # processed_gr = gr_val * 1.0
        pass

# 关闭曲线
for log_name in log_names:
    pygg.close("LOG", "STATUS_OLD", log_name)

# 关闭集
pygg.close("SET", "STATUS_OLD", set_name)

# 关闭井
pygg.close("WELL", "STATUS_OLD", well_name)

# 终止项目
pygg.term()
""",
            'pygg_write': """#!/usr/bin/env python3
# Python GG 模板 - 写入数据到数据库
# 使用 pygg 模块创建新曲线并写入数据

# 导入 pygg 模块
import pygg
import numpy as np

# 初始化项目
status = pygg.init("MY_PROJECT")
if status <= 0:
    print("项目�失败")
    exit(1)

# 启动审计
pygg.audit("my_script", "创建新曲线")

# 打开井（写入）
well_name = "PARADIGM"
status = pygg.open("WELL", "STATUS_NEW", well_name)
if status <= 0:
    print(f"打开井失败: {well_name}")
    pygg.term()
    exit(1)

# 打开集（写入）
set_name = "WIRE"
status = pygg.open("SET", "STATUS_NEW", set_name)
if status <= 0:
    print(f"打开集失败: {set_name}")
    pygg.term()
    exit(1)

# 打开曲线（写入）
output_log_name = "NEW_LOG"
status = pygg.open("LOG", "STATUS_NEW", output_log_name)
if status <= 0:
    print(f"打开曲线失败: {output_log_name}")
    pygg.term()
    exit(1)

# 写入数据（示例）
# 假设我们已经从其他来源读取了数据
data_values = [100.0, 105.0, 110.0, 108.0, 112.0]
depth_values = [1000.0, 1000.1524, 1000.3048, 1000.4572, 1000.6096]

# 写入数据帧
for i in range(len(data_values)):
    # 写入深度
    pygg.putn("LOG", "DEPTH", depth_values[i])
    # 写入值
    pygg.putn("LOG", output_log_name, data_values[i])
    
    # 写入数据到数据库
    status = pygg.write()
    if status <= 0:
        print("写入数据失败")
        break

# 关闭曲线（写入）
pygg.close("LOG", "STATUS_NEW", output_log_name)

# 关闭集（写入）
pygg.close("SET", "STATUS_NEW", set_name)

# 关闭井（写入）
pygg.close("WELL", "STATUS_NEW", well_name)

# 终止项目
pygg.term()
""",
            'pygg_report': """#!/usr/bin/env python3
# Python GG 模板 - 项目报告
# 报告项目中的所有井、集、曲线和属性

# 导入 pygg 模块
import pygg

# 初始化项目
status = pygg.init("MY_PROJECT")
if status <= 0:
    print("项目�失败")
    exit(1)

# 启动审计
pygg.audit("project_report", "项目结构报告")

# 获取井列表
# 注意：pygg 没有直接列出井的函数
# 需要知道井名或从其他方式获取

well_name = "PARADIGM"
print(f"\\n报告井: {well_name}")
print("=" * 50)

# 打开井（读取）
status = pygg.open("WELL", "STATUS_OLD", well_name)
if status <= 0:
    print(f"打开井失败: {well_name}")
    pygg.term()
    exit(1)

# 打开集（读取）
set_name = "WIRE"
status = pygg.open("SET", "STATUS_OLD", set_name)
if status <= 0:
    print(f"打开集失败: {set_name}")
    pygg.term()
    exit(1)

print(f"\\n集: {set_name}")
print("-" * 50)

# 打开曲线（读取）
log_names = ["GR", "RT", "RHOB", "NPHI", "DEPTH"]
for log_name in log_names:
    status = pygg.open("LOG", "STATUS_OLD", log_name)
    if status > 0:
        # 读取第一条记录获取信息
        pygg.read()
        
        # 获取曲线属性
        log_comment = pygg.getc("COMMENT", log_name)
        log_unit = pygg.getc("ATTRIBUTE", f"{log_name}.UNITS")
        
        print(f"曲线: {log_name:20s} 单位: {log_unit:15s}")
        if log_comment:
            print(f"      注释: {log_comment}")
        
        # 关闭曲线
        pygg.close("LOG", "STATUS_OLD", log_name)
    else:
        print(f"曲线 {log_name} 不存在或无法打开")

# 关闭集
pygg.close("SET", "STATUS_OLD", set_name)

# 关闭井
pygg.close("WELL", "STATUS_OLD", well_name)

# 终止项目
pygg.term()

print("\\n报告完成")
"""
        }

        return templates.get(template_name, templates['basic'])

    def generate_info_file(self, config: Dict) -> str:
        """生成符合新规范的.info文件

        基于examples文件夹和用户提供的rt_wavelet_enhancement-m.info生成
        确保格式完全符合Geolog标准

        关键格式要点（基于rt_wavelet_enhancement-m.info）：
        1. 列标题：MODE:  ARG:         VAR:         TYPE:     REPEAT: DEFAULT: VALIDATION:        LOCATION: UNIT: VISIBLE: TAB_LABEL: COMMENT=
        2. 包含 MARKDOWN = Yes 字段
        3. FILE类型的参数LOCATION字段为空
        4. 常量参数使用LOCATION=PARAMETER（不是CONSTANT）
        5. 常量参数类型使用ALPHA, INT, REAL（不是NAME_ALPHA等）
        6. LOG类型的参数使用NAME_REAL等类型
        7. 所有列之间使用固定数量的空格分隔

        参数:
            config: 包含以下键的字典:
                - script_name: 脚本名称（不带扩展名，可选）
                - description: 详细描述（可选，可用于DESCRIPTION_DETAIL）
                - inputs: 输入变量列表 [{'var': 'name', 'type': 'NAME_REAL', 'unit': 'GAPI', 'comment': '说明', 'default': 'DEP'}]
                - outputs: 输出变量列表 [{'var': 'name', 'type': 'NAME_REAL', 'unit': 'GAPI', 'comment': '说明', 'default': 'OUT'}]
                - constants: 常量参数列表 [{'var': 'name', 'type': 'REAL', 'default': '1.0', 'validation': '', 'comment': '说明'}]
                         注意：constants中的type应该是ALPHA, INT, REAL，不是NAME_ALPHA等

        返回:
            .info文件内容字符串
        """
        lines = []

        # 文件头 - 基于rt_wavelet_enhancement-m.info的格式
        lines.append("# spec : ")
        lines.append("LANGUAGE = PYTHON")

        # 添加DESCRIPTION_DETAIL（空字符串或用户提供的描述）
        if 'description' in config and config['description']:
            # 转义特殊字符
            desc = config['description'].replace('"', '\\"')
            lines.append(f'DESCRIPTION_DETAIL = "{desc}"')
        else:
            # 默认为空字符串
            lines.append('DESCRIPTION_DETAIL = ""')

        # 添加MARKDOWN标志
        lines.append("MARKDOWN = Yes")

        # 列标题 - 精确匹配rt_wavelet_enhancement-m.info的格式
        lines.append("MODE:  ARG:         VAR:         TYPE:     REPEAT: DEFAULT: VALIDATION:        LOCATION: UNIT: VISIBLE: TAB_LABEL: COMMENT=")
        lines.append("#====  ====         ====         =====     ======= ======== ===========        ========= ===== ======== ========== ========                         ")

        # 输入变量（FILE_IN和FILE_OUT是必须的）
        # FILE类型：LOCATION字段为空
        lines.append("INPUT  FILE_IN      file_in      FILE      \"\"      \"\"       \"\"                 \"\"        \"\"    TRUE     \"\"         \"Input table (pipe).\"")
        lines.append("INPUT  FILE_OUT     file_out     FILE      \"\"      \"\"       \"\"                 \"\"        \"\"    TRUE     \"\"         \"Output table (pipe).\"")

        # 常量参数 - LOCATION为PARAMETER，类型为ALPHA/INT/REAL
        if 'constants' in config and config['constants']:
            for const in config['constants']:
                validation = const.get('validation', '')
                var_name = const['var'].upper()
                var_lower = const['var']
                type_name = const['type']  # 应该是ALPHA, INT, REAL
                default = const['default']
                comment = const.get('comment', '')

                # 确定UNIT字段（对于ALPHA类型通常是ALPHA，其他为空）
                if type_name == 'ALPHA':
                    unit = 'ALPHA'
                else:
                    unit = ''

                # 格式参考：INPUT  WAVELET_TYPE wavelet_type ALPHA     ""      sym4     haar,db4,sym4,coif PARAMETER ALPHA TRUE     ""         "小波类型"
                lines.append(f"INPUT  {var_name:<13} {var_lower:<13} {type_name:<9} \"\"      {default:<8} {validation:<18} PARAMETER {unit:<5} TRUE     \"\"         \"{comment}\"")

        # 输入变量（LOG类型的输入） - LOCATION为LOG，类型为NAME_REAL等
        if 'inputs' in config and config['inputs']:
            for inp in config['inputs']:
                var_name = inp['var'].upper()
                var_lower = inp['var']
                type_name = inp['type']  # 应该是NAME_REAL, NAME_INT等
                unit = inp.get('unit', '')
                comment = inp.get('comment', '')
                default = inp.get('default', inp['var'].upper())
                # 格式参考：INPUT  DEPTH        depth        NAME_REAL ""      DEPTH    ""                 LOG       ""    TRUE     ""         DEPTH
                lines.append(f"INPUT  {var_name:<13} {var_lower:<13} {type_name:<9} \"\"      {default:<8} \"\"                 LOG       {unit:<5} TRUE     \"\"         {comment}")

        # 输出变量 - LOCATION为LOG，类型为NAME_REAL等
        if 'outputs' in config and config['outputs']:
            for out in config['outputs']:
                var_name = out['var'].upper()
                var_lower = out['var']
                type_name = out['type']  # 应该是NAME_REAL, NAME_INT等
                unit = out.get('unit', '')
                comment = out.get('comment', '')
                default = out.get('default', out['var'].upper())
                # 格式参考：OUTPUT RT_ENG       rt_eng       NAME_REAL ""      RT_ENG   ""                 LOG       ""    TRUE     ""         Resistivity
                lines.append(f"OUTPUT {var_name:<13} {var_lower:<13} {type_name:<9} \"\"      {default:<8} \"\"                 LOG       {unit:<5} TRUE     \"\"         {comment}")

        return '\n'.join(lines) + '\n'

    def generate_pysh_file(self, config: Dict) -> str:
        """生成.pysh文件

        参数:
            config: 包含以下键的字典:
                - template: 模板名称（'basic', 'table', 'advanced'等）
                - imports: 额外导入的模块列表
                - processing_code: 核心处理代码字符串
                - data_mode: 数据模式（'row' 或 'table'）

        返回:
            .pysh文件内容字符串
        """
        template = config.get('template', 'basic')
        template_code = self.generate_code_template(template)

        # 提取文件头和导入部分
        lines = template_code.split('\n')
        header_lines = []
        import_lines = []

        for line in lines:
            if line.startswith('#') or line.strip() == '':
                header_lines.append(line)
            elif line.startswith('import '):
                import_lines.append(line)
                # 添加额外导入
                if 'imports' in config:
                    for extra_import in config['imports']:
                        if extra_import not in '\n'.join(import_lines):
                            import_lines.append(f"import {extra_import}")
            else:
                break

        # 查找数据读取和写入的模式
        if config.get('data_mode', 'row') == 'table':
            read_pattern = 'if geolog.gettable():'
            write_pattern = '    geolog.puttable()'
        else:
            read_pattern = 'while geolog.getrow():'
            write_pattern = '    geolog.putrow()'

        # 构建完整代码
        result = '\n'.join(header_lines) + '\n'
        result += '\n'.join(import_lines) + '\n\n'

        # 添加注释标记
        result += "# ===== 核心处理代码 =====\n"
        result += config.get('processing_code', '# 在这里添加您的处理代码\n')
        result += "# ===== 核心处理代码结束 =====\n\n"

        # 添加数据读写框架
        result += "# 从Geolog读取数据\n"
        result += read_pattern + '\n'
        result += "    # 在这里调用您的处理函数\n"
        result += write_pattern + '\n'

        return result

    def generate_files(self, script_name: str, description: str, inputs: List[Dict], outputs: List[Dict],
                       constants: List[Dict], processing_code: str, template: str = 'table') -> Dict[str, str]:
        """生成完整的.info和.pysh文件

        参数:
            script_name: 脚本名称（不带扩展名）
            description: 详细描述（Markdown格式）
            inputs: 输入变量列表
            outputs: 输出变量列表
            constants: 常量参数列表
            processing_code: 核心处理代码
            template: 模板类型（'basic', 'table', 'advanced'）

        返回:
            字典包含 'info_content' 和 'pysh_content'
        """
        # 生成.info文件内容
        info_config = {
            'script_name': script_name,
            'description': description,
            'inputs': inputs,
            'outputs': outputs,
            'constants': constants
        }
        info_content = self.generate_info_file(info_config)

        # 生成.pysh文件内容
        pysh_config = {
            'template': template,
            'processing_code': processing_code,
            'data_mode': 'table' if template == 'table' else 'row'
        }
        pysh_content = self.generate_pysh_file(pysh_config)

        return {
            'info_content': info_content,
            'pysh_content': pysh_content
        }
    
    def validate_script(self, pysh_path: str) -> Dict[str, List[str]]:
        """验证脚本，返回详细的问题报告"""
        result = {
            'errors': [],
            'warnings': [],
            'suggestions': [],
            'best_practices': []
        }
        
        try:
            with open(pysh_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查必需的导入
            if 'import geolog' not in content:
                result['errors'].append('缺少 geolog 模块导入')
            
            # 检查数据读取函数
            if 'geolog.getrow()' not in content and 'geolog.gettable()' not in content:
                result['warnings'].append('未找到 geolog.getrow() 或 geolog.gettable() 调用')
            
            # 检查数据写入函数
            if 'geolog.putrow()' not in content and 'geolog.puttable()' not in content:
                result['warnings'].append('未找到 geolog.putrow() 或 geolog.puttable() 调用')
            
            # 检查模式混用
            if 'geolog.getrow()' in content and 'geolog.gettable()' in content:
                result['errors'].append('不能同时使用 getrow() 和 gettable() 模式')
            
            if 'geolog.putrow()' in content and 'geolog.puttable()' in content:
                result['errors'].append('不能同时使用 putrow() 和 puttable() 模式')
            
            # 检查缺失值处理
            if 'numpy' in content.lower() and 'nan' in content.lower():
                if 'math.isnan' not in content and not any(x in content for x in ['nansum', 'nanmean', 'nanmedium']):
                    result['suggestions'].append('考虑使用 math.isnan() 或 numpy 的 nan 函数处理缺失值')
            
            # 检查编码
            if '# -*- coding:' not in content:
                result['best_practices'].append('建议在文件开头添加编码声明（虽然Geolog默认使用UTF-8）')
            
            # 检查整数数组
            if 'dtype=int64' not in content:
                result['best_practices'].append('对于整数数组，建议指定 numpy dtype=int64 以匹配Geolog的32位整数需求')
            
        except Exception as e:
            result['errors'].append(f'文件读取错误: {e}')
        
        return result
    
    def suggest_improvements(self, pysh_path: str) -> List[str]:
        """基于PDF规范建议改进"""
        suggestions = []
        
        try:
            with open(pysh_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 基于PDF规范的改进建议
            if '# python loglan' not in content and '#!/usr/bin/env python3' not in content:
                suggestions.append('建议添加标准的Geolog Python文件头')
            
            # 检查常用库的使用
            common_packages = self.pdf_knowledge['common_packages']['core']
            for package in common_packages:
                if package == 'numpy':
                    if package not in content.lower():
                        suggestions.append(f'考虑使用 {package} 库进行科学计算和数组处理（必需）')
                elif package == 'pandas':
                    if package not in content.lower():
                        suggestions.append(f'考虑使用 {package} 库进行数据分析和DataFrame操作')
                elif package == 'matplotlib':
                    if package not in content.lower():
                        suggestions.append(f'考虑使用 {package} 库进行数据可视化')
                elif package == 'scipy':
                    if package not in content.lower():
                        suggestions.append(f'考虑使用 {package} 库进行信号处理、滤波和科学计算')
            
            # 建议高级库的使用（基于应用场景）
            if 'gr' in content.lower() or 'rt' in content.lower() or 'resistivity' in content.lower():
                if 'scipy' not in content.lower():
                    suggestions.append('考虑使用 scipy.signal 进行曲线滤波和去噪')
                if 'sklearn' not in content.lower():
                    suggestions.append('考虑使用 sklearn 进行测井相分类和聚类分析')
            
            if 'image' in content.lower() or 'fmi' in content.lower() or 'emi' in content.lower():
                if 'cv2' not in content.lower():
                    suggestions.append('考虑使用 OpenCV (cv2) 进行成像测井处理和边缘检测')
                if 'scipy.ndimage' not in content.lower():
                    suggestions.append('考虑使用 scipy.ndimage 进行图像处理和形态学操作')
            
            if 't2' in content.lower() or 'nmr' in content.lower():
                if 'matplotlib' not in content.lower():
                    suggestions.append('考虑使用 matplotlib 进行T2谱热图可视化')
                if 'scipy.signal' not in content.lower():
                    suggestions.append('考虑使用 scipy.signal 进行T2谱分析')
            
            # 检查注释
            comment_lines = len([line for line in content.split('\n') if line.strip().startswith('#')])
            code_lines = len([line for line in content.split('\n') if line.strip() and not line.strip().startswith('#')])
            if code_lines > 10 and comment_lines / code_lines < 0.1:
                suggestions.append('建议增加代码注释以提高可读性')
            
            # 检查变量命名
            uppercase_vars = re.findall(r'\b([A-Z][A-Z_]+)\b', content)
            if uppercase_vars:
                suggestions.append(f'Geolog变量名应使用小写：{", ".join(uppercase_vars[:3])}...')
            
            # 检查matplotlib后端设置
            if 'matplotlib' in content.lower():
                if 'matplotlib.use' not in content:
                    suggestions.append('建议设置matplotlib后端（例如：matplotlib.use("TKAgg", warn=False, force=True)）')
            
        except Exception as e:
            suggestions.append(f'分析错误: {e}')
        
        return suggestions

if __name__ == "__main__":
    # 示例使用
    agent = GeologPythonAgent('d:\\Python_Project\\geolog')
    print(agent.generate_summary())
    
    # 生成代码模板
    print("\n=== 基础代码模板 ===")
    print(agent.generate_code_template('basic'))
    
    # 验证脚本
    if agent.pysh_files:
        validation = agent.validate_script(agent.pysh_files[0])
        print("\n=== 脚本验证结果 ===")
        if validation['errors']:
            print("错误:")
            for error in validation['errors']:
                print(f"  - {error}")
        if validation['warnings']:
            print("警告:")
            for warning in validation['warnings']:
                print(f"  - {warning}")
        if validation['suggestions']:
            print("建议:")
            for suggestion in validation['suggestions']:
                print(f"  - {suggestion}")
        
        # 改进建议
        improvements = agent.suggest_improvements(agent.pysh_files[0])
        if improvements:
            print("\n=== 改进建议 ===")
            for improvement in improvements:
                print(f"  - {improvement}")
        
        # 变量映射
        if agent.info_files:
            mapping = agent.generate_variable_mapping(agent.pysh_files[0], agent.info_files[0])
            print("\n=== 变量映射分析 ===")
            print(f"匹配的输入变量: {len(mapping['input_variables'])}")
            print(f"匹配的输出变量: {len(mapping['output_variables'])}")
            print(f"匹配的常量: {len(mapping['constants'])}")
            if mapping['unmatched_info_vars']:
                print("未在.pysh中使用的变量:")
                for var in mapping['unmatched_info_vars'][:5]:
                    print(f"  - {var}")
            if mapping['unmatched_pysh_vars']:
                print(f"未在.info中定义的变量: {', '.join(mapping['unmatched_pysh_vars'][:5])}")
    
    print("\n=== PDF知识要点 ===")
    print(f"推荐Python版本: {agent.pdf_knowledge['python_version']}")
    print(f"文件编码: {agent.pdf_knowledge['encoding']}")
    print(f"缺失值表示: {agent.pdf_knowledge['missing_value']}")
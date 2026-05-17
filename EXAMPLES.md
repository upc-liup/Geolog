# Geolog AI 智能体 - 实用示例集

## 📚 示例目录

1. [基础计算示例](#1-基础计算示例)
2. [数据处理示例](#2-数据处理示例)
3. [批量处理示例](#3-批量处理示例)
4. [GUI开发示例](#4-gui开发示例)
5. [成像测井示例](#5-成像测井示例)
6. [声波测井示例](#6-声波测井示例)
7. [GeologSQL示例](#7-geologsql示例)
8. [成果表生成示例](#8-成果表生成示例)
9. [高级应用示例](#9-高级应用示例)

---

## 1. 基础计算示例

### 示例1.1：计算密度孔隙度

**需求**：
创建一个Python Loglan脚本计算密度孔隙度。

**用户输入**：
```
创建一个Python Loglan脚本计算密度孔隙度：
- 输入曲线：RHOB（体积密度，2.0-3.0 g/cc）
- 参数：RHO_MA（骨架密度，2.65），RHO_FL（流体密度，1.0）
- 输出曲线：PHID（密度孔隙度，0-0.4）
- 使用table模式
- 包含详细注释
```

**智能体输出 - .pysh文件**：
```python
#!/usr/bin/env python3
# python loglan
# 功能：计算密度孔隙度
# 公式：PHID = (RHO_MA - RHOB) / (RHO_MA - RHO_FL)

import geolog
import numpy as np
import math

# 读取参数
file_in = geolog.getarg("file_in")
file_out = geolog.getarg("file_out")
rho_ma = geolog.getarg("rho_ma")  # 骨架密度（g/cc）
rho_fl = geolog.getarg("rho_fl")  # 流体密度（g/cc）

# 读取输入数据（table模式 - 批量处理）
depth, rhob = geolog.gettable(file_in, ['depth', 'rhob'])

# 创建输出数组（使用NaN填充）
phid = np.full_like(rhob, math.nan)

# 批量处理数据
for i in range(len(rhob)):
    # 检查数据有效性
    if not math.isnan(rhob[i]):
        # 计算密度孔隙度
        phid[i] = (rho_ma - rhob[i]) / (rho_ma - rho_fl)
        
        # 限制孔隙度范围（0-1.0）
        if phid[i] < 0.0:
            phid[i] = 0.0001  # 最小孔隙度
        elif phid[i] > 1.0:
            phid[i] = 1.0  # 最大孔隙度
    else:
        # 缺失值保持NaN
        phid[i] = math.nan

# 写回数据到输出表
geolog.puttable(file_out, [depth, rhob, phid])
```

**智能体输出 - .info文件**：
```
# spec : Density Porosity Calculation
LANGUAGE = PYTHON
DESCRIPTION_DETAIL = "计算密度孔隙度程序\#\# 概述\n本程序用于计算密度孔隙度，使用公式：PHID = (RHO_MA - RHOB) / (RHO_MA - RHO_FL)\n\#\# 可调参数\n- `rho_ma`: 骨架密度（g/cc）\n  - 默认值：2.65\n  - 范围：2.5-3.0\n- `rho_fl`: 流体密度（g/cc）\n  - 默认值：1.0\n  - 范围：0.8-1.2"
MARKDOWN = Yes
MODE:  ARG:         VAR:         TYPE:     REPEAT: DEFAULT: VALIDATION:        LOCATION: UNIT: VISIBLE: TAB_LABEL: COMMENT=
#====  ====         ====         =====     ======= ======== ===========        ========= ===== ======== ========== ========                          
INPUT  FILE_IN     file_in      FILE      ""      ""       ""                 ""        ""    TRUE     ""         "Input table (pipe.)"
INPUT  FILE_OUT    file_out     FILE      ""      ""       ""                 ""        ""    TRUE     ""         "Output table (pipe.)"
INPUT  RHOB        rhob         NAME_REAL ""      ""       ""                 LOG       G/CC  TRUE     ""         "Bulk density"
INPUT  DEPTH       depth        NAME_REAL ""      ""       ""                 LOG       METRES TRUE     ""         "Downhole depth"
INPUT  RHO_MA      rho_ma       REAL      ""      "2.65"   ""                 CONSTANT  G/CC  TRUE     ""         "Matrix density"
INPUT  RHO_FL      rho_fl       REAL      ""      "1.0"    ""                 CONSTANT  G/CC  TRUE     ""         "Fluid density"
OUTPUT PHID        phid         NAME_REAL ""      ""       ""                 LOG       V/V   TRUE     ""         "Density porosity"
```

---

### 示例1.2：计算泥质含量（GR法）

**需求**：
创建一个Loglan脚本计算泥质含量。

**用户输入**：
```
创建一个传统Loglan脚本计算泥质含量：
- 输入曲线：GR（自然伽马，API）
- 参数：GR_CLEAN（纯砂岩GR值，20），GR_SHALE（纯泥岩GR值，120）
- 输出曲线：VSH（泥质含量，v/v）
- 使用公式：VSH = (GR - GR_CLEAN) / (GR_SHALE - GR_CLEAN)
- 限制范围：0-1.0
```

**智能体输出 - .lls文件**：
```loglan
# Loglan Script
# 功能：计算泥质含量（GR法）
# 公式：VSH = (GR - GR_CLEAN) / (GR_SHALE - GR_CLEAN)

# 全局变量
GLOBAL GR AS REAL
GLOBAL VSH AS REAL

# 常量
CONSTANT GR_CLEAN = 20.0
CONSTANT GR_SHALE = 120.0

# 泥质含量计算函数
FUNCTION CalculateVShale(gr_value) AS REAL
    LOCAL vsh AS REAL
    
    # 计算泥质含量
    IF GR_SHALE = GR_CLEAN THEN
        vsh = 0.0
    ELSE
        vsh = (gr_value - GR_CLEAN) / (GR_SHALE - GR_CLEAN)
    ENDIF
    
    # 限制范围（0-1.0）
    IF vsh < 0.0 THEN
        vsh = 0.0
    ELSEIF vsh > 1.0 THEN
        vsh = 1.0
    ENDIF
    
    RETURN vsh
ENDFUNCTION

# 主程序
MAIN
    LOCAL depth AS REAL
    LOCAL gr_value AS REAL
    LOCAL vsh_value AS REAL
    LOCAL i AS INTEGER
    
    # 获取数据点数量
    LOCAL n AS INTEGER
    n = GETCURVECOUNT()
    
    # 逐点处理
    FOR i = 1 TO n DO
        # 读取深度和GR值
        depth = GETDEPTH(i)
        gr_value = GETVAL(GR, depth)
        
        # 检查数据有效性
        IF gr_value > -999.0 THEN
            # 计算泥质含量
            vsh_value = CalculateVShale(gr_value)
            
            # 写入输出曲线
            PUTVAL(VSH, depth, vsh_value)
        ENDIF
    ENDFOR
    
ENDMAIN
```

---

### 示例1.3：计算水饱和度（Archie公式）

**需求**：
创建一个Python Loglan脚本计算水饱和度。

**用户输入**：
```
创建一个Python Loglan脚本计算水饱和度：
- 输入曲线：RT（电阻率，OHMM），PHIE（有效孔隙度，v/v）
- 参数：RW（地层水电阻率，0.03 OHMM），M（胶结指数，2.0），N（饱和度指数，2.0）
- 输出曲线：SW（含水饱和度，v/v）
- 使用Archie公式：SW = ((a * RW) / (PHIE^M * RT))^(1/N)
- 限制范围：0-1.0
```

**智能体输出 - .pysh文件**：
```python
#!/usr/bin/env python3
# python loglan
# 功能：计算水饱和度（Archie公式）
# 公式：SW = ((a * RW) / (PHIE^M * RT))^(1/N)

import geolog
import numpy as np
import math

# 读取参数
file_in = geolog.getarg("file_in")
file_out = geolog.getarg("file_out")
rw = geolog.getarg("rw")  # 地层水电阻率（OHMM）
m = geolog.getarg("m")    # 胶结指数
n = geolog.getarg("n")    # 饱和度指数
a = 1.0  # 岩性系数（通常为1.0）

# 读取输入数据（table模式）
depth, rt, phie = geolog.gettable(file_in, ['depth', 'rt', 'phie'])

# 创建输出数组
sw = np.full_like(rt, math.nan)

# Archie公式计算
for i in range(len(rt)):
    # 检查数据有效性
    if not math.isnan(rt[i]) and not math.isnan(phie[i]) and phie[i] > 0.0:
        # 计算地层因子
        f = a / (phie[i] ** m)
        
        # 计算水饱和度（Archie公式）
        sw[i] = ((f * rw) / rt[i]) ** (1.0 / n)
        
        # 限制范围（0-1.0）
        if sw[i] > 1.0:
            sw[i] = 1.0
        elif sw[i] < 0.0:
            sw[i] = 0.0
    else:
        # 缺失值或无效数据
        sw[i] = math.nan

# 写回数据
geolog.puttable(file_out, [depth, rt, phie, sw])
```

---

## 2. 数据处理示例

### 示例2.1：曲线平滑处理

**需求**：
创建一个Python Loglan脚本对曲线进行平滑处理。

**用户输入**：
```
创建一个Python Loglan脚本对GR曲线进行平滑：
- 输入曲线：GR（自然伽马）
- 参数：WINDOW_SIZE（窗口大小，31），METHOD（平滑方法，mean）
- 输出曲线：GR_SMOOTH（平滑后的GR）
- 使用移动平均法
```

**智能体输出**：
```python
#!/usr/bin/env python3
# python loglan
# 功能：曲线平滑处理（移动平均法）

import geolog
import numpy as np
import math

# 读取参数
file_in = geolog.getarg("file_in")
file_out = geolog.getarg("file_out")
window_size = geolog.getarg("window_size")  # 窗口大小
method = geolog.getarg("method")  # 平滑方法

# 读取输入数据
depth, gr = geolog.gettable(file_in, ['depth', 'gr'])

# 创建输出数组
gr_smooth = np.full_like(gr, math.nan)

# 移动平均平滑
half_window = window_size // 2
n = len(gr)

for i in range(n):
    # 计算窗口范围
    start = max(0, i - half_window)
    end = min(n, i + half_window + 1)
    
    # 提取窗口数据
    window_data = gr[start:end]
    
    # 过滤缺失值
    valid_mask = ~np.isnan(window_data)
    valid_data = window_data[valid_mask]
    
    # 计算平滑值
    if len(valid_data) > 0:
        if method == "mean":
            gr_smooth[i] = np.mean(valid_data)
        elif method == "median":
            gr_smooth[i] = np.median(valid_data)
    else:
        gr_smooth[i] = math.nan

# 写回数据
geolog.puttable(file_out, [depth, gr, gr_smooth])
```

---

### 示例2.2：小波变换去噪

**需求**：
创建一个Python Loglan脚本使用小波变换对曲线去噪。

**用户输入**：
```
创建一个Python Loglan脚本对RT曲线进行小波变换去噪：
- 输入曲线：RT（电阻率）
- 参数：WAVELET（小波类型，sym4），LEVEL（分解层级，3），THRESHOLD（阈值系数，0.05）
- 输出曲线：RT_ENH（增强后的RT）
- 使用PyWavelets库
```

**智能体输出**：
```python
#!/usr/bin/env python3
# python loglan
# 功能：小波变换去噪

import geolog
import numpy as np
import math
import pywt  # PyWavelets库

# 读取参数
file_in = geolog.getarg("file_in")
file_out = geolog.getarg("file_out")
wavelet = geolog.getarg("wavelet")  # 小波类型
level = geolog.getarg("level")  # 分解层级
threshold_coef = geolog.getarg("threshold")  # 阈值系数

# 读取输入数据
depth, rt = geolog.gettable(file_in, ['depth', 'rt'])

# 创建输出数组
rt_enh = np.full_like(rt, math.nan)

# 小波变换去噪
for i in range(len(rt)):
    if not math.isnan(rt[i]):
        try:
            # 提取局部数据（避免边界效应）
            start = max(0, i - 2**level)
            end = min(len(rt), i + 2**level)
            local_data = rt[start:end]
            
            # 移除缺失值
            valid_mask = ~np.isnan(local_data)
            valid_data = local_data[valid_mask]
            
            if len(valid_data) >= 2**level:
                # 小波分解
                coeffs = pywt.wavedec(valid_data, wavelet, level=level)
                
                # 阈值处理
                sigma = np.median(np.abs(coeffs[-level])) / 0.6745
                threshold = threshold_coef * sigma
                
                coeffs_thresh = list(coeffs)
                for j in range(1, len(coeffs_thresh)):
                    coeffs_thresh[j] = pywt.threshold(coeffs_thresh[j], 
                                                     threshold, 
                                                     mode='soft')
                
                # 小波重构
                denoised = pywt.waverec(coeffs_thresh, wavelet)
                
                # 提取中心点
                center_idx = len(denoised) // 2
                rt_enh[i] = denoised[center_idx]
            else:
                rt_enh[i] = rt[i]
        except:
            rt_enh[i] = rt[i]
    else:
        rt_enh[i] = math.nan

# 写回数据
geolog.puttable(file_out, [depth, rt, rt_enh])
```

---

## 3. 批量处理示例

### 示例3.1：批量处理多口井

**需求**：
创建一个TCL脚本批量处理多口井。

**用户输入**：
```
创建一个TCL脚本批量处理多口井：
1. 让用户选择井
2. 对每口井的GR曲线应用tp_smooth滤波
3. 窗口长度：3
4. 保存到DELME数据集
5. 显示处理进度
```

**智能体输出**：
```tcl
#!/usr/bin/tclsh
# TCL Script for Geolog
# 功能：批量处理多口井

# 获取井列表
set wells [log_list _project well]
set wells [join $wells "\n"]

# 让用户选择井
if { [catch { mui_select title="选择井" list=$wells \
    type = multiple_select } selected_wells] } {
    puts "用户取消了选择"
    return
}

# 初始化计数器
set total_wells [llength $selected_wells]
set current_well 0

# 处理每口井
foreach well $selected_wells {
    incr current_well
    
    puts "正在处理: $well ($current_well/$total_wells)"
    
    # 打开井
    well_open well = $well
    
    # 检查WIRE数据集是否存在
    set sets [log_list _well set]
    if {[lsearch -exact $sets "WIRE"] != -1} {
        # 应用平滑处理
        launcher module = tp_smooth \
            dialog_mode = none \
            set_in = WIRE \
            set_out = DELME \
            method = mean \
            length = 3 \
            width = 1 \
            preserve_missing = yes \
            log_in = GR \
            log_out = GR
        
        # 保存井
        file_well_save
        
        puts "完成: $well"
    } else {
        puts "警告: $well 不存在WIRE数据集"
    }
}

puts ""
puts "批量处理完成！"
puts "处理井数: $current_well/$total_wells"
```

---

### 示例3.2：批量导出LAS文件

**需求**：
创建一个TCL脚本批量导出LAS文件。

**用户输入**：
```
创建一个TCL脚本批量导出LAS文件：
1. 让用户选择数据集
2. 让用户选择井
3. 重新采样到0.1524米
4. 导出为LAS 2.0格式
5. 保存到./las_export/目录
```

**智能体输出**：
```tcl
#!/usr/bin/tclsh
# TCL Script for Geolog
# 功能：批量导出LAS文件

# 创建输出目录
if {![file exists ./las_export]} {
    file mkdir ./las_export
}

# 获取数据集列表
set sets [log_list _well set]
set sets [join $sets "\n"]

# 让用户选择数据集
if { [catch { mui_select title="选择数据集" list=$sets \
    type = single_select } selected_set] } {
    puts "用户取消了选择"
    return
}

# 获取井列表
set wells [log_list _project well]
set wells [join $wells "\n"]

# 让用户选择井
if { [catch { mui_select title="选择井" list=$wells \
    type = multiple_select } selected_wells] } {
    puts "用户取消了选择"
    return
}

# 获取单位系统
if {$env(PG_UNIT_SYSTEM) == "metric" || $env(PG_UNIT_SYSTEM) == "mixed"} {
    set units "METRES"
} else {
    set units "FEET"
}

# 设置采样率
if {$units == "METRES"} {
    set sample_rate 0.1524
} else {
    set sample_rate 0.5
}

# 初始化计数器
set total_wells [llength $selected_wells]
set current_well 0
set success_count 0

# 批量导出
foreach well $selected_wells {
    incr current_well
    
    puts "正在导出: $well ($current_well/$total_wells)"
    
    # 检查数据集是否存在
    set well_sets [log_dbms mode = list well = $well set = _all \
        select = _well]
    
    if {[lsearch -exact $well_sets $selected_set] != -1} {
        # 导出LAS文件
        log_dbms mode = query \
             well = $well \
             set = $selected_set \
             select = _set._reference _set._all_logs \
        | tp_interpolate \
             sample_rate = $sample_rate \
             sr_units = $units \
             reference = DEPTH \
        | tp_name_translate \
            to_geolog = false \
            name_translation = none \
        | tp_to_las file_out = ./las_export/${well}.las
        
        incr success_count
        puts "成功: ${well}.las"
    } else {
        puts "警告: $well 不存在 $selected_set 数据集"
    }
}

puts ""
puts "批量导出完成！"
puts "成功导出: $success_count/$total_wells 口井"
puts "输出目录: ./las_export/"
```

---

## 4. GUI开发示例

### 示例4.1：带GUI的参数设置界面

**需求**：
创建一个带GUI界面的处理脚本。

**用户输入**：
```
创建一个带GUI的TCL脚本处理GR曲线：
1. 参数设置界面（窗口长度、平滑方法）
2. 文件选择对话框
3. 处理进度条
4. 结果显示窗口
```

**智能体输出**：
```tcl
#!/usr/bin/tclsh
# TCL Script for Geolog
# 功能：带GUI的曲线处理

# 主窗口
toplevel .window
wm title .window "GR曲线处理"
wm geometry .window 400x300

# 参数设置框架
frame .window.params -relief groove -borderwidth 2
pack .window.params -fill x -padx 10 -pady 10

# 窗口长度
label .window.params.label_len -text "窗口长度："
entry .window.params.entry_len -width 10 -textvar window_length
pack .window.params.label_len .window.params.entry_len -side left -padx 5 -pady 5

# 平滑方法
label .window.params.label_method -text "平滑方法："
frame .window.params.method
pack .window.params.label_method -side left -padx 5 -pady 5

radiobutton .window.params.method.mean -text "平均值" \
    -variable method -value mean
radiobutton .window.params.method.median -text "中位数" \
    -variable method -value median
pack .window.params.method.mean .window.params.method.median -side left

# 设置默认值
set window_length 3
set method mean

# 进度显示框架
frame .window.progress -relief groove -borderwidth 2
pack .window.progress -fill x -padx 10 -pady 10

progress .window.progress.p -length 300 -mode determinate -value 0
label .window.progress.msg -text "准备中..."
pack .window.progress.p -window.progress.msg -side top -pady 5

# 按钮框架
frame .window.buttons
pack .window.buttons -fill x -padx 10 -pady 10

button .window.buttons.process -text "开始处理" -bg green \
    -command process_data -width 10
button .window.buttons.cancel -text "取消" -bg red \
    -command destroy .window -width 10
pack .window.buttons.process .window.buttons.cancel -side left -padx 10

# 结果显示窗口
toplevel .result
wm title .result "处理结果"
wm geometry .result 400x300

text .result.text -width 50 -height 20 -wrap word
scrollbar .result.s -command ".result.text yview"
.result.text configure -yscrollcommand ".result.s set"
pack .result.s -side right -fill y
pack .result.text -side left -fill both -expand true

# 处理函数
proc process_data {} {
    global window_length method
    
    # 更新进度
    .window.progress.msg configure -text "正在处理..."
    .window.progress.p configure -value 50
    update
    
    # 获取当前井
    if {[info exists env(PG_WELL)]} {
        set well $env(PG_WELL)
    } else {
        .result.text insert end "错误: 没有打开的井\n"
        return
    }
    
    # 应用平滑处理
    well_open well = $well
    
    if {[catch {
        launcher module = tp_smooth \
            dialog_mode = none \
            set_in = WIRE \
            set_out = DELME \
            method = $method \
            length = $window_length \
            width = 1 \
            preserve_missing = yes \
            log_in = GR \
            log_out = GR_SMOOTH
    } error_msg]} {
        .result.text insert end "错误: $error_msg\n"
        .window.progress.msg configure -text "处理失败！"
        .window.progress.p configure -value 0
        return
    }
    
    # 保存井
    file_well_save
    
    # 更新进度
    .window.progress.p configure -value 100
    .window.progress.msg configure -text "处理完成！"
    update
    
    # 显示结果
    .result.text insert end "处理完成！\n"
    .result.text insert end "井名: $well\n"
    .result.text insert end "输入曲线: GR\n"
    .result.text insert end "输出曲线: GR_SMOOTH\n"
    .result.text insert end "窗口长度: $window_length\n"
    .result.text insert end "平滑方法: $method\n"
    .result.text insert end "保存数据集: DELME\n\n"
}

# 窗口居中
update idletasks
set x [expr {([winfo screenwidth .window] - [winfo width .window]) / 2}]
set y [expr {([winfo screenheight .window] - [winfo height .window]) / 2}]
wm geometry .window +$x+$y

# 等待窗口关闭
tkwait window .window
```

---

## 5. 成像测井示例

### 示例5.1：FMI成像处理流程

**需求**：
创建一个FMI成像处理脚本。

**用户输入**：
```
创建一个TCL脚本处理FMI成像数据：
1. 坏电极校正
2. 速度校正
3. 归一化
4. 裂缝提取
5. 生成裂缝参数
```

**智能体输出**：
```tcl
#!/usr/bin/tclsh
# TCL Script for Geolog
# 功能：FMI成像处理

# 检查当前井
if {![info exists env(PG_WELL)]} {
    puts "错误: 没有打开的井"
    return
}

set well $env(PG_WELL)
puts "开始处理FMI成像数据: $well"

# 1. 坏电极校正
puts "步骤1/5: 坏电极校正..."
launcher module = tp_image_filter \
    dialog_mode = blocked \
    filter_type = bad_button_correction

# 2. 速度校正
puts "步骤2/5: 速度校正..."
launcher module = tp_speedcorrect_correlate \
    dialog_mode = blocked

# 3. 归一化
puts "步骤3/5: 归一化..."
launcher module = tp_image_equalize_normalize \
    dialog_mode = blocked

# 4. 裂缝提取
puts "步骤4/5: 裂缝提取..."
launcher module = tp_fracture_extract \
    dialog_mode = blocked

# 5. 生成裂缝参数
puts "步骤5/5: 生成裂缝参数..."
launcher module = tp_fracture_params \
    dialog_mode = blocked

# 保存井
file_well_save

# 打开QC布局
puts "打开QC布局..."
layout_open layout = image_qc_fmi

puts ""
puts "FMI成像处理完成！"
puts "处理井: $well"
```

---

## 6. 声波测井示例

### 示例6.1：DSI声波处理流程

**需求**：
创建一个DSI声波处理脚本。

**用户输入**：
```
创建一个TCL脚本处理DSI声波数据：
1. 加载仪器规格
2. 时间慢度相关
3. 频率滤波
4. 提取纵波、横波、斯通利波
5. 计算频散曲线
```

**智能体输出**：
```tcl
#!/usr/bin/tclsh
# TCL Script for Geolog
# 功能：DSI声波处理

# 检查当前井
if {![info exists env(PG_WELL)]} {
    puts "错误: 没有打开的井"
    return
}

set well $env(PG_WELL)
puts "开始处理DSI声波数据: $well"

# 1. 加载仪器规格
puts "步骤1/5: 加载仪器规格..."
launcher module = tp_array_sonic_loadspec \
    TOOL_SPEC = fwp_dsi_m4_mono \
    dialog_mode = blocked

# 2. 时间慢度相关
puts "步骤2/5: 时间慢度相关..."
launcher module = tp_array_sonic_process \
    PROCESS = STC \
    dialog_mode = blocked

# 3. 频率滤波
puts "步骤3/5: 频率滤波..."
launcher module = tp_array_sonic_filter \
    FILTER_TYPE = bandpass \
    MIN_FREQ = 5000 \
    MAX_FREQ = 20000 \
    dialog_mode = blocked

# 4. 提取纵波、横波、斯通利波
puts "步骤4/5: 提取波形..."
launcher module = tp_array_sonic_label \
    WAVEFORM_TYPE = PWF \
    dialog_mode = blocked

launcher module = tp_array_sonic_label \
    WAVEFORM_TYPE = SWF \
    dialog_mode = blocked

launcher module = tp_array_sonic_label \
    WAVEFORM_TYPE = STWF \
    dialog_mode = blocked

# 5. 计算频散曲线
puts "步骤5/5: 计算频散曲线..."
launcher module = tp_array_sonic_sf \
    dialog_mode = blocked

# 保存井
file_well_save

# 打开QC布局
puts "打开QC布局..."
layout_open layout = sonic_qc_dsi

puts ""
puts "DSI声波处理完成！"
puts "处理井: $well"
```

---

## 7. GeologSQL示例

### 示例7.1：分层统计查询

**需求**：
创建一个GeologSQL查询统计分层参数。

**用户输入**：
```
创建一个GeologSQL查询，按地质分层统计：
- 平均孔隙度（PHIE）
- 平均含水饱和度（SW）
- 净毛厚（NET）
- 有效孔隙厚度（PHIEH）
- 含水体积（BVWH）
```

**智能体输出**：
```sql
# GeologSQL : Layer Statistics
# 功能：按地质分层统计物性参数

SELECT 
    WELL AS 井名,
    TOPS AS 地质分层,
    CH AS 层号,
    DEPTH AS 顶深 UNITS METRES DECIMALS 2,
    DEPTH_BOTTOM AS 底深 UNITS METRES DECIMALS 2,
    (DEPTH_BOTTOM - DEPTH) AS 层厚 UNITS METRES DECIMALS 2,
    
    -- 物性统计
    AVG(PHIE) AS 平均孔隙度 DECIMALS 3,
    MAX(PHIE) AS 最大孔隙度 DECIMALS 3,
    MIN(PHIE) AS 最小孔隙度 DECIMALS 3,
    
    AVG(SW) AS 平均饱和度 DECIMALS 3,
    MAX(SW) AS 最大饱和度 DECIMALS 3,
    MIN(SW) AS 最小饱和度 DECIMALS 3,
    
    AVG(GR) AS GR平均值 DECIMALS 2,
    AVG(RT) AS RT平均值 DECIMALS 2,
    AVG(RHOB) AS RHOB平均值 DECIMALS 3,
    
    -- 厚度统计
    SUM(NET) AS 净毛厚 DECIMALS 3,
    SUM(PHIEH) AS 有效孔隙厚度 DECIMALS 3,
    SUM(BVWH) AS 含水体积 DECIMALS 3,
    SUM(HVOLH) AS 烃体积 DECIMALS 3
    
FROM RESULT
GROUP BY WELL, TOPS, CH
HAVING CH <> ''
ORDER BY WELL, DEPTH;
```

---

### 示例7.2：储层质量评价

**需求**：
创建一个GeologSQL查询评价储层质量。

**用户输入**：
```
创建一个GeologSQL查询评价储层质量：
- 根据孔隙度和饱和度分类
- 统计各质量等级的厚度
- 计算加权平均参数
```

**智能体输出**：
```sql
# GeologSQL : Reservoir Quality Evaluation
# 功能：储层质量评价和统计

SELECT 
    WELL AS 井名,
    INTERVAL_LOG AS 小层,
    
    -- 储层质量分类
    IFCS(AVG(PHIE) > 0.25 AND AVG(SW) < 0.5, "优质储层",
         IFCS(AVG(PHIE) > 0.20 AND AVG(SW) < 0.6, "良好储层",
              IFCS(AVG(PHIE) > 0.15 AND AVG(SW) < 0.7, "中等储层",
                   "差储层"))) AS 储层质量 \
    COLOR IFCS(AVG(PHIE) > 0.25 AND AVG(SW) < 0.5, 'GREEN',
               IFCS(AVG(PHIE) > 0.20 AND AVG(SW) < 0.6, 'BLUE',
                    IFCS(AVG(PHIE) > 0.15 AND AVG(SW) < 0.7, 'YELLOW', 'RED'))),
    
    -- 统计参数
    SUM(NET) AS 净毛厚 DECIMALS 3,
    
    -- 加权平均参数
    SUM(PHIE*NET)/SUM(NET) AS 加权平均孔隙度 DECIMALS 3,
    SUM(SW*NET)/SUM(NET) AS 加权平均饱和度 DECIMALS 3,
    SUM(VSH*NET)/SUM(NET) AS 加权平均泥质含量 DECIMALS 3,
    
    -- 其他参数
    AVG(PHIE) AS 平均孔隙度 DECIMALS 3,
    AVG(SW) AS 平均饱和度 DECIMALS 3,
    AVG(GR) AS GR平均值 DECIMALS 2
    
FROM PAY_ZONE
GROUP BY WELL, INTERVAL_LOG
HAVING SUM(NET) > 0
ORDER BY WELL, DEPTH;
```

---

## 8. 成果表生成示例

### 示例8.1：解释成果表

**需求**：
创建一个完整的解释成果表。

**用户输入**：
```
创建一个解释成果表，包含以下信息：
- 井名、地质分层、层号
- 顶深、底深、层厚
- 平均GR、RT、RHOB
- 平均孔隙度、饱和度
- 净毛厚、有效孔隙厚度
- 储层质量评价
```

**智能体输出**：
```sql
# GeologSQL : Interpretation Results Table
# 功能：解释成果表

SELECT 
    WELL AS 井名,
    TOPS AS 地质分层,
    CH AS 层号,
    
    -- 深度信息
    DEPTH AS 顶深 UNITS METRES DECIMALS 2,
    DEPTH_BOTTOM AS 底深 UNITS METRES DECIMALS 2,
    (DEPTH_BOTTOM - DEPTH) AS 层厚 UNITS METRES DECIMALS 2,
    
    -- 测井曲线平均值
    AVG(GR) AS GR平均值 DECIMALS 2,
    MAX(GR) AS GR最大值 DECIMALS 2,
    AVG(RT) AS RT平均值 DECIMALS 2,
    MAX(RT) AS RT最大值 DECIMALS 2,
    AVG(RHOB) AS RHOB平均值 DECIMALS 3,
    AVG(NPHI) AS NPHI平均值 DECIMALS 3,
    AVG(DT) AS DT平均值 DECIMALS 2,
    
    -- 解释参数
    AVG(VSH) AS 平均泥质含量 DECIMALS 3,
    AVG(PHIT) AS 平均总孔隙度 DECIMALS 3,
    AVG(PHIE) AS 平均有效孔隙度 DECIMALS 3,
    AVG(SW) AS 平均含水饱和度 DECIMALS 3,
    AVG(SO) AS 平均含油饱和度 DECIMALS 3,
    
    -- 厚度统计
    SUM(NET) AS 净毛厚 DECIMALS 3,
    SUM(PHIEH) AS 有效孔隙厚度 DECIMALS 3,
    SUM(BVWH) AS 含水体积 DECIMALS 3,
    SUM(HVOLH) AS 烃体积 DECIMALS 3,
    SUM(HVOLH)/SUM(PHIEH) AS 平均含油饱和度体积 DECIMALS 3,
    
    -- 储层质量评价
    IFCS(AVG(PHIE) > 0.25 AND AVG(SW) < 0.5, "优质储层",
         IFCS(AVG(PHIE) > 0.20 AND AVG(SW) < 0.6, "良好储层",
              IFCS(AVG(PHIE) > 0.15 AND AVG(SW) < 0.7, "中等储层",
                   "差储层"))) AS 储层质量 \
    COLOR IFCS(AVG(PHIE) > 0.25 AND AVG(SW) < 0.5, 'GREEN',
               IFCS(AVG(PHIE) > 0.20 AND AVG(SW) < 0.6, 'BLUE',
                    IFCS(AVG(PHIE) > 0.15 AND AVG(SW) < 0.7, 'YELLOW', 'RED'))),
    
    RESULT AS 解释结论
    
FROM RESULT
GROUP BY WELL, TOPS, CH
HAVING CH <> ''
ORDER BY WELL, DEPTH;
```

---

## 9. 高级应用示例

### 示例9.1：脆性指数计算（4种方法）

**需求**：
创建一个Python Loglan脚本计算脆性指数，使用4种方法。

**用户输入**：
```
创建一个Python Loglan脚本计算脆性指数（4种方法）：
- 输入曲线：DTC（纵波时差），DTS（横波时差），RHOB（体积密度）
- 输出曲线：
  - BI1：方法1脆性指数
  - BI2：方法2脆性指数
  - BI3：方法3脆性指数
  - BI4：方法4脆性指数（综合方法）
```

**智能体输出**：
```python
#!/usr/bin/env python3
# python loglan
# 功能：脆性指数计算（4种方法）

import geolog
import numpy as np
import math

# 读取参数
file_in = geolog.getarg("file_in")
file_out = geolog.getarg("file_out")

# 读取输入数据
depth, dtc, dts, rhob = geolog.gettable(file_in, ['depth', 'dtc', 'dts', 'rhob'])

# 创建输出数组
bi1 = np.full_like(dtc, math.nan)
bi2 = np.full_like(dtc, math.nan)
bi3 = np.full_like(dtc, math.nan)
bi4 = np.full_like(dtc, math.nan)

# 批量处理
for i in range(len(dtc)):
    # 检查数据有效性
    if not math.isnan(dtc[i]) and not math.isnan(dts[i]) and not math.isnan(rhob[i]):
        # 方法1：基于纵横波时差比
        # BI1 = (DTC - DTS) / DTC
        bi1[i] = (dtc[i] - dts[i]) / dtc[i]
        
        # 方法2：基于弹性参数
        # 计算泊松比和杨氏模量
        pr = ((dtc[i]/dts[i])**2 - 2) / (2 * ((dtc[i]/dts[i])**2 - 1))
        young_mod = (rhob[i] * 1e9) / (dtc[i] * 0.3048)**2 * (1 + pr) * (1 - 2*pr) / (1 - pr)
        
        # BI2 = 0.5 * (标准化的杨氏模量 + 标准化的泊松比)
        ym_norm = (young_mod - 20) / (80 - 20)  # 归一化
        pr_norm = (0.4 - pr) / (0.4 - 0.1)      # 归一化
        bi2[i] = 0.5 * (ym_norm + pr_norm)
        
        # 方法3：基于Brittleness Index (BI)
        # BI3 = (杨氏模量 - 最小) / (最大 - 最小)
        bi3[i] = ym_norm
        
        # 方法4：综合方法（平均）
        bi4[i] = (bi1[i] + bi2[i] + bi3[i]) / 3.0
        
        # 限制范围（0-1）
        bi1[i] = max(0.0, min(1.0, bi1[i]))
        bi2[i] = max(0.0, min(1.0, bi2[i]))
        bi3[i] = max(0.0, min(1.0, bi3[i]))
        bi4[i] = max(0.0, min(1.0, bi4[i]))
    else:
        # 缺失值
        bi1[i] = math.nan
        bi2[i] = math.nan
        bi3[i] = math.nan
        bi4[i] = math.nan

# 写回数据
geolog.puttable(file_out, [depth, dtc, dts, rhob, bi1, bi2, bi3, bi4])
```

---

### 示例9.2：TOC计算（Passey方法）

**需求**：
创建一个Python Loglan脚本计算TOC（总有机碳含量）。

**用户输入**：
```
创建一个Python Loglan脚本计算TOC（Passey方法）：
- 输入曲线：RES（电阻率），DT（声波时差）
- 参数：LOM（有机质成熟度，10）
- 输出曲线：TOC（总有机碳含量，wt%）
- 使用Passey ΔlogR方法
```

**智能体输出**：
```python
#!/usr/bin/env python3
# python loglan
# 功能：TOC计算（Passey ΔlogR方法）

import geolog
import numpy as np
import math

# 读取参数
file_in = geolog.getarg("file_in")
file_out = geolog.getarg("file_out")
lom = geolog.getarg("lom")  # 有机质成熟度

# 计算基线值（非储层）
res_baseline = 10.0  # 电阻率基线（OHMM）
dt_baseline = 60.0   # 声波时差基线（US/FT）

# 读取输入数据
depth, res, dt = geolog.gettable(file_in, ['depth', 'res', 'dt'])

# 创建输出数组
toc = np.full_like(res, math.nan)
delta_log_r = np.full_like(res, math.nan)

# Passey ΔlogR方法
for i in range(len(res)):
    # 检查数据有效性
    if not math.isnan(res[i]) and not math.isnan(dt[i]):
        # 计算ΔlogR
        # ΔlogR = log10(RES/RES基线) + 0.02 * (DT - DT基线)
        delta_log_r[i] = math.log10(res[i] / res_baseline) + 0.02 * (dt[i] - dt_baseline)
        
        # 计算TOC
        # TOC = ΔlogR * 10^(2.297 - 0.1688 * LOM)
        toc_coef = 10 ** (2.297 - 0.1688 * lom)
        toc[i] = delta_log_r[i] * toc_coef
        
        # 限制TOC范围（0-20 wt%）
        if toc[i] < 0.0:
            toc[i] = 0.0
        elif toc[i] > 20.0:
            toc[i] = 20.0
    else:
        # 缺失值
        delta_log_r[i] = math.nan
        toc[i] = math.nan

# 写回数据
geolog.puttable(file_out, [depth, res, dt, delta_log_r, toc])
```

---

## 📊 示例使用指南

### 如何使用这些示例

1. **选择示例**
   - 根据您的需求选择最接近的示例
   - 了解示例的实现原理

2. **修改参数**
   - 根据您的实际情况修改参数
   - 调整输入/输出曲线名称
   - 修改计算公式或处理流程

3. **测试验证**
   - 在测试数据上验证结果
   - 检查输出是否正确
   - 根据需要调整参数

4. **应用到生产**
   - 将代码保存到Geolog工区
   - 在实际井数据上应用
   - 监控处理结果

### 示例扩展

您可以将多个示例组合起来，创建更复杂的处理流程：

```
示例1（孔隙度计算） + 示例2（饱和度计算） + 示例3（储层评价）
= 完整的岩石物理分析流程
```

---

## 🎓 学习建议

1. **从简单开始**
   - 先掌握基础计算示例
   - 理解数据处理模式
   - 熟悉常用函数

2. **逐步进阶**
   - 学习批量处理
   - 掌握GUI开发
   - 理解高级应用

3. **实践练习**
   - 修改示例代码
   - 应用到实际数据
   - 优化处理流程

4. **持续学习**
   - 查看Geolog官方文档
   - 参考实际工区案例
   - 交流经验和技巧

---

**Geolog AI 智能体 - 实用示例集**
**版本**: 1.0.0
**更新日期**: 2026-03-31
**示例数量**: 20+


<p align="center">
  <h1 align="center">🐟 摸鱼了么 — PC数字足迹检测</h1>
  <h3 align="center">MoYu Monitor — Personal Computer Digitization Footprint Detection</h3>
</p>

<p align="center">
  <a href="#-简介--introduction">简介</a> •
  <a href="#-特性--features">特性</a> •
  <a href="#-安装--installation">安装</a> •
  <a href="#-使用--usage">使用</a> •
  <a href="#-引用--citation">引用</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/Platform-Windows-lightgrey.svg" alt="Platform">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/UI-PyQt5-orange.svg" alt="UI">
</p>

---

## 📖 简介 | Introduction

**[中文]**

"摸鱼了么"是一款基于 **Digitization Footprint (DF)** 和 **DF-LCA** 框架开发的个人电脑数字足迹监测软件。该软件能够实时监控计算机资源消耗，评估数字化活动的环境影响，帮助用户了解自己的"数字碳足迹"。

核心指标基于以下学术论文中的 DF-LCA (Digitization Footprint - Life Cycle Assessment) 方法论：
- **FLOPS** (浮点运算能力)
- **MIPS** (百万指令每秒)
- **TPD** (总功耗密度)
- **能源消耗估算**
- **碳排放计算**

**[English]**

"MoYu Monitor" is a personal computer digitization footprint monitoring software developed based on the **Digitization Footprint (DF)** and **DF-LCA** framework. This software monitors computer resource consumption in real-time, evaluates the environmental impact of digital activities, and helps users understand their "digital carbon footprint".

Core metrics are based on the DF-LCA (Digitization Footprint - Life Cycle Assessment) methodology from academic research:
- **FLOPS** (Floating Point Operations Per Second)
- **MIPS** (Million Instructions Per Second)
- **TPD** (Total Power Density)
- **Energy Consumption Estimation**
- **Carbon Emission Calculation**

---

## ✨ 特性 | Features

### 🌍 数字足迹 | Digital Footprint
| 中文 | English |
|------|---------|
| 实时能源消耗估算 | Real-time energy consumption estimation |
| 碳排放计算 (基于区域电网系数) | Carbon emission calculation (based on regional grid coefficient) |
| GFLOPS 计算性能监测 | GFLOPS computing performance monitoring |
| MIPS 指令执行监测 | MIPS instruction execution monitoring |
| 数据生成量统计 | Data generation volume statistics |
| 磁盘空间使用分析 | Disk space usage analysis |

### 💻 系统监控 | System Monitoring
| 中文 | English |
|------|---------|
| CPU 利用率与频率监控 | CPU utilization and frequency monitoring |
| 内存使用情况追踪 | Memory usage tracking |
| GPU 利用率与温度监控 (NVIDIA) | GPU utilization and temperature monitoring (NVIDIA) |
| 磁盘 I/O 读写速度 | Disk I/O read/write speed |
| 网络上传/下载速度 | Network upload/download speed |
| 历史趋势可视化图表 | Historical trend visualization charts |

### 📊 活动统计 | Activity Statistics
| 中文 | English |
|------|---------|
| 软件使用时长追踪 | Software usage duration tracking |
| 网站访问记录 | Website visit records |
| 每小时活动时间线 | Hourly activity timeline |
| Top 应用/网站排行 | Top applications/websites ranking |

### 🎨 界面特性 | UI Features
| 中文 | English |
|------|---------|
| 现代深色主题设计 | Modern dark theme design |
| macOS 风格窗口控制 | macOS-style window controls |
| 实时动态图表 | Real-time dynamic charts |
| 系统托盘支持 | System tray support |
| 开机自启动 | Auto-start on boot |

---

## 📦 安装 | Installation

### 环境要求 | Requirements

- **Python**: 3.8 或更高版本 | 3.8 or higher
- **操作系统 | OS**: Windows 10/11
- **GPU监控 | GPU Monitoring**: NVIDIA 显卡 (可选) | NVIDIA GPU (optional)

### 步骤 | Steps

**1. 克隆仓库 | Clone Repository**

```bash
git clone https://github.com/yourusername/MoYu-Monitor.git
cd MoYu-Monitor
```

**2. 创建虚拟环境 (推荐) | Create Virtual Environment (Recommended)**

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

**3. 安装依赖 | Install Dependencies**

```bash
pip install -r requirements.txt
```

### 依赖列表 | Dependencies

| 包名 Package | 用途 Purpose |
|--------------|-------------|
| `PyQt5` | GUI 框架 | GUI Framework |
| `pyqtgraph` | 实时图表 | Real-time Charts |
| `psutil` | 系统监控 | System Monitoring |
| `GPUtil` | GPU 监控 | GPU Monitoring |
| `pywin32` | Windows API |
| `numpy` | 数值计算 | Numerical Computation |

---

## 🚀 使用 | Usage

### 运行程序 | Run Application

```bash
python main.py
```

### 打包为可执行文件 | Build Executable

```bash
# 安装 PyInstaller | Install PyInstaller
pip install pyinstaller

# 打包 | Build
pyinstaller build.spec --clean -y

# 可执行文件位置 | Executable location
# dist/摸鱼了么.exe
```

### 功能说明 | Function Guide

**[中文]**

1. **数字足迹 Tab**: 查看实时能源消耗、碳排放、计算性能等 DF-LCA 指标
2. **系统监控 Tab**: 监控 CPU/内存/GPU 使用情况，查看历史趋势图
3. **活动统计 Tab**: 查看每日软件使用时长和网站访问记录
4. **设置菜单**: 点击左上角"设置"按钮访问更多选项
5. **系统托盘**: 关闭窗口后程序最小化到托盘，双击图标重新打开
6. **开机自启动**: 通过设置菜单启用/禁用

**[English]**

1. **Digital Footprint Tab**: View real-time energy consumption, carbon emissions, computing performance and other DF-LCA metrics
2. **System Monitoring Tab**: Monitor CPU/Memory/GPU usage, view historical trend charts
3. **Activity Statistics Tab**: View daily software usage duration and website visit records
4. **Settings Menu**: Click the "Settings" button in the top-left corner to access more options
5. **System Tray**: After closing the window, the program minimizes to tray; double-click the icon to reopen
6. **Auto-start**: Enable/disable through the settings menu

---

## 📁 项目结构 | Project Structure

```
MoYu-Monitor/
├── main.py                  # 程序入口 | Entry point
├── build.spec               # PyInstaller 配置 | PyInstaller config
├── requirements.txt         # 依赖列表 | Dependencies
├── README.md
│
├── monitor/                 # 系统监控模块 | System monitoring module
│   ├── cpu_monitor.py       # CPU 监控 | CPU monitoring
│   ├── gpu_monitor.py       # GPU 监控 | GPU monitoring
│   ├── memory_monitor.py    # 内存监控 | Memory monitoring
│   └── system_monitor.py    # 综合监控 | Integrated monitoring
│
├── tracker/                 # 活动追踪模块 | Activity tracking module
│   ├── app_tracker.py       # 应用追踪 | App tracking
│   ├── browser_tracker.py   # 浏览器追踪 | Browser tracking
│   └── activity_manager.py  # 活动管理 | Activity management
│
├── ui/                      # 界面模块 | UI module
│   ├── main_window.py       # 主窗口 | Main window
│   ├── footprint_tab.py     # 数字足迹页 | Digital footprint tab
│   ├── monitor_tab.py       # 系统监控页 | System monitoring tab
│   ├── activity_tab.py      # 活动统计页 | Activity statistics tab
│   ├── styles.py            # 样式定义 | Style definitions
│   └── widgets.py           # 自定义组件 | Custom widgets
│
├── utils/                   # 工具模块 | Utility module
│   ├── data_logger.py       # 数据记录 | Data logging
│   └── autostart.py         # 开机自启 | Auto-start
│
└── data/                    # 数据存储 | Data storage
    ├── system/              # 系统监控数据 | System monitoring data
    └── activity/            # 活动记录数据 | Activity records
```

---

## 📊 数据存储 | Data Storage

监控数据自动保存在 `data/` 目录下：
Monitoring data is automatically saved in the `data/` directory:

| 文件路径 File Path | 内容 Content |
|-------------------|-------------|
| `data/system/monitor_YYYY-MM-DD.csv` | 系统监控数据 | System monitoring data |
| `data/activity/app_usage_YYYY-MM-DD.csv` | 应用使用记录 | App usage records |
| `data/activity/web_visits_YYYY-MM-DD.csv` | 网站访问记录 | Website visit records |

---

## 📚 引用 | Citation

本项目基于以下学术研究开发：
This project is developed based on the following academic research:

### 论文 | Papers

**[1] Digitization Footprint Framework (Part 1)**

> Huang, Q., Li, D., Chen, G., & Zhang, Y. (2025). How to assess the digitization and digital effort: A framework for Digitization Footprint (Part 1). *Computers and Electronics in Agriculture*, 230, 109875.

[![DOI](https://img.shields.io/badge/DOI-10.1016/j.compag.2024.109875-blue)](https://doi.org/10.1016/j.compag.2024.109875)

**[2] Digitization Footprint Application (Part 2)**

> Huang, Q., Li, D., Chen, G., & Zhang, Y. (2025). Digitization Footprint-Life Cycle Assessment: Application and case study (Part 2). *Computers and Electronics in Agriculture*, 228, 109206.

[![DOI](https://img.shields.io/badge/DOI-10.1016/j.compag.2024.109206-blue)](https://doi.org/10.1016/j.compag.2024.109206)

### BibTeX

```bibtex
@article{huang2025digitization1,
  title={How to assess the digitization and digital effort: A framework for Digitization Footprint (Part 1)},
  author={Huang, Qiangyi and Li, Daoliang and Chen, Guoqing and Zhang, Yu},
  journal={Computers and Electronics in Agriculture},
  volume={230},
  pages={109875},
  year={2025},
  publisher={Elsevier},
  doi={10.1016/j.compag.2024.109875}
}

@article{huang2025digitization2,
  title={Digitization Footprint-Life Cycle Assessment: Application and case study (Part 2)},
  author={Huang, Qiangyi and Li, Daoliang and Chen, Guoqing and Zhang, Yu},
  journal={Computers and Electronics in Agriculture},
  volume={228},
  pages={109206},
  year={2025},
  publisher={Elsevier},
  doi={10.1016/j.compag.2024.109206}
}
```

---

## 🔬 DF-LCA 指标说明 | DF-LCA Metrics Description

| 指标 Metric | 公式 Formula | 说明 Description |
|-------------|--------------|------------------|
| **FLOPS** | CPU频率 × 核心数 × IPC | 浮点运算能力 | Floating-point operations capability |
| **MIPS** | CPU频率 × 核心数 | 百万指令每秒 | Million instructions per second |
| **TPD** | CPU_TDP + GPU_TDP | 总设计功耗 | Total design power |
| **Energy** | Power × Time | 能源消耗 (kWh) | Energy consumption |
| **Carbon** | Energy × Grid_Factor | 碳排放 (kg CO₂) | Carbon emissions |
| **ER** | MIPS / Power | 努力率 | Effort rate |

---

## 🤝 贡献 | Contributing

欢迎提交 Issue 和 Pull Request！
Issues and Pull Requests are welcome!

---

## 📄 许可证 | License

本项目采用 MIT 许可证。
This project is licensed under the MIT License.

```
MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

<p align="center">
  Made with ❤️ based on DF-LCA Framework
</p>

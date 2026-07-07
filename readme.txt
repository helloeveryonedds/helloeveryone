================================================
  房价预测系统 v2.0
  基于链家二手房数据的双城市房价预测系统
================================================

一、项目简介
-----------
本系统使用机器学习模型预测广州和上海两座城市的二手房总价。
用户输入面积、户型、楼层、朝向、行政区等信息，系统返回
预测房价及单价，并提供数据看板展示城市房价分布、各区均价、
户型分布等统计数据。

二、技术栈
-----------
- 后端：Python Flask
- 前端：Bootstrap 5 + ECharts 5
- 机器学习：scikit-learn (RandomForestRegressor)
- 模型存储：joblib

三、项目结构
-----------
项目根目录/
├── 启动系统.bat          # 一键启动脚本
├── requirements.txt      # Python 依赖清单
├── readme.txt            # 本说明文件
├── auto_train.py         # 自动训练脚本（支持新数据集）
│
├── app/                  # Web 应用
│   ├── server.py         # Flask 主程序（含所有 API）
│   ├── templates/
│   │   ├── index.html    # 预测页面
│   │   └── dashboard.html # 数据看板页面
│   └── static/
│       ├── css/style.css # 样式文件
│       └── js/
│           ├── main.js      # 预测页面逻辑
│           └── dashboard.js # 数据看板逻辑
│
├── model/                # 训练好的模型文件
│   ├── best_model.pkl    # 广州 RandomForest 模型 (75MB)
│   ├── scaler.pkl        # 广州特征归一化器
│   ├── feature_cols.pkl  # 广州特征列名
│   ├── encoders.pkl      # 广州标签编码器
│   ├── sh_model.pkl      # 上海 RandomForest 模型 (262MB)
│   ├── sh_scaler.pkl     # 上海特征归一化器
│   ├── sh_feature_cols.pkl # 上海特征列名
│   ├── sh_encoders.pkl   # 上海标签编码器
│   └── filtered_data.csv # 广州清洗后的数据（用于看板统计）
│
├── 广州链家二手房数据.xlsx   # 广州原始数据集
└── 上海链家二手房.csv        # 上海原始数据集（用于看板统计）

四、使用方式
-----------
1. 双击「启动系统.bat」
2. 脚本自动安装依赖（首次运行需联网）
3. 浏览器自动打开 http://127.0.0.1:5000
4. 在「房价预测」页面输入房源信息进行预测
5. 在「数据看板」页面查看统计数据与图表

五、API 接口
-----------
POST /predict            # 房价预测
GET  /api/stats?city=xx  # 统计数据
GET  /api/districts?city=xx  # 行政区列表
GET  /api/features?city=xx   # 特征重要性排名
GET  /api/cities         # 支持的城市列表

六、模型信息
-----------
广州模型：
  - 算法: RandomForestRegressor
  - 特征数: 16
  - 训练样本: ~15,000 条
  - 决定系数 R²: ~0.88
  - 核心特征: 面积(58%)、地段(25%)、楼层(9%)

上海模型：
  - 算法: RandomForestRegressor
  - 特征数: 12
  - 训练样本: ~72,000 条
  - 决定系数 R²: ~0.91
  - 核心特征: 面积(69%)、地段(17%)、楼层(8%)

七、重新训练
-----------
如需用新数据集重新训练模型，运行：
  python auto_train.py --file 数据集路径.xlsx --update

支持自动检测城市格式（广州/上海），训练后自动覆盖系统模型。

================================================
  小组成员：7人课程项目
  数据来源：链家
================================================

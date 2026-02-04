# 1. 创建闪电帝国商业门户目录
mkdir -p ~/lightning-empire-portal
cd ~/lightning-empire-portal

# 2. 创建核心文件结构
touch index.html products.html contracts.html dashboard.html
mkdir -p assets/{css,js,images} docs contracts

# 3. 初始化版本控制
git init
git add .
git commit -m "⚡ 闪电帝国商业门户 v1.0 - 初始化"
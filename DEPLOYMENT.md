# MetaIgnite-backend 部署手册

## 📋 目录

1. [系统要求](#系统要求)
2. [项目下载和安装](#项目下载和安装)
3. [环境准备](#环境准备)
4. [依赖包安装](#依赖包安装)
5. [环境配置](#环境配置)
6. [OAuth第三方登录配置](#oauth第三方登录配置)
7. [数据库设置](#数据库设置)
8. [服务启动和验证](#服务启动和验证)
9. [API文档访问](#api文档访问)
10. [常见问题和故障排除](#常见问题和故障排除)
11. [生产环境部署](#生产环境部署)

---

## 🖥️ 系统要求

### 最低系统要求
- **操作系统**: Linux, macOS, Windows
- **Python版本**: Python 3.8+
- **内存**: 最少 2GB RAM
- **存储空间**: 最少 1GB 可用空间
- **网络**: 稳定的互联网连接（用于OAuth和API调用）

### 推荐系统配置
- **Python版本**: Python 3.10+
- **内存**: 4GB+ RAM
- **CPU**: 2核心+
- **存储空间**: 5GB+ 可用空间

---

## 📥 项目下载和安装

### 1. 克隆项目
```bash
git clone <repository-url>
cd MetaIgnite-backend-main
```

### 2. 检查项目结构
确保项目包含以下关键文件：
```
MetaIgnite-backend-main/
├── app/                    # 应用主目录
├── requirements.txt        # Python依赖
├── .env.example           # 环境变量模板
├── conf.yaml.example      # 配置文件模板
├── README.md              # 项目说明
└── log-config.yml         # 日志配置
```

---

## 🔧 环境准备

### 1. 安装Python
确保系统已安装Python 3.8+：
```bash
python --version
# 或
python3 --version
```

### 2. 创建虚拟环境
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Linux/macOS:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### 3. 验证虚拟环境
```bash
which python  # 应该指向venv目录
pip --version # 确认pip可用
```

---

## 📦 依赖包安装

### 1. 升级pip
```bash
pip install --upgrade pip
```

### 2. 安装项目依赖
```bash
pip install -r requirements.txt
```

### 3. 验证关键依赖
```bash
python -c "import fastapi, uvicorn, sqlalchemy; print('核心依赖安装成功')"
```

---

## ⚙️ 环境配置

### 1. 复制配置文件
```bash
# 复制环境变量文件
cp .env.example .env

# 复制配置文件
cp conf.yaml.example conf.yaml
```

### 2. 编辑 .env 文件
打开 `.env` 文件，配置以下关键参数：

```env
# 应用设置
DEBUG=True
APP_ENV=development

# CORS设置
ALLOWED_ORIGINS=http://localhost:3000

# 数据库配置
DATABASE_URL="sqlite:///./metaignite.db"

# JWT配置
JWT_SECRET_KEY="your-secure-jwt-secret-key-change-in-production"
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# 搜索引擎API（可选）
SEARCH_API=tavily
TAVILY_API_KEY=your-tavily-api-key

# OpenRouter API（用于AI功能）
OPEN_ROUTER_API_KEY="your-openrouter-api-key"
```

### 3. 编辑 conf.yaml 文件
配置AI模型设置：

```yaml
BASIC_MODEL:
  base_url: https://openrouter.ai/api/v1
  model: "moonshotai/kimi-k2:free"
  api_key: your-openrouter-api-key
```

---

## 🔐 OAuth第三方登录配置

### 1. Google OAuth配置

#### 步骤1：创建Google OAuth应用
1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目或选择现有项目
3. 启用 Google+ API 或 Google Identity API
4. 转到「凭据」页面，创建「OAuth 2.0 客户端ID」
5. 选择「Web应用程序」
6. 设置授权重定向URI：`http://localhost:8001/api/v1/auth/google/callback`

#### 步骤2：配置Google凭据
在 `.env` 文件中添加：
```env
# Google OAuth
GOOGLE_CLIENT_ID="your-google-client-id"
GOOGLE_CLIENT_SECRET="your-google-client-secret"
GOOGLE_REDIRECT_URI="http://localhost:8001/api/v1/auth/google/callback"
```

### 2. GitHub OAuth配置

#### 步骤1：创建GitHub OAuth应用
1. 访问 [GitHub Developer Settings](https://github.com/settings/developers)
2. 点击「New OAuth App」
3. 填写应用信息：
   - Application name: MetaIgnite Backend
   - Homepage URL: `http://localhost:8001`
   - Authorization callback URL: `http://localhost:8001/api/v1/auth/github/callback`

#### 步骤2：配置GitHub凭据
在 `.env` 文件中添加：
```env
# GitHub OAuth
GITHUB_CLIENT_ID="your-github-client-id"
GITHUB_CLIENT_SECRET="your-github-client-secret"
GITHUB_REDIRECT_URI="http://localhost:8001/api/v1/auth/github/callback"
```

---

## 🗄️ 数据库设置

### 1. SQLite数据库（默认）
项目默认使用SQLite数据库，无需额外配置。数据库文件将自动创建为 `metaignite.db`。

### 2. 数据库初始化
启动服务时，数据库表会自动创建。如需手动初始化：
```bash
python -c "from app.core.database import init_db; init_db()"
```

### 3. 使用其他数据库（可选）
如需使用PostgreSQL或MySQL，修改 `.env` 中的 `DATABASE_URL`：

```env
# PostgreSQL
DATABASE_URL="postgresql://username:password@localhost/metaignite"

# MySQL
DATABASE_URL="mysql+pymysql://username:password@localhost/metaignite"
```

---

## 🚀 服务启动和验证

### 1. 启动服务
```bash
# 确保虚拟环境已激活
source venv/bin/activate

# 启动FastAPI服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001 --log-config log-config.yml
```

### 2. 验证服务状态
服务启动后，您应该看到类似输出：
```
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 3. 基础功能测试
```bash
# 测试根路径
curl http://localhost:8001/

# 预期响应：
# {"status":"ok","message":"Welcome to the MetaIgnite AI API V1!"}
```

---

## 📚 API文档访问

### 1. Swagger UI文档
访问：http://localhost:8001/docs

### 2. ReDoc文档
访问：http://localhost:8001/redoc

### 3. 主要API端点

#### 认证相关
- `GET /api/v1/auth/google/login` - Google OAuth登录
- `GET /api/v1/auth/github/login` - GitHub OAuth登录
- `GET /api/v1/auth/me` - 获取当前用户信息
- `POST /api/v1/auth/logout` - 用户登出
- `POST /api/v1/auth/refresh` - 刷新访问令牌

#### 产品分析
- `POST /api/v1/pm/analysis` - AI创业想法分析

---

## 🔧 常见问题和故障排除

### 1. 端口占用问题
**问题**: `Address already in use`
**解决方案**:
```bash
# 查找占用端口的进程
lsof -i :8001

# 终止进程
kill -9 <PID>

# 或使用不同端口
uvicorn app.main:app --port 8002
```

### 2. 依赖安装失败
**问题**: pip install 失败
**解决方案**:
```bash
# 升级pip
pip install --upgrade pip

# 清理缓存
pip cache purge

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

### 3. OAuth登录失败
**问题**: OAuth回调错误
**解决方案**:
1. 检查OAuth应用配置中的回调URL是否正确
2. 确认客户端ID和密钥配置正确
3. 检查网络连接和防火墙设置

### 4. 数据库连接问题
**问题**: 数据库连接失败
**解决方案**:
```bash
# 检查数据库文件权限
ls -la metaignite.db

# 重新初始化数据库
rm metaignite.db
python -c "from app.core.database import init_db; init_db()"
```

### 5. JWT Token问题
**问题**: Token验证失败
**解决方案**:
1. 确认JWT_SECRET_KEY配置正确
2. 检查token是否过期
3. 验证token格式是否正确

---

## 🌐 生产环境部署

### 1. 环境变量配置
```env
# 生产环境设置
DEBUG=False
APP_ENV=production

# 使用强密钥
JWT_SECRET_KEY="your-very-secure-production-jwt-secret-key"

# 配置生产数据库
DATABASE_URL="postgresql://user:password@localhost/metaignite_prod"

# 更新OAuth回调URL
GOOGLE_REDIRECT_URI="https://yourdomain.com/api/v1/auth/google/callback"
GITHUB_REDIRECT_URI="https://yourdomain.com/api/v1/auth/github/callback"
```

### 2. 使用Gunicorn部署
```bash
# 安装Gunicorn
pip install gunicorn

# 启动生产服务
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001
```

### 3. 使用Docker部署
创建 `Dockerfile`：
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

构建和运行：
```bash
docker build -t metaignite-backend .
docker run -p 8001:8001 metaignite-backend
```

### 4. 反向代理配置（Nginx）
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 5. 安全注意事项
- 使用HTTPS（SSL/TLS证书）
- 定期更新依赖包
- 设置防火墙规则
- 启用日志监控
- 定期备份数据库
- 使用环境变量管理敏感信息

---

## 📞 技术支持

如果在部署过程中遇到问题，请：

1. 检查日志文件获取详细错误信息
2. 参考本手册的故障排除部分
3. 查看项目的GitHub Issues
4. 联系技术支持团队

---

## 📝 更新日志

- **v1.0.0** - 初始版本，包含基础功能和OAuth集成
- **v1.1.0** - 添加了完整的部署文档和故障排除指南

---

**祝您部署顺利！** 🎉
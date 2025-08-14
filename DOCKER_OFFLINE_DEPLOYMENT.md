# MetaIgnite Backend Docker 离线部署指南

本文档详细说明如何在内网环境中进行MetaIgnite Backend的Docker离线部署。

## 📋 目录

- [系统要求](#系统要求)
- [文件清单](#文件清单)
- [快速开始](#快速开始)
- [详细部署步骤](#详细部署步骤)
- [配置说明](#配置说明)
- [故障排除](#故障排除)
- [维护操作](#维护操作)

## 🔧 系统要求

### 最低要求
- **操作系统**: Linux/macOS/Windows
- **Docker**: 20.10.0+
- **Docker Compose**: 2.0.0+
- **内存**: 1GB RAM
- **存储**: 2GB 可用空间
- **CPU**: 1 核心

### 推荐配置
- **内存**: 2GB+ RAM
- **存储**: 5GB+ 可用空间
- **CPU**: 2+ 核心

## 📦 文件清单

确保以下文件存在于部署目录中：

```
MetaIgnite-backend/
├── Dockerfile                    # Docker镜像构建文件
├── docker-compose.yml           # Docker编排配置
├── .dockerignore                # Docker构建忽略文件
├── offline-deploy.sh            # 离线部署脚本
├── requirements.txt             # Python依赖列表
├── .env.example                 # 环境变量模板
├── conf.yaml.example           # 配置文件模板
├── log-config.yml              # 日志配置
├── app/                        # 应用源代码
└── DOCKER_OFFLINE_DEPLOYMENT.md # 本文档
```

## 🚀 快速开始

### 方式一：使用部署脚本（推荐）

```bash
# 1. 进入项目目录
cd MetaIgnite-backend

# 2. 完整部署（构建+导出+运行）
./offline-deploy.sh full

# 3. 检查服务状态
./offline-deploy.sh status
```

### 方式二：使用Docker Compose

```bash
# 1. 复制环境配置文件
cp .env.example .env

# 2. 启动服务
docker-compose up -d

# 3. 检查服务状态
docker-compose ps
```

## 📝 详细部署步骤

### 步骤1：准备环境配置

```bash
# 复制并编辑环境配置文件
cp .env.example .env
cp conf.yaml.example conf.yaml

# 编辑.env文件，配置必要的环境变量
vim .env
```

### 步骤2：构建Docker镜像

```bash
# 使用脚本构建
./offline-deploy.sh build

# 或手动构建
docker build -t metaignite-backend:latest .
```

### 步骤3：导出镜像（用于离线传输）

```bash
# 使用脚本导出
./offline-deploy.sh export

# 或手动导出
docker save metaignite-backend:latest > metaignite-backend-latest.tar
```

### 步骤4：离线环境部署

在目标离线环境中：

```bash
# 1. 传输文件到目标服务器
# - metaignite-backend-latest.tar
# - docker-compose.yml
# - .env
# - offline-deploy.sh

# 2. 导入镜像
./offline-deploy.sh import

# 3. 启动服务
./offline-deploy.sh deploy
```

## ⚙️ 配置说明

### 环境变量配置 (.env)

```bash
# 基础配置
DEBUG=False
APP_ENV=production
HOST=0.0.0.0
PORT=8001

# 数据库配置（SQLite适合离线环境）
DATABASE_URL=sqlite:///./data/metaignite.db

# JWT配置
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OAuth配置（离线环境可能无法使用）
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# AI服务配置（离线环境可能无法使用）
OPENROUTER_API_KEY=your-openrouter-api-key
TAVILY_API_KEY=your-tavily-api-key

# 日志配置
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### Docker Compose配置

主要配置项说明：

- **端口映射**: `8001:8001`
- **数据持久化**: `./data:/app/data`
- **日志持久化**: `./logs:/app/logs`
- **健康检查**: 30秒间隔检查服务状态
- **重启策略**: `unless-stopped`

## 🔍 故障排除

### 常见问题

#### 1. 容器启动失败

```bash
# 查看容器日志
./offline-deploy.sh logs

# 或使用docker命令
docker logs metaignite-backend
```

#### 2. 端口被占用

```bash
# 检查端口占用
lsof -i :8001

# 修改docker-compose.yml中的端口映射
ports:
  - "8002:8001"  # 改为8002端口
```

#### 3. 权限问题

```bash
# 确保数据目录权限正确
sudo chown -R 1000:1000 ./data ./logs

# 或使用当前用户
sudo chown -R $(id -u):$(id -g) ./data ./logs
```

#### 4. 内存不足

```bash
# 检查系统资源
docker stats metaignite-backend

# 调整docker-compose.yml中的资源限制
deploy:
  resources:
    limits:
      memory: 512M  # 降低内存限制
```

### 健康检查

```bash
# 检查服务健康状态
curl -f http://localhost:8001/

# 检查API文档
curl -f http://localhost:8001/docs

# 检查容器健康状态
docker inspect --format='{{.State.Health.Status}}' metaignite-backend
```

## 🛠️ 维护操作

### 日常维护

```bash
# 查看服务状态
./offline-deploy.sh status

# 查看日志
./offline-deploy.sh logs

# 重启服务
./offline-deploy.sh restart

# 停止服务
./offline-deploy.sh stop

# 启动服务
./offline-deploy.sh start
```

### 数据备份

```bash
# 备份数据目录
tar -czf backup-$(date +%Y%m%d).tar.gz ./data

# 备份数据库（如果使用SQLite）
cp ./data/metaignite.db ./data/metaignite.db.backup
```

### 更新部署

```bash
# 1. 停止当前服务
./offline-deploy.sh stop

# 2. 备份数据
cp -r ./data ./data.backup

# 3. 导入新镜像
./offline-deploy.sh import

# 4. 启动新服务
./offline-deploy.sh deploy
```

### 清理资源

```bash
# 清理未使用的Docker资源
./offline-deploy.sh cleanup

# 手动清理
docker system prune -f
docker volume prune -f
```

## 📊 监控和日志

### 日志位置

- **应用日志**: `./logs/`
- **容器日志**: `docker logs metaignite-backend`
- **系统日志**: `/var/log/docker/`

### 监控指标

```bash
# 查看资源使用情况
docker stats metaignite-backend

# 查看容器详细信息
docker inspect metaignite-backend

# 查看端口监听情况
netstat -tlnp | grep 8001
```

## 🔒 安全建议

1. **更改默认密钥**: 修改`.env`文件中的`JWT_SECRET_KEY`
2. **限制网络访问**: 配置防火墙规则
3. **定期更新**: 定期更新Docker镜像和依赖
4. **数据加密**: 对敏感数据进行加密存储
5. **访问控制**: 配置适当的用户权限

## 📞 技术支持

如果遇到问题，请：

1. 查看本文档的故障排除部分
2. 检查容器日志：`./offline-deploy.sh logs`
3. 验证配置文件：检查`.env`和`conf.yaml`
4. 检查系统资源：内存、磁盘空间、网络

## 📄 附录

### 脚本命令参考

```bash
./offline-deploy.sh help     # 显示帮助信息
./offline-deploy.sh build    # 构建镜像
./offline-deploy.sh export   # 导出镜像
./offline-deploy.sh import   # 导入镜像
./offline-deploy.sh deploy   # 部署服务
./offline-deploy.sh start    # 启动容器
./offline-deploy.sh stop     # 停止容器
./offline-deploy.sh restart  # 重启容器
./offline-deploy.sh status   # 检查状态
./offline-deploy.sh logs     # 显示日志
./offline-deploy.sh cleanup  # 清理资源
./offline-deploy.sh full     # 完整部署
./offline-deploy.sh offline  # 离线部署
```

### Docker Compose命令参考

```bash
docker-compose up -d         # 后台启动服务
docker-compose down          # 停止并删除容器
docker-compose ps            # 查看服务状态
docker-compose logs          # 查看日志
docker-compose restart       # 重启服务
docker-compose pull          # 拉取最新镜像
docker-compose build         # 构建镜像
```

---

**版本**: 1.0.0  
**更新日期**: 2024年  
**维护者**: MetaIgnite Team
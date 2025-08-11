# GitHub 上传指导

## 项目准备状态

✅ **已完成的步骤：**
- 检查并保护敏感信息（.env文件已被.gitignore忽略）
- 完善.gitignore文件，确保敏感文件不会被上传
- 初始化Git仓库
- 添加所有项目文件并创建初始提交

## 接下来需要完成的步骤

### 1. 在GitHub上创建新仓库

1. 打开 [GitHub](https://github.com) 并登录您的账户
2. 点击右上角的 "+" 按钮，选择 "New repository"
3. 填写仓库信息：
   - **Repository name**: `MetaIgnite-backend`（或您喜欢的名称）
   - **Description**: `MetaIgnite AI Backend with OAuth Integration - FastAPI based backend service`
   - **Visibility**: 选择 Public 或 Private（根据您的需求）
   - **不要**勾选 "Initialize this repository with a README"（因为我们已经有本地代码）
   - **不要**添加 .gitignore 或 license（我们已经配置好了）
4. 点击 "Create repository"

### 2. 连接本地仓库到GitHub

在您的终端中执行以下命令（请将 `YOUR_USERNAME` 替换为您的GitHub用户名，`REPOSITORY_NAME` 替换为您创建的仓库名称）：

```bash
# 添加远程仓库
git remote add origin https://github.com/YOUR_USERNAME/REPOSITORY_NAME.git

# 推送代码到GitHub
git branch -M main
git push -u origin main
```

### 3. 验证上传

1. 刷新您的GitHub仓库页面
2. 确认所有文件都已成功上传
3. 检查以下敏感文件是否**没有**被上传：
   - `.env` 文件
   - `conf.yaml` 文件
   - `venv/` 目录
   - `__pycache__/` 目录
   - `*.db` 数据库文件

## 重要安全提醒

🔒 **敏感信息保护：**
- `.env` 文件包含OAuth客户端密钥等敏感信息，已被.gitignore忽略
- 如果您需要与团队共享配置，请使用 `.env.example` 文件作为模板
- 在生产环境中，请确保使用环境变量或安全的配置管理服务

## 分支管理指导

### 为什么使用个人分支？

使用个人分支而不是直接提交到主分支有以下优势：
- 🔒 **保护主分支**：避免直接修改主分支，保持代码稳定性
- 🔄 **代码审查**：通过Pull Request进行代码审查
- 🚀 **并行开发**：多人可以同时在不同分支上工作
- 📝 **版本控制**：更好的版本管理和回滚能力

### 1. 创建个人分支

#### 方法一：从本地创建分支
```bash
# 创建并切换到新分支（推荐使用有意义的分支名）
git checkout -b feature/your-feature-name

# 或者分别执行
git branch feature/your-feature-name  # 创建分支
git checkout feature/your-feature-name  # 切换到分支
```

#### 方法二：从GitHub创建分支
1. 在GitHub仓库页面点击分支下拉菜单
2. 输入新分支名称
3. 点击"Create branch"
4. 在本地拉取新分支：
   ```bash
   git fetch origin
   git checkout feature/your-feature-name
   ```

#### 分支命名建议
- `feature/功能名称` - 新功能开发
- `bugfix/问题描述` - 修复bug
- `hotfix/紧急修复` - 紧急修复
- `docs/文档更新` - 文档更新
- `refactor/重构内容` - 代码重构

### 2. 在个人分支上工作

```bash
# 查看当前分支
git branch

# 查看分支状态
git status

# 添加修改的文件
git add .

# 提交更改
git commit -m "feat: 添加新功能描述"

# 查看提交历史
git log --oneline
```

#### 提交信息规范建议
- `feat:` 新功能
- `fix:` 修复bug
- `docs:` 文档更新
- `style:` 代码格式调整
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建过程或辅助工具的变动

### 3. 推送个人分支到GitHub

```bash
# 第一次推送分支到远程仓库
git push -u origin feature/your-feature-name

# 后续推送（已设置上游分支后）
git push
```

### 4. 创建Pull Request

#### 在GitHub网页上创建PR
1. 推送分支后，GitHub会显示"Compare & pull request"按钮
2. 点击按钮或手动创建：
   - 进入仓库页面
   - 点击"Pull requests"标签
   - 点击"New pull request"
3. 选择分支：
   - **base**: `main`（目标分支）   
   - **compare**: `feature/your-feature-name`（您的分支）
4. 填写PR信息：
   - **标题**：简洁描述更改内容
   - **描述**：详细说明更改、原因和测试情况
5. 点击"Create pull request"

#### PR描述模板建议
```markdown
## 更改说明
- 添加了什么功能
- 修复了什么问题
- 重构了什么代码

## 测试情况
- [ ] 本地测试通过
- [ ] API测试通过
- [ ] OAuth功能测试通过

## 相关Issue
- 关闭 #issue_number

## 截图（如适用）
<!-- 添加相关截图 -->
```

### 5. 分支管理最佳实践

#### 保持分支同步
```bash
# 切换到主分支
git checkout main

# 拉取最新更改
git pull origin main

# 切换回您的分支
git checkout feature/your-feature-name

# 合并主分支的最新更改
git merge main

# 或使用rebase（推荐）
git rebase main
```

#### 清理已合并的分支
```bash
# 删除本地分支（PR合并后）
git branch -d feature/your-feature-name

# 删除远程分支
git push origin --delete feature/your-feature-name

# 清理本地的远程分支引用
git remote prune origin
```

#### 多人协作建议
1. **定期同步**：每天开始工作前先同步主分支
2. **小步提交**：频繁提交小的更改，便于追踪和回滚
3. **描述清晰**：提交信息和PR描述要清晰明了
4. **代码审查**：认真进行代码审查，提供建设性反馈
5. **测试完整**：确保所有测试通过再创建PR

### 6. 常见问题解决

#### 分支冲突解决
```bash
# 如果合并时出现冲突
git status  # 查看冲突文件

# 手动编辑冲突文件，解决冲突标记
# <<<<<<< HEAD
# 您的更改
# =======
# 其他人的更改
# >>>>>>> branch-name

# 解决冲突后
git add .
git commit -m "resolve: 解决合并冲突"
```

#### 撤销更改
```bash
# 撤销工作区的更改
git checkout -- filename

# 撤销暂存区的更改
git reset HEAD filename

# 撤销最后一次提交（保留更改）
git reset --soft HEAD~1

# 撤销最后一次提交（丢弃更改）
git reset --hard HEAD~1
```

## 后续步骤建议

### 1. 更新README.md
建议在GitHub上编辑或本地更新README.md文件，添加：
- 项目简介
- OAuth配置说明
- 部署指南链接
- API文档链接
- 分支管理规范

### 2. 设置GitHub Actions（可选）
可以考虑添加CI/CD流水线：
- 自动化测试
- 代码质量检查
- 自动部署
- PR检查

### 3. 配置分支保护（推荐）
如果是团队项目，强烈建议：
- 保护main分支
- 要求Pull Request审查
- 启用状态检查
- 要求分支保持最新
- 限制推送权限

## 故障排除

### 如果推送失败：

1. **认证问题**：
   ```bash
   # 如果使用HTTPS，可能需要个人访问令牌
   # 在GitHub Settings > Developer settings > Personal access tokens 中创建
   ```

2. **远程仓库已存在内容**：
   ```bash
   # 强制推送（谨慎使用）
   git push -f origin main
   ```

3. **网络问题**：
   ```bash
   # 检查网络连接
   git remote -v
   ping github.com
   ```

## 联系支持

如果遇到问题，可以：
1. 查看GitHub官方文档
2. 检查Git配置：`git config --list`
3. 查看详细错误信息并搜索解决方案

---

**注意**：本指导假设您已经有GitHub账户。如果没有，请先在 [GitHub](https://github.com) 注册账户。
#!/bin/bash

# MetaIgnite Backend 离线部署脚本
# 用于内网环境的Docker离线部署

set -e  # 遇到错误时退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置变量
IMAGE_NAME="metaignite-backend"
IMAGE_TAG="latest"
TAR_FILE="${IMAGE_NAME}-${IMAGE_TAG}.tar"
CONTAINER_NAME="metaignite-backend"
PORT="8001"

# 函数：打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 函数：检查Docker是否安装
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker未安装，请先安装Docker"
        exit 1
    fi
    print_success "Docker已安装"
}

# 函数：构建Docker镜像
build_image() {
    print_info "开始构建Docker镜像..."
    if docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .; then
        print_success "Docker镜像构建成功: ${IMAGE_NAME}:${IMAGE_TAG}"
    else
        print_error "Docker镜像构建失败"
        exit 1
    fi
}

# 函数：导出Docker镜像
export_image() {
    print_info "导出Docker镜像到文件: ${TAR_FILE}"
    if docker save ${IMAGE_NAME}:${IMAGE_TAG} > ${TAR_FILE}; then
        print_success "镜像导出成功: ${TAR_FILE}"
        print_info "镜像文件大小: $(du -h ${TAR_FILE} | cut -f1)"
    else
        print_error "镜像导出失败"
        exit 1
    fi
}

# 函数：导入Docker镜像
import_image() {
    if [ ! -f "${TAR_FILE}" ]; then
        print_error "镜像文件不存在: ${TAR_FILE}"
        exit 1
    fi
    
    print_info "导入Docker镜像: ${TAR_FILE}"
    if docker load < ${TAR_FILE}; then
        print_success "镜像导入成功"
    else
        print_error "镜像导入失败"
        exit 1
    fi
}

# 函数：停止并删除现有容器
stop_container() {
    if docker ps -q -f name=${CONTAINER_NAME} | grep -q .; then
        print_info "停止现有容器: ${CONTAINER_NAME}"
        docker stop ${CONTAINER_NAME}
    fi
    
    if docker ps -aq -f name=${CONTAINER_NAME} | grep -q .; then
        print_info "删除现有容器: ${CONTAINER_NAME}"
        docker rm ${CONTAINER_NAME}
    fi
}

# 函数：运行容器
run_container() {
    print_info "启动容器: ${CONTAINER_NAME}"
    
    # 创建数据和日志目录
    mkdir -p ./data ./logs
    
    # 检查.env文件是否存在
    if [ ! -f ".env" ]; then
        print_warning ".env文件不存在，将使用默认配置"
        if [ -f ".env.example" ]; then
            print_info "复制.env.example到.env"
            cp .env.example .env
        fi
    fi
    
    # 运行容器
    if docker run -d \
        --name ${CONTAINER_NAME} \
        -p ${PORT}:${PORT} \
        -v $(pwd)/data:/app/data \
        -v $(pwd)/logs:/app/logs \
        --env-file .env \
        --restart unless-stopped \
        ${IMAGE_NAME}:${IMAGE_TAG}; then
        print_success "容器启动成功"
        print_info "服务地址: http://localhost:${PORT}"
        print_info "API文档: http://localhost:${PORT}/docs"
    else
        print_error "容器启动失败"
        exit 1
    fi
}

# 函数：检查容器状态
check_status() {
    print_info "检查容器状态..."
    if docker ps -f name=${CONTAINER_NAME} --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -q ${CONTAINER_NAME}; then
        print_success "容器运行正常"
        docker ps -f name=${CONTAINER_NAME} --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        
        # 等待服务启动
        print_info "等待服务启动..."
        sleep 10
        
        # 检查健康状态
        if curl -f http://localhost:${PORT}/ > /dev/null 2>&1; then
            print_success "服务健康检查通过"
        else
            print_warning "服务可能还在启动中，请稍后检查"
        fi
    else
        print_error "容器未运行"
        exit 1
    fi
}

# 函数：显示日志
show_logs() {
    print_info "显示容器日志 (最后50行):"
    docker logs --tail 50 ${CONTAINER_NAME}
}

# 函数：清理资源
cleanup() {
    print_info "清理Docker资源..."
    docker system prune -f
    print_success "清理完成"
}

# 函数：显示帮助信息
show_help() {
    echo "MetaIgnite Backend 离线部署脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  build     构建Docker镜像"
    echo "  export    导出Docker镜像到tar文件"
    echo "  import    从tar文件导入Docker镜像"
    echo "  deploy    部署应用（停止旧容器，启动新容器）"
    echo "  start     启动容器"
    echo "  stop      停止容器"
    echo "  restart   重启容器"
    echo "  status    检查容器状态"
    echo "  logs      显示容器日志"
    echo "  cleanup   清理Docker资源"
    echo "  full      完整部署（构建+导出+部署）"
    echo "  offline   离线部署（导入+部署）"
    echo "  help      显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 full      # 完整部署流程"
    echo "  $0 offline   # 离线环境部署"
    echo "  $0 status    # 检查服务状态"
}

# 主函数
main() {
    case "$1" in
        "build")
            check_docker
            build_image
            ;;
        "export")
            check_docker
            export_image
            ;;
        "import")
            check_docker
            import_image
            ;;
        "deploy")
            check_docker
            stop_container
            run_container
            check_status
            ;;
        "start")
            check_docker
            run_container
            ;;
        "stop")
            check_docker
            stop_container
            ;;
        "restart")
            check_docker
            stop_container
            run_container
            check_status
            ;;
        "status")
            check_docker
            check_status
            ;;
        "logs")
            check_docker
            show_logs
            ;;
        "cleanup")
            check_docker
            cleanup
            ;;
        "full")
            check_docker
            build_image
            export_image
            stop_container
            run_container
            check_status
            ;;
        "offline")
            check_docker
            import_image
            stop_container
            run_container
            check_status
            ;;
        "help"|"--help"|"-h")
            show_help
            ;;
        "")
            print_info "使用 '$0 help' 查看帮助信息"
            show_help
            ;;
        *)
            print_error "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"
# 项目规则：全栈项目（Vue + FastAPI + MySQL + MongoDB + Redis + Celery + RabbitMQ + Docker）

## 1. 技术栈概览

| 层级 | 技术选型 | 说明 |
|------|----------|------|
| 前端 | Vue 3 + TypeScript + Vite + Pinia | 组件库建议使用 Element Plus 或 Ant Design Vue |
| 后端 | Python 3.9.12 + FastAPI + Uvicorn | 使用 Pydantic v2 进行数据验证 |
| 关系数据库 | MySQL 8.0 | ORM 使用 SQLAlchemy 2.0，异步驱动使用 aiomysql |
| 非关系数据库 | MongoDB 6.0 | ODM 使用 Motor（异步） |
| 缓存 | Redis 7.0 | 用于会话、缓存、速率限制 |
| 任务队列 | Celery + RabbitMQ | Celery 作为分布式任务队列，RabbitMQ 作为 broker |
| 部署 | Docker + Docker Compose | 容器化部署，多阶段构建 |

## 2. 目录结构规范

### 后端目录结构
backend/
├── app/
│ ├── api/ # 路由层（FastAPI 路由）
│ │ ├── v1/ # API 版本
│ │ │ ├── endpoints/ # 具体端点模块
│ │ │ └── deps.py # 依赖注入
│ ├── core/ # 核心配置、安全、数据库连接
│ │ ├── config.py # 环境变量配置
│ │ ├── security.py # 认证、加密
│ │ └── database.py # 数据库会话管理
│ ├── models/ # SQLAlchemy 模型（MySQL）
│ ├── schemas/ # Pydantic 模型（请求/响应）
│ ├── services/ # 业务逻辑层
│ ├── repositories/ # 数据访问层（可选）
│ ├── tasks/ # Celery 任务
│ │ ├── celery_app.py
│ │ └── worker.py
│ └── utils/ # 工具函数
├── tests/ # 单元测试
├── alembic/ # 数据库迁移
├── docker/ # Docker 相关文件
├── .env.example
├── requirements.txt # 或 pyproject.toml
└── docker-compose.yml
### 前端目录结构
frontend/
├── public/
├── src/
│ ├── api/ # 后端 API 调用封装
│ ├── assets/ # 静态资源
│ ├── components/ # 公共组件
│ ├── composables/ # 组合式函数
│ ├── layouts/ # 布局组件
│ ├── router/ # Vue Router
│ ├── stores/ # Pinia 状态管理
│ ├── types/ # TypeScript 类型定义
│ ├── utils/ # 工具函数
│ ├── views/ # 页面组件
│ ├── App.vue
│ └── main.ts
├── .env.example
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── Dockerfile
## 3. 编码规范

### 3.1 Python（后端）
- 使用 **Black** 格式化，行宽 88。
- 使用 **Flake8** 或 **Ruff** 进行代码检查。
- 所有函数和类必须包含类型注解（Type Hints）。
- 异步接口：使用 `async def` 配合 `await`，数据库操作使用异步驱动。
- 错误处理：使用 FastAPI 的 `HTTPException`，自定义异常类放在 `core/exceptions.py`。

### 3.2 Vue（前端）
- 使用 **组合式 API**（`<script setup>`）编写组件。
- 组件命名采用 **PascalCase**，文件名采用 `kebab-case`。
- Props 必须定义 TypeScript 类型，并尽量设置默认值或标记 `required`。
- 状态管理：优先使用 Pinia，禁止直接修改 store 外的状态。
- API 请求：统一封装在 `src/api` 下，使用 axios，并配置拦截器处理 token 和错误。

## 4. 数据库规范

### 4.1 MySQL
- 表名使用 `snake_case`，单数形式（如 `user`, `order_item`）。
- 必须包含 `id`（自增主键）、`created_at`、`updated_at` 字段。
- 索引命名：`idx_表名_字段名`，唯一索引：`uniq_表名_字段名`。
- 使用 Alembic 管理迁移，所有迁移脚本必须可回滚。

### 4.2 MongoDB
- 集合名使用 `snake_case`，复数形式（如 `users`, `logs`）。
- 文档必须包含 `_id`（ObjectId），并建议添加 `created_at`、`updated_at`（ISO 日期）。
- 索引在代码中定义（Motor 的 `create_indexes`），并在应用启动时自动创建。

### 4.3 Redis
- 键命名规则：`项目名:模块:用途:标识`（如 `myapp:session:{user_id}`）。
- 设置合理的过期时间，避免内存泄漏。
- 在代码中使用 Redis 连接池。

## 5. 异步任务与消息队列

### 5.1 Celery 配置
- Celery 应用放在 `backend/app/tasks/celery_app.py`。
- 任务函数使用 `@celery_app.task` 装饰器，并定义清晰的任务名。
- 任务结果后端：使用 Redis（配置 `result_backend`）。
- 周期性任务（beat）单独编写配置。

### 5.2 RabbitMQ
- 交换机（Exchange）命名：`项目名.exchange.类型`。
- 队列（Queue）命名：`项目名.queue.功能`。
- 路由键（Routing Key）使用点分隔的层次结构（如 `order.created`）。

## 6. 容器化部署规范

### 6.1 Dockerfile 最佳实践
- 后端使用多阶段构建，最终镜像基于 `python:3.9.12-slim`。
- 前端使用 `node:18-alpine` 构建，最终镜像基于 `nginx:alpine` 提供静态文件。
- 所有镜像应设置非 root 用户运行。
- 使用 `.dockerignore` 排除不必要的文件。

### 6.2 Docker Compose 服务编排
- 服务包括：`backend`、`frontend`、`mysql`、`mongodb`、`redis`、`rabbitmq`、`celery_worker`、`celery_beat`（如需）。
- 所有服务使用自定义网络（`internal`），只暴露必要的端口。
- 环境变量统一通过 `.env` 文件注入，该文件不提交到版本库。

### 6.3 环境变量示例
MYSQL_ENGINE = "mysql+pymysql"
MYSQL_HOST = os.getenv('MYSQL_HOST', '192.168.1.236')
MYSQL_PORT = os.getenv('MYSQL_PORT', '3306')
MYSQL_USER = os.getenv('MYSQL_USER', 'root')
MYSQL_PWD = os.getenv('MYSQL_PWD', '123456')
MYSQL_DB = os.getenv('MYSQL_DB', 'house')
MONGO_HOST = os.getenv('MONGO_HOST', '192.168.1.236')
MONGO_PORT = os.getenv('MONGO_PORT', 27017)
MONGO_USER = os.getenv('MONGO_USER')
MONGO_PWD = os.getenv('MONGO_PWD')
MONGO_DB = os.getenv('MONGO_DB', 'house')
REDIS_HOST = os.environ.get('REDIS_HOST', "192.168.1.236")
REDIS_PORT = os.environ.get('REDIS_PORT', 6379)
RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST', '192.168.1.236')
RABBITMQ_PORT = os.environ.get('RABBITMQ_PORT', '5672')
RABBITMQ_USER = os.environ.get('RABBITMQ_USER', 'user')
RABBITMQ_PWD = os.environ.get('RABBITMQ_PWD', '123456')
## 7. 工作流程（可选）

遵循 **6A 工作流** 以提高 AI 辅助开发的准确性：

1. **Align**：需求对齐，生成 `docs/ALIGNMENT.md`。
2. **Architect**：架构设计，生成 `docs/DESIGN.md`（包含 Mermaid 架构图）。
3. **Atomize**：任务拆分，生成 `docs/TASKS.md`，定义每个子任务的输入/输出。
4. **Approve**：暂停等待人工审批。
5. **Automate**：自动执行代码编写、测试。
6. **Assess**：评估交付，生成验收报告。

## 8. 注意事项

- 所有配置文件（`docker-compose.yml`、`.env.example`）必须提供示例，便于新成员上手。
- 提交代码前必须通过所有单元测试，并确保 lint 检查通过。
- 容器化部署时，确保各服务健康检查（healthcheck）配置正确。
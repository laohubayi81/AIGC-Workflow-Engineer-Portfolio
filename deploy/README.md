# Docker 部署 ComfyUI（Day 22）

镜像里只有代码和节点。**权重挂盘，不打进镜像。**

本机日常是 **Comfy Desktop**（Python 3.13 / CUDA 13 / 8188）。容器是另一套 Ubuntu + CUDA 12.4 base，方便以后搬云 4090。

**本机结论（2026-09-04）：步骤如下。实际 `up` 因拉 CUDA 层只有 KB/s 已跳过，容器未跑通。面试不要说 Docker 已部署成功。**

---

## 部署步骤（以后网络好了按这个做）

### 1. 打开 Docker Desktop

托盘图标变成 Running。Settings → Resources → File sharing：勾选 **D:**。

### 2. 修好 Docker Hub（国内必做）

Settings → **Docker Engine**，JSON **保留原有字段**，补上：

```json
"registry-mirrors": ["https://docker.m.daocloud.io"],
"ipv6": false
```

Apply & restart。

若 Clash 已开：Settings → Resources → **Proxies** → Manual，填 `http://127.0.0.1:7890`（端口以你的代理为准）。第一次失败就是因为没代理、还走了 IPv6。

### 3. 关掉 Comfy Desktop

否则和容器抢 **8188**。

### 4. 写环境变量

```powershell
cd D:\my\AIGC-Workflow-Engineer-Portfolio
copy /Y deploy\docker\.env.example deploy\docker\.env
```

默认挂载：

- 模型 `D:/Comfy-Desktop/ComfyUI-Shared/models` → `/models`
- 输入 `.../input` → `/input`
- 输出 `.../output` → `/output`

### 5. 构建并启动

```powershell
docker compose -f deploy\docker\compose.yml up --build
```

第一次会拉基础镜像 + 装 PyTorch，要几十分钟。某一层长期停在 KB/s：`Ctrl+C` 停掉，不要空等。

起来后浏览器：`http://127.0.0.1:8188`

### 6. 测写真 API（另开窗口）

```powershell
python agent-project\examples\generate_one.py
```

### 7. 停止

终端 `Ctrl+C`，或：

```powershell
docker compose -f deploy\docker\compose.yml down
```

---

## 文件

| 文件 | 作用 |
|---|---|
| `deploy/docker/Dockerfile` | CUDA 12.4 **base** + ComfyUI + 写真节点 + IdentityGate |
| `deploy/docker/compose.yml` | GPU、`8188`、三个 bind-mount |
| `deploy/docker/extra_model_paths.yaml` | 容器内 `/models` |
| `deploy/docker/.env.example` | Windows 路径 |

默认镜像 **不含** LTX / GGUF / ReActor / RIFE。不要把 Windows 的 `custom_nodes` 整个挂进 Linux。

---

## 本机已经踩过的坑

| 现象 | 原因 |
|---|---|
| `dockerDesktopLinuxEngine` 找不到 | Desktop 没开 |
| `registry-1.docker.io` IPv6 超时 | Hub 直连失败，要镜像或代理 |
| 670MB 一层只有 **KB/s** | DaoCloud 拉 `nvidia/cuda` 也会堵；已改用更小的 `cuda:base`，仍可能慢 |
| 和 Desktop 抢端口 | 两边都是 8188 |

云上用同一份 compose，改 `.env` 里的目录；机器要有 NVIDIA Container Toolkit。

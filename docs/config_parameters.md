# DUIX 配置文件参数详解

本文档详细说明 `config.j` 文件中各个参数的含义和作用。

## 📋 配置文件结构

`config.j` 是加密的 JSON 配置文件，解密后格式如下：

```json
{
  "width": 540,
  "height": 960,
  "need_png": 1,
  "res_fmt": "sij",
  "modelkind": 0,
  "ranges": null,
  "reverse": null,
  "removegreen": true
}
```

---

## 🔧 参数详解

### 1. `width` / `height`

**类型**: `int`  
**默认值**: `540` / `960`  
**说明**: 视频分辨率（宽度 × 高度）

- 用于设置模型输入和输出的视频尺寸
- 通常为 540×960（竖屏）或 960×540（横屏）

---

### 2. `need_png` ⚠️

**类型**: `int`  
**默认值**: `0`  
**可选值**: `0` 或 `1`  
**说明**: 控制是否启用 mask 功能

#### ⚠️ 重要说明

**`need_png` 参数不决定 `raw_jpgs` 目录中图片的实际格式！**

图片格式由**文件内容**（文件头 Magic Number）决定：
- JPEG 文件头：`FF D8 FF`（JFIF 格式）
- PNG 文件头：`89 50 4E 47 0D 0A 1A 0A`

#### 参数行为

| 值 | 行为 | 说明 |
|---|---|---|
| `0` (默认) | 检查 `pha` 和 `raw_sg` 目录是否存在 | 如果两个目录都存在，则启用 mask 功能（`hasMask=true`），会从 `pha` 目录加载 PNG 格式的 mask 文件 |
| `1` | 直接禁用 mask 功能 | 设置 `hasMask=false`，不加载 mask 文件，即使 `pha` 和 `raw_sg` 目录存在 |

#### 代码逻辑（反编译）

```java
// ModelInfoLoader.java 第 592-632 行
int need_png = config.optInt("need_png", 0);
boolean hasMask = false;

if (need_png == 0) {
    // 检查 pha 和 raw_sg 目录是否存在
    File phaDir = new File(path, "pha");
    File rawSgDir = new File(path, "raw_sg");
    if (phaDir.exists() && rawSgDir.exists()) {
        hasMask = true;  // 启用 mask 功能
    }
} else {
    // need_png == 1，直接禁用 mask 功能
    hasMask = false;
}

modelInfo.setHasMask(hasMask);
```

#### 实际影响

- **`hasMask=true`** 时：
  - 会从 `pha` 目录加载 PNG 格式的 mask 文件
  - 会从 `raw_sg` 目录加载对应的文件
  - 用于更精细的人脸区域控制

- **`hasMask=false`** 时：
  - 不加载额外的 mask 文件
  - 使用默认的人脸处理流程

#### 常见误解

❌ **错误理解**：`need_png=1` 表示图片是 PNG 格式  
✅ **正确理解**：`need_png=1` 表示不需要额外的 PNG mask 文件

---

### 3. `res_fmt`

**类型**: `string`  
**默认值**: `"sij"`  
**说明**: 资源文件扩展名（仅用于标识，不影响实际格式）

- 用于指定 `raw_jpgs` 目录中图片文件的扩展名
- 常见值：`"sij"`、`"jpg"`、`"png"`
- **注意**：这只是文件扩展名，实际图片格式由文件内容决定

#### 示例

```json
{
  "res_fmt": "sij"  // raw_jpgs 目录中的文件扩展名为 .sij
}
```

即使 `res_fmt="sij"`，如果文件内容是 JPEG（文件头是 `FF D8 FF`），它就是 JPEG 格式。

---

### 4. `modelkind`

**类型**: `int`  
**默认值**: `0`  
**说明**: 模型类型

- `0`: 标准模型
- `128`: 128 通道模型
- `168`: 168 通道模型（更常见）

影响模型初始化和推理流程。

---

### 5. `ranges`

**类型**: `array` 或 `null`  
**默认值**: `null`  
**说明**: 范围区域配置

用于定义静音区域或动作区域：

```json
{
  "ranges": [
    {
      "min": 0,      // 起始帧索引
      "max": 100,    // 结束帧索引
      "type": 0      // 0=静音, 1=动作
    }
  ]
}
```

---

### 6. `reverse`

**类型**: `boolean` 或 `null`  
**默认值**: `null`  
**说明**: 是否反向播放

---

### 7. `removegreen`

**类型**: `boolean`  
**默认值**: `false`  
**说明**: 是否需要去除绿幕

- `true`: 启用绿幕去除功能
- `false`: 不处理绿幕

---

## 📝 总结

### 关键要点

1. **图片格式由文件内容决定**，不是由配置参数决定
2. **`need_png` 只控制 mask 功能**，不决定图片格式
3. **`res_fmt` 只是文件扩展名**，不影响实际格式
4. 即使 `need_png=1`，如果文件内容是 JPEG，它就是 JPEG 格式

### 检查图片格式的方法

```bash
# 使用 file 命令检查
file raw_jpgs/1.sij

# 使用 hexdump 查看文件头
hexdump -C raw_jpgs/1.sij | head -1

# JPEG 文件头: FF D8 FF
# PNG 文件头: 89 50 4E 47 0D 0A 1A 0A
```

---

## 🔗 相关文档

- [加密机制分析](./encryption_analysis.md)
- [资源加载器反编译结果](../resource_loader_decompiled/README.md)
- [Android 数据流分析](./android_data_flow.md)

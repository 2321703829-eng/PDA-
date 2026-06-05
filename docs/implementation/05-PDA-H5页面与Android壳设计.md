# PDA H5 页面 + Android 壳层设计

> 版本: v1.0
> 日期: 2026-06-05
> 设备: 优博讯 i6310（5.5寸屏，720×1280）
> 架构: Kotlin WebView 壳 + Vue3 H5

---

## 一、H5 页面结构

### 1.1 页面清单

| # | 页面 | 路由 | 核心功能 |
|---|------|------|---------|
| 1 | 登录页 | `/login` | 账号密码 + 选仓库 |
| 2 | 首页 | `/home` | 今日任务看板 + 功能入口 |
| 3 | 入库收货 - 列表 | `/receipt/list` | 待收货任务列表 |
| 4 | 入库收货 - 操作 | `/receipt/:id` | 逐行扫码确认 |
| 5 | 上架作业 - 列表 | `/putaway/list` | 待上架任务列表 |
| 6 | 上架作业 - 操作 | `/putaway/:id` | 扫商品→扫库位→确认 |
| 7 | 拣货任务 - 列表 | `/pick/list` | 待拣货任务列表 |
| 8 | 拣货任务 - 操作 | `/pick/:id` | 按路径拣货 |
| 9 | 退库操作 | `/return/create` | 创建退库 + 逐行添加 |
| 10 | 退货入库 - 列表 | `/sale-return/list` | 待退货入库列表 |
| 11 | 退货入库 - 操作 | `/sale-return/:id` | 扫码确认+品质标记 |
| 12 | 库存查询 | `/inventory` | 扫码查商品/库位库存 |

### 1.2 页面流转

```
登录 → 首页
         ├── 入库收货列表 → 收货操作页 → 完成 → 返回列表
         ├── 上架作业列表 → 上架操作页 → 完成 → 返回列表
         ├── 拣货任务列表 → 拣货操作页 → 完成 → 返回列表
         ├── 退库操作 → 逐行添加 → 提交 → 返回首页
         ├── 退货入库列表 → 退货操作页 → 完成 → 返回列表
         └── 库存查询 → 扫码查看结果
```

---

## 二、关键页面设计

### 2.1 首页（任务看板）

```
┌──────────────────────────────────┐
│  默认主仓          张三    ⚙️   │  ← 顶部栏：仓库名 + 用户 + 设置
├──────────────────────────────────┤
│                                  │
│  今日任务                         │
│  ┌──────┐  ┌──────┐             │
│  │  15  │  │   8  │             │
│  │待收货│  │待出库│             │
│  └──────┘  └──────┘             │
│  ┌──────┐  ┌──────┐             │
│  │  36  │  │   5  │             │
│  │待拣货│  │待盘点│             │
│  └──────┘  └──────┘             │
│                                  │
├──────────────────────────────────┤
│  功能                            │
│  ┌────┐┌────┐┌────┐┌────┐      │
│  │收货││上架││拣货││退库│      │
│  └────┘└────┘└────┘└────┘      │
│  ┌────┐┌────┐                    │
│  │退货││查询│                    │
│  │入库││库存│                    │
│  └────┘└────┘                    │
│                                  │
├──────────────────────────────────┤
│  [扫一扫] 万能扫码入口            │  ← 底部大按钮，扫码自动跳转
└──────────────────────────────────┘
```

**"扫一扫" 万能入口逻辑：**
- 扫到任务条码 → 自动跳转到对应操作页
- 扫到商品条码 → 跳转库存查询
- 扫到库位条码 → 跳转库位库存

### 2.2 拣货操作页（核心页面）

```
┌──────────────────────────────────┐
│ ← 返回    WMS-PICK-000128       │
│ 美宜多【黎冲店】  XC...00389     │
├──────────────────────────────────┤
│ 进度: ████░░░░ 2/5  (42%)       │
├──────────────────────────────────┤
│                                  │
│ 当前: 第3行                       │
│ ┌────────────────────────────┐  │
│ │ 📍 库位: A-02-01            │  │  ← 高亮显示下一个要去的位置
│ │ 📦 伊利 每益添原味350ml     │  │
│ │ 条码: 6907992103471         │  │
│ │ 需求: 60 瓶                  │  │
│ │                              │  │
│ │ 已拣: [    0    ] 瓶        │  │  ← 输入框
│ └────────────────────────────┘  │
│                                  │
│ ┌──────────────────────────────┐│
│ │ [扫描库位] → [扫描商品] → ✓ ││  ← 步骤提示
│ └──────────────────────────────┘│
│                                  │
├──────────────────────────────────┤
│ 待拣列表:                         │
│ ✅ 光明鲜牛奶 60/60 A-01-02     │
│ ✅ 卡士鲜酪乳 192/192 A-01-05  │
│ → 伊利每益添 0/60 A-02-01      │  ← 当前行
│ ○ 伊利百香果 0/40 A-02-01      │
│ ○ 蒙牛八连杯 0/60 A-03-02      │
│                                  │
├──────────────────────────────────┤
│       [ 完成拣货 ]                │  ← 全部行拣完后可点
└──────────────────────────────────┘
```

**交互流程：**

1. 进入页面 → 自动定位到第一个未拣行
2. 显示目标库位（大字高亮）
3. 操作员走到库位 → 按扫码键扫描库位码
4. 库位验证通过 → 提示扫描商品
5. 按扫码键扫描商品码
6. 商品验证通过 → 数量输入框聚焦（默认填入需求数量）
7. 确认数量 → 提交 → 自动跳转下一行
8. 全部行完成 → "完成拣货"按钮可用

**扫码事件处理（核心）：**

```javascript
// 监听 Android 壳传来的扫码结果
window.pda = window.pda || {}
window.pda.onScan = (code) => {
  switch (currentStep) {
    case 'scan_location':
      validateLocation(code)
      break
    case 'scan_product':
      validateProduct(code)
      break
    default:
      // 万能解析
      universalParse(code)
  }
}
```

### 2.3 入库收货操作页

```
┌──────────────────────────────────┐
│ ← 返回    WMS-REC-000201        │
│ 华农大食品  RK...00018           │
├──────────────────────────────────┤
│ 进度: ████████░░ 4/5  (80%)     │
├──────────────────────────────────┤
│                                  │
│ 📦 扫描商品条码确认收货           │
│                                  │
│ 上一条: 华农 学士奶 4080/4080 ✅ │
│                                  │
│ 待收货列表:                       │
│ ✅ 华农 学士奶    4080/4080      │
│ ✅ 华农 原味酸奶  800/800        │
│ ✅ 简爱 超级桶    300/300        │
│ ✅ 风行 乐悠黄桃  108/108        │
│ → 风行 乐悠黄桃(赠) 0/36       │  ← 待确认
│                                  │
├──────────────────────────────────┤
│  差异: 0 行    总计: 5288件      │
├──────────────────────────────────┤
│ [ 部分完成 ]    [ 全部完成 ]      │
└──────────────────────────────────┘
```

**交互：** 扫商品码 → 弹出数量确认框（预填 expected_qty）→ 确认 → 下一行

### 2.4 上架操作页

```
┌──────────────────────────────────┐
│ ← 返回    WMS-PUT-000305        │
│ 来源: 收货暂存区                  │
├──────────────────────────────────┤
│                                  │
│ 步骤 1: 扫描商品条码              │
│ 步骤 2: 扫描目标库位              │
│ 步骤 3: 确认数量                  │
│                                  │
│ ┌────────────────────────────┐  │
│ │ 商品: 华农 学士奶236ml      │  │
│ │ 待上架: 4080 盒             │  │
│ │                              │  │
│ │ 目标库位: [扫描库位]         │  │
│ │ 上架数量: [  4080  ]         │  │
│ └────────────────────────────┘  │
│                                  │
│ 已上架:                           │
│ ✅ 华农酸奶 → A-01-03 (800杯)  │
│ ✅ 简爱桶 → A-02-05 (300桶)    │
│                                  │
├──────────────────────────────────┤
│  剩余: 2种商品待上架              │
├──────────────────────────────────┤
│         [ 确认上架 ]              │
└──────────────────────────────────┘
```

### 2.5 退库操作页

```
┌──────────────────────────────────┐
│ ← 返回    新建退库单              │
├──────────────────────────────────┤
│                                  │
│ 退库类型: [退供应商 ▼]           │
│ 备注:     [                ]     │
│                                  │
├──────────────────────────────────┤
│ 扫描商品添加:                     │
│                                  │
│ ┌─────────────────────────────┐ │
│ │ 1. 珠江 原浆罐980ml×6       │ │
│ │    数量: 1件  原因: 破损     │ │
│ │                        [删] │ │
│ ├─────────────────────────────┤ │
│ │ 2. 可口可乐 矮罐330ml×24   │ │
│ │    数量: 3件  原因: 破损     │ │
│ │                        [删] │ │
│ └─────────────────────────────┘ │
│                                  │
│ 合计: 2种 4件                    │
│                                  │
├──────────────────────────────────┤
│         [ 提交退库 ]              │
└──────────────────────────────────┘
```

### 2.6 库存查询页

```
┌──────────────────────────────────┐
│ ← 返回    库存查询                │
├──────────────────────────────────┤
│                                  │
│  [扫描商品 或 库位条码]           │
│                                  │
├──────────────────────────────────┤
│ 光明 新鲜牧场鲜牛奶950ml         │
│ 条码: 6901209257452              │
│ 总库存: 2400  预留: 600          │
│ 可用: 1800                       │
│                                  │
│ 库位分布:                         │
│ ┌─────────────────────────────┐ │
│ │ A-01-02  1200  (预留300)    │ │
│ │ A-01-03   800  (预留200)    │ │
│ │ B-02-01   400  (预留100)    │ │
│ └─────────────────────────────┘ │
│                                  │
└──────────────────────────────────┘
```

---

## 三、H5 技术实现

### 3.1 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Vue 3 | 3.4+ | 框架 |
| Vite | 5.x | 构建工具 |
| Pinia | 2.x | 状态管理 |
| Vue Router | 4.x | 路由 |
| Vant 4 | 4.x | 移动端 UI 组件库 |
| Axios | 1.x | HTTP 请求 |

### 3.2 项目结构

```
pda-h5/
├── public/
│   └── favicon.ico
├── src/
│   ├── main.js
│   ├── App.vue
│   ├── router/
│   │   └── index.js
│   ├── stores/
│   │   ├── auth.js          # token、用户、仓库
│   │   ├── scan.js          # 扫码状态管理
│   │   └── task.js          # 当前任务缓存
│   ├── api/
│   │   ├── request.js       # axios 封装 + token 注入
│   │   ├── auth.js
│   │   ├── receipt.js
│   │   ├── putaway.js
│   │   ├── pick.js
│   │   ├── return.js
│   │   ├── saleReturn.js
│   │   └── inventory.js
│   ├── composables/
│   │   ├── useScan.js       # 监听 window.pda.onScan
│   │   ├── useBeep.js       # 调用 window.pda.beep
│   │   └── useNetwork.js    # 网络状态
│   ├── views/
│   │   ├── Login.vue
│   │   ├── Home.vue
│   │   ├── receipt/
│   │   │   ├── List.vue
│   │   │   └── Detail.vue
│   │   ├── putaway/
│   │   │   ├── List.vue
│   │   │   └── Detail.vue
│   │   ├── pick/
│   │   │   ├── List.vue
│   │   │   └── Detail.vue
│   │   ├── return/
│   │   │   └── Create.vue
│   │   ├── saleReturn/
│   │   │   ├── List.vue
│   │   │   └── Detail.vue
│   │   └── inventory/
│   │       └── Query.vue
│   ├── components/
│   │   ├── ScanIndicator.vue  # 扫码状态指示器
│   │   ├── TaskCard.vue       # 任务卡片
│   │   ├── LineItem.vue       # 明细行组件
│   │   ├── QtyInput.vue       # 数量输入（大按钮加减）
│   │   └── PhotoCapture.vue   # 拍照组件
│   └── utils/
│       ├── bridge.js         # JS Bridge 封装
│       └── offline.js        # 离线队列
├── vite.config.js
└── package.json
```

### 3.3 核心 composable: useScan

```javascript
// src/composables/useScan.js
import { ref, onMounted, onUnmounted } from 'vue'

export function useScan(callback) {
  const lastCode = ref('')
  const scanTime = ref(null)

  const handler = (code) => {
    lastCode.value = code
    scanTime.value = Date.now()
    callback(code)
  }

  onMounted(() => {
    // 注册到全局 bridge
    window.pda = window.pda || {}
    window.pda.onScan = handler
  })

  onUnmounted(() => {
    window.pda.onScan = null
  })

  return { lastCode, scanTime }
}
```

### 3.4 核心 composable: bridge 封装

```javascript
// src/utils/bridge.js
const bridge = {
  beep() {
    window.pda?.beep?.()
  },
  vibrate(ms = 100) {
    window.pda?.vibrate?.(ms)
  },
  async takePhoto() {
    return window.pda?.takePhoto?.()
  },
  getDeviceInfo() {
    return window.pda?.getDeviceInfo?.() || { model: 'browser', imei: 'dev' }
  },
  networkStatus() {
    return window.pda?.networkStatus?.() || 'wifi'
  }
}

export default bridge
```

---

## 四、Android 壳层设计（Kotlin）

### 4.1 核心职责

Android 壳 **不处理任何业务逻辑**，仅负责：

| 能力 | 实现方式 | JS Bridge 接口 |
|------|---------|----------------|
| 扫码 | Urovo ScanManager 广播 | `window.pda.onScan(code)` |
| 蜂鸣 | Android ToneGenerator | `window.pda.beep()` |
| 震动 | Android Vibrator | `window.pda.vibrate(ms)` |
| 拍照 | CameraX + 上传 OSS | `window.pda.takePhoto() → url` |
| 设备信息 | Android Build | `window.pda.getDeviceInfo()` |
| 网络状态 | ConnectivityManager | `window.pda.networkStatus()` |
| 自动更新 | DownloadManager + Install | 启动时自动检查 |

### 4.2 Urovo i6310 扫码集成

优博讯 i6310 使用 `android.device.ScanManager` SDK：

```kotlin
// scanner/ScannerManager.kt
import android.device.ScanManager

class ScannerManager(private val webView: WebView) {
    private var scanManager: ScanManager? = null

    fun init() {
        scanManager = ScanManager()
        scanManager?.openScanner()
        scanManager?.switchOutputMode(0) // 0 = Intent 模式

        // 注册广播接收器
        val filter = IntentFilter()
        filter.addAction("android.intent.ACTION_DECODE_DATA")
        context.registerReceiver(scanReceiver, filter)
    }

    private val scanReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context, intent: Intent) {
            val barcode = intent.getStringExtra("barcode_string") ?: return
            // 传递给 H5
            webView.evaluateJavascript(
                "window.pda && window.pda.onScan && window.pda.onScan('$barcode')",
                null
            )
            // 蜂鸣反馈
            beep()
        }
    }

    fun destroy() {
        scanManager?.closeScanner()
        context.unregisterReceiver(scanReceiver)
    }
}
```

### 4.3 JS Bridge 注入

```kotlin
// bridge/JSBridge.kt
class JSBridge(private val activity: MainActivity) {

    @JavascriptInterface
    fun beep() {
        val toneGen = ToneGenerator(AudioManager.STREAM_NOTIFICATION, 100)
        toneGen.startTone(ToneGenerator.TONE_PROP_BEEP, 150)
    }

    @JavascriptInterface
    fun vibrate(ms: Int) {
        val vibrator = activity.getSystemService(Context.VIBRATOR_SERVICE) as Vibrator
        vibrator.vibrate(VibrationEffect.createOneShot(ms.toLong(), 200))
    }

    @JavascriptInterface
    fun takePhoto(): String {
        // 启动相机 → 拍照 → 上传 OSS → 返回 URL
        // 实际实现通过 callback 异步返回
        return "" // 通过 evaluateJavascript 回调
    }

    @JavascriptInterface
    fun getDeviceInfo(): String {
        return JSONObject().apply {
            put("model", Build.MODEL)  // "UROVO i6310"
            put("imei", getIMEI())
            put("android", Build.VERSION.RELEASE)
            put("app_version", BuildConfig.VERSION_NAME)
        }.toString()
    }

    @JavascriptInterface
    fun networkStatus(): String {
        val cm = activity.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
        val network = cm.activeNetwork ?: return "offline"
        val caps = cm.getNetworkCapabilities(network) ?: return "offline"
        return when {
            caps.hasTransport(NetworkCapabilities.TRANSPORT_WIFI) -> "wifi"
            caps.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR) -> "4g"
            else -> "other"
        }
    }
}
```

### 4.4 MainActivity

```kotlin
// MainActivity.kt
class MainActivity : AppCompatActivity() {
    private lateinit var webView: WebView
    private lateinit var scannerManager: ScannerManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        webView = WebView(this).apply {
            settings.javaScriptEnabled = true
            settings.domStorageEnabled = true
            settings.allowFileAccess = true
            addJavascriptInterface(JSBridge(this@MainActivity), "pda")
            webViewClient = WebViewClient()
            loadUrl("https://your-odoo-server/pda/")  // H5 入口
        }
        setContentView(webView)

        scannerManager = ScannerManager(webView)
        scannerManager.init()

        // 检查更新
        UpdateManager(this).checkUpdate()
    }

    override fun onDestroy() {
        scannerManager.destroy()
        super.onDestroy()
    }
}
```

### 4.5 自动更新

```kotlin
// update/UpdateManager.kt
class UpdateManager(private val context: Context) {

    fun checkUpdate() {
        // 请求服务端版本号
        val serverVersion = fetchServerVersion() // GET /api/wms/v1/app/version
        val currentVersion = BuildConfig.VERSION_CODE

        if (serverVersion > currentVersion) {
            downloadAndInstall(apkUrl)
        }
    }

    private fun downloadAndInstall(url: String) {
        val request = DownloadManager.Request(Uri.parse(url))
        request.setDestinationInExternalPublicDir(Environment.DIRECTORY_DOWNLOADS, "pda-update.apk")
        val dm = context.getSystemService(Context.DOWNLOAD_SERVICE) as DownloadManager
        dm.enqueue(request)
        // 下载完成后触发安装 Intent
    }
}
```

---

## 五、开发计划（PDA 端）

| 阶段 | 工作 | 预估 | 产出 |
|------|------|------|------|
| 1 | Android 壳 + 扫码集成 | 2天 | APK 可装到 i6310 上，扫码有响应 |
| 2 | H5 框架搭建 + 登录 + 首页 | 1天 | 基本页面跑通 |
| 3 | 入库收货页面 + API 对接 | 2天 | 收货流程可用 |
| 4 | 拣货页面 + API 对接 | 2天 | 拣货流程可用 |
| 5 | 上架/退库/退货/库存查询 | 3天 | 全功能可用 |
| 6 | 拍照留痕 + 离线缓存 | 2天 | 增强功能 |
| 7 | 真机联调 + 修 bug | 2天 | 可交付 |
| **合计** | | **14天** | |

---

## 六、设备适配预留

若后续更换设备（非优博讯），只需修改 Android 壳层的 `ScannerManager`：

| 品牌 | 修改点 |
|------|--------|
| 新大陆 | Action → `nlscan.action.SCANNER_RESULT`，Key → `SCAN_BARCODE1` |
| 斑马 | 使用 DataWedge Profile 配置，Action/Key 可自定义 |
| iData | Action → `android.intent.action.SCANRESULT`，Key → `value` |
| 通用方案 | 将 Action/Key 写入 App 配置页，运行时可改 |

**推荐**：在 APK 设置页增加"扫码配置"选项，支持手动填写 Action 和 Key，做到一个 APK 适配所有品牌。

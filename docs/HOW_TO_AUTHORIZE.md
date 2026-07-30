# 强哥怎么给客户授权（自己看就行）

免费期到 **2027-12-31**。这之前用户界面**不会出现**授权按钮/价格。  
从 **2028-01-01** 起，没授权码就不能下载；这时界面才会弹出「输入授权码」。

## 你怎么发卡（3 步）

在电脑打开仓库目录，运行：

### ① 客户买断（收 ¥15）→ 生成永久码

```powershell
cd g:\lyt\wechat-channels-download
python tools\gen_license.py --life
```

屏幕会打印类似：

```text
授权码: SSQG-LIFE-XXXXXXXXXX
```

把这一整串发给客户即可。

### ② 客户月付（收 ¥5）→ 生成约 1 个月码

```powershell
python tools\gen_license.py --month --days 31
```

或指定到期日：

```powershell
python tools\gen_license.py --month --until 2028-03-31
```

### ③ 客户怎么用你的码

1. 打开软件（过期后会提示要授权）
2. 点 **「输入授权码」**
3. 粘贴你发的 `SSQG-...` → 确定  
   成功后就能继续下载

命令行用户也可以：

```powershell
python scripts\download_sph.py --license SSQG-你的码
```

## 收款怎么跟客户说（话术可直接复制）

> 视频号下载器 · 上海三松强哥出品  
> 2027年底前免费；之后继续用：  
> · 月付 5 元  
> · 买断 15 元（一次付清永久）  
> 付款后把截图发我，我发授权码给你。

## 注意

- 每个客户付款后，**现场再生成**一个码发给他（买断码可重复使用同一串，但建议按客户分别生成记录）
- 月付码到期后要再收 5 元、再发新码
- 生成工具在：`tools/gen_license.py`（只有你会用，不用给客户）

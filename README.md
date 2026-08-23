# 《一头醒狮的七日远行》交互网页

打开 `index.html` 即可预览。移动优先的纵向滚动叙事 H5，展示广东建院启智润心实践队在连州的非遗、科创与红色成长课堂。

## 已实现

- 移动端优先纵向滚动，顶部章节导航 + 故事进度条；
- 首屏 hero：醒狮 + 金色数据带 + 队徽 + 逐字入场；
- 交互：点醒醒狮 / 展开漆扇纹样 / 发射水火箭（含孩子愿望随机句）；
- 红色南粤：冯达飞「学生演 + 学生讲」史实表达提示卡；
- **传播引擎**：「为连州孩子，留下一句话」→ 输入祝福，生成专属纸飞机分享卡片（Canvas 出图 + 分享/复制）；
- **合规**：队徽（topbar + 结尾落款）、学校/学院/实践队署名、AI 辅助生成标注、`og:*`/微信分享 meta、`prefers-reduced-motion` 降级；
- **命门修复**：`.reveal` 默认 `opacity:1`，入场用 transform+blur——整页截图绝不空白（附件4 页面截图评审安全）。

## 资产

- `assets/team_logo.png`：队徽（蓝金）；`assets/*.webp`：示例图 WebP 版本；
- 示例图为占位，正式参赛请替换成真实学生照片、原话、舞台剧片段与成果展视频。

## 截图交付（附件4：JPEG / RGB / 100DPI / <10MB）

```bash
python3 make_shots.py   # 输出 shots/{full_desktop,hero_desktop,full_mobile,hero_mobile}.jpg
```

## 互动点亮瞬间关键帧（提交图集加分）

```bash
python3 make_keyframes.py  # 输出 shots/keyframes/{kf_01_hero_lion,kf_02_paint,kf_03_rocket,kf_04_wish_card,kf_05_hero_desktop}.jpg
```

## 自动化检查

```bash
python3 verify_page.py  # 冒烟测试：断言无 .reveal 为 opacity:0、既有交互、纸飞机 UGC、队徽、AI 标注
```

提交规范与「需真人补齐」清单见 `提交准备_校赛粤易创新.md`。创意/合规蓝图见 `升级蓝图_眼前一亮_v1.md`。

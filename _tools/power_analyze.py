# 7月和8月日用电对比 + 视频生产关联分析
days_jul = {
    1: 10.35, 2: 9.96, 3: 9.06, 4: 19.86, 5: 15.71, 6: 9.24, 7: 8.92,
    8: 6.29, 9: 6.89, 10: 6.14, 11: 20.08, 12: 34.50, 13: 18.22, 14: 12.69,
    15: 8.08, 16: 6.44, 17: 6.34, 18: 15.69, 19: 18.07, 20: 15.81, 21: 11.20,
    22: 11.34, 23: 12.26, 24: 16.10, 25: 13.84, 26: 2.99, 27: 5.62, 28: 8.69,
    29: 7.75, 30: 9.14, 31: 7.17
}
days_aug = {
    1: 15.16, 2: 14.20, 3: 8.61, 4: 8.78, 5: 10.89, 6: 15.20, 7: 12.41,
    8: 23.59, 9: 17.35, 10: 24.26, 11: 22.19, 12: 23.85, 13: 21.91, 14: 3.98,
    15: 7.95, 16: 25.19, 17: 13.52, 18: 12.32, 19: 15.74, 20: 12.54, 21: 10.25,
    22: 23.88, 23: 14.08, 24: 13.15, 25: 13.58,
}
video_renders = {
    '08-20': 5, '08-21': 0, '08-22': 0,
    '08-23': 20, '08-24': 5,
    '08-25': 49,
    '08-26': 23, '08-27': 8,
}

print("="*72)
print("【1】 7月 vs 8月 总体对比")
print("="*72)
total_jul = sum(days_jul.values())
total_aug = sum(days_aug.values())
print(f"7月(31天):  {total_jul:7.2f} 度  | 日均 {total_jul/31:5.2f} 度")
print(f"8月(25天,有数据): {total_aug:7.2f} 度  | 日均 {total_aug/25:5.2f} 度")
print(f"7月最低日: {min(days_jul.values()):.2f} (7/26) | 7月最高日: {max(days_jul.values()):.2f} (7/12)")
print(f"8月最低日: {min(days_aug.values()):.2f} (8/14) | 8月最高日: {max(days_aug.values()):.2f} (8/16)")
print()

print("="*72)
print("【2】 基础用电估算(剔除天气/周末效应)")
print("="*72)
all_days = []
for d, v in days_jul.items(): all_days.append(('7/'+str(d).zfill(2), v))
for d, v in days_aug.items(): all_days.append(('8/'+str(d).zfill(2), v))
vals = sorted([v for _,v in all_days])
print(f"所有日用电分布(7月+8月, {len(vals)}天):")
print(f"  最小 {vals[0]:.2f}, P10 {vals[len(vals)//10]:.2f}, 中位数 {vals[len(vals)//2]:.2f}, P75 {vals[len(vals)*3//4]:.2f}, 最大 {vals[-1]:.2f}")
print()

print("="*72)
print("【3】 视频生产日的用电表现(8月20日之后)")
print("="*72)
# 用8月11-19号(无视频生产)作为基线
base_window = [v for d,v in days_aug.items() if 11 <= d <= 19]
base_avg = sum(base_window)/len(base_window)
base_med = sorted(base_window)[len(base_window)//2]
print(f"基线(8月11-19,无视频生产)均值={base_avg:.2f} 中位数={base_med:.2f}")
print()

# 视频生产日(高耗日的用电 - 基线)
print("视频高产量日期:")
for d in [20, 23, 24, 25, 26]:
    v = days_aug.get(d)
    key = f'08-{d:02d}'
    rd = video_renders.get(key, 0)
    if v and rd > 0:
        delta = v - base_avg
        print(f"  8/{d:2d}: 段数={rd:2d}, 用电={v:5.2f}, 较基线{'+' if delta>0 else ''}{delta:5.2f}度")

print()
print("8月11-19基线日详情:")
for d in range(11,20):
    if d in days_aug:
        print(f"  8/{d:2d}: 用电={days_aug[d]:5.2f}")
print()

print("="*72)
print("【4】 用电增量分析")
print("="*72)
high_aug = [v for d,v in days_aug.items() if v >= 20]
print(f"8月用电>=20度的日子: {len(high_aug)}天, 合计 {sum(high_aug):.2f}度")
high_jul = [v for d,v in days_jul.items() if v >= 20]
print(f"7月用电>=20度的日子: {len(high_jul)}天, 合计 {sum(high_jul):.2f}度")
print()

print("=== 单段视频电耗估算(粗) ===")
total_render = sum(video_renders.values())
print(f"总视频渲染段数(8月20-27): {total_render}")
# 用最近相似温度天对照
print("\n8月(8月11-19,无视频生产):")
base_aug = sum(days_aug[d] for d in range(11,20))/9
print(f"  基线均值: {base_aug:.2f}度/天")
# 总生产电费: (高产量日用电 - 基线) 之和
overuse = 0
for d in [23, 24, 25]:
    v = days_aug[d]
    delt = max(0, v - base_aug)
    overuse += delt
    rd = video_renders[f'08-{d:02d}']
    print(f"  8/{d}: 用电{v:.2f} - 基线{base_aug:.2f} = 增量{delt:.2f}度 / {rd}段 = {delt/rd:.2f}度/段")
print(f"\n3个高产量日累计增量(超基线): {overuse:.2f}度")
print(f"对照同样天数(8/11-13): {sum(days_aug[d] for d in [11,12,13]):.2f}度")
print(f"差额(视频生产电费): {sum(days_aug[d] for d in [11,12,13]) - overuse:.2f}度")
# 注意: 8/22是另一个高耗日(无生产任务, 空调日)
print()
print(f"8/22用电23.88, 无视频生产(08-22=0段), 推测是空调日, 不能归入视频生产电费")
print()
print("="*72)
print("【5】 总额对比(估算)")
print("="*72)
# 8/20-27 8天总用电
aug_last8 = sum(days_aug[d] for d in range(20,26))  # 26日缺数据
# 基线对照(用8/11-19平均*8)
base_8 = base_avg * 6  # 实际有效对照天
print(f"8/20-25 实际用电: {aug_last8:.2f}度(6天)")
print(f"对照基线(用8/11-19均值): 6*{base_avg:.2f} = {6*base_avg:.2f}度")
delta_6days = aug_last8 - 6*base_avg
print(f"6天差额: {delta_6days:+.2f}度(视频生产用电增量)")
print(f"渲染总段数: {sum(video_renders[k] for k in video_renders if '08-2' in k)}段")
print(f"粗算单段电耗: {delta_6days / max(1,sum(video_renders[k] for k in video_renders if '08-2' in k)):.2f}度/段")

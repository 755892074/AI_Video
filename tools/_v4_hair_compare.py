import imageio_ffmpeg, subprocess, os
ff = imageio_ffmpeg.get_ffmpeg_exe()
out_dir = 'D:/WorkBuddy/AI_Video/shots/rebirth_cg_v4/output/_frames'
os.makedirs(out_dir, exist_ok=True)

ref = 'D:/WorkBuddy/AI_Video/shots/rebirth_cg_vertical/refs/char_female_lead.png'

# 参考图：左半（正面）裁 1:1
ref_face = f'{out_dir}/_ref_face.png'
subprocess.run([ff, '-y', '-i', ref, '-vf', 'crop=ih:ih:0:0,scale=512:512', '-frames:v', '1', ref_face], capture_output=True)
# 参考图：右半（背面）裁 1:1
ref_back = f'{out_dir}/_ref_back.png'
subprocess.run([ff, '-y', '-i', ref, '-vf', 'crop=ih:ih:iw-ih:0,scale=512:512', '-frames:v', '1', ref_back], capture_output=True)

# v4_01 背面 + 正面（中间侧脸帧类似背面，删掉）
v4 = 'D:/WorkBuddy/AI_Video/shots/rebirth_cg_v4/output/shot01.mp4'
v_face0 = f'{out_dir}/_v4_03s.png'
v_face4 = f'{out_dir}/_v4_47s.png'
for t, out in [(0.3, v_face0), (4.7, v_face4)]:
    subprocess.run([ff, '-y', '-ss', str(t), '-i', v4,
                    '-vf', 'crop=ih:ih:(iw-ih)/2:0,scale=512:512',
                    '-frames:v', '1', out], capture_output=True)

# 上排 2 张（参考正/背） = 1024x512
top = f'{out_dir}/_top.png'
r1 = subprocess.run([ff, '-y', '-i', ref_face, '-i', ref_back,
                '-filter_complex', '[0:v][1:v]hstack', top], capture_output=True, text=True)
print('top stderr:', r1.stderr[-200:])

# 下排 2 张（v4 背/正） = 1024x512
bot = f'{out_dir}/_bot.png'
r2 = subprocess.run([ff, '-y', '-i', v_face0, '-i', v_face4,
                '-filter_complex', '[0:v][1:v]hstack', bot], capture_output=True, text=True)
print('bot stderr:', r2.stderr[-200:])

# 上下 vstack → 1024x1024
final = f'{out_dir}/v4s1_hair_compare.png'
r3 = subprocess.run([ff, '-y', '-i', top, '-i', bot,
                '-filter_complex', '[0:v][1:v]vstack', final], capture_output=True, text=True)
print('final stderr:', r3.stderr[-200:])

print('size:', os.path.getsize(final) if os.path.exists(final) else 'NOT FOUND')

import shutil, os

mapping = [
    ('clipboard-2026-09-04T16-16-23-449Z-e317653a.jpg', 'characters/she_is_still_here/jiangche/bean_jiangche.png'),
    ('clipboard-2026-09-04T16-16-23-453Z-1ed842ba.jpg', 'shots/she_is_still_here/scenes/bean_ward_cg.png'),
    ('clipboard-2026-09-04T16-16-23-451Z-d93ac827.jpg', 'shots/she_is_still_here/scenes/bean_ward_cyber.png'),
    ('clipboard-2026-09-04T16-16-23-452Z-23adfc96.jpg', 'shots/she_is_still_here/scenes/bean_ward_liveaction.jpeg'),
    ('clipboard-2026-09-04T16-16-23-454Z-baae94fe.jpg', 'characters/she_is_still_here/linmian_comatose/bean_linmian_comatose.png'),
    ('clipboard-2026-09-04T16-16-23-456Z-cf99181c.jpg', 'characters/she_is_still_here/linmian_awake/bean_linmian_awake.png'),
]

base_in = r'C:\Users\Administrator\.workbuddy\clipboard-images'
base_out = r'D:\WorkBuddy\AI_Video'

for src, dst in mapping:
    full_in = os.path.join(base_in, src)
    full_out = os.path.join(base_out, dst)
    os.makedirs(os.path.dirname(full_out), exist_ok=True)
    shutil.copy2(full_in, full_out)
    sz = os.path.getsize(full_out) // 1024
    print(f'{src[-12:]} -> {dst}  ({sz} KB)')

print('ALL DONE')
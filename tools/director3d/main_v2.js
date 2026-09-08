// Director3D · Walkscene v1
// 目标：一个人形角色沿 z 走路，镜头侧后跟拍 + 周围物体（路灯/车/树/墙/长凳）+ 配角
// Three.js r160 ESM via importmap
import * as THREE from './three.module.js';

// ---------- Renderer ----------
const canvas = document.getElementById('c');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setPixelRatio(1);
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.setClearColor(0xb8c0c8); // 灰蓝天

// ---------- Scene ----------
const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0xb8c0c8, 12, 60);
scene.background = new THREE.Color(0xb8c0c8);

// ---------- Camera ----------
const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 200);
camera.position.set(2, 1.6, 6);
camera.lookAt(0, 1.0, 0);

// ---------- Lights ----------
const sun = new THREE.DirectionalLight(0xfff0d8, 1.6);
sun.position.set(8, 12, 6);
sun.castShadow = true;
sun.shadow.mapSize.set(1024, 1024);
sun.shadow.camera.left = -12; sun.shadow.camera.right = 12;
sun.shadow.camera.top = 12; sun.shadow.camera.bottom = -12;
sun.shadow.camera.near = 0.5; sun.shadow.camera.far = 40;
scene.add(sun);
scene.add(new THREE.AmbientLight(0x8090a0, 0.6));
scene.add(new THREE.HemisphereLight(0xc0d0e0, 0x6a5040, 0.4));

// ---------- Ground ----------
const ground = new THREE.Mesh(
  new THREE.PlaneGeometry(60, 60, 1, 1),
  new THREE.MeshStandardMaterial({ color: 0x6a6258, roughness: 0.95 })
);
ground.rotation.x = -Math.PI / 2;
ground.receiveShadow = true;
scene.add(ground);

// grid 线（导演台味）
const grid = new THREE.GridHelper(60, 30, 0x444444, 0x333333);
grid.position.y = 0.01;
grid.material.transparent = true; grid.material.opacity = 0.35;
scene.add(grid);

// ---------- Helpers ----------
const mat = (c, r=0.85) => new THREE.MeshStandardMaterial({ color: c, roughness: r, metalness: 0.0 });

// ---------- Character factory（人形 = 头 + 躯干 + 上下臂 + 上下腿，带关节 pivot） ----------
function makeHuman(opts) {
  const { skin=0xe8c4a0, shirt=0x6b7a8a, pants=0x2a3040, hairColor=0x222 } = opts || {};
  const root = new THREE.Group();
  // 身体轻微上下 bounce
  const body = new THREE.Group();
  root.add(body);

  // 头（含头发 + 脖子）
  const head = new THREE.Mesh(new THREE.SphereGeometry(0.18, 16, 12), mat(skin));
  head.position.y = 1.62; head.castShadow = true; body.add(head);
  const hair = new THREE.Mesh(new THREE.SphereGeometry(0.19, 16, 12, 0, Math.PI*2, 0, Math.PI*0.55), mat(hairColor, 0.7));
  hair.position.y = 1.66; body.add(hair);
  // 躯干
  const torso = new THREE.Mesh(new THREE.BoxGeometry(0.42, 0.55, 0.26), mat(shirt));
  torso.position.y = 1.10; torso.castShadow = true; body.add(torso);
  // 大腿 pivot 在 y=0.85
  function makeLeg(side) {
    const g = new THREE.Group();
    g.position.set(side*0.10, 0.85, 0);
    const upper = new THREE.Mesh(new THREE.CylinderGeometry(0.07, 0.06, 0.42, 8), mat(pants));
    upper.position.y = -0.21; upper.castShadow = true; g.add(upper);
    const lower = new THREE.Group();
    lower.position.y = -0.42;
    g.add(lower);
    const low = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.055, 0.42, 8), mat(pants));
    low.position.y = -0.21; low.castShadow = true; lower.add(low);
    body.add(g);
    return { hip: g, knee: lower };
  }
  // 手臂 pivot 在 y=1.32（肩）
  function makeArm(side) {
    const g = new THREE.Group();
    g.position.set(side*0.26, 1.32, 0);
    const upper = new THREE.Mesh(new THREE.CylinderGeometry(0.055, 0.05, 0.36, 8), mat(shirt));
    upper.position.y = -0.18; upper.castShadow = true; g.add(upper);
    const lower = new THREE.Group();
    lower.position.y = -0.36;
    g.add(lower);
    const low = new THREE.Mesh(new THREE.CylinderGeometry(0.045, 0.04, 0.34, 8), mat(skin));
    low.position.y = -0.17; low.castShadow = true; lower.add(low);
    body.add(g);
    return { shoulder: g, elbow: lower };
  }
  const legL = makeLeg(-1), legR = makeLeg(+1);
  const armL = makeArm(-1), armR = makeArm(+1);

  // v2: 大步伐 (H3 域迁移走路幅度测试)
  root.userData.walk = (phase, bounce) => {
    const s = Math.sin(phase), c = Math.cos(phase);
    legL.hip.rotation.x  =  s * 1.1;       // v2 大腿 0.7→1.1
    legR.hip.rotation.x  = -s * 1.1;
    legL.knee.rotation.x = Math.max(0, -c) * 1.3;  // v2 膝盖 0.9→1.3
    legR.knee.rotation.x = Math.max(0,  c) * 1.3;
    armL.shoulder.rotation.x = -s * 0.95;   // v2 肩膀 0.6→0.95
    armR.shoulder.rotation.x =  s * 0.95;
    body.position.y = bounce;                         // 全身上下
    torso.rotation.z = s * 0.08;                      // v2 躯干侧倾 0.04→0.08
  };
  return root;
}

// ---------- 主角色：走路人 ----------
const hero = makeHuman({ skin: 0xe8c4a0, shirt: 0xa07b5a /* tan trench */, pants: 0x3a3540, hairColor: 0x3a2a20 });
hero.position.set(0, 0, 0);
scene.add(hero);

// ---------- 配角：站路边 ----------
const npc = makeHuman({ skin: 0xd0a890, shirt: 0x2a3a4a, pants: 0x222 /* dark jacket */, hairColor: 0x1a1a1a });
npc.position.set(1.6, 0, 3.5);
npc.rotation.y = -0.6;
scene.add(npc);
// 配角头微低（看手机）
npc.children[0].rotation.x = 0.25; // body group

// ---------- 物体工厂 ----------
function lamp(x, z, color=0x7a7466) {
  const g = new THREE.Group();
  const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.10, 0.13, 3.2, 10), mat(color));
  pole.position.y = 1.6; pole.castShadow = true; g.add(pole);
  const head = new THREE.Mesh(new THREE.ConeGeometry(0.30, 0.4, 12), mat(0xf5e07a, 0.5));
  head.position.y = 3.0; head.castShadow = true; g.add(head);
  const bulb = new THREE.Mesh(new THREE.SphereGeometry(0.18, 12, 8), new THREE.MeshBasicMaterial({ color: 0xfff0a0 }));
  bulb.position.y = 2.95; g.add(bulb);
  g.position.set(x, 0, z);
  return g;
}
function tree(x, z, scale=1, color=0x5e7a48) {
  const g = new THREE.Group();
  const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.14*scale, 0.18*scale, 1.2*scale, 8), mat(0x5a4030));
  trunk.position.y = 0.6*scale; trunk.castShadow = true; g.add(trunk);
  const crown = new THREE.Mesh(new THREE.SphereGeometry(0.7*scale, 12, 10), mat(color, 0.85));
  crown.position.y = 1.4*scale; crown.castShadow = true; g.add(crown);
  g.position.set(x, 0, z);
  return g;
}
function car(x, z, rot=0, color=0xa35040) {
  const g = new THREE.Group();
  const body = new THREE.Mesh(new THREE.BoxGeometry(1.8, 0.7, 4.2), mat(color, 0.5));
  body.position.y = 0.5; body.castShadow = true; g.add(body);
  const cabin = new THREE.Mesh(new THREE.BoxGeometry(1.6, 0.55, 2.0), mat(0x303540, 0.4));
  cabin.position.set(0, 1.10, 0.1); cabin.castShadow = true; g.add(cabin);
  // 4 个轮子
  for (const [sx, sz] of [[-0.8,-1.3],[0.8,-1.3],[-0.8,1.3],[0.8,1.3]]) {
    const w = new THREE.Mesh(new THREE.CylinderGeometry(0.32, 0.32, 0.2, 12), mat(0x1a1a1a, 0.7));
    w.rotation.z = Math.PI/2; w.position.set(sx, 0.32, sz); w.castShadow = true; g.add(w);
  }
  g.position.set(x, 0, z); g.rotation.y = rot;
  return g;
}
function bench(x, z) {
  const g = new THREE.Group();
  const seat = new THREE.Mesh(new THREE.BoxGeometry(1.2, 0.08, 0.4), mat(0x7a5430));
  seat.position.y = 0.4; seat.castShadow = true; g.add(seat);
  for (const sx of [-0.5, 0.5]) {
    const leg = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.4, 0.36), mat(0x4a3020));
    leg.position.set(sx, 0.2, 0); leg.castShadow = true; g.add(leg);
  }
  g.position.set(x, 0, z);
  return g;
}
function trash(x, z) {
  return new THREE.Mesh(new THREE.CylinderGeometry(0.22, 0.20, 0.5, 10), mat(0x3a4a4a));
}

// ---------- 沿街布景（角色沿 +z 走，物体在 x ± 两侧） ----------
scene.add(car(-2.4, 0.5, 0.2));          // 红车在角色左前方路边
scene.add(lamp(2.0, -0.3));              // 灯柱在右后
scene.add(lamp(-2.0, 4.0));              // 灯柱在左中
scene.add(lamp(2.0, 8.0));               // 灯柱在右远
scene.add(tree(-2.4, 6.0, 1.0));
scene.add(tree(2.5, 2.0, 0.9));
scene.add(tree(2.5, 6.5, 1.1, 0x6a8a4a));
scene.add(bench(-2.2, 5.0));
const t1 = trash(1.5, 1.2); t1.position.y = 0.25; scene.add(t1);
const t2 = trash(1.5, 7.5); t2.position.y = 0.25; scene.add(t2);

// 远处灰墙
const wall = new THREE.Mesh(new THREE.BoxGeometry(20, 2.5, 0.3), mat(0xa8a4a0));
wall.position.set(0, 1.25, 12);
wall.castShadow = true; wall.receiveShadow = true;
scene.add(wall);

// ---------- 主循环 ----------
const start = performance.now();
const DURATION = 10.0; // 10s 动画
const WALK_DIST = 8.0; // 沿 z 走 8m
const STEP_HZ = 1.6;   // v2 步频 1.8→1.6 (慢一点让单步更清晰)

const camOffset = new THREE.Vector3(1.6, 1.7, -2.0); // 相机相对角色（侧后 1.6 偏 x，+1.7 高度，-2.0 落后）
const camLookLead = new THREE.Vector3(0, 1.2, 1.5);  // 看角色前方 1.5m
const camPos = new THREE.Vector3();
const camLook = new THREE.Vector3();
const camPosSmoothed = new THREE.Vector3(2, 1.7, 6);
const camLookSmoothed = new THREE.Vector3(0, 1.2, 1.5);

function frame() {
  const t = (performance.now() - start) / 1000; // s
  // 角色位置：ease-in-out + 线性（避免突进）
  const tn = Math.min(t / DURATION, 1.0);
  const eased = tn * tn * (3 - 2 * tn); // smoothstep
  hero.position.z = eased * WALK_DIST;
  // 走路动画
  const phase = t * STEP_HZ * Math.PI * 2; // 角频率
  const bounce = Math.abs(Math.sin(phase * 0.5)) * 0.12; // v2 上下 bounce 0.05→0.12 (更明显)
  hero.userData.walk(phase, bounce);

  // 配角头低 + 看手机（轻微晃动）
  npc.children[0].rotation.x = 0.25 + Math.sin(t*1.5)*0.04;

  // 相机跟随（位置 + lookAt 平滑）
  camPos.set(hero.position.x + camOffset.x, camOffset.y, hero.position.z + camOffset.z);
  camLook.set(hero.position.x + camLookLead.x, camLookLead.y, hero.position.z + camLookLead.z);
  // 简单 lerp 平滑
  const k = 0.12;
  camPosSmoothed.lerp(camPos, k);
  camLookSmoothed.lerp(camLook, k);
  camera.position.copy(camPosSmoothed);
  camera.lookAt(camLookSmoothed);

  renderer.render(scene, camera);

  if (t < DURATION + 0.1) {
    requestAnimationFrame(frame);
  } else {
    // 动画结束：在 body 加 ready 信号供 playwright 探测
    document.body.dataset.ready = "1";
    document.title = "Director3D - DONE";
  }
}
requestAnimationFrame(frame);

// 兼容窗口尺寸
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

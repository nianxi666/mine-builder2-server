#!/usr/bin/env python3
"""
view_schematic.py - 查看 Minecraft 建筑图纸/存档的简易查看器
支持加载材质包、存档、方块ID字典，并保留模型部件信息
"""

import os
import json
import base64
import zipfile
import tempfile
import logging
import argparse
from flask import Flask, render_template_string, jsonify, send_file

# --- 配置 ---
PORT = 5001
INPUT_DIR = "input"
SCHEMATIC_FILE = None  # 将通过命令行参数或自动扫描设置

# --- 日志设置 ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [VIEW_SCHEMATIC] - %(levelname)s - %(message)s')

# --- Flask 应用初始化 ---
app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# --- 辅助函数 ---

def find_first_file(directory, extensions):
    """在指定目录中查找第一个具有给定扩展名的文件"""
    if not os.path.isdir(directory):
        logging.warning(f"目录 '{directory}' 不存在")
        return None
    logging.info(f"正在扫描目录 '{directory}'，查找文件类型: {extensions}")
    for filename in sorted(os.listdir(directory)):
        if any(filename.lower().endswith(ext) for ext in extensions):
            path = os.path.join(directory, filename)
            logging.info(f"找到文件: {path}")
            return path
    logging.warning(f"在 '{directory}' 中未找到类型为 {extensions} 的文件")
    return None

def read_file_as_base64(filepath):
    """读取文件并将其内容作为 Base64 编码的字符串返回"""
    if not filepath or not os.path.exists(filepath):
        return None
    try:
        with open(filepath, "rb") as f:
            return base64.b64encode(f.read()).decode('utf-8')
    except Exception as e:
        logging.error(f"无法读取文件 {filepath}: {e}")
        return None

def load_schematic_file(filepath):
    """加载存档/图纸文件"""
    try:
        if filepath.endswith('.zip'):
            # 加载ZIP格式的存档文件
            with zipfile.ZipFile(filepath, 'r') as zipf:
                with zipf.open('save_data.json') as f:
                    data = json.load(f)
                    logging.info(f"成功加载存档文件: {filepath}")
                    return data
        elif filepath.endswith('.json'):
            # 直接加载JSON格式
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logging.info(f"成功加载JSON文件: {filepath}")
                return data
        else:
            logging.error(f"不支持的文件格式: {filepath}")
            return None
    except Exception as e:
        logging.error(f"加载存档文件失败: {e}")
        return None

# --- HTML 前端 ---
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>建筑图纸查看器</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.7.1/jszip.min.js"></script>
    <style>
        body { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #f3f4f6; 
            overflow: hidden; 
            margin: 0; 
            padding: 0; 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        #main-container { position: relative; width: 100vw; height: 100vh; }
        #mount { width: 100%; height: 100%; display: block; }
        .panel {
            background: rgba(17, 24, 39, 0.9);
            backdrop-filter: blur(10px);
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .btn {
            transition: all 0.3s ease;
            border-radius: 8px;
            font-weight: 600;
        }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4); }
        .btn:active { transform: translateY(0); }
        #loading { 
            position: fixed; 
            top: 50%; 
            left: 50%; 
            transform: translate(-50%, -50%); 
            z-index: 1000;
            background: rgba(17, 24, 39, 0.95);
            padding: 2rem 3rem;
            border-radius: 12px;
            text-align: center;
        }
        .spinner {
            border: 4px solid rgba(255, 255, 255, 0.1);
            border-left-color: #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 1rem;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
    </style>
</head>
<body>
    <div id="loading">
        <div class="spinner"></div>
        <div class="text-lg font-semibold">正在加载建筑图纸...</div>
    </div>

    <div id="main-container">
        <div id="mount"></div>

        <!-- 左侧控制面板 -->
        <div class="absolute top-4 left-4 panel p-4 w-72 max-h-[90vh] overflow-y-auto z-10">
            <h2 class="text-xl font-bold mb-4 text-purple-400">🏗️ 建筑图纸查看器</h2>
            
            <div class="mb-4">
                <h3 class="text-sm font-semibold mb-2 text-gray-300">📁 已加载文件</h3>
                <div id="file-status" class="text-xs text-gray-400 space-y-1">
                    <div id="schematic-status">图纸: <span class="text-yellow-400">加载中...</span></div>
                    <div id="texture-status">材质包: <span class="text-yellow-400">加载中...</span></div>
                </div>
            </div>

            <div class="mb-4 border-t border-gray-700 pt-4">
                <h3 class="text-sm font-semibold mb-2 text-gray-300">🎬 镜头控制</h3>
                <div class="grid grid-cols-3 gap-2">
                    <button onclick="setCameraView('front')" class="btn bg-blue-600 hover:bg-blue-700 text-white py-2 px-3 text-xs">前</button>
                    <button onclick="setCameraView('back')" class="btn bg-blue-600 hover:bg-blue-700 text-white py-2 px-3 text-xs">后</button>
                    <button onclick="setCameraView('top')" class="btn bg-blue-600 hover:bg-blue-700 text-white py-2 px-3 text-xs">顶</button>
                    <button onclick="setCameraView('left')" class="btn bg-blue-600 hover:bg-blue-700 text-white py-2 px-3 text-xs">左</button>
                    <button onclick="setCameraView('right')" class="btn bg-blue-600 hover:bg-blue-700 text-white py-2 px-3 text-xs">右</button>
                    <button onclick="setCameraView('bottom')" class="btn bg-blue-600 hover:bg-blue-700 text-white py-2 px-3 text-xs">底</button>
                </div>
                <button onclick="setCameraView('iso')" class="btn bg-purple-600 hover:bg-purple-700 text-white py-2 px-3 text-xs w-full mt-2">等距视角</button>
            </div>

            <div class="mb-4 border-t border-gray-700 pt-4">
                <h3 class="text-sm font-semibold mb-2 text-gray-300">📸 功能</h3>
                <button onclick="takeScreenshot()" class="btn bg-green-600 hover:bg-green-700 text-white py-2 px-3 text-xs w-full mb-2">截图</button>
                <button onclick="toggleWireframe()" class="btn bg-yellow-600 hover:bg-yellow-700 text-white py-2 px-3 text-xs w-full">线框模式</button>
            </div>

            <div class="border-t border-gray-700 pt-4">
                <h3 class="text-sm font-semibold mb-2 text-gray-300">📊 统计信息</h3>
                <div class="text-xs text-gray-400 space-y-1">
                    <div>方块总数: <span id="block-count" class="text-white font-semibold">0</span></div>
                    <div>部件数量: <span id="part-count" class="text-white font-semibold">0</span></div>
                    <div>材质数量: <span id="material-count" class="text-white font-semibold">0</span></div>
                </div>
            </div>
        </div>

        <!-- 右侧部件列表 -->
        <div class="absolute top-4 right-4 panel p-4 w-64 max-h-[90vh] overflow-y-auto z-10">
            <h3 class="text-lg font-bold mb-3 text-purple-400">🧩 模型部件</h3>
            <div id="parts-list" class="text-xs text-gray-400">
                暂无部件信息
            </div>
        </div>
    </div>

    <script>
        // ====================================================================
        // 全局变量
        // ====================================================================
        const VOXEL_RESOLUTION = 32;
        const GRID_SIZE = 10;
        const VOXEL_SIZE = GRID_SIZE / VOXEL_RESOLUTION;

        // Minecraft 方块ID字典 (与原始材质名称映射)
        const BLOCK_ID_DICT = {{ block_id_dict | tojson }};
        
        // 纹理键到默认颜色的映射 (当材质包中没有对应纹理时使用)
        const TEXTURE_FALLBACK_COLORS = {
            'stone': 0x888888,
            'grass': 0x74b44a,
            'grass_top': 0x74b44a,
            'grass_side': 0x90ac50,
            'dirt': 0x8d6b4a,
            'cobblestone': 0x7a7a7a,
            'planks_oak': 0xaf8f58,
            'planks_spruce': 0x806038,
            'planks_birch': 0xdace9b,
            'planks_jungle': 0xac7d5a,
            'log_oak': 0x685133,
            'log_spruce': 0x513f27,
            'brick': 0xa05050,
            'sand': 0xe3dbac,
            'gravel': 0x84807b,
            'gold_block': 0xffff00,
            'iron_block': 0xd8d8d8,
            'diamond_block': 0x7dedde,
            'wool_colored_white': 0xffffff,
            'wool_colored_red': 0xff0000,
            'glass': 0xaaddff,
            'unknown': 0xff00ff
        };

        let scene, camera, renderer, controls;
        let voxelContainerGroup;
        let loadedTextures = new Map();
        let schematicData = null;
        let wireframeMode = false;

        // ====================================================================
        // 初始化
        // ====================================================================
        async function init() {
            console.log('初始化 3D 场景...');
            
            // 设置 Three.js 场景
            const mount = document.getElementById('mount');
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x1a1a2e);
            scene.fog = new THREE.Fog(0x1a1a2e, 20, 50);

            camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.set(GRID_SIZE * 1.2, GRID_SIZE * 1.2, GRID_SIZE * 1.2);

            renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.setPixelRatio(window.devicePixelRatio);
            renderer.shadowMap.enabled = true;
            renderer.shadowMap.type = THREE.PCFSoftShadowMap;
            mount.appendChild(renderer.domElement);

            controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.05;
            controls.target.set(0, GRID_SIZE / 2, 0);
            controls.update();

            // 光照
            scene.add(new THREE.AmbientLight(0xffffff, 0.6));
            
            const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
            directionalLight.position.set(GRID_SIZE, GRID_SIZE * 2, GRID_SIZE);
            directionalLight.castShadow = true;
            directionalLight.shadow.mapSize.width = 2048;
            directionalLight.shadow.mapSize.height = 2048;
            scene.add(directionalLight);

            // 地面网格
            const gridHelper = new THREE.GridHelper(GRID_SIZE, VOXEL_RESOLUTION, 0x4a5568, 0x2d3748);
            scene.add(gridHelper);

            // 地面接受阴影
            const groundPlane = new THREE.Mesh(
                new THREE.PlaneGeometry(GRID_SIZE * 2, GRID_SIZE * 2),
                new THREE.ShadowMaterial({ opacity: 0.3 })
            );
            groundPlane.rotation.x = -Math.PI / 2;
            groundPlane.position.y = -0.01;
            groundPlane.receiveShadow = true;
            scene.add(groundPlane);

            // 体素容器
            voxelContainerGroup = new THREE.Group();
            scene.add(voxelContainerGroup);

            // 窗口大小调整
            window.addEventListener('resize', onWindowResize);

            // 开始动画循环
            animate();

            // 加载数据
            await loadData();
        }

        function animate() {
            requestAnimationFrame(animate);
            controls.update();
            renderer.render(scene, camera);
        }

        function onWindowResize() {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }

        // ====================================================================
        // 数据加载
        // ====================================================================
        async function loadData() {
            try {
                console.log('从服务器获取数据...');
                const response = await fetch('/api/data');
                if (!response.ok) throw new Error(`服务器响应错误: ${response.status}`);
                
                const data = await response.json();
                console.log('接收到数据:', data);

                // 加载材质包
                if (data.texturePackData) {
                    document.getElementById('texture-status').innerHTML = '材质包: <span class="text-green-400">✓ 已加载</span>';
                    await loadTexturePack(data.texturePackData);
                } else {
                    document.getElementById('texture-status').innerHTML = '材质包: <span class="text-red-400">✗ 未找到</span>';
                    console.warn('未找到材质包');
                }

                // 加载图纸数据
                if (data.schematicData) {
                    document.getElementById('schematic-status').innerHTML = '图纸: <span class="text-green-400">✓ 已加载</span>';
                    schematicData = data.schematicData;
                    displaySchematic();
                } else {
                    document.getElementById('schematic-status').innerHTML = '图纸: <span class="text-red-400">✗ 未找到</span>';
                    console.error('未找到图纸数据');
                }

                // 隐藏加载提示
                document.getElementById('loading').style.display = 'none';

            } catch (error) {
                console.error('加载数据失败:', error);
                document.getElementById('loading').innerHTML = 
                    '<div class="text-red-400 text-lg font-semibold">❌ 加载失败: ' + error.message + '</div>';
            }
        }

        async function loadTexturePack(base64Data) {
            try {
                console.log('加载材质包...');
                const binaryString = atob(base64Data);
                const bytes = new Uint8Array(binaryString.length);
                for (let i = 0; i < binaryString.length; i++) {
                    bytes[i] = binaryString.charCodeAt(i);
                }

                const zip = await JSZip.loadAsync(bytes);
                const textureLoader = new THREE.TextureLoader();
                const texturePromises = [];
                const texturePathPrefix = 'assets/minecraft/textures/blocks/';

                zip.forEach((relativePath, zipEntry) => {
                    if (relativePath.startsWith(texturePathPrefix) && 
                        relativePath.toLowerCase().endsWith('.png') && 
                        !zipEntry.dir) {
                        
                        const textureName = relativePath
                            .substring(texturePathPrefix.length)
                            .replace(/\\.png$/i, '');
                        
                        if (textureName) {
                            texturePromises.push(
                                zipEntry.async('blob').then(blob => {
                                    const url = URL.createObjectURL(blob);
                                    return new Promise((resolve) => {
                                        textureLoader.load(url, (texture) => {
                                            texture.magFilter = THREE.NearestFilter;
                                            texture.minFilter = THREE.NearestFilter;
                                            loadedTextures.set(textureName, texture);
                                            URL.revokeObjectURL(url);
                                            resolve();
                                        }, undefined, (err) => {
                                            console.error('纹理加载失败:', textureName, err);
                                            resolve();
                                        });
                                    });
                                })
                            );
                        }
                    }
                });

                await Promise.all(texturePromises);
                console.log(`材质包加载完成，共 ${loadedTextures.size} 个纹理`);
                document.getElementById('material-count').textContent = loadedTextures.size;

            } catch (error) {
                console.error('加载材质包失败:', error);
            }
        }

        // ====================================================================
        // 显示图纸
        // ====================================================================
        function displaySchematic() {
            if (!schematicData || !schematicData.voxel_data) {
                console.error('图纸数据无效');
                return;
            }

            console.log('开始显示图纸...');

            // 清除现有体素
            while (voxelContainerGroup.children.length > 0) {
                const child = voxelContainerGroup.children[0];
                voxelContainerGroup.remove(child);
                if (child.geometry) child.geometry.dispose();
                if (child.material) {
                    if (Array.isArray(child.material)) {
                        child.material.forEach(m => m.dispose());
                    } else {
                        child.material.dispose();
                    }
                }
            }

            const voxelData = schematicData.voxel_data;
            
            // 按材质分组体素
            const materialGroups = new Map();
            let totalBlocks = 0;
            const partIds = new Set();

            for (const coordString in voxelData) {
                const voxelProps = voxelData[coordString];
                const blockId = voxelProps.blockId || 1;
                const metaData = voxelProps.metaData || 0;
                const partId = voxelProps.partId;

                if (partId) partIds.add(partId);

                // 获取纹理键
                const textureKey = getTextureKeyForBlock(blockId, metaData);
                
                if (!materialGroups.has(textureKey)) {
                    materialGroups.set(textureKey, []);
                }

                const [x, y, z] = coordString.split(',').map(Number);
                materialGroups.get(textureKey).push({ x, y, z, coord: coordString, partId });
                totalBlocks++;
            }

            console.log(`总方块数: ${totalBlocks}, 材质类型: ${materialGroups.size}`);

            // 创建实例化网格
            const baseGeometry = new THREE.BoxGeometry(
                VOXEL_SIZE * 0.98, 
                VOXEL_SIZE * 0.98, 
                VOXEL_SIZE * 0.98
            );

            materialGroups.forEach((voxels, textureKey) => {
                if (voxels.length === 0) return;

                // 创建材质
                let material;
                const texture = loadedTextures.get(textureKey);
                
                if (texture) {
                    // 使用用户材质包中的纹理
                    material = new THREE.MeshStandardMaterial({ 
                        map: texture, 
                        metalness: 0.1, 
                        roughness: 0.8 
                    });
                } else {
                    // 使用后备颜色
                    const color = TEXTURE_FALLBACK_COLORS[textureKey] || TEXTURE_FALLBACK_COLORS['unknown'];
                    material = new THREE.MeshLambertMaterial({ color });
                }

                // 创建实例化网格
                const instancedMesh = new THREE.InstancedMesh(baseGeometry, material, voxels.length);
                instancedMesh.castShadow = true;
                instancedMesh.receiveShadow = true;

                const dummy = new THREE.Object3D();
                const halfGrid = GRID_SIZE / 2;

                voxels.forEach((voxel, i) => {
                    const posX = -halfGrid + (voxel.x + 0.5) * VOXEL_SIZE;
                    const posY = (voxel.y + 0.5) * VOXEL_SIZE;
                    const posZ = -halfGrid + (voxel.z + 0.5) * VOXEL_SIZE;

                    dummy.position.set(posX, posY, posZ);
                    dummy.updateMatrix();
                    instancedMesh.setMatrixAt(i, dummy.matrix);
                });

                instancedMesh.instanceMatrix.needsUpdate = true;
                instancedMesh.userData.textureKey = textureKey;
                voxelContainerGroup.add(instancedMesh);
            });

            // 更新统计信息
            document.getElementById('block-count').textContent = totalBlocks;
            document.getElementById('part-count').textContent = partIds.size;

            // 显示部件列表
            displayPartsList(partIds);

            console.log('图纸显示完成');
        }

        function displayPartsList(partIds) {
            const partsList = document.getElementById('parts-list');
            
            if (partIds.size === 0) {
                partsList.innerHTML = '<div class="text-gray-500">暂无部件信息</div>';
                return;
            }

            let html = '<div class="space-y-2">';
            let index = 1;
            partIds.forEach(partId => {
                html += `
                    <div class="bg-gray-800 p-2 rounded border border-gray-700">
                        <div class="font-semibold text-purple-300">部件 ${index}</div>
                        <div class="text-xs text-gray-500 mt-1">ID: ${partId.substring(0, 8)}...</div>
                    </div>
                `;
                index++;
            });
            html += '</div>';
            
            partsList.innerHTML = html;
        }

        function getTextureKeyForBlock(blockId, metaData) {
            const blockEntry = BLOCK_ID_DICT[blockId.toString()];
            if (!blockEntry) return 'unknown';

            const metaEntry = blockEntry[metaData.toString()];
            if (!metaEntry) return 'unknown';

            if (typeof metaEntry === 'string') {
                return metaEntry.split(':')[0];
            }

            if (typeof metaEntry === 'object' && metaEntry !== null) {
                // 处理多面纹理 (优先使用通用纹理 '*')
                const key = metaEntry['*'] || metaEntry.top || metaEntry.side || metaEntry.north || 'unknown';
                return key.split(':')[0];
            }

            return 'unknown';
        }

        // ====================================================================
        // 交互功能
        // ====================================================================
        function setCameraView(view) {
            const distance = GRID_SIZE * 1.5;
            const target = new THREE.Vector3(0, GRID_SIZE / 2, 0);

            let newPos;
            switch (view) {
                case 'front':
                    newPos = new THREE.Vector3(0, GRID_SIZE / 2, distance);
                    break;
                case 'back':
                    newPos = new THREE.Vector3(0, GRID_SIZE / 2, -distance);
                    break;
                case 'left':
                    newPos = new THREE.Vector3(-distance, GRID_SIZE / 2, 0);
                    break;
                case 'right':
                    newPos = new THREE.Vector3(distance, GRID_SIZE / 2, 0);
                    break;
                case 'top':
                    newPos = new THREE.Vector3(0, distance, 0);
                    break;
                case 'bottom':
                    newPos = new THREE.Vector3(0, -distance, 0);
                    break;
                case 'iso':
                default:
                    newPos = new THREE.Vector3(distance, distance, distance);
                    break;
            }

            animateCameraTo(newPos, target);
        }

        function animateCameraTo(newPosition, newTarget) {
            const startPosition = camera.position.clone();
            const startTarget = controls.target.clone();
            const duration = 1000;
            const startTime = Date.now();

            function animate() {
                const elapsed = Date.now() - startTime;
                const progress = Math.min(elapsed / duration, 1);
                const eased = easeInOutCubic(progress);

                camera.position.lerpVectors(startPosition, newPosition, eased);
                controls.target.lerpVectors(startTarget, newTarget, eased);
                controls.update();

                if (progress < 1) {
                    requestAnimationFrame(animate);
                }
            }

            animate();
        }

        function easeInOutCubic(t) {
            return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
        }

        function takeScreenshot() {
            renderer.render(scene, camera);
            renderer.domElement.toBlob((blob) => {
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'schematic_screenshot_' + Date.now() + '.png';
                a.click();
                URL.revokeObjectURL(url);
            });
        }

        function toggleWireframe() {
            wireframeMode = !wireframeMode;
            voxelContainerGroup.children.forEach(child => {
                if (child.material) {
                    if (Array.isArray(child.material)) {
                        child.material.forEach(m => m.wireframe = wireframeMode);
                    } else {
                        child.material.wireframe = wireframeMode;
                    }
                }
            });
        }

        // ====================================================================
        // 启动
        // ====================================================================
        document.addEventListener('DOMContentLoaded', init);
    </script>
</body>
</html>
"""

# --- Flask 路由 ---

@app.route('/')
def index():
    """提供主HTML页面"""
    # 传递方块ID字典到前端
    return render_template_string(HTML_CONTENT, block_id_dict=get_block_id_dictionary())

@app.route('/api/data')
def get_data():
    """API端点，返回图纸数据和材质包"""
    logging.info("收到数据请求...")
    
    result = {
        'schematicData': None,
        'texturePackData': None
    }
    
    # 1. 加载图纸/存档文件
    if SCHEMATIC_FILE and os.path.exists(SCHEMATIC_FILE):
        schematic_data = load_schematic_file(SCHEMATIC_FILE)
        if schematic_data:
            result['schematicData'] = schematic_data
            logging.info(f"图纸文件已加载: {SCHEMATIC_FILE}")
    else:
        # 尝试从input目录自动查找
        schematic_path = find_first_file(INPUT_DIR, ['.zip', '.json'])
        if schematic_path:
            schematic_data = load_schematic_file(schematic_path)
            if schematic_data:
                result['schematicData'] = schematic_data
                logging.info(f"自动加载图纸文件: {schematic_path}")
    
    # 2. 加载材质包
    texture_pack_path = find_first_file('.', ['.zip'])
    if texture_pack_path:
        texture_data = read_file_as_base64(texture_pack_path)
        if texture_data:
            result['texturePackData'] = texture_data
            logging.info(f"材质包已加载: {texture_pack_path}")
    
    return jsonify(result)

def get_block_id_dictionary():
    """返回Minecraft方块ID字典"""
    return {
        "1": {"0": "stone", "1": "granite", "2": "polished_granite", "3": "stone_diorite", "4": "polished_diorite", "5": "andersite", "6": "polished_andersite"},
        "2": {"0": {"top": "grass_top", "bottom": "dirt", "*": "grass_side"}},
        "3": {"0": "dirt", "1": "coarse_dirt", "2": "podzol"},
        "4": {"0": "cobblestone"},
        "5": {"0": "planks_oak", "1": "planks_spruce", "2": "planks_birch", "3": "planks_jungle", "4": "planks_acacia", "5": "planks_big_oak"},
        "7": {"0": "cobblestone"},
        "12": {"0": "sand", "1": "red_sand"},
        "13": {"0": "gravel"},
        "14": {"0": "gold_ore"},
        "15": {"0": "iron_ore"},
        "16": {"0": "coal_ore"},
        "17": {
            "0": {"top": "log_oak_top", "bottom": "log_oak_top", "*": "log_oak"},
            "1": {"top": "log_spruce_top", "bottom": "log_spruce_top", "*": "log_spruce"},
            "2": {"top": "log_birch_top", "bottom": "log_birch_top", "*": "log_birch"},
            "3": {"top": "log_jungle_top", "bottom": "log_jungle_top", "*": "log_jungle"}
        },
        "24": {
            "0": {"top": "sandstone_top", "bottom": "sandstone_bottom", "*": "sandstone_normal"},
            "1": {"top": "sandstone_top", "bottom": "sandstone_bottom", "*": "sandstone_carved"},
            "2": {"top": "sandstone_top", "bottom": "sandstone_bottom", "*": "sandstone_smooth"}
        },
        "35": {
            "0": "wool_colored_white", "1": "wool_colored_orange", "2": "wool_colored_magenta",
            "3": "wool_colored_light_blue", "4": "wool_colored_yellow", "5": "wool_colored_lime",
            "6": "wool_colored_pink", "7": "wool_colored_gray", "8": "wool_colored_silver",
            "9": "wool_colored_cyan", "10": "wool_colored_purple", "11": "wool_colored_blue",
            "12": "wool_colored_brown", "13": "wool_colored_green", "14": "wool_colored_red",
            "15": "wool_colored_black"
        },
        "41": {"0": "gold_block"},
        "42": {"0": "iron_block"},
        "43": {
            "0": {"top": "stone_slab_top", "bottom": "stone_slab_top", "*": "stone_slab_side"},
            "1": {"top": "sandstone_top", "bottom": "sandstone_bottom", "*": "sandstone_normal"},
            "2": "planks_oak",
            "3": "cobblestone",
            "4": "brick",
            "5": "stonebrick",
            "6": "nether_brick",
            "7": "quartz_block_side"
        },
        "45": {"0": "brick"},
        "46": {"*": {"top": "tnt_top", "bottom": "tnt_bottom", "*": "tnt_side"}},
        "48": {"0": "cobblestone_mossy"},
        "49": {"0": "obsidian"},
        "56": {"0": "diamond_ore"},
        "57": {"0": "diamond_block"},
        "73": {"0": "redstone_ore"},
        "79": {"0": "ice"},
        "80": {"0": "snow"},
        "82": {"0": "clay"},
        "86": {
            "0": {"top": "pumpkin_top", "bottom": "pumpkin_top", "south": "pumpkin_face_off", "*": "pumpkin_side"}
        },
        "87": {"0": "netherrack"},
        "88": {"0": "soul_sand"},
        "89": {"0": "glowstone"},
        "95": {
            "0": "glass_white", "1": "glass_orange", "2": "glass_magenta",
            "3": "glass_light_blue", "4": "glass_yellow", "5": "glass_lime"
        },
        "98": {"0": "stonebrick", "1": "stonebrick_mossy", "2": "stonebrick_cracked", "3": "stonebrick_carved"},
        "103": {"0": {"top": "melon_top", "bottom": "melon_bottom", "*": "melon_side"}},
        "112": {"0": "nether_brick"},
        "129": {"0": "emerald_ore"},
        "133": {"0": "emerald_block"},
        "152": {"0": "redstone_block"},
        "155": {
            "0": {"top": "quartz_block_top", "bottom": "quartz_block_bottom", "*": "quartz_block_side"},
            "1": {"top": "quartz_block_chiseled_top", "bottom": "quartz_block_bottom", "*": "quartz_block_chiseled"}
        },
        "172": {"0": "hardened_clay"},
        "173": {"0": "coal_block"}
    }

# --- 主程序入口 ---

def main():
    """主函数，用于设置并运行Web服务器"""
    global SCHEMATIC_FILE
    
    # 参数解析
    parser = argparse.ArgumentParser(description="Minecraft 建筑图纸查看器")
    parser.add_argument('--schematic', type=str, help='要加载的图纸/存档文件路径 (.zip 或 .json)')
    parser.add_argument('--port', type=int, default=PORT, help=f'服务器端口 (默认: {PORT})')
    args = parser.parse_args()
    
    if args.schematic:
        if os.path.exists(args.schematic):
            SCHEMATIC_FILE = args.schematic
            logging.info(f"将加载指定的图纸文件: {SCHEMATIC_FILE}")
        else:
            logging.warning(f"指定的图纸文件不存在: {args.schematic}")
    
    # 确保input目录存在
    if not os.path.exists(INPUT_DIR):
        logging.info(f"正在创建 '{INPUT_DIR}' 目录")
        os.makedirs(INPUT_DIR)
    
    # 打印使用说明
    print("\n" + "="*70)
    print("🏗️  Minecraft 建筑图纸查看器")
    print(f"服务器正在 http://127.0.0.1:{args.port} 上运行")
    print("\n" + "-"*70)
    print("使用说明:")
    print(f"1. 将图纸/存档文件 (.zip 或 .json) 放入 '{INPUT_DIR}/' 文件夹")
    print(f"   或使用 --schematic <文件路径> 参数直接指定")
    print("2. 将 Minecraft 材质包 (.zip) 放在当前目录")
    print("3. 在浏览器中打开上述地址")
    print("\n特性:")
    print("✓ 从用户材质包加载真实纹理 (不使用代码生成的草方块等)")
    print("✓ 保留存档中的所有模型部件信息")
    print("✓ 支持方块ID字典映射")
    print("="*70 + "\n")
    
    # 启动 Flask 服务器
    app.run(host='0.0.0.0', port=args.port, debug=False)

if __name__ == '__main__':
    main()

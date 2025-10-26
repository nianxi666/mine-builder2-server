<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI 建筑生成器 V6 (元素魔法)</title>
    
    <!-- 1. 加载 Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    
    <!-- 2. 加载 Three.js 核心库 -->
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/build/three.min.js"></script>
    
    <!-- 3. 加载 OrbitControls -->
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>

    <style>
        body, html { margin: 0; padding: 0; overflow: hidden; font-family: 'Inter', sans-serif; background-color: #87CEEB; }
        canvas { display: block; }
        #loading-overlay { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background-color: #87CEEB; display: flex; justify-content: center; align-items: center; font-size: 1.5rem; color: white; z-index: 100; }
        #ai-output .cursor { display: inline-block; width: 10px; height: 1.2em; background-color: #4ade80; animation: blink 0.7s infinite; margin-left: 2px; vertical-align: middle; }
        @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }
        select {
            background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e");
            background-position: right 0.5rem center; background-repeat: no-repeat; background-size: 1.5em 1.5em;
            -webkit-appearance: none; -moz-appearance: none; appearance: none;
        }
        #ui-container { position: absolute; top: 1rem; left: 1rem; z-index: 10; pointer-events: none; width: 95%; max-width: 500px; }
        #ui-container > div { pointer-events: auto; }
        .ui-panel { background-color: rgba(31, 41, 55, 0.85) !important; backdrop-filter: blur(4px); -webkit-backdrop-filter: blur(4px); }
        .ui-log-panel { background-color: rgba(0, 0, 0, 0.7) !important; }
        #panel-content { transition: all 0.3s ease-in-out; max-height: 1000px; overflow: hidden; }
        #panel-content.collapsed { max-height: 0; padding-top: 0; padding-bottom: 0; margin-top: 0; opacity: 0; }
        #toggle-icon { transition: transform 0.3s ease-in-out; }
        #toggle-icon.collapsed { transform: rotate(-90deg); }
        /* 滑块样式 */
        input[type=range] { -webkit-appearance: none; appearance: none; width: 100%; height: 8px; background: #4b5563; border-radius: 5px; outline: none; opacity: 0.7; transition: opacity .2s; }
        input[type=range]:hover { opacity: 1; }
        input[type=range]::-webkit-slider-thumb { -webkit-appearance: none; appearance: none; width: 20px; height: 20px; background: #10b981; border-radius: 50%; cursor: pointer; }
        input[type=range]::-moz-range-thumb { width: 20px; height: 20px; background: #10b981; border-radius: 50%; cursor: pointer; }
    </style>
</head>
<body>
    <!-- UI 容器 (V6: 元素魔法 + 密度滑块) -->
    <div id="ui-container">
        <div class="mx-auto"> 
            <h1 class="text-3xl font-bold text-center mb-6 text-white text-shadow-lg">
                <span class="text-green-400">AI</span> 建筑生成器 V6
            </h1>

            <div class="bg-gray-800 rounded-lg shadow-xl flex flex-col ui-panel">
                <!-- 可点击的标题栏 -->
                <div id="panel-toggle-button" class="flex justify-between items-center p-4 cursor-pointer">
                    <h2 class="text-xl font-semibold text-white">控制面板</h2>
                    <svg id="toggle-icon" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7" />
                    </svg>
                </div>

                <!-- 可折叠的内容区域 -->
                <div id="panel-content" class="px-6 pb-6">
                    <!-- 1. 建筑动画 -->
                    <label for="effectSelector" class="block text-sm font-medium text-gray-300 mb-2">1. 建筑动画:</label>
                    <select id="effectSelector" class="w-full bg-gray-700 border border-gray-600 text-white py-2 px-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-400">
                        <option value="magic-gradient">渐变 (Gradient)</option>
                        <option value="vortex">旋涡 (Vortex)</option>
                        <option value="ripple">波纹 (Ripple)</option>
                        <option value="rain-down">天降 (Rain Down)</option>
                        <option value="ground-up">从地升起 (Ground Up)</option>
                        <option value="layer-scan">逐层扫描 (Layer Scan)</option>
                        <option value="assemble">组装 (Assemble)</option>
                        <option value="simple">闪现 (Simple)</option>
                    </select>

                    <!-- 2. 魔法主题 (V6) -->
                    <label for="magicSelector" class="block text-sm font-medium text-gray-300 mb-2 mt-4">2. 魔法主题:</label>
                    <select id="magicSelector" class="w-full bg-gray-700 border border-gray-600 text-white py-2 px-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-400">
                        <option value="rune-energy" selected>符文能量 (绿色)</option>
                        <option value="fire">烈焰 (红色/橙色)</option>
                        <option value="ice">寒冰 (蓝色/白色)</option>
                        <option value="shadow">暗影 (紫色)</option>
                        <option value="none">无 (None)</option>
                    </select>

                    <!-- 3. 粒子密度 (V6) -->
                    <div class="flex justify-between items-center mt-4">
                        <label for="particleSlider" class="block text-sm font-medium text-gray-300">3. 粒子密度:</label>
                        <span id="particleDensityLabel" class="text-sm text-gray-400">33%</span>
                    </div>
                    <input type="range" id="particleSlider" min="0" max="100" value="33" class="w-full mt-2">

                    <button id="startButton" class="w-full bg-green-500 hover:bg-green-600 text-white font-bold py-3 px-4 rounded-lg transition-all duration-300 shadow-lg mt-6 focus:outline-none focus:ring-2 focus:ring-green-400 focus:ring-opacity-75">
                        开始生成
                    </button>
                    
                    <h3 class="text-lg font-semibold mt-6 mb-3 text-white">AI 生成日志:</h3>
                    <pre id="ai-output-container" class="flex-grow bg-black text-green-400 text-sm p-4 rounded-md overflow-y-auto h-40 font-mono whitespace-pre-wrap ui-log-panel">
                        <span id="ai-output"></span><span class="cursor"></span>
                    </pre>
                </div>
            </div>
        </div>
    </div>

    <!-- 加载提示 -->
    <div id="loading-overlay">正在加载 3D 场景...</div>

    <!-- 主脚本 -->
    <script type="module">
        // 等待库加载
        document.addEventListener('DOMContentLoaded', init);

        // --- 全局变量 ---
        let startButton, aiOutput, aiOutputContainer, effectSelector, magicSelector, particleSlider, particleDensityLabel;
        let panelToggle, panelContent, toggleIcon;
        let blockGroup, particleSystem;
        const particles = [];
        const blockMaterials = {}; // 只存储颜色
        let isBuilding = false;
        let currentEffect = 'magic-gradient'; // 默认运动
        let currentMagicTheme = 'rune-energy'; // 默认魔法 V6
        let particleDensity = 33; // V6 粒子密度
        const MAX_PARTICLES_PER_BLOCK = 30; // V6 粒子上限
        
        // AI 日志
        const aiLogBase = [ "初始化 AI 模型...", "分析提示: '建造一个炫酷的 Minecraft 房屋'", "正在解析结构...", "生成方块坐标...", "图纸 (Schematic) 定义:", "  类型: 小型房屋", "  地基: 6x6 (木板)", "  墙体: 4x4 (圆石)", "  屋顶: 6x6 (木台阶)", "总方块数: 88", ];
        
        // 房屋图纸
        const schematicData = [];
        const MAT_WOOD = 'wood'; const MAT_COBBLE = 'cobble'; const MAT_ROOF = 'roof';
        for (let x = -3; x <= 2; x++) for (let z = -3; z <= 2; z++) schematicData.push({ x, y: 0.5, z, type: MAT_WOOD }); 
        for (let y = 1; y <= 2; y++) {
            for (let x = -3; x <= 2; x++) { schematicData.push({ x, y: y+0.5, z: -3, type: MAT_COBBLE }); schematicData.push({ x, y: y+0.5, z: 2, type: MAT_COBBLE }); }
            for (let z = -2; z <= 1; z++) { schematicData.push({ x: -3, y: y+0.5, z, type: MAT_COBBLE }); schematicData.push({ x: 2, y: y+0.5, z, type: MAT_COBBLE }); }
        }
        for (let x = -3; x <= 2; x++) for (let z = -3; z <= 2; z++) schematicData.push({ x, y: 3.5, z, type: MAT_ROOF });
        for (let x = -2; x <= 1; x++) for (let z = -2; z <= 1; z++) schematicData.push({ x, y: 4.5, z, type: MAT_ROOF });


        // --- 主初始化函数 ---
        function init() {
            // --- 获取 DOM 元素 ---
            startButton = document.getElementById('startButton');
            aiOutput = document.getElementById('ai-output');
            aiOutputContainer = document.getElementById('ai-output-container');
            effectSelector = document.getElementById('effectSelector');
            magicSelector = document.getElementById('magicSelector'); 
            particleSlider = document.getElementById('particleSlider'); // V6
            particleDensityLabel = document.getElementById('particleDensityLabel'); // V6
            panelToggle = document.getElementById('panel-toggle-button');
            panelContent = document.getElementById('panel-content');
            toggleIcon = document.getElementById('toggle-icon');
            effectSelector.value = currentEffect;
            magicSelector.value = currentMagicTheme;
            
            // --- 场景设置 ---
            const scene = new THREE.Scene();
            scene.background = new THREE.Color(0x87CEEB);
            scene.fog = new THREE.Fog(0x87CEEB, 20, 50);
            const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.set(0, 5, 10); 
            const renderer = new THREE.WebGLRenderer({ antialias: true }); 
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.setPixelRatio(window.devicePixelRatio); 
            document.body.appendChild(renderer.domElement);
            const controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true; controls.dampingFactor = 0.05;
            controls.maxPolarAngle = Math.PI / 2 - 0.05; 
            controls.minDistance = 2; controls.maxDistance = 60;
            controls.target.set(0, 0, 0); 
            const ambientLight = new THREE.AmbientLight(0xcccccc, 0.8);
            scene.add(ambientLight);
            const directionalLight = new THREE.DirectionalLight(0xffffff, 0.6);
            directionalLight.position.set(10, 20, 5);
            directionalLight.castShadow = true; 
            scene.add(directionalLight);

            // --- 纹理和地面 (平坦世界) ---
            function createPixelTexture(colorData, width = 16, height = 16) {
                const canvas = document.createElement('canvas'); canvas.width = width; canvas.height = height;
                const context = canvas.getContext('2d');
                for (let y = 0; y < height; y++) for (let x = 0; x < width; x++) { context.fillStyle = colorData(x, y); context.fillRect(x, y, 1, 1); }
                const texture = new THREE.CanvasTexture(canvas);
                texture.magFilter = THREE.NearestFilter; texture.minFilter = THREE.NearestFilter;
                return texture;
            }
            function randColor(base, variance) { const c = base + Math.floor((Math.random() - 0.5) * variance); return Math.max(0, Math.min(255, c)).toString(16).padStart(2, '0'); }
            const grassTopTexture = createPixelTexture(() => `#${randColor(80, 20)}${randColor(150, 30)}${randColor(60, 20)}`);
            const dirtTexture = createPixelTexture(() => `#${randColor(130, 20)}${randColor(90, 15)}${randColor(70, 10)}`);
            const grassSideTexture = createPixelTexture((x, y) => (y < 4) ? `#${randColor(80, 20)}${randColor(150, 30)}${randColor(60, 20)}` : `#${randColor(130, 20)}${randColor(90, 15)}${randColor(70, 10)}`);
            const groundSize = 50; 
            const blockGeometry = new THREE.BoxGeometry(1, 1, 1);
            const groundBlockMaterials = [ new THREE.MeshLambertMaterial({ map: grassSideTexture }), new THREE.MeshLambertMaterial({ map: grassSideTexture }), new THREE.MeshLambertMaterial({ map: grassTopTexture }),  new THREE.MeshLambertMaterial({ map: dirtTexture }), new THREE.MeshLambertMaterial({ map: grassSideTexture }), new THREE.MeshLambertMaterial({ map: grassSideTexture }) ];
            const groundMesh = new THREE.InstancedMesh(blockGeometry, groundBlockMaterials, groundSize * groundSize);
            const dummy = new THREE.Object3D(); 
            let index = 0;
            for (let x = -groundSize / 2; x < groundSize / 2; x++) for (let z = -groundSize / 2; z < groundSize / 2; z++) { dummy.position.set(x + 0.5, -0.5, z + 0.5); dummy.updateMatrix(); groundMesh.setMatrixAt(index++, dummy.matrix); }
            scene.add(groundMesh);

            // --- 云 (平坦世界) ---
            const cloudGroup = new THREE.Group();
            const cloudBlockGeo = new THREE.BoxGeometry(1, 1, 1);
            const cloudMaterial = new THREE.MeshBasicMaterial({ color: 0xffffff }); 
            for (let i = 0; i < 15; i++) {
                const cloud = new THREE.Group();
                for (let j = 0; j < (Math.floor(Math.random() * 6) + 4); j++) {
                    const block = new THREE.Mesh(cloudBlockGeo, cloudMaterial);
                    block.position.set((Math.random() - 0.5) * 5, (Math.random() - 0.5) * 1.5, (Math.random() - 0.5) * 3);
                    block.scale.set(Math.random() * 0.5 + 1, Math.random() * 0.5 + 1, Math.random() * 0.5 + 1);
                    cloud.add(block);
                }
                cloud.position.set((Math.random() - 0.5) * groundSize * 1.5, Math.random() * 5 + 20, (Math.random() - 0.5) * groundSize * 1.5);
                cloudGroup.add(cloud);
            }
            scene.add(cloudGroup);
            
            // --- 9. AI 建筑 3D 对象 (V6: 只存颜色) ---
            blockMaterials[MAT_WOOD] = new THREE.Color(0x8b5a2b); 
            blockMaterials[MAT_COBBLE] = new THREE.Color(0x808080); 
            blockMaterials[MAT_ROOF] = new THREE.Color(0x6b4423); 
            blockGroup = new THREE.Group();
            scene.add(blockGroup);

            // 粒子系统
            const particleGeometry = new THREE.BufferGeometry();
            const positions = new Float32Array(2000 * 3); const colors = new Float32Array(2000 * 3); const sizes = new Float32Array(2000);
            for (let i = 0; i < 2000; i++) { sizes[i] = 1; } 
            particleGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
            particleGeometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
            particleGeometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1));
            const particleMaterial = new THREE.PointsMaterial({ size: 0.1, sizeAttenuation: true, vertexColors: true, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false });
            particleSystem = new THREE.Points(particleGeometry, particleMaterial);
            particleSystem.visible = false; 
            scene.add(particleSystem);

            // --- 10. 动画循环 (合并) ---
            function animate() {
                requestAnimationFrame(animate);
                cloudGroup.children.forEach(cloud => {
                    cloud.position.x += 0.01;
                    if (cloud.position.x > groundSize) { cloud.position.x = -groundSize; cloud.position.z = (Math.random() - 0.5) * groundSize * 1.5; }
                });
                if (particleSystem.visible) updateParticles();
                controls.update(); 
                renderer.render(scene, camera);
            }

            // --- 11. 窗口大小调整 ---
            window.addEventListener('resize', () => {
                camera.aspect = window.innerWidth / window.innerHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(window.innerWidth, window.innerHeight);
            });

            // --- 12. 辅助函数 (文本、建筑、特效) ---
            
            // 文本打字机
            function typeText(lines, onFinished) {
                let lineIndex = 0, charIndex = 0; aiOutput.innerHTML = ''; 
                startButton.disabled = true; startButton.textContent = '正在生成中...';
                effectSelector.disabled = true; magicSelector.disabled = true; particleSlider.disabled = true;
                function typeChar() {
                    if (lineIndex >= lines.length) {
                        startButton.disabled = false; startButton.textContent = '重新生成';
                        effectSelector.disabled = false; magicSelector.disabled = false; particleSlider.disabled = false;
                        if (onFinished) onFinished(); return;
                    }
                    const currentLine = lines[lineIndex];
                    if (charIndex < currentLine.length) { aiOutput.innerHTML += currentLine.charAt(charIndex); charIndex++; aiOutputContainer.scrollTop = aiOutputContainer.scrollHeight; setTimeout(typeChar, 20); }
                    else { aiOutput.innerHTML += '\n'; lineIndex++; charIndex = 0; setTimeout(typeChar, 200); }
                }
                typeChar();
            }

            // 建筑动画总路由器 (V6)
            function animateBuild() {
                if (isBuilding) return;
                isBuilding = true;
                while (blockGroup.children.length > 0) { blockGroup.remove(blockGroup.children[0]); }
                
                // V6: 根据魔法主题和密度决定粒子系统是否可见
                particleSystem.visible = (currentMagicTheme !== 'none' && particleDensity > 0);

                switch (currentEffect) {
                    case 'layer-scan': startBuild_LayerScan(); break;
                    case 'ripple': startBuild_Ripple(); break;
                    default:
                        // 所有其他特效都走随机序列
                        startBuildSequence(getAnimationFunction(currentEffect), 30);
                        break;
                }
            }

            // V6: 获取动画函数的帮助器 (无变化)
            function getAnimationFunction(effectName) {
                switch (effectName) {
                    case 'magic-gradient': return animateBlock_MagicGradient;
                    case 'vortex': return animateBlock_Vortex;
                    case 'rain-down': return animateBlock_RainDown;
                    case 'ground-up': return animateBlock_GroundUp;
                    case 'assemble': return animateBlock_Assemble;
                    case 'simple':
                    default: return animateBlock_Simple;
                }
            }

            // 通用建筑序列 (随机) (V6)
            function startBuildSequence(animationFunction, delay) {
                const shuffledData = [...schematicData].sort(() => Math.random() - 0.5);
                let blockIndex = 0;
                function placeNextBlock() {
                    if (blockIndex >= shuffledData.length) { isBuilding = false; return; }
                    const blockData = shuffledData[blockIndex];
                    const baseColor = blockMaterials[blockData.type] || blockMaterials[MAT_COBBLE];
                    
                    const block = animationFunction(blockData, baseColor); 
                    
                    // V6: 魔法主题函数负责附加特效
                    applyMagicTheme(block, blockData, currentMagicTheme);
                    
                    blockIndex++;
                    setTimeout(placeNextBlock, delay);
                }
                placeNextBlock();
            }

            // --- V6: 魔法主题应用 ---
            
            // V6: 新增 - 魔法主题总控制器
            function applyMagicTheme(block, blockData, magicTheme) {
                switch (magicTheme) {
                    case 'rune-energy':
                        emitParticles(blockData, 'green');
                        animateGlow(block, 'green');
                        break;
                    case 'fire':
                        emitParticles(blockData, 'fire');
                        animateGlow(block, 'fire');
                        break;
                    case 'ice':
                        emitParticles(blockData, 'ice');
                        animateGlow(block, 'ice');
                        break;
                    case 'shadow':
                        emitParticles(blockData, 'shadow');
                        animateGlow(block, 'shadow');
                        break;
                    case 'none':
                    default:
                        // 什么也不做
                        break;
                }
            }

            // V6: 新增 - 奥术光辉动画 (带主题)
            function animateGlow(block, theme) {
                // 确保材质是克隆的并且可以发光
                if (!block.material.clone) return; 
                block.material = block.material.clone(); 
                
                let emissiveColor;
                switch (theme) {
                    case 'fire': emissiveColor = 0xff8800; break;
                    case 'ice': emissiveColor = 0x88ccff; break;
                    case 'shadow': emissiveColor = 0xcc88ff; break;
                    case 'green':
                    default: emissiveColor = 0x88ff88; break;
                }
                block.material.emissive = new THREE.Color(emissiveColor);
                block.material.emissiveIntensity = 0;

                let progress = 0, duration = 800, startTime = Date.now();
                function animate() {
                    const elapsed = Date.now() - startTime;
                    progress = Math.min(1, elapsed / duration);
                    if (progress < 0.5) { block.material.emissiveIntensity = progress * 2; }
                    else { block.material.emissiveIntensity = (1 - progress) * 2; }
                    if (progress < 1) { requestAnimationFrame(animate); }
                    else { block.material.emissiveIntensity = 0; }
                }
                animate();
            }

            // --- 特效实现 (8种运动) ---
            // V6: 所有函数现在都创建、添加并返回 block，但不应用魔法

            // 特效 1: 渐变 (Gradient)
            function animateBlock_MagicGradient(blockData, baseColor) {
                const blockGeometry = new THREE.BoxGeometry(1, 1, 1);
                const blockMaterial = new THREE.MeshLambertMaterial({ color: baseColor, transparent: true, opacity: 0.01 });
                const block = new THREE.Mesh(blockGeometry, blockMaterial);
                block.position.set(blockData.x, blockData.y, blockData.z);
                block.scale.set(0.8, 0.8, 0.8);
                blockGroup.add(block);

                let progress = 0, duration = 1000, startTime = Date.now();
                const startScale = block.scale.clone();
                const targetScale = new THREE.Vector3(1, 1, 1);
                function animate() {
                    const elapsed = Date.now() - startTime;
                    progress = Math.min(1, elapsed / duration);
                    const easedProgress = Math.pow(progress, 2);
                    block.material.opacity = 0.01 + 0.99 * easedProgress;
                    block.scale.lerpVectors(startScale, targetScale, easedProgress);
                    if (progress < 1) { requestAnimationFrame(animate); }
                    else { block.material.opacity = 1; block.scale.set(1, 1, 1); }
                }
                animate();
                return block;
            }

            // 特效 2: 旋涡 (Vortex)
            function animateBlock_Vortex(blockData, baseColor) {
                const blockGeometry = new THREE.BoxGeometry(1, 1, 1);
                const blockMaterial = new THREE.MeshLambertMaterial({ color: baseColor });
                const block = new THREE.Mesh(blockGeometry, blockMaterial);
                blockGroup.add(block);

                let progress = 0, duration = 800, startTime = Date.now();
                const startRadius = 10.0, startAngle = Math.random() * Math.PI * 2;
                const totalRotations = 3 * Math.PI * 2, startY = blockData.y + 5 + Math.random() * 3;
                function animate() {
                    const elapsed = Date.now() - startTime;
                    progress = Math.min(1, elapsed / duration);
                    const easedProgress = 1 - Math.pow(1 - progress, 3); 
                    const currentRadius = startRadius * (1 - easedProgress);
                    const currentAngle = startAngle + totalRotations * easedProgress;
                    const currentY = startY + (blockData.y - startY) * easedProgress;
                    block.position.x = blockData.x + currentRadius * Math.cos(currentAngle);
                    block.position.z = blockData.z + currentRadius * Math.sin(currentAngle);
                    block.position.y = currentY;
                    block.rotation.y = currentAngle; 
                    if (progress < 1) { requestAnimationFrame(animate); }
                    else { block.rotation.set(0,0,0); block.position.set(blockData.x, blockData.y, blockData.z); }
                }
                animate();
                return block;
            }

            // 特效 3: 天降 (Rain Down)
            function animateBlock_RainDown(blockData, baseColor) {
                const blockGeometry = new THREE.BoxGeometry(1, 1, 1);
                const blockMaterial = new THREE.MeshLambertMaterial({ color: baseColor });
                const block = new THREE.Mesh(blockGeometry, blockMaterial);
                block.position.set(blockData.x, blockData.y + 15, blockData.z); 
                block.scale.set(1.1, 0.8, 1.1); 
                blockGroup.add(block);
                let progress = 0, duration = 500, startTime = Date.now();
                const startY = block.position.y, targetY = blockData.y;
                function animate() {
                    const elapsed = Date.now() - startTime;
                    progress = Math.min(1, elapsed / duration);
                    const easedProgress = 1 - Math.pow(1 - progress, 3);
                    block.position.y = startY + (targetY - startY) * easedProgress;
                    if (progress < 1) { requestAnimationFrame(animate); }
                    else { animateBounce(block); }
                }
                function animateBounce(b) {
                    let bounceProgress = 0, bounceDuration = 200, bounceStart = Date.now();
                    function bounce() {
                        const elapsed = Date.now() - bounceStart;
                        bounceProgress = Math.min(1, elapsed / bounceDuration);
                        const scaleY = 0.8 + 0.2 * Math.abs(Math.sin(bounceProgress * Math.PI));
                        const scaleXZ = 1.1 - 0.1 * Math.abs(Math.sin(bounceProgress * Math.PI));
                        b.scale.set(scaleXZ, scaleY, scaleXZ);
                        if (bounceProgress < 1) { requestAnimationFrame(bounce); }
                        else { b.scale.set(1, 1, 1); }
                    }
                    bounce();
                }
                animate();
                return block;
            }

            // 特效 4: 从地升起 (Ground Up)
            function animateBlock_GroundUp(blockData, baseColor) {
                const blockGeometry = new THREE.BoxGeometry(1, 1, 1);
                const blockMaterial = new THREE.MeshLambertMaterial({ color: baseColor });
                const block = new THREE.Mesh(blockGeometry, blockMaterial);
                block.position.set(blockData.x, -5, blockData.z); 
                blockGroup.add(block);
                let progress = 0, duration = 600, startTime = Date.now();
                const startY = block.position.y, targetY = blockData.y;
                function animate() {
                    const elapsed = Date.now() - startTime;
                    progress = Math.min(1, elapsed / duration);
                    const easedProgress = 1 - Math.pow(1 - progress, 3);
                    block.position.y = startY + (targetY - startY) * easedProgress;
                    if (progress < 1) { requestAnimationFrame(animate); }
                }
                animate();
                return block;
            }

            // 特效 5: 组装 (Assemble)
            function animateBlock_Assemble(blockData, baseColor) {
                const blockGeometry = new THREE.BoxGeometry(1, 1, 1);
                const blockMaterial = new THREE.MeshLambertMaterial({ color: baseColor });
                const block = new THREE.Mesh(blockGeometry, blockMaterial);
                const startX = blockData.x > 0 ? blockData.x + 15 : blockData.x - 15;
                block.position.set(startX, blockData.y, blockData.z);
                blockGroup.add(block);
                let progress = 0, duration = 400, startTime = Date.now();
                const targetX = blockData.x;
                function animate() {
                    const elapsed = Date.now() - startTime;
                    progress = Math.min(1, elapsed / duration);
                    const easedProgress = progress * progress; 
                    block.position.x = startX + (targetX - startX) * easedProgress;
                    if (progress < 1) { requestAnimationFrame(animate); }
                }
                animate();
                return block;
            }

            // 特效 6: 闪现 (Simple)
            function animateBlock_Simple(blockData, baseColor) {
                const blockGeometry = new THREE.BoxGeometry(1, 1, 1);
                const blockMaterial = new THREE.MeshLambertMaterial({ color: baseColor });
                const block = new THREE.Mesh(blockGeometry, blockMaterial);
                block.position.set(blockData.x, blockData.y, blockData.z);
                block.scale.set(0, 0, 0);
                blockGroup.add(block);
                let progress = 0, duration = 100, startTime = Date.now();
                function animate() {
                    const elapsed = Date.now() - startTime;
                    progress = Math.min(1, elapsed / duration);
                    block.scale.set(progress, progress, progress);
                    if (progress < 1) { requestAnimationFrame(animate); }
                }
                animate();
                return block;
            }

            // --- 特殊序列 (V6: 重构) ---
            
            // 特效 7: 逐层扫描 (Layer Scan)
            function startBuild_LayerScan() {
                const sortedData = [...schematicData].sort((a, b) => a.y - b.y);
                const layers = new Map();
                sortedData.forEach(blockData => { if (!layers.has(blockData.y)) layers.set(blockData.y, []); layers.get(blockData.y).push(blockData); });
                const layerKeys = Array.from(layers.keys());
                let layerIndex = 0;
                function buildNextLayer() {
                    if (layerIndex >= layerKeys.length) { isBuilding = false; return; }
                    const currentLayerY = layerKeys[layerIndex];
                    const blocksInLayer = layers.get(currentLayerY);
                    blocksInLayer.forEach(blockData => {
                        const baseColor = blockMaterials[blockData.type] || blockMaterials[MAT_COBBLE];
                        const block = animateBlock_Simple(blockData, baseColor); // 运动
                        applyMagicTheme(block, blockData, currentMagicTheme); // 魔法
                    });
                    layerIndex++;
                    setTimeout(buildNextLayer, 300); 
                }
                buildNextLayer();
            }

            // 特效 8: 波纹 (Ripple)
            function startBuild_Ripple() {
                const distanceData = schematicData.map(blockData => ({ ...blockData, dist: Math.sqrt(blockData.x * blockData.x + blockData.z * blockData.z) }));
                distanceData.sort((a, b) => a.dist - b.dist);
                const ripples = new Map();
                distanceData.forEach(blockData => { const rippleIndex = Math.floor(blockData.dist); if (!ripples.has(rippleIndex)) ripples.set(rippleIndex, []); ripples.get(rippleIndex).push(blockData); });
                const rippleKeys = Array.from(ripples.keys()).sort((a, b) => a - b);
                let rippleIndex = 0;
                function buildNextRipple() {
                    if (rippleIndex >= rippleKeys.length) { isBuilding = false; return; }
                    const currentRippleKey = rippleKeys[rippleIndex];
                    const blocksInRipple = ripples.get(currentRippleKey);
                    blocksInRipple.forEach(blockData => {
                        const baseColor = blockMaterials[blockData.type] || blockMaterials[MAT_COBBLE];
                        const block = animateBlock_GroundUp(blockData, baseColor); // 运动
                        applyMagicTheme(block, blockData, currentMagicTheme); // 魔法
                    });
                    rippleIndex++;
                    setTimeout(buildNextRipple, 100); 
                }
                buildNextRipple();
            }

            // --- 粒子系统 (V6: 主题化 + 密度) ---
            function updateParticles() {
                const positions = particleSystem.geometry.attributes.position.array, colors = particleSystem.geometry.attributes.color.array, sizes = particleSystem.geometry.attributes.size.array; 
                for (let i = 0; i < particles.length; i++) {
                    const p = particles[i]; if (p.life <= 0) continue;
                    // V6: 自定义重力
                    p.velocity.y -= p.gravity; 
                    p.position.add(p.velocity);
                    p.life -= 0.01; p.opacity = p.life / p.maxLife;
                    if (p.life <= 0) { positions[i * 3 + 1] = -100; } 
                    else {
                        positions[i * 3] = p.position.x; positions[i * 3 + 1] = p.position.y; positions[i * 3 + 2] = p.position.z;
                        colors[i * 3] = p.color.r * p.opacity; colors[i * 3 + 1] = p.color.g * p.opacity; colors[i * 3 + 2] = p.color.b * p.opacity;
                        sizes[i] = p.size * p.opacity;
                    }
                }
                particleSystem.geometry.attributes.position.needsUpdate = true;
                particleSystem.geometry.attributes.color.needsUpdate = true;
                particleSystem.geometry.attributes.size.needsUpdate = true;
            }

            function emitParticles(blockData, theme) {
                // V6: 根据密度计算粒子数量
                const numToEmit = Math.floor((particleDensity / 100) * MAX_PARTICLES_PER_BLOCK);
                if (numToEmit === 0) return;
                
                let colorBase, velY, life, gravity;
                // V6: 根据主题设置物理和颜色
                switch (theme) {
                    case 'fire':
                        colorBase = 0xff8800; velY = [0.08, 0.12]; life = [0.6, 1.0]; gravity = 0.0005; // 上升
                        break;
                    case 'ice':
                        colorBase = 0x88ccff; velY = [0.01, 0.05]; life = [1.0, 1.5]; gravity = 0.0015; // 缓慢
                        break;
                    case 'shadow':
                        colorBase = 0xcc88ff; velY = [0.03, 0.08]; life = [1.0, 1.2]; gravity = 0.0008; // 漂浮
                        break;
                    case 'green':
                    default:
                        colorBase = 0x88ff88; velY = [0.08, 0.12]; life = [0.8, 1.2]; gravity = 0.001; // 经典
                        break;
                }

                for (let i = 0; i < numToEmit; i++) {
                    let foundParticle = false;
                    for (let j = 0; j < particles.length; j++) {
                        if (particles[j].life <= 0) {
                            const p = particles[j];
                            p.position.set(blockData.x, blockData.y, blockData.z);
                            p.velocity.set((Math.random() - 0.5) * 0.05, velY[0] + Math.random() * (velY[1] - velY[0]), (Math.random() - 0.5) * 0.05);
                            p.color = new THREE.Color(colorBase).multiplyScalar(0.7 + Math.random() * 0.3); 
                            p.maxLife = p.life = life[0] + Math.random() * (life[1] - life[0]);
                            p.size = 1 + Math.random() * 2;
                            p.gravity = gravity; // V6
                            foundParticle = true; break;
                        }
                    }
                    if (!foundParticle && particles.length < 2000) { 
                        const p = {
                            position: new THREE.Vector3(blockData.x, blockData.Y, blockData.z),
                            velocity: new THREE.Vector3((Math.random() - 0.5) * 0.05, velY[0] + Math.random() * (velY[1] - velY[0]), (Math.random() - 0.5) * 0.05),
                            color: new THREE.Color(colorBase).multiplyScalar(0.7 + Math.random() * 0.3),
                            maxLife: life[0] + Math.random() * (life[1] - life[0]), life: life[0] + Math.random() * (life[1] - life[0]),
                            size: 1 + Math.random() * 2, opacity: 1, gravity: gravity
                        };
                        particles.push(p);
                    }
                }
            }

            // --- 13. 启动和事件监听 ---
            document.getElementById('loading-overlay').style.display = 'none';
            animate();

            // 折叠面板事件
            panelToggle.addEventListener('click', () => {
                panelContent.classList.toggle('collapsed');
                toggleIcon.classList.toggle('collapsed');
            });

            // V6: 三个控件的事件
            effectSelector.addEventListener('change', (e) => { currentEffect = e.target.value; });
            magicSelector.addEventListener('change', (e) => { currentMagicTheme = e.target.value; });
            particleSlider.addEventListener('input', (e) => { 
                particleDensity = parseInt(e.target.value, 10);
                particleDensityLabel.textContent = `${particleDensity}%`;
            });

            // 开始按钮事件
            startButton.addEventListener('click', () => {
                if (isBuilding) return; 
                const effectName = effectSelector.options[effectSelector.selectedIndex].text;
                const magicName = magicSelector.options[magicSelector.selectedIndex].text;
                const dynamicLog = [...aiLogBase, `动画: ${effectName}`, `主题: ${magicName}`, `密度: ${particleDensity}%`, "开始建造!"];
                typeText(dynamicLog, () => { animateBuild(); });
            });

            aiOutput.textContent = "准备就绪。请组合动画和魔法！";
        }
    </script>
</body>
</html>

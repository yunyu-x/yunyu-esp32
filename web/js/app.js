/**
 * web/js/app.js
 * -------------
 * microUnit 3D 渲染视口、用户交互控制器与实时遥测图表绑定
 */

(function () {
    // 1. 初始化物理引擎
    const engine = new WebPhysicsEngine();
    let isRunning = true;
    let timeScale = 1.0;

    // 2. Three.js 场景与渲染器
    const canvas = document.getElementById('webgl-canvas');
    let renderer;
    try {
        renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
        renderer.setPixelRatio(window.devicePixelRatio || 1);
        renderer.setSize(canvas.parentElement.clientWidth, canvas.parentElement.clientHeight);
    } catch (e) {
        console.warn('WebGL init fallback:', e);
    }

    const scene = new THREE.Scene();

    const camera = new THREE.PerspectiveCamera(
        45,
        canvas.parentElement.clientWidth / canvas.parentElement.clientHeight,
        0.01,
        20
    );
    camera.position.set(0.35, 0.45, 0.60);

    const controls = new THREE.OrbitControls(camera, canvas);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.target.set(0, 0, 0.03);

    // 光照系统
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.9);
    scene.add(ambientLight);

    const dirLight = new THREE.DirectionalLight(0xffffff, 1.2);
    dirLight.position.set(0.8, 1.5, 1.0);
    scene.add(dirLight);

    const cyanRimLight = new THREE.PointLight(0x06b6d4, 1.0, 3.0);
    cyanRimLight.position.set(-0.6, 0.5, -0.4);
    scene.add(cyanRimLight);

    // 地面网格与反光平面
    const gridHelper = new THREE.GridHelper(3.0, 60, 0x38bdf8, 0x1e293b);
    gridHelper.position.y = 0;
    scene.add(gridHelper);

    const floorGeo = new THREE.PlaneGeometry(6, 6);
    const floorMat = new THREE.MeshStandardMaterial({
        color: 0x070a12,
        roughness: 0.85,
        metalness: 0.2
    });
    const floorMesh = new THREE.Mesh(floorGeo, floorMat);
    floorMesh.rotation.x = -Math.PI / 2;
    floorMesh.receiveShadow = true;
    scene.add(floorMesh);

    // 单元 3D 网格池
    const unitMeshGroup = new THREE.Group();
    scene.add(unitMeshGroup);

    // 辅助箭头与光束组
    const gizmoGroup = new THREE.Group();
    scene.add(gizmoGroup);

    // 障碍物网格组
    const obstacleGroup = new THREE.Group();
    scene.add(obstacleGroup);

    // 材质定义
    const cubeMaterials = [
        new THREE.MeshStandardMaterial({ color: 0xef4444, metalness: 0.3, roughness: 0.4 }), // Front (+X) 红
        new THREE.MeshStandardMaterial({ color: 0x3b82f6, metalness: 0.3, roughness: 0.4 }), // Back (-X) 蓝
        new THREE.MeshStandardMaterial({ color: 0x10b981, metalness: 0.3, roughness: 0.4 }), // Left (+Y) 绿
        new THREE.MeshStandardMaterial({ color: 0xf59e0b, metalness: 0.3, roughness: 0.4 }), // Right (-Y) 橙
        new THREE.MeshStandardMaterial({ color: 0xfacc15, metalness: 0.3, roughness: 0.4 }), // Top (+Z) 黄
        new THREE.MeshStandardMaterial({ color: 0x64748b, metalness: 0.5, roughness: 0.5 })  // Bottom (-Z) 灰
    ];
    const rotorMaterial = new THREE.MeshStandardMaterial({ color: 0xd97706, metalness: 0.8, roughness: 0.2 });

    function createUnitMesh(unitId) {
        const group = new THREE.Group();
        group.userData = { unitId };

        // 50mm 立方体外壳 (倒角盒网格)
        const boxGeo = new THREE.BoxGeometry(0.050, 0.050, 0.050);
        const cube = new THREE.Mesh(boxGeo, cubeMaterials);
        cube.castShadow = true;
        cube.receiveShadow = true;
        group.add(cube);

        // 内部微型动量轮转子
        const rotorGeo = new THREE.CylinderGeometry(0.0135, 0.0135, 0.005, 24);
        const rotor = new THREE.Mesh(rotorGeo, rotorMaterial);
        rotor.rotation.x = Math.PI / 2;
        rotor.name = 'rotor';
        group.add(rotor);

        // 端面 EPM 磁极指示光圈
        const ringGeo = new THREE.RingGeometry(0.006, 0.010, 16);
        const ringMat = new THREE.MeshBasicMaterial({ color: 0x38bdf8, side: THREE.DoubleSide });
        const ring = new THREE.Mesh(ringGeo, ringMat);
        ring.position.z = 0.0251;
        group.add(ring);

        // 力向量指示箭头
        const arrow = new THREE.ArrowHelper(
            new THREE.Vector3(1, 0, 0),
            new THREE.Vector3(0, 0, 0),
            0.04,
            0xef4444,
            0.015,
            0.01
        );
        arrow.visible = false;
        arrow.name = 'forceArrow';
        group.add(arrow);

        return group;
    }

    // 重构 3D 视口中的几何体
    function sync3DSceneObjects() {
        // 清理旧网格
        while (unitMeshGroup.children.length > 0) {
            unitMeshGroup.remove(unitMeshGroup.children[0]);
        }
        while (obstacleGroup.children.length > 0) {
            obstacleGroup.remove(obstacleGroup.children[0]);
        }

        // 创建新单元
        engine.units.forEach(u => {
            const mesh = createUnitMesh(u.id);
            unitMeshGroup.add(mesh);
        });

        // 创建障碍物
        engine.obstacles.forEach(obs => {
            const obsGeo = new THREE.CylinderGeometry(obs.radius, obs.radius, 0.12, 32);
            const obsMat = new THREE.MeshStandardMaterial({
                color: 0xef4444,
                metalness: 0.4,
                roughness: 0.3,
                transparent: true,
                opacity: 0.75
            });
            const obsMesh = new THREE.Mesh(obsGeo, obsMat);
            obsMesh.position.set(obs.x, 0.06, obs.y);
            obsMesh.castShadow = true;
            obstacleGroup.add(obsMesh);
        });
    }

    sync3DSceneObjects();

    // ==========================================
    // 3. 实时 Chart.js 图表初始化
    // ==========================================
    const maxDataPoints = 60;
    const timeLabels = [];

    function makeChart(canvasId, label, color, yUnit = '') {
        const ctx = document.getElementById(canvasId).getContext('2d');
        return new Chart(ctx, {
            type: 'line',
            data: {
                labels: timeLabels,
                datasets: [{
                    label: label,
                    data: [],
                    borderColor: color,
                    backgroundColor: color.replace('1)', '0.15)'),
                    borderWidth: 1.8,
                    pointRadius: 0,
                    tension: 0.25,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: {
                        display: false,
                        grid: { display: false }
                    },
                    y: {
                        grid: { color: 'rgba(255, 255, 255, 0.06)' },
                        ticks: {
                            color: '#9ca3af',
                            font: { size: 9 },
                            callback: v => v + yUnit
                        }
                    }
                }
            }
        });
    }

    const chartAttitude = makeChart('chart-attitude', '姿态角 / 质心', 'rgba(245, 158, 11, 1)', '°');
    const chartActuation = makeChart('chart-actuation', '转速 / 力矩', 'rgba(56, 189, 248, 1)', '');
    const chartEnergy = makeChart('chart-energy', '做功与能耗', 'rgba(16, 185, 129, 1)', 'J');
    const chartMetrics = makeChart('chart-metrics', '极化度 / 应力', 'rgba(168, 85, 247, 1)', '');

    let chartTick = 0;
    function updateCharts(t) {
        chartTick++;
        if (chartTick % 3 !== 0) return; // 约 20Hz 刷新图表

        timeLabels.push(t.time);
        if (timeLabels.length > maxDataPoints) timeLabels.shift();

        // 1. Attitude / Position
        let valAttitude = 0;
        if (t.scenario === 'single' || t.scenario === 'realistic') valAttitude = parseFloat(t.pitchDeg);
        else if (t.scenario === 'dual') valAttitude = parseFloat(t.relAngleDeg);
        else if (t.scenario === 'multi') valAttitude = parseFloat(t.comX) * 100;
        else if (t.scenario === 'swarm') valAttitude = parseFloat(t.formationRmseM) * 1000;

        chartAttitude.data.datasets[0].data.push(valAttitude);
        if (chartAttitude.data.datasets[0].data.length > maxDataPoints) chartAttitude.data.datasets[0].data.shift();
        chartAttitude.update();

        // 2. Actuation
        let valAct = 0;
        if (t.scenario === 'single' || t.scenario === 'realistic') valAct = parseFloat(t.flywheelRpm);
        else if (t.scenario === 'dual') valAct = parseFloat(t.flywheelRpmB);
        else if (t.scenario === 'multi') valAct = parseFloat(t.maxStressN);
        else if (t.scenario === 'swarm') valAct = parseFloat(t.polarization) * 1000;

        chartActuation.data.datasets[0].data.push(valAct);
        if (chartActuation.data.datasets[0].data.length > maxDataPoints) chartActuation.data.datasets[0].data.shift();
        chartActuation.update();

        // 3. Energy / Heat
        let valEnergy = 0;
        if (t.scenario === 'realistic') valEnergy = parseFloat(t.totalHeatJ || t.elecEnergy);
        else if (t.scenario === 'single') valEnergy = parseFloat(t.elecEnergy);
        else if (t.scenario === 'dual') valEnergy = parseFloat(t.totalEnergy);
        else if (t.scenario === 'multi') valEnergy = parseFloat(t.totalEnergy);
        else if (t.scenario === 'swarm') valEnergy = parseFloat(t.numAgents || 16) * 0.5;

        chartEnergy.data.datasets[0].data.push(valEnergy);
        if (chartEnergy.data.datasets[0].data.length > maxDataPoints) chartEnergy.data.datasets[0].data.shift();
        chartEnergy.update();

        // 4. Metrics / Slip
        let valMetric = 0;
        if (t.scenario === 'realistic') valMetric = parseFloat(t.slipDistMm || 0);
        else if (t.scenario === 'single') valMetric = parseFloat(t.ccui);
        else if (t.scenario === 'dual') valMetric = parseFloat(t.interfaceForceN);
        else if (t.scenario === 'multi') valMetric = parseFloat(t.maxStressN);
        else if (t.scenario === 'swarm') valMetric = parseFloat(t.polarization);

        chartMetrics.data.datasets[0].data.push(valMetric);
        if (chartMetrics.data.datasets[0].data.length > maxDataPoints) chartMetrics.data.datasets[0].data.shift();
        chartMetrics.update();
    }

    // ==========================================
    // 4. UI 交互与事件监听绑定
    // ==========================================
    // 悬浮 Toast 提示机制
    function showToast(msg, type = 'info') {
        let toast = document.getElementById('sim-toast');
        if (!toast) {
            toast = document.createElement('div');
            toast.id = 'sim-toast';
            toast.className = 'sim-toast';
            document.body.appendChild(toast);
        }
        toast.innerHTML = msg;
        toast.className = 'sim-toast show ' + type;
        clearTimeout(toast._timeout);
        toast._timeout = setTimeout(() => {
            toast.className = 'sim-toast';
        }, 1600);
    }

    // 场景与右侧面板字典
    const tabs = document.querySelectorAll('.tab-btn');
    const paramCards = {
        single: document.getElementById('params-single'),
        dual: document.getElementById('params-dual'),
        multi: document.getElementById('params-multi'),
        swarm: document.getElementById('params-swarm'),
        realistic: document.getElementById('params-realistic'),
        prototype: document.getElementById('params-prototype'),
        free: document.getElementById('params-single')
    };
    const sliderUnitCount = document.getElementById('slider-unit-count');
    const valUnitCount = document.getElementById('val-unit-count');

    // 统一全局场景切换调度器
    function switchScenario(scen, options = {}) {
        // 1. 顶部 Tab 高亮
        tabs.forEach(b => {
            if (b.dataset.scenario === scen) b.classList.add('active');
            else b.classList.remove('active');
        });

        // 2. 右侧参数卡片联动切换
        Object.keys(paramCards).forEach(k => {
            if (paramCards[k]) paramCards[k].style.display = (k === scen) ? 'block' : 'none';
        });

        // 3. 单元数量滑块与相机视角联动
        if (scen === 'single' || scen === 'realistic' || scen === 'prototype') {
            const count = options.numUnits || 1;
            sliderUnitCount.value = count;
            valUnitCount.innerText = count;
            camera.position.set(0.25, 0.35, 0.45);
            controls.target.set(0, 0, 0.025);
        } else if (scen === 'dual') {
            const count = options.numUnits || 2;
            sliderUnitCount.value = count;
            valUnitCount.innerText = count;
            camera.position.set(0.35, 0.40, 0.50);
            controls.target.set(0.025, 0, 0.04);
        } else if (scen === 'multi') {
            const count = options.numUnits || parseInt(sliderUnitCount.value) || 4;
            const validCount = Math.max(2, count);
            sliderUnitCount.value = validCount;
            valUnitCount.innerText = validCount;
            options.numUnits = validCount;
            camera.position.set(0.50, 0.60, 0.75);
            controls.target.set(0, 0, 0.025);
        } else if (scen === 'swarm') {
            const count = options.numAgents || parseInt(sliderUnitCount.value) || 16;
            const validCount = Math.max(4, count);
            sliderUnitCount.value = validCount;
            valUnitCount.innerText = validCount;
            options.numAgents = validCount;
            camera.position.set(0.0, 1.20, 1.20);
            controls.target.set(0.2, 0, 0.0);
        } else if (scen === 'free') {
            const count = options.count || parseInt(sliderUnitCount.value) || 3;
            sliderUnitCount.value = count;
            valUnitCount.innerText = count;
            camera.position.set(0.40, 0.50, 0.65);
            controls.target.set(0, 0, 0.03);
        }

        engine.loadScenario(scen, options);
        sync3DSceneObjects();
    }

    // 顶部场景导航 Tab 点击
    tabs.forEach(btn => {
        btn.addEventListener('click', () => {
            switchScenario(btn.dataset.scenario);
        });
    });

    // 运行/暂停与步进
    const btnPlayPause = document.getElementById('btn-play-pause');
    const playIcon = document.getElementById('play-icon');
    btnPlayPause.addEventListener('click', () => {
        isRunning = !isRunning;
        playIcon.innerText = isRunning ? '⏸' : '▶';
        btnPlayPause.innerHTML = `<span id="play-icon">${isRunning ? '⏸' : '▶'}</span> ${isRunning ? '运行中' : '已暂停'}`;
        showToast(isRunning ? '▶ 仿真恢复运行' : '⏸ 仿真已暂停');
    });

    document.getElementById('btn-step').addEventListener('click', () => {
        isRunning = false;
        playIcon.innerText = '▶';
        btnPlayPause.innerHTML = `<span id="play-icon">▶</span> 已暂停`;
        engine.step();
        showToast('⏯ 单步执行 (5ms)');
    });

    document.getElementById('btn-reset').addEventListener('click', () => {
        const activeTab = document.querySelector('.tab-btn.active');
        const scen = activeTab ? activeTab.dataset.scenario : 'single';
        switchScenario(scen);
        showToast('🔄 仿真环境与状态机已重置');
    });

    document.getElementById('speed-select').addEventListener('change', e => {
        timeScale = parseFloat(e.target.value);
        showToast(`⚡ 求解倍速: ${timeScale}x`);
    });

    // 单元装配管理器滑块智能响应
    sliderUnitCount.addEventListener('input', e => {
        const count = parseInt(e.target.value);
        valUnitCount.innerText = count;

        if (count === 1) {
            if (engine.activeScenario !== 'single' && engine.activeScenario !== 'realistic') {
                switchScenario('single', { numUnits: 1 });
                showToast('已切换至单体仿真模式');
            }
        } else if (count === 2 && (engine.activeScenario === 'single' || engine.activeScenario === 'realistic')) {
            switchScenario('dual', { numUnits: 2 });
            showToast('已切换至双体爬升模式');
        } else if (engine.activeScenario === 'multi') {
            engine.initMultiUnitScenario({ numUnits: count, topology: engine.multiTopology });
            sync3DSceneObjects();
        } else if (engine.activeScenario === 'swarm') {
            engine.initSwarmScenario({ numAgents: count });
            sync3DSceneObjects();
        } else if (engine.activeScenario === 'free') {
            engine.initFreeSandboxScenario({ count });
            sync3DSceneObjects();
        } else if (count > 2 && (engine.activeScenario === 'single' || engine.activeScenario === 'realistic' || engine.activeScenario === 'dual')) {
            switchScenario('multi', { numUnits: count, topology: 'CHAIN' });
            showToast(`已切换至多体装配 (${count} 单元)`);
        }
    });

    // 拓扑切换按键
    function highlightTopologyButton(activeBtnId) {
        ['btn-topo-chain', 'btn-topo-lattice', 'btn-topo-ring', 'btn-topo-free'].forEach(id => {
            const el = document.getElementById(id);
            if (el) {
                if (id === activeBtnId) el.classList.add('highlight');
                else el.classList.remove('highlight');
            }
        });
    }

    document.getElementById('btn-topo-chain').addEventListener('click', () => {
        highlightTopologyButton('btn-topo-chain');
        const count = Math.max(3, parseInt(sliderUnitCount.value) || 4);
        switchScenario('multi', { topology: 'CHAIN', numUnits: count });
        showToast(`🔗 切换拓扑: 链式装配 (${count} 单元)`);
    });

    document.getElementById('btn-topo-lattice').addEventListener('click', () => {
        highlightTopologyButton('btn-topo-lattice');
        const count = Math.max(4, parseInt(sliderUnitCount.value) || 4);
        switchScenario('multi', { topology: 'LATTICE', numUnits: count });
        showToast(`▦ 切换拓扑: 晶格网格 (${count} 单元)`);
    });

    document.getElementById('btn-topo-ring').addEventListener('click', () => {
        highlightTopologyButton('btn-topo-ring');
        const count = Math.max(4, parseInt(sliderUnitCount.value) || 6);
        switchScenario('multi', { topology: 'RING', numUnits: count });
        showToast(`⭕ 切换拓扑: 闭合环形 (${count} 单元)`);
    });

    document.getElementById('btn-topo-free').addEventListener('click', () => {
        highlightTopologyButton('btn-topo-free');
        const count = Math.max(8, parseInt(sliderUnitCount.value) || 16);
        switchScenario('swarm', { numAgents: count });
        showToast(`✨ 切换模式: 集群自由散布 (${count} 单元)`);
    });

    // 受力与扭矩推注
    const sliderForceMag = document.getElementById('slider-force-mag');
    sliderForceMag.addEventListener('input', e => {
        document.getElementById('val-force-mag').innerText = e.target.value + ' N';
    });

    function getForceMag() {
        return parseFloat(sliderForceMag.value) || 1.5;
    }

    function getTargetUnitId() {
        if (engine.activeScenario === 'dual') return 1;
        return 0;
    }

    document.getElementById('btn-push-right').addEventListener('click', () => {
        const mag = getForceMag();
        engine.applyForceToUnit(getTargetUnitId(), mag, 0, 0);
        showToast(`▶ 前进推力 +${mag.toFixed(1)} N`);
    });
    document.getElementById('btn-push-left').addEventListener('click', () => {
        const mag = getForceMag();
        engine.applyForceToUnit(getTargetUnitId(), -mag, 0, 0);
        showToast(`◀ 后退推力 -${mag.toFixed(1)} N`);
    });
    document.getElementById('btn-push-forward').addEventListener('click', () => {
        const mag = getForceMag();
        engine.applyForceToUnit(getTargetUnitId(), 0, mag, 0);
        showToast(`● 侧向推力 +${mag.toFixed(1)} N (左推)`);
    });
    document.getElementById('btn-push-back').addEventListener('click', () => {
        const mag = getForceMag();
        engine.applyForceToUnit(getTargetUnitId(), 0, -mag, 0);
        showToast(`▼ 侧向推力 -${mag.toFixed(1)} N (右推)`);
    });
    document.getElementById('btn-push-up').addEventListener('click', () => {
        const mag = getForceMag() * 2.5;
        engine.applyForceToUnit(getTargetUnitId(), 0, 0, mag);
        showToast(`▲ 跃升推力 +${mag.toFixed(1)} N`);
    });

    document.getElementById('btn-torque-cw').addEventListener('click', () => {
        engine.applyForceToUnit(getTargetUnitId(), 0, 0, 0, 0.06);
        showToast('↷ 顺时针翻转力矩 +0.06 N*m');
    });
    document.getElementById('btn-torque-ccw').addEventListener('click', () => {
        engine.applyForceToUnit(getTargetUnitId(), 0, 0, 0, -0.06);
        showToast('↶ 逆时针翻转力矩 -0.06 N*m');
    });

    // 执行机构操作
    document.getElementById('btn-fire-coil').addEventListener('click', () => {
        engine.fireCoil(getTargetUnitId());
        showToast('⚡ 触发高能电磁线圈脉冲', 'warning');
    });

    document.getElementById('btn-impulse-brake').addEventListener('click', () => {
        engine.impulseBrake(getTargetUnitId());
        showToast('🛑 触发飞轮脉冲制动力矩', 'danger');
    });

    document.getElementById('btn-toggle-epm').addEventListener('click', () => {
        const state = engine.toggleEpm(getTargetUnitId());
        showToast('🧲 EPM 锁止状态: ' + (state ? '已锁止 (ON)' : '已解锁 (OFF)'));
    });

    document.getElementById('btn-trigger-climb').addEventListener('click', () => {
        if (engine.activeScenario !== 'dual') {
            switchScenario('dual');
        }
        engine.triggerDualClimb();
        showToast('🪜 触发双体自主爬升步态');
    });

    // 参数滑动条监听
    document.getElementById('slider-rpm').addEventListener('input', e => {
        const val = parseFloat(e.target.value);
        document.getElementById('val-rpm').innerText = val.toLocaleString() + ' RPM';
        if (engine.units[0]) engine.units[0].targetRpm = val;
    });

    document.getElementById('slider-brake-torque').addEventListener('input', e => {
        const val = parseFloat(e.target.value);
        document.getElementById('val-brake-torque').innerText = val.toFixed(2) + ' N*m';
        if (engine.units[0]) engine.units[0].brakeTorque = val;
    });

    document.getElementById('slider-epm-force').addEventListener('input', e => {
        const val = parseFloat(e.target.value);
        document.getElementById('val-epm-force').innerText = val + ' N';
        if (engine.units[0]) engine.units[0].epmGroundForce = val;
    });

    document.getElementById('slider-inter-epm').addEventListener('input', e => {
        const val = parseFloat(e.target.value);
        document.getElementById('val-inter-epm').innerText = val + ' N';
        if (engine.units[1]) engine.units[1].epmMaxForce = val;
    });

    document.getElementById('btn-toggle-anchor-a').addEventListener('click', () => {
        if (engine.units[0]) {
            engine.units[0].isAnchored = !engine.units[0].isAnchored;
            document.getElementById('val-anchor-a').innerText = engine.units[0].isAnchored ? '开启' : '关闭';
        }
    });

    document.getElementById('slider-wave-freq').addEventListener('input', e => {
        const val = parseFloat(e.target.value);
        document.getElementById('val-wave-freq').innerText = val.toFixed(1) + ' Hz';
        engine.multiWaveFreq = val;
    });

    document.getElementById('slider-pull-load').addEventListener('input', e => {
        const val = parseFloat(e.target.value);
        document.getElementById('val-pull-load').innerText = val + ' N';
        engine.multiPullLoad = val;
    });

    // 集群编队形态切换
    ['square', 'line', 'circle', 'v', 'hex', 'stair'].forEach(shape => {
        const btn = document.getElementById('btn-shape-' + shape);
        if (btn) {
            btn.addEventListener('click', () => {
                const shapeMap = {
                    square: 'SQUARE',
                    line: 'LINE',
                    circle: 'CIRCLE',
                    v: 'V_SHAPE',
                    hex: 'HEX',
                    stair: 'STAIR'
                };
                engine.swarmFormation = shapeMap[shape] || 'SQUARE';
                engine.recomputeSwarmTargets();
                const shapeLabels = {
                    square: '方阵 Grid',
                    line: '直线 Line',
                    circle: '强固圆环 Ring',
                    v: 'V梯队 V-Shape',
                    hex: '蜂窝六边形 Hex',
                    stair: '3D立体阶梯 Stair'
                };
                document.getElementById('val-formation-shape').innerText = shapeLabels[shape] || shape.toUpperCase();
                showToast(`已切换目标阵列形貌: ${shapeLabels[shape] || shape}`, 'info');
            });
        }
    });

    document.getElementById('btn-mode-flock').addEventListener('click', () => {
        engine.swarmMode = 'FLOCKING';
        document.getElementById('val-swarm-mode').innerText = '游弋 Flocking';
        showToast('已切换至 Reynolds 自由游弋群集模式', 'info');
    });

    document.getElementById('btn-mode-assemble').addEventListener('click', () => {
        engine.swarmMode = 'SELF_ASSEMBLY';
        engine.recomputeSwarmTargets();
        document.getElementById('val-swarm-mode').innerText = '晶格组装 Assembly';
        showToast('已启动虚拟弹簧晶格对接组装', 'info');
    });

    const btnModeNeuro = document.getElementById('btn-mode-neuromorphic');
    if (btnModeNeuro) {
        btnModeNeuro.addEventListener('click', () => {
            engine.swarmMode = 'NEUROMORPHIC_SWARM';
            engine.recomputeSwarmTargets();
            document.getElementById('val-swarm-mode').innerText = '⚡ 仿生群智阵列';
            showToast('已激活 FlyDrones 仿生神经形态反射 + DCBA 去中心化竞价阵列自组装', 'info');
        });
    }

    const btnInjectFault = document.getElementById('btn-inject-fault');
    if (btnInjectFault) {
        btnInjectFault.addEventListener('click', () => {
            engine.injectSwarmFault();
            showToast('⚡ 突发故障注入: 1台模块掉电掉线，触发去中心化容错重塑', 'warning');
        });
    }

    const btnSelfHealing = document.getElementById('btn-self-healing');
    if (btnSelfHealing) {
        btnSelfHealing.addEventListener('click', () => {
            engine.triggerSwarmSelfHealing();
            showToast('🛡️ 群策群力自愈成功: 存活集群已自发完成槽位再拍卖与阵列闭环重构', 'success');
        });
    }

    document.getElementById('btn-add-obstacle').addEventListener('click', () => {
        const ox = (Math.random() - 0.5) * 0.8;
        const oy = (Math.random() - 0.5) * 0.8;
        engine.obstacles.push({ x: ox, y: oy, radius: 0.12 });
        sync3DSceneObjects();
        showToast('已在集群场域中放置动态避障柱', 'info');
    });

    // 真实高保真物理模式全局开关
    const btnToggleRealistic = document.getElementById('btn-toggle-realistic');
    const valRealisticBadge = document.getElementById('val-realistic-badge');
    if (btnToggleRealistic) {
        btnToggleRealistic.addEventListener('click', () => {
            engine.realisticMode = !engine.realisticMode;
            if (valRealisticBadge) {
                valRealisticBadge.innerText = engine.realisticMode ? '开启' : '关闭';
                valRealisticBadge.style.color = engine.realisticMode ? '#38bdf8' : '#9ca3af';
            }
        });
    }

    // 真实高保真参数滑块与 EPM 切换
    const sliderFilletR = document.getElementById('slider-fillet-r');
    if (sliderFilletR) {
        sliderFilletR.addEventListener('input', e => {
            const val = parseFloat(e.target.value);
            document.getElementById('val-fillet-r').innerText = val.toFixed(1) + ' mm';
            engine.filletR = val / 1000.0;
        });
    }

    const sliderMuS = document.getElementById('slider-mu-s');
    if (sliderMuS) {
        sliderMuS.addEventListener('input', e => {
            const val = parseFloat(e.target.value);
            document.getElementById('val-mu-s').innerText = val.toFixed(2);
            engine.muStatic = val;
            engine.muKinetic = Math.max(0.05, val - 0.10);
        });
    }

    const sliderRInt = document.getElementById('slider-r-int');
    if (sliderRInt) {
        sliderRInt.addEventListener('input', e => {
            const val = parseFloat(e.target.value);
            document.getElementById('val-r-int').innerText = val + ' mΩ';
            engine.batRInternal = val / 1000.0;
        });
    }

    const sliderRTh = document.getElementById('slider-r-th');
    if (sliderRTh) {
        sliderRTh.addEventListener('input', e => {
            const val = parseFloat(e.target.value);
            document.getElementById('val-r-th').innerText = val.toFixed(1) + ' K/W';
            engine.thermalRKperW = val;
        });
    }

    const btnToggleRealisticEpm = document.getElementById('btn-toggle-realistic-epm');
    if (btnToggleRealisticEpm) {
        btnToggleRealisticEpm.addEventListener('click', () => {
            if (engine.units[0]) {
                engine.units[0].groundEpmActive = !engine.units[0].groundEpmActive;
                document.getElementById('val-realistic-epm').innerText = engine.units[0].groundEpmActive ? '开启 (抗滑移)' : '关闭 (极易打滑)';
            }
        });
    }

    const btnRunPrototypeBench = document.getElementById('btn-run-prototype-bench');
    if (btnRunPrototypeBench) {
        btnRunPrototypeBench.addEventListener('click', async () => {
            showToast('⏳ 正在调用后端多物理场数字孪生求解引擎...', 'info');
            try {
                const resp = await fetch('/api/prototype/simulate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        target_rpm: 18000.0,
                        brake_torque: 0.25,
                        ground_epm: true,
                        duration_s: 0.70
                    })
                });
                if (resp.ok) {
                    const data = await resp.json();
                    showToast(`✅ 原型机仿真成功: 峰值=${data.max_pitch_deg.toFixed(1)}°, 滑移=${data.slip_distance_mm.toFixed(3)}mm, 稳压=${data.vreg_3v3_stable}`, 'success');
                    if (engine.units[0]) {
                        engine.units[0].pitch = Math.PI / 2;
                        engine.units[0].state = 'COMPLETED';
                    }
                } else {
                    showToast('⚠️ 后端仿真接口调用失败', 'danger');
                }
            } catch (e) {
                // 前端离线模式直接驱动引擎
                engine.impulseBrake(0);
                showToast('⚡ 本地物理引擎已触发动量轮急刹翻转', 'warning');
            }
        });
    }

    // 底部仪表盘收起/展开
    const dashboard = document.getElementById('bottom-dashboard');
    document.getElementById('dashboard-toggle').addEventListener('click', () => {
        dashboard.classList.toggle('collapsed');
        const isCollapsed = dashboard.classList.contains('collapsed');
        document.getElementById('toggle-hint').innerText = isCollapsed ? '▲ 展开' : '▼ 收起';
        setTimeout(() => onWindowResize(), 300);
    });

    // ==========================================
    // 5. 动画与主循环渲染
    // ==========================================
    const hudTime = document.getElementById('hud-time');
    const hudState = document.getElementById('hud-state');
    const hudAttitude = document.getElementById('hud-attitude');
    const hudMetric = document.getElementById('hud-metric');
    const hudSlip = document.getElementById('hud-slip');
    const hudVoltage = document.getElementById('hud-voltage');
    const hudTemp = document.getElementById('hud-temp');

    function animate() {
        requestAnimationFrame(animate);

        // 物理动力学步
        if (isRunning) {
            const steps = Math.round(timeScale);
            for (let i = 0; i < steps; i++) {
                engine.step();
            }
        }

        // 同步 3D 网格位置与姿态
        unitMeshGroup.children.forEach(mesh => {
            const uId = mesh.userData.unitId;
            const u = engine.units.find(item => item.id === uId);
            if (u) {
                // 位置
                mesh.position.set(u.pos.x, u.pos.z !== undefined ? u.pos.z : 0.025, u.pos.y || 0);

                // 旋转姿态
                if (engine.activeScenario === 'single' || engine.activeScenario === 'realistic') {
                    mesh.rotation.set(0, 0, -u.pitch);
                } else if (engine.activeScenario === 'dual') {
                    if (u.id === 0) {
                        mesh.rotation.set(0, 0, -u.pitch);
                    } else if (u.id === 1) {
                        mesh.rotation.set(0, 0, -u.relAngle);
                    }
                } else if (engine.activeScenario === 'swarm') {
                    if (u.heading !== undefined) {
                        mesh.rotation.set(0, -u.heading, 0);
                    }
                }

                // 动量轮自转动效
                const rotor = mesh.getObjectByName('rotor');
                if (rotor) {
                    const vel = u.flywheelVel || 50;
                    rotor.rotation.z += vel * 0.001;
                }

                // 施加外力箭头指示
                const arrow = mesh.getObjectByName('forceArrow');
                if (arrow && u.extForce) {
                    const fMag = Math.hypot(u.extForce.x, u.extForce.y, u.extForce.z || 0);
                    if (fMag > 0.05 || (u.forceTimer && u.forceTimer > 0)) {
                        arrow.visible = true;
                        const dir = new THREE.Vector3(u.extForce.x, u.extForce.z || 0, u.extForce.y);
                        if (dir.lengthSq() > 1e-4) arrow.setDirection(dir.normalize());
                        arrow.setLength(Math.max(0.04, Math.min(0.14, Math.max(fMag, 1.2) * 0.025)));
                    } else {
                        arrow.visible = false;
                    }
                    if (u.forceTimer && u.forceTimer > 0) {
                        u.forceTimer -= 0.016;
                    }
                }
            }
        });

        // 刷新 HUD 文本
        const t = engine.telemetry;
        if (t) {
            hudTime.innerText = t.time + ' s';
            hudState.innerText = t.state || (t.mode || 'NORMAL');

            if (t.scenario === 'single' || t.scenario === 'realistic') {
                hudAttitude.innerText = t.pitchDeg + '°';
                hudMetric.innerText = t.scenario === 'realistic' ? ('Slip: ' + (t.slipDistMm || '0.0') + 'mm') : ('CCUI: ' + t.ccui);
            } else if (t.scenario === 'dual') {
                hudAttitude.innerText = t.relAngleDeg + '°';
                hudMetric.innerText = 'Lock: ' + t.interfaceForceN + 'N';
            } else if (t.scenario === 'multi') {
                hudAttitude.innerText = (parseFloat(t.comX) * 100).toFixed(1) + 'cm';
                hudMetric.innerText = 'Max: ' + t.maxStressN + 'N';
            } else if (t.scenario === 'swarm') {
                hudAttitude.innerText = 'Phi: ' + t.polarization;
                hudMetric.innerText = 'RMSE: ' + (parseFloat(t.formationRmseM) * 1000).toFixed(0) + 'mm';
                
                const elHsVs = document.getElementById('val-hs-vs-pulse');
                if (elHsVs && t.hsVsPulse) elHsVs.innerText = t.hsVsPulse;
                const elGf = document.getElementById('val-gf-alert');
                if (elGf && t.giantFiberAlerts !== undefined) elGf.innerText = 'BURST (' + t.giantFiberAlerts + ')';
                const elDnp03 = document.getElementById('val-dnp03-status');
                if (elDnp03 && t.dnp03Alerts !== undefined) elDnp03.innerText = 'SACCADE (' + t.dnp03Alerts + ')';
                const elHaltere = document.getElementById('val-haltere-status');
                if (elHaltere && t.haltereStatus) elHaltere.innerText = t.haltereStatus;
                const elSafetyGov = document.getElementById('val-safety-gov');
                if (elSafetyGov && t.safetyGovStatus) elSafetyGov.innerText = t.safetyGovStatus;
                const elDcba = document.getElementById('val-dcba-converged');
                if (elDcba && t.dcbaConverged) elDcba.innerText = t.dcbaConverged;
                const elMcu = document.getElementById('val-mcu-timing');
                if (elMcu && t.mcuTimingUs) elMcu.innerText = t.mcuTimingUs;
            }

            // 更新高保真物理指标 (打滑、电压、温度)
            if (hudSlip) {
                if (t.isSlipping) {
                    hudSlip.innerText = 'SLIP! ' + (t.slipDistMm || '0.0') + 'mm';
                    hudSlip.className = 'hud-value orange';
                } else {
                    hudSlip.innerText = (t.hasEverSlipped ? 'SLIPPED ' : 'LOCKED ') + (t.slipDistMm || '0.0') + 'mm';
                    hudSlip.className = t.hasEverSlipped ? 'hud-value orange' : 'hud-value green';
                }
            }
            if (hudVoltage) {
                hudVoltage.innerText = (t.batVoltage !== undefined ? t.batVoltage : '4.20') + ' V';
            }
            if (hudTemp) {
                hudTemp.innerText = (t.temperatureC !== undefined ? t.temperatureC : '25.0') + ' °C';
            }

            // 更新遥测折线图
            updateCharts(t);
        }

        controls.update();
        renderer.render(scene, camera);
    }

    function onWindowResize() {
        const w = canvas.parentElement.clientWidth;
        const h = canvas.parentElement.clientHeight;
        camera.aspect = w / h;
        camera.updateProjectionMatrix();
        renderer.setSize(w, h);
    }

    window.addEventListener('resize', onWindowResize);
    requestAnimationFrame(animate);

    console.log('[microUnit] 网页 3D 物理仿真控制平台启动成功');
})();

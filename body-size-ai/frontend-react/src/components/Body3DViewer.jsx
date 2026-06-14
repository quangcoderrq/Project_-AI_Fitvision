import React, { useEffect, useRef, useState } from 'react';
import { User, X } from 'lucide-react';

export default function Body3DViewer({ measurements, gender, isOpen, onClose }) {
    const canvasRef = useRef(null);
    const viewerInstance = useRef(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (!isOpen || !canvasRef.current || !measurements) return;

        let active = true;

        const loadScript = (src) => {
            return new Promise((resolve, reject) => {
                const script = document.createElement('script');
                script.src = src;
                script.onload = resolve;
                script.onerror = reject;
                document.head.appendChild(script);
            });
        };

        const initThree = async () => {
            setLoading(true);
            try {
                if (typeof window.THREE === 'undefined') {
                    await loadScript('https://cdnjs.cloudflare.com/ajax/libs/three.js/0.147.0/three.min.js');
                    await loadScript('https://cdn.jsdelivr.net/npm/three@0.147.0/examples/js/loaders/GLTFLoader.js');
                    try {
                        await loadScript('https://cdn.jsdelivr.net/npm/three@0.147.0/examples/js/environments/RoomEnvironment.js');
                    } catch (e) {
                        console.warn('Room Environment load failed, using fallback lighting');
                    }
                }

                if (!active) return;

                const THREE = window.THREE;
                const GLTFLoader = window.THREE.GLTFLoader;
                const RoomEnvironment = window.THREE.RoomEnvironment;

                const canvas = canvasRef.current;
                const width = canvas.width;
                const height = canvas.height;

                const scene = new THREE.Scene();
                scene.background = new THREE.Color(0x0f172a); // match dark mode background

                const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100);
                camera.position.set(0, 0, 5.5);

                const renderer = new THREE.WebGLRenderer({
                    canvas: canvas,
                    antialias: true,
                    alpha: false
                });
                renderer.setSize(width, height);
                renderer.setPixelRatio(window.devicePixelRatio || 1);
                renderer.toneMapping = THREE.ACESFilmicToneMapping;
                renderer.toneMappingExposure = 1.0;
                renderer.shadowMap.enabled = true;
                renderer.shadowMap.type = THREE.PCFSoftShadowMap;

                if (RoomEnvironment) {
                    const pmremGenerator = new THREE.PMREMGenerator(renderer);
                    scene.environment = pmremGenerator.fromScene(new RoomEnvironment(), 0.04).texture;
                }

                const mainLight = new THREE.DirectionalLight(0xffffff, 2.5);
                mainLight.position.set(2, 5, 4);
                mainLight.castShadow = true;
                scene.add(mainLight);

                const fillLight = new THREE.DirectionalLight(0xa29bfe, 1.0);
                fillLight.position.set(-5, 3, 5);
                scene.add(fillLight);

                const backLight = new THREE.DirectionalLight(0x00cec9, 2.0);
                backLight.position.set(0, 4, -5);
                scene.add(backLight);

                const floorGeom = new THREE.PlaneGeometry(10, 10);
                const floorMat = new THREE.MeshStandardMaterial({
                    color: 0x0f172a,
                    roughness: 1.0,
                    metalness: 0.0
                });
                const floor = new THREE.Mesh(floorGeom, floorMat);
                floor.rotation.x = -Math.PI / 2;
                floor.position.y = -1.5;
                floor.receiveShadow = true;
                scene.add(floor);

                const bodyGroup = new THREE.Group();
                scene.add(bodyGroup);

                // Morph skin material
                const skinMaterial = new THREE.MeshPhysicalMaterial({
                    color: 0xdfd3c3,
                    roughness: 0.45,
                    metalness: 0.05,
                    transmission: 0.1,
                    thickness: 0.5,
                    envMapIntensity: 1.0
                });

                // Standard fallbacks (procedural capsules)
                const scale = 3.0 / (measurements.height_cm || 170);
                const chestRadius = ((measurements.chest || 90) / (2 * Math.PI)) * scale;
                const waistRadius = ((measurements.waist || 75) / (2 * Math.PI)) * scale;
                const hipRadius = ((measurements.hip || 95) / (2 * Math.PI)) * scale;
                const shoulderW = (measurements.shoulder_width_cm || 42) * scale * 0.5;
                const neckRadius = ((measurements.neck_circumference || 36) / (2 * Math.PI)) * scale;
                const backLen = (measurements.back_length || 45) * scale;
                const isMale = gender === 'male';

                const torsoPoints = [];
                const torsoHeight = backLen;
                const profiles = [
                    { y: torsoHeight + neckRadius * 0.3, r: neckRadius * 1.3 },
                    { y: torsoHeight * 0.85, r: chestRadius * (isMale ? 0.95 : 0.85) },
                    { y: torsoHeight * 0.45, r: waistRadius * (isMale ? 0.95 : 0.9) },
                    { y: torsoHeight * 0.15, r: hipRadius * (isMale ? 0.95 : 1.0) },
                    { y: -torsoHeight * 0.1, r: hipRadius * 0.85 }
                ];

                const spline = new THREE.SplineCurve(profiles.map(p => new THREE.Vector2(p.r, p.y)));
                for (let i = 0; i <= 32; i++) {
                    torsoPoints.push(spline.getPoint(i / 32));
                }

                const torsoGeom = new THREE.LatheGeometry(torsoPoints, 48);
                const torso = new THREE.Mesh(torsoGeom, skinMaterial);
                torso.scale.set(1 / 0.84, 1, 0.65 / 0.84);
                torso.castShadow = true;
                torso.receiveShadow = true;

                const createBone = (radius, boneLen, parent) => {
                    const capLen = Math.max(0.01, boneLen - radius * 2);
                    const geom = new THREE.CapsuleGeometry(radius, capLen, 16, 32);
                    const mesh = new THREE.Mesh(geom, skinMaterial);
                    mesh.castShadow = true;
                    mesh.receiveShadow = true;
                    mesh.position.y = -boneLen / 2;
                    parent.add(mesh);
                    return mesh;
                };

                const neckLen = 0.12;
                const armCirc = ((measurements.arm_circumference || 28) / (2 * Math.PI)) * scale;
                const thighCirc = ((measurements.thigh_circumference || 52) / (2 * Math.PI)) * scale;
                const armLength = (measurements.height_cm || 170) * scale * 0.44;
                const upperArmLen = armLength * 0.48;
                const forearmLen = armLength * 0.52;
                const inseamLen = (measurements.inseam || 75) * scale;
                const legSpacing = hipRadius * (1 / 0.84) * 0.42;
                const thighLen = inseamLen * 0.52;
                const calfLen = inseamLen * 0.48;

                const neckGroup = new THREE.Group();
                neckGroup.position.y = torsoHeight + neckRadius * 0.3;
                torso.add(neckGroup);
                createBone(neckRadius * 0.95, neckLen, neckGroup);

                const headGeom = new THREE.CapsuleGeometry(neckRadius * 1.6, neckRadius * 1.0, 16, 32);
                const head = new THREE.Mesh(headGeom, skinMaterial);
                head.castShadow = true;
                head.position.y = neckLen / 2 + neckRadius * 1.8;
                neckGroup.add(head);

                [-1, 1].forEach(side => {
                    const rArmGroup = new THREE.Group();
                    rArmGroup.position.set(side * shoulderW * 0.95, torsoHeight * 0.82, 0);
                    rArmGroup.rotation.z = side * (isMale ? 0.15 : 0.12);
                    torso.add(rArmGroup);
                    createBone(armCirc * 0.8, upperArmLen, rArmGroup);

                    const rForearmGroup = new THREE.Group();
                    rForearmGroup.position.set(0, -upperArmLen, 0);
                    rForearmGroup.rotation.z = side * 0.05;
                    rArmGroup.add(rForearmGroup);
                    createBone(armCirc * 0.65, forearmLen, rForearmGroup);
                });

                [-1, 1].forEach(side => {
                    const rLegGroup = new THREE.Group();
                    rLegGroup.position.set(side * legSpacing, -torsoHeight * 0.05, 0);
                    rLegGroup.rotation.z = side * -0.04;
                    torso.add(rLegGroup);
                    createBone(thighCirc * 0.75, thighLen, rLegGroup);

                    const rCalfGroup = new THREE.Group();
                    rCalfGroup.position.set(0, -thighLen, 0);
                    rLegGroup.add(rCalfGroup);
                    createBone(thighCirc * 0.55, calfLen, rCalfGroup);
                });

                bodyGroup.add(torso);
                const box = new THREE.Box3().setFromObject(bodyGroup);
                const center = box.getCenter(new THREE.Vector3());
                bodyGroup.position.y -= center.y;

                let rotationY = 0;
                let isDragging = false;
                let previousMousePosition = { x: 0, y: 0 };

                const handleStart = (clientX) => {
                    isDragging = true;
                    previousMousePosition.x = clientX;
                };

                const handleMove = (clientX) => {
                    if (!isDragging) return;
                    const deltaX = clientX - previousMousePosition.x;
                    rotationY += deltaX * 0.01;
                    previousMousePosition.x = clientX;
                };

                canvas.addEventListener('mousedown', (e) => handleStart(e.clientX));
                canvas.addEventListener('mousemove', (e) => handleMove(e.clientX));
                window.addEventListener('mouseup', () => isDragging = false);

                canvas.addEventListener('touchstart', (e) => {
                    if (e.touches.length > 0) handleStart(e.touches[0].clientX);
                });
                canvas.addEventListener('touchmove', (e) => {
                    if (e.touches.length > 0) handleMove(e.touches[0].clientX);
                });
                window.addEventListener('touchend', () => isDragging = false);

                const animate = () => {
                    if (!active) return;
                    requestAnimationFrame(animate);
                    if (!isDragging) {
                        rotationY += 0.005;
                    }
                    bodyGroup.rotation.y = rotationY;
                    renderer.render(scene, camera);
                };

                animate();
                setLoading(false);

                viewerInstance.current = {
                    destroy: () => {
                        active = false;
                        renderer.dispose();
                    }
                };

            } catch (err) {
                console.error(err);
                setLoading(false);
            }
        };

        initThree();

        return () => {
            active = false;
            if (viewerInstance.current) {
                viewerInstance.current.destroy();
            }
        };
    }, [isOpen, measurements, gender]);

    if (!isOpen) return null;

    return (
        <div style={{
            position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
            background: 'rgba(15, 23, 42, 0.95)',
            display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
            zIndex: 1100, padding: '1rem'
        }}>
            <div className="glass-panel" style={{ position: 'relative', maxWidth: '450px', width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <button 
                    onClick={onClose}
                    style={{
                        position: 'absolute', top: '15px', right: '15px',
                        background: 'transparent', border: 'none', color: 'var(--text-primary)',
                        cursor: 'pointer'
                    }}
                >
                    <X size={24} />
                </button>

                <h3 style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <User size={20} color="var(--primary-color)" /> Mô hình 3D cơ thể
                </h3>

                <div style={{ position: 'relative', width: '350px', height: '450px', background: '#090d16', borderRadius: 'var(--card-radius)', overflow: 'hidden' }}>
                    {loading && (
                        <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', color: 'var(--primary-color)' }}>
                            Đang tải mô hình...
                        </div>
                    )}
                    <canvas ref={canvasRef} width="350" height="450" style={{ cursor: 'grab' }} />
                </div>
                
                <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '1rem' }}>
                    Kéo chuột hoặc vuốt để xoay mô hình 3D
                </p>
            </div>
        </div>
    );
}

import React, { useRef, useEffect } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

interface PendulumVisualizerProps {
  armAngle: number;         // Radians
  pendulumAngle: number;    // Radians
  width?: number;
  height?: number;
  onShapeModelLoad?: (model: THREE.Object3D) => void;
}

interface PendulumState {
  armAngle: number;
  pendulumAngle: number;
}

export const PendulumVisualizer3D: React.FC<PendulumVisualizerProps> = ({
  armAngle,
  pendulumAngle,
  width = 600,
  height = 400,
  onShapeModelLoad
}) => {
  const mountRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<THREE.Scene>();
  const rendererRef = useRef<THREE.WebGLRenderer>();
  const armRef = useRef<THREE.Group>();
  const pendulumRef = useRef<THREE.Group>();
  const animationRef = useRef<number>();

  // Initialize Three.js scene
  useEffect(() => {
    if (!mountRef.current) return;

    // Scene setup
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x1a1a2e);
    sceneRef.current = scene;

    // Camera setup
    const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
    camera.position.set(1, 1, 1);
    camera.lookAt(0, 0, 0);

    // Renderer setup
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    rendererRef.current = renderer;

    // Lighting
    const ambientLight = new THREE.AmbientLight(0x404040, 0.4);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(2, 2, 2);
    directionalLight.castShadow = true;
    directionalLight.shadow.mapSize.width = 2048;
    directionalLight.shadow.mapSize.height = 2048;
    scene.add(directionalLight);

    // Ground plane
    const groundGeometry = new THREE.PlaneGeometry(2, 2);
    const groundMaterial = new THREE.MeshLambertMaterial({ 
      color: 0x333333,
      transparent: true,
      opacity: 0.3
    });
    const ground = new THREE.Mesh(groundGeometry, groundMaterial);
    ground.rotation.x = -Math.PI / 2;
    ground.position.y = -0.5;
    ground.receiveShadow = true;
    scene.add(ground);

    // Create pendulum components
    createPendulumModel(scene);

    // Controls
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;

    // Mount to DOM
    mountRef.current.appendChild(renderer.domElement);

    // Animation loop
    const animate = () => {
      animationRef.current = requestAnimationFrame(animate);
      
      controls.update();
      
      renderer.render(scene, camera);
    };
    animate();

    // Cleanup
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
      if (mountRef.current && renderer.domElement) {
        mountRef.current.removeChild(renderer.domElement);
      }
      renderer.dispose();
    };
  }, [width, height]);

  // Create the pendulum 3D model
  const createPendulumModel = (scene: THREE.Scene) => {
    // Base platform
    const baseGeometry = new THREE.CylinderGeometry(0.08, 0.08, 0.03, 16);
    const baseMaterial = new THREE.MeshPhongMaterial({ color: 0x666666 });
    const base = new THREE.Mesh(baseGeometry, baseMaterial);
    base.position.y = 0.015;
    base.castShadow = true;
    scene.add(base);

    // Arm group (rotates around Y-axis)
    const armGroup = new THREE.Group();
    armRef.current = armGroup;
    scene.add(armGroup);

    // Arm rod
    const armGeometry = new THREE.CylinderGeometry(0.008, 0.008, 0.3, 8);
    const armMaterial = new THREE.MeshPhongMaterial({ color: 0xff4444 });
    const arm = new THREE.Mesh(armGeometry, armMaterial);
    arm.rotation.z = Math.PI / 2; // Make horizontal
    arm.position.x = 0.15; // Half length offset
    arm.position.y = 0.05;
    arm.castShadow = true;
    armGroup.add(arm);

    // Motor housing
    const motorGeometry = new THREE.BoxGeometry(0.06, 0.06, 0.04);
    const motorMaterial = new THREE.MeshPhongMaterial({ color: 0x444444 });
    const motor = new THREE.Mesh(motorGeometry, motorMaterial);
    motor.position.y = 0.05;
    motor.castShadow = true;
    armGroup.add(motor);

    // Pendulum group (rotates around X-axis at end of arm)
    const pendulumGroup = new THREE.Group();
    pendulumGroup.position.set(0.3, 0.05, 0); // At end of arm
    pendulumRef.current = pendulumGroup;
    armGroup.add(pendulumGroup);

    // Pendulum rod
    const pendulumGeometry = new THREE.CylinderGeometry(0.005, 0.005, 0.4, 8);
    const pendulumMaterial = new THREE.MeshPhongMaterial({ color: 0x44ff44 });
    const pendulumRod = new THREE.Mesh(pendulumGeometry, pendulumMaterial);
    pendulumRod.position.y = -0.2; // Hang down
    pendulumRod.castShadow = true;
    pendulumGroup.add(pendulumRod);

    // Pendulum weight
    const weightGeometry = new THREE.SphereGeometry(0.025, 16, 16);
    const weightMaterial = new THREE.MeshPhongMaterial({ color: 0x4444ff });
    const weight = new THREE.Mesh(weightGeometry, weightMaterial);
    weight.position.y = -0.4; // At end of rod
    weight.castShadow = true;
    pendulumGroup.add(weight);

    // Encoder disc
    const encoderGeometry = new THREE.CylinderGeometry(0.02, 0.02, 0.005, 16);
    const encoderMaterial = new THREE.MeshPhongMaterial({ 
      color: 0xffff44,
      transparent: true,
      opacity: 0.8
    });
    const encoder = new THREE.Mesh(encoderGeometry, encoderMaterial);
    encoder.position.set(0.3, 0.08, 0);
    encoder.castShadow = true;
    armGroup.add(encoder);
  };

  // Update pendulum pose when angles change
  useEffect(() => {
    if (armRef.current && pendulumRef.current) {
      // Update arm rotation (around Y-axis)
      armRef.current.rotation.y = armAngle;
      
      // Update pendulum rotation (around X-axis, relative to arm)
      pendulumRef.current.rotation.x = pendulumAngle;
    }
  }, [armAngle, pendulumAngle]);

  return (
    <div className="pendulum-visualizer">
      <div className="visualizer-header">
        <h3>🎯 3D Pendulum Visualization</h3>
        <div className="pose-info">
          <span>Arm: {(armAngle * 180 / Math.PI).toFixed(1)}°</span>
          <span>Pendulum: {(pendulumAngle * 180 / Math.PI).toFixed(1)}°</span>
        </div>
      </div>
      <div 
        ref={mountRef} 
        style={{ 
          width: `${width}px`, 
          height: `${height}px`,
          border: '2px solid #333',
          borderRadius: '8px',
          overflow: 'hidden'
        }} 
      />
      <div className="model-controls">
        <FileUploadSection onModelLoad={onShapeModelLoad} />
      </div>
    </div>
  );
};

// Component for uploading OnShape models
interface FileUploadSectionProps {
  onModelLoad?: (model: THREE.Object3D) => void;
}

const FileUploadSection: React.FC<FileUploadSectionProps> = ({ onModelLoad }) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    const file = files[0];
    const fileExtension = file.name.split('.').pop()?.toLowerCase();

    try {
      if (fileExtension === 'stl') {
        await loadSTLModel(file, onModelLoad);
      } else if (fileExtension === 'obj') {
        await loadOBJModel(file, onModelLoad);
      } else if (fileExtension === 'gltf' || fileExtension === 'glb') {
        await loadGLTFModel(file, onModelLoad);
      } else {
        alert('Supported formats: STL, OBJ, GLTF, GLB');
      }
    } catch (error) {
      console.error('Model loading failed:', error);
      alert('Failed to load model. Please check the file format.');
    }
  };

  return (
    <div className="file-upload-section">
      <h4>📂 Upload OnShape Model</h4>
      <p>Supported formats: STL, OBJ, GLTF, GLB</p>
      <input
        ref={fileInputRef}
        type="file"
        accept=".stl,.obj,.gltf,.glb"
        onChange={handleFileUpload}
        style={{ display: 'none' }}
      />
      <button 
        onClick={() => fileInputRef.current?.click()}
        className="upload-button"
      >
        🎯 Choose OnShape Model File
      </button>
      <div className="upload-instructions">
        <h5>📋 How to Export from OnShape:</h5>
        <ol>
          <li>Right-click your part in OnShape</li>
          <li>Select "Export"</li>
          <li>Choose format: 
            <ul>
              <li><strong>STL</strong> - Best for simple geometry</li>
              <li><strong>OBJ</strong> - Good with materials</li>
              <li><strong>GLTF</strong> - Best for web (recommended)</li>
            </ul>
          </li>
          <li>Download and upload here</li>
        </ol>
      </div>
    </div>
  );
};

// Model loading functions
async function loadSTLModel(file: File, onLoad?: (model: THREE.Object3D) => void) {
  const { STLLoader } = await import('three/examples/jsm/loaders/STLLoader.js');
  
  const loader = new STLLoader();
  const fileBuffer = await file.arrayBuffer();
  
  const geometry = loader.parse(fileBuffer);
  const material = new THREE.MeshPhongMaterial({ color: 0x888888 });
  const mesh = new THREE.Mesh(geometry, material);
  
  // Scale and position appropriately
  mesh.scale.setScalar(0.001); // Adjust as needed
  mesh.position.set(0, 0, 0);
  
  onLoad?.(mesh);
  console.log('✅ STL model loaded successfully');
}

async function loadOBJModel(file: File, onLoad?: (model: THREE.Object3D) => void) {
  const { OBJLoader } = await import('three/examples/jsm/loaders/OBJLoader.js');
  
  const loader = new OBJLoader();
  const fileText = await file.text();
  
  const object = loader.parse(fileText);
  object.scale.setScalar(0.001);
  
  onLoad?.(object);
  console.log('✅ OBJ model loaded successfully');
}

async function loadGLTFModel(file: File, onLoad?: (model: THREE.Object3D) => void) {
  const { GLTFLoader } = await import('three/examples/jsm/loaders/GLTFLoader.js');
  
  const loader = new GLTFLoader();
  const fileBuffer = await file.arrayBuffer();
  
  return new Promise((resolve, reject) => {
    loader.parse(fileBuffer, '', (gltf) => {
      const model = gltf.scene;
      model.scale.setScalar(0.001);
      
      onLoad?.(model);
      console.log('✅ GLTF model loaded successfully');
      resolve(model);
    }, reject);
  });
}

export default PendulumVisualizer3D;

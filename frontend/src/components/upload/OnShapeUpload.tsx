import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import './OnShapeUpload.css';

interface UploadedFile {
  filename: string;
  originalFilename: string;
  size: number;
  type: string;
  format: string;
  path: string;
}

interface OnShapeUploadProps {
  onUploadComplete: (files: UploadedFile[]) => void;
  onUrdfGenerated: (urdfPath: string) => void;
}

export const OnShapeUpload: React.FC<OnShapeUploadProps> = ({
  onUploadComplete,
  onUrdfGenerated
}) => {
  const [uploading, setUploading] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [generatingUrdf, setGeneratingUrdf] = useState(false);
  const [urdfGenerated, setUrdfGenerated] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    setUploading(true);
    setUploadProgress(0);
    
    const newUploadedFiles: UploadedFile[] = [];
    
    for (let i = 0; i < acceptedFiles.length; i++) {
      const file = acceptedFiles[i];
      
      try {
        const formData = new FormData();
        formData.append('file', file);
        
        // Determine model type from filename
        const filename = file.name.toLowerCase();
        let modelType = 'complete';
        if (filename.includes('base')) modelType = 'base';
        else if (filename.includes('arm') || filename.includes('lever')) modelType = 'arm';
        else if (filename.includes('pendulum') || filename.includes('rod')) modelType = 'pendulum';
        
        formData.append('model_type', modelType);

        const response = await fetch('http://localhost:8003/onshape/upload-model', {
          method: 'POST',
          body: formData,
        });

        if (response.ok) {
          const result = await response.json();
          newUploadedFiles.push(result);
        } else {
          console.error(`Failed to upload ${file.name}`);
        }
        
        setUploadProgress(((i + 1) / acceptedFiles.length) * 100);
        
      } catch (error) {
        console.error(`Error uploading ${file.name}:`, error);
      }
    }
    
    setUploadedFiles(prev => [...prev, ...newUploadedFiles]);
    setUploading(false);
    setUploadProgress(100);
    
    if (newUploadedFiles.length > 0) {
      onUploadComplete(newUploadedFiles);
    }
  }, [onUploadComplete]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'model/gltf+json': ['.gltf'],
      'model/gltf-binary': ['.glb'],
      'model/stl': ['.stl'],
      'model/obj': ['.obj'],
      'application/xml': ['.urdf']
    },
    multiple: true
  });

  const generateUrdf = async () => {
    setGeneratingUrdf(true);
    
    try {
      const response = await fetch('http://localhost:8003/onshape/generate-urdf', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const result = await response.json();
        setUrdfGenerated(true);
        onUrdfGenerated(result.urdf_path);
      } else {
        console.error('Failed to generate URDF');
      }
    } catch (error) {
      console.error('Error generating URDF:', error);
    } finally {
      setGeneratingUrdf(false);
    }
  };

  const clearFiles = async () => {
    try {
      await fetch('http://localhost:8003/onshape/clear-uploads', {
        method: 'DELETE',
      });
      setUploadedFiles([]);
      setUrdfGenerated(false);
    } catch (error) {
      console.error('Error clearing files:', error);
    }
  };

  const downloadUrdf = async () => {
    try {
      const response = await fetch('http://localhost:8003/onshape/download-urdf');
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = 'rotary_pendulum.urdf';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
      }
    } catch (error) {
      console.error('Error downloading URDF:', error);
    }
  };

  return (
    <div className="onshape-upload">
      <div className="upload-header">
        <h3>🎯 OnShape Model Integration</h3>
        <p>Upload your OnShape models for physics simulation</p>
      </div>

      {/* Drop Zone */}
      <div
        {...getRootProps()}
        className={`dropzone ${isDragActive ? 'active' : ''} ${uploading ? 'uploading' : ''}`}
      >
        <input {...getInputProps()} />
        
        {uploading ? (
          <div className="upload-progress">
            <div className="spinner"></div>
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${uploadProgress}%` }}
              ></div>
            </div>
            <p>Uploading... {Math.round(uploadProgress)}%</p>
          </div>
        ) : (
          <div className="drop-content">
            <div className="upload-icon">📁</div>
            <div className="upload-text">
              <strong>Drop OnShape files here or click to browse</strong>
              <p>Supported: GLTF, GLB, STL, OBJ</p>
              <small>
                💡 Tip: Name files with "base", "arm", or "pendulum" for automatic part recognition
              </small>
            </div>
          </div>
        )}
      </div>

      {/* File List */}
      {uploadedFiles.length > 0 && (
        <div className="uploaded-files">
          <h4>📋 Uploaded Files ({uploadedFiles.length})</h4>
          <div className="file-list">
            {uploadedFiles.map((file, index) => (
              <div key={index} className="file-item">
                <div className="file-info">
                  <div className="file-name">{file.originalFilename}</div>
                  <div className="file-details">
                    <span className="file-type">{file.type}</span>
                    <span className="file-format">{file.format}</span>
                    <span className="file-size">{(file.size / 1024).toFixed(1)} KB</span>
                  </div>
                </div>
                <div className="file-status">✅</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Actions */}
      {uploadedFiles.length > 0 && (
        <div className="upload-actions">
          <button
            onClick={generateUrdf}
            disabled={generatingUrdf || urdfGenerated}
            className="generate-btn"
          >
            {generatingUrdf ? (
              <>
                <div className="btn-spinner"></div>
                Generating URDF...
              </>
            ) : urdfGenerated ? (
              '✅ URDF Generated'
            ) : (
              '🔧 Generate URDF for Simulation'
            )}
          </button>

          {urdfGenerated && (
            <button onClick={downloadUrdf} className="download-btn">
              📥 Download URDF
            </button>
          )}

          <button onClick={clearFiles} className="clear-btn">
            🗑️ Clear All Files
          </button>
        </div>
      )}

      {/* Instructions */}
      <div className="upload-instructions">
        <h4>📖 How to Export from OnShape:</h4>
        <ol>
          <li>
            <strong>For Complete Assembly (Recommended):</strong>
            <ul>
              <li>Right-click your assembly in OnShape</li>
              <li>Select "Export" → "GLTF"</li>
              <li>Enable "Include Appearances" for materials</li>
              <li>Upload the .gltf file here</li>
            </ul>
          </li>
          <li>
            <strong>For Individual Parts:</strong>
            <ul>
              <li>Export each part as STL</li>
              <li>Name files: "base.stl", "arm.stl", "pendulum.stl"</li>
              <li>Upload all STL files together</li>
            </ul>
          </li>
          <li>
            <strong>After Upload:</strong>
            <ul>
              <li>Click "Generate URDF" to create physics model</li>
              <li>Your OnShape model will replace the default visualization</li>
              <li>Start simulation to see your design in action!</li>
            </ul>
          </li>
        </ol>
      </div>

      {/* Format Comparison */}
      <div className="format-guide">
        <h4>📊 Format Comparison:</h4>
        <div className="format-grid">
          <div className="format-item">
            <strong>GLTF/GLB</strong>
            <div className="format-pros">✅ Materials & Colors</div>
            <div className="format-pros">✅ Best for Web</div>
            <div className="format-pros">✅ Single File</div>
          </div>
          <div className="format-item">
            <strong>STL</strong>
            <div className="format-pros">✅ Best for Physics</div>
            <div className="format-pros">✅ Most Compatible</div>
            <div className="format-cons">❌ No Materials</div>
          </div>
          <div className="format-item">
            <strong>OBJ</strong>
            <div className="format-pros">✅ Good Compromise</div>
            <div className="format-pros">✅ Materials Support</div>
            <div className="format-cons">❌ Multiple Files</div>
          </div>
        </div>
      </div>
    </div>
  );
};

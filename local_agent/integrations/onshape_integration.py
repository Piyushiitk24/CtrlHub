"""
OnShape API Integration for CtrlHub
Direct model fetching from OnShape workspace
"""

import requests
import base64
import json
import time
from typing import Dict, Optional, Tuple
from pathlib import Path

class OnShapeModelFetcher:
    """Fetch CAD models directly from OnShape using their REST API."""
    
    def __init__(self, access_key: str, secret_key: str):
        """Initialize with OnShape API credentials."""
        self.access_key = access_key
        self.secret_key = secret_key
        self.base_url = "https://cad.onshape.com/api"
        
    def get_auth_header(self) -> Dict[str, str]:
        """Generate authentication header for OnShape API."""
        credentials = f"{self.access_key}:{self.secret_key}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        return {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/json"
        }
    
    def list_documents(self) -> Dict:
        """List all documents in the user's OnShape account."""
        url = f"{self.base_url}/documents"
        headers = self.get_auth_header()
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    
    def get_document_workspaces(self, document_id: str) -> Dict:
        """Get workspaces for a specific document."""
        url = f"{self.base_url}/documents/{document_id}/workspaces"
        headers = self.get_auth_header()
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    
    def export_stl(self, document_id: str, workspace_id: str, element_id: str) -> bytes:
        """Export a part as STL."""
        url = f"{self.base_url}/partstudios/d/{document_id}/w/{workspace_id}/e/{element_id}/stl"
        headers = self.get_auth_header()
        
        # STL export parameters
        params = {
            "mode": "binary",  # binary STL format
            "grouping": True,  # group parts
            "scale": 1.0,      # scale factor
            "units": "millimeter"  # units
        }
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.content
    
    def export_gltf(self, document_id: str, workspace_id: str, element_id: str) -> Dict:
        """Export assembly as GLTF."""
        url = f"{self.base_url}/assemblies/d/{document_id}/w/{workspace_id}/e/{element_id}/gltf"
        headers = self.get_auth_header()
        
        # GLTF export parameters
        params = {
            "includeAppearances": True,  # Include materials
            "outputSeparateFiles": False,  # Embed everything in one file
            "units": "millimeter"
        }
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def find_pendulum_document(self, search_term: str = "pendulum") -> Optional[Tuple[str, str, str]]:
        """Find a document containing 'pendulum' in the name."""
        try:
            documents = self.list_documents()
            
            for doc in documents.get("items", []):
                if search_term.lower() in doc.get("name", "").lower():
                    doc_id = doc["id"]
                    
                    # Get workspaces
                    workspaces = self.get_document_workspaces(doc_id)
                    if workspaces.get("items"):
                        workspace_id = workspaces["items"][0]["id"]
                        
                        # For simplicity, assume first element
                        # In practice, you'd need to query elements
                        return doc_id, workspace_id, "element_id_placeholder"
            
            return None
            
        except Exception as e:
            print(f"Error finding pendulum document: {e}")
            return None
    
    async def download_pendulum_model(self, output_path: str = "pendulum_model.stl") -> bool:
        """Download the pendulum model from OnShape."""
        try:
            # Find pendulum document
            doc_info = self.find_pendulum_document()
            if not doc_info:
                print("❌ No pendulum document found in OnShape")
                return False
            
            doc_id, workspace_id, element_id = doc_info
            
            # Export as STL
            stl_data = self.export_stl(doc_id, workspace_id, element_id)
            
            # Save to file
            with open(output_path, "wb") as f:
                f.write(stl_data)
            
            print(f"✅ Pendulum model downloaded: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to download model: {e}")
            return False


# Integration with CtrlHub backend
class OnShapeIntegration:
    """Integration between OnShape and CtrlHub simulation."""
    
    def __init__(self):
        self.fetcher = None
        self.model_cache = {}
    
    def setup_credentials(self, access_key: str, secret_key: str):
        """Setup OnShape API credentials."""
        self.fetcher = OnShapeModelFetcher(access_key, secret_key)
    
    async def sync_pendulum_model(self) -> Dict[str, any]:
        """Sync the latest pendulum model from OnShape."""
        if not self.fetcher:
            return {"success": False, "error": "OnShape credentials not configured"}
        
        try:
            # Download latest model
            model_path = "temp_pendulum_model.stl"
            success = await self.fetcher.download_pendulum_model(model_path)
            
            if success:
                # Convert to format suitable for Three.js
                with open(model_path, "rb") as f:
                    model_data = f.read()
                
                # Cache the model
                self.model_cache["pendulum"] = {
                    "data": base64.b64encode(model_data).decode(),
                    "format": "stl",
                    "timestamp": time.time()
                }
                
                # Clean up temp file
                Path(model_path).unlink()
                
                return {
                    "success": True,
                    "message": "Model synced successfully",
                    "model": self.model_cache["pendulum"]
                }
            else:
                return {"success": False, "error": "Failed to download model"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}


# Usage example
if __name__ == "__main__":
    # Example usage (requires OnShape API credentials)
    print("🔧 OnShape Integration Example")
    print("=" * 50)
    
    print("1. To use this integration:")
    print("   - Get OnShape API credentials from https://dev-portal.onshape.com")
    print("   - Set access_key and secret_key")
    print("   - Call setup_credentials() and sync_pendulum_model()")
    
    print("\n2. Manual Export (Recommended for now):")
    print("   - Export your model from OnShape as GLTF/STL")
    print("   - Use the file upload in the 3D visualizer")
    print("   - CtrlHub will automatically load and display it")
    
    print("\n3. Your model will replace the default pendulum visualization")
    print("   - Real-time physics simulation continues")
    print("   - OnShape model moves based on simulation state")
    print("   - Full PID control remains functional")

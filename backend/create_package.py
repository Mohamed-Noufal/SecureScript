import zipfile
import os
from pathlib import Path

def create_zip():
    # Helper to create deployment package
    # Run this from the 'backend' directory or adjust paths
    
    script_dir = Path(__file__).parent
    base_dir = script_dir
    package_dir = base_dir / "package_linux"
    zip_path = base_dir / "backend.zip"
    
    print(f"📦 Creating Zip Package: {zip_path}")
    print(f"   Source Dependencies: {package_dir}")
    
    if not package_dir.exists():
        print("❌ Error: package_linux directory not found!")
        print("   Please run the Docker build step first.")
        return False
        
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Add all files from package_linux (dependencies)
            count = 0
            for root, _, files in os.walk(package_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(package_dir)
                    zf.write(file_path, arcname)
                    count += 1
            print(f"   Added {count} dependency files")
            
            # Add source files
            source_files = ["server.py", "context.py"]
            for src in source_files:
                src_path = base_dir / src
                if src_path.exists():
                    zf.write(src_path, src)
                    print(f"   Added source: {src}")
                else:
                    print(f"⚠️  Warning: Source file {src} not found!")

        print("✅ Zip creation complete.")
        
        # Verification
        with zipfile.ZipFile(zip_path, 'r') as zf:
            files = zf.namelist()
            if any("pydantic/" in f for f in files):
                print("✅ Verified: pydantic is present")
            else:
                print("❌ Error: pydantic missing from zip!")
                
        return True
        
    except Exception as e:
        print(f"❌ Failed to create zip: {e}")
        return False

if __name__ == "__main__":
    create_zip()

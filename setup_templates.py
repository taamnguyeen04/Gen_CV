import os
import shutil

def setup_template_structure():
    """Tạo cấu trúc thư mục templates đúng format"""
    
    # Tạo thư mục templates
    templates_dir = "templates"
    os.makedirs(templates_dir, exist_ok=True)
    
    # Danh sách templates
    templates = {
        "minimal": {
            "source_file": "cv_template_minimal.html",
            "colors": {"primary": "#2c3e50", "secondary": "#34495e"},
            "fonts": {"heading": "Georgia", "body": "Times New Roman"}
        },
        "modern": {
            "source_file": "cv_template_modern.html", 
            "colors": {"primary": "#667eea", "secondary": "#764ba2"},
            "fonts": {"heading": "Inter", "body": "Source Sans Pro"}
        },
        "tech": {
            "source_file": "cv_template_tech.html",
            "colors": {"primary": "#00d9ff", "secondary": "#ff006e"},
            "fonts": {"heading": "JetBrains Mono", "body": "Inter"}
        }
    }
    
    for template_name, config in templates.items():
        # Tạo thư mục cho template
        template_dir = os.path.join(templates_dir, template_name)
        os.makedirs(template_dir, exist_ok=True)
        
        # Copy template file
        source_path = config["source_file"]
        dest_path = os.path.join(template_dir, "template.html")
        
        if os.path.exists(source_path):
            shutil.copy2(source_path, dest_path)
            print(f"✅ Copied {source_path} -> {dest_path}")
        else:
            print(f"⚠️ Template file {source_path} not found")
        
        # Tạo config.yaml
        config_content = f"""template:
  name: "{template_name}"
  description: "CV template với phong cách {template_name}"
  colors:
    primary: "{config['colors']['primary']}"
    secondary: "{config['colors']['secondary']}"
  fonts:
    heading: "{config['fonts']['heading']}"
    body: "{config['fonts']['body']}"
"""
        
        config_path = os.path.join(template_dir, "config.yaml")
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(config_content)
        print(f"✅ Created config: {config_path}")
    
    # Tạo thư mục output
    os.makedirs("output", exist_ok=True)
    
    print(f"\n🎯 Template structure created successfully!")
    print(f"📁 Templates directory: {templates_dir}/")
    print(f"📁 Output directory: output/")

if __name__ == "__main__":
    setup_template_structure()

# demo_usage.py
from cv_generator import CVGenerator, sample_cv_data
import os

def create_templates_structure():
    """Tạo cấu trúc thư mục templates"""
    templates = ['modern', 'minimal', 'tech']
    
    for template in templates:
        template_dir = f"templates/{template}"
        os.makedirs(template_dir, exist_ok=True)
        
        # Tạo config file cho mỗi template
        config_content = f"""
template:
  name: "{template}"
  description: "CV template với phong cách {template}"
  colors:
    primary: "{get_template_colors(template)['primary']}"
    secondary: "{get_template_colors(template)['secondary']}"
  fonts:
    heading: "{get_template_fonts(template)['heading']}"
    body: "{get_template_fonts(template)['body']}"
"""
        
        with open(f"{template_dir}/config.yaml", 'w', encoding='utf-8') as f:
            f.write(config_content.strip())

def get_template_colors(template_name):
    colors = {
        'modern': {'primary': '#667eea', 'secondary': '#764ba2'},
        'minimal': {'primary': '#2c3e50', 'secondary': '#34495e'},
        'tech': {'primary': '#00d9ff', 'secondary': '#ff006e'}
    }
    return colors.get(template_name, colors['modern'])

def get_template_fonts(template_name):
    fonts = {
        'modern': {'heading': 'Inter', 'body': 'Source Sans Pro'},
        'minimal': {'heading': 'Georgia', 'body': 'Times New Roman'},
        'tech': {'heading': 'JetBrains Mono', 'body': 'Inter'}
    }
    return fonts.get(template_name, fonts['modern'])

def demo_cv_generation():
    """Demo tạo CV với các template khác nhau"""
    
    # Tạo cấu trúc thư mục
    create_templates_structure()
    
    # Initialize CV Generator
    cv_gen = CVGenerator("templates")
    
    # Danh sách templates có sẵn
    templates = ['modern', 'minimal', 'tech']
    
    print("🚀 CV Generator Demo")
    print("=" * 50)
    
    # Tạo CV cho từng template
    for template in templates:
        print(f"\n📄 Generating {template.upper()} CV...")
        
        try:
            # Customize data theo template
            customized_data = customize_data_for_template(sample_cv_data, template)
            
            # Generate CV
            html_content = cv_gen.generate_cv(
                template_name=template,
                cv_data=customized_data,
                output_path=f"output/cv_{template}.html"
            )
            
            if html_content:
                print(f"✅ Successfully generated: cv_{template}.html")
                print(f"   📏 Length: {len(html_content)} characters")
            else:
                print(f"❌ Failed to generate {template} CV")
                
        except Exception as e:
            print(f"❌ Error generating {template} CV: {str(e)}")
    
    print(f"\n🎯 Generated CVs saved in 'output/' directory")
    print(f"📋 Available templates: {', '.join(templates)}")

def customize_data_for_template(base_data, template_name):
    """Customize dữ liệu cho từng template"""
    data = base_data.copy()
    
    if template_name == 'tech':
        # Tech template - focus on programming
        data['personal_info']['title'] = 'Full Stack Developer & Tech Enthusiast'
        data['summary'] = (
            "Code-driven developer với passion for clean architecture và cutting-edge technology. "
            "Chuyên về React ecosystem, Node.js backends, và cloud infrastructure. "
            "Luôn tìm kiếm cơ hội để optimize performance và user experience."
        )
        
    elif template_name == 'minimal':
        # Minimal template - more formal
        data['personal_info']['title'] = 'Software Engineer'
        data['summary'] = (
            "Experienced software engineer với focus vào scalable web applications và system optimization. "
            "Proven track record trong việc lead technical teams và deliver high-quality solutions "
            "cho enterprise clients."
        )
        
    elif template_name == 'modern':
        # Modern template - balanced
        data['personal_info']['title'] = 'Full Stack Developer'
        
    return data

def create_output_directory():
    """Tạo thư mục output"""
    os.makedirs("output", exist_
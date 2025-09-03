import yaml
from jinja2 import Environment, FileSystemLoader, Template
import os
from datetime import datetime
from typing import Dict, Any, List
import json

class CVGenerator:
    def __init__(self, templates_dir: str = "templates"):
        self.templates_dir = templates_dir
        self.env = Environment(loader=FileSystemLoader(templates_dir))
        
    def load_cv_data(self, data_path: str = None, data_dict: dict = None) -> Dict[Any, Any]:
        """Load CV data from YAML file or dictionary"""
        if data_dict:
            return data_dict
        elif data_path:
            with open(data_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        else:
            raise ValueError("Either data_path or data_dict must be provided")
    
    def generate_cv(self, template_name: str, cv_data: Dict[Any, Any], output_path: str = None) -> str:
        """Generate CV HTML from template and data"""
        try:
            # Load template
            template = self.env.get_template(f"{template_name}/template.html")
            
            # Load template config
            config_path = os.path.join(self.templates_dir, template_name, "config.yaml")
            template_config = {}
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    template_config = yaml.safe_load(f)
            
            # Merge data with config
            render_data = {
                'cv': cv_data,
                'config': template_config,
                'generated_date': datetime.now().strftime("%B %Y")
            }
            
            # Render template
            html_content = template.render(**render_data)
            
            # Save to file if output_path provided
            if output_path:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                print(f"CV generated successfully: {output_path}")
            
            return html_content
            
        except Exception as e:
            print(f"Error generating CV: {str(e)}")
            return ""
    
    def list_available_templates(self) -> List[str]:
        """List all available templates"""
        templates = []
        if os.path.exists(self.templates_dir):
            for item in os.listdir(self.templates_dir):
                template_path = os.path.join(self.templates_dir, item)
                if os.path.isdir(template_path) and os.path.exists(os.path.join(template_path, "template.html")):
                    templates.append(item)
        return templates

# Sample CV Data Structure
sample_cv_data = {
    "personal_info": {
        "name": "Nguyễn Văn Minh",
        "title": "Full Stack Developer",
        "email": "nguyenvanminh@email.com",
        "phone": "+84 123 456 789",
        "location": "TP. Hồ Chí Minh, Việt Nam",
        "website": "https://minhnguyen.dev",
        "linkedin": "https://linkedin.com/in/minhnguyen",
        "github": "https://github.com/minhnguyen"
    },
    "summary": "Passionate Full Stack Developer với 3+ năm kinh nghiệm phát triển ứng dụng web sử dụng React, Node.js, và Python. Có kinh nghiệm làm việc với các dự án từ startup đến enterprise, đam mê về clean code và user experience.",
    "experience": [
        {
            "title": "Senior Frontend Developer",
            "company": "TechViet Solutions",
            "location": "TP.HCM",
            "duration": "01/2023 - Present",
            "achievements": [
                "Phát triển và maintain 5+ ứng dụng React với hơn 100k users",
                "Cải thiện performance ứng dụng lên 40% thông qua code optimization",
                "Lead team 4 developers trong dự án e-commerce platform",
                "Implement CI/CD pipeline giảm deployment time từ 2h xuống 15 phút"
            ]
        },
        {
            "title": "Full Stack Developer",
            "company": "Digital Agency ABC",
            "location": "TP.HCM", 
            "duration": "06/2021 - 12/2022",
            "achievements": [
                "Xây dựng RESTful APIs phục vụ 50k+ requests/day",
                "Phát triển admin dashboard với React và Material-UI",
                "Optimize database queries giảm response time 60%",
                "Mentor 2 junior developers"
            ]
        }
    ],
    "projects": [
        {
            "name": "E-commerce Platform",
            "description": "Full-stack e-commerce platform với tính năng thanh toán online, quản lý inventory và analytics dashboard",
            "tech_stack": ["React", "Node.js", "MongoDB", "Stripe API", "Docker"],
            "github_url": "https://github.com/minhnguyen/ecommerce-platform",
            "live_url": "https://ecommerce-demo.minhnguyen.dev",
            "highlights": [
                "Xử lý 1000+ transactions/day",
                "Responsive design cho mobile và desktop",
                "Real-time inventory management"
            ]
        },
        {
            "name": "Task Management App",
            "description": "Collaborative task management tool với real-time updates và team collaboration features",
            "tech_stack": ["Vue.js", "Express.js", "PostgreSQL", "Socket.io"],
            "github_url": "https://github.com/minhnguyen/task-manager",
            "highlights": [
                "Real-time collaboration với 100+ concurrent users",
                "Drag & drop interface",
                "Integration với Slack và Google Calendar"
            ]
        }
    ],
    "skills": {
        "programming_languages": ["JavaScript", "TypeScript", "Python", "Java"],
        "frontend": ["React", "Vue.js", "Next.js", "HTML5", "CSS3", "Tailwind CSS"],
        "backend": ["Node.js", "Express.js", "Django", "Spring Boot"],
        "databases": ["MongoDB", "PostgreSQL", "MySQL", "Redis"],
        "tools": ["Git", "Docker", "AWS", "Jenkins", "Figma"]
    },
    "education": [
        {
            "degree": "Cử nhân Công nghệ Thông tin",
            "school": "Đại học Bách Khoa TP.HCM",
            "duration": "2017 - 2021",
            "gpa": "3.6/4.0"
        }
    ],
    "certifications": [
        {
            "name": "AWS Certified Developer Associate",
            "issuer": "Amazon Web Services",
            "date": "2023"
        },
        {
            "name": "Google Analytics Certified",
            "issuer": "Google",
            "date": "2022"
        }
    ]
}

# Usage Example
if __name__ == "__main__":
    # Initialize CV Generator
    cv_gen = CVGenerator("templates")
    
    # Generate CV with modern template
    html_content = cv_gen.generate_cv(
        template_name="modern",
        cv_data=sample_cv_data,
        output_path="generated_cv.html"
    )
    
    # List available templates
    templates = cv_gen.list_available_templates()
    print("Available templates:", templates)
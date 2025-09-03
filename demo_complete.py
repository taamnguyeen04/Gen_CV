import os
import json
from typing import Dict, List, Optional
from cv_generator import CVGenerator, sample_cv_data
from get_readme import analyze_repo, GITHUB_TOKEN, GOOGLE_API_KEY
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

class CVSystem:
    def __init__(self):
        self.cv_generator = CVGenerator()
        self.github_token = GITHUB_TOKEN
        self.google_api_key = GOOGLE_API_KEY
        
        # Initialize Gemini for JD optimization
        if self.google_api_key:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                temperature=0.3,
                max_tokens=2000,
                timeout=30,
                max_retries=2,
            )
        else:
            self.llm = None
            print("⚠️ Không tìm thấy Google API key. Chức năng tối ưu theo JD sẽ không khả dụng.")
    
    def create_cv_from_input(
        self, 
        personal_info: Dict,
        github_repos: List[str] = None,
        experience: List[Dict] = None,
        education: List[Dict] = None,
        skills: Dict = None,
        certifications: List[Dict] = None,
        job_description: str = None,
        template: str = "modern",
        output_path: str = None
    ) -> str:
        """
        Tạo CV từ thông tin đầu vào của người dùng
        
        Args:
            personal_info: Thông tin cá nhân (name, title, email, phone, etc.)
            github_repos: Danh sách URLs của GitHub repos
            experience: Kinh nghiệm làm việc
            education: Học vấn
            skills: Kỹ năng
            certifications: Chứng chỉ
            job_description: Mô tả công việc để tối ưu CV
            template: Template CV (minimal, modern, tech)
            output_path: Đường dẫn file output
        """
        
        # 1. Xây dựng dữ liệu CV cơ bản
        cv_data = {
            "personal_info": personal_info,
            "experience": experience or [],
            "education": education or [],
            "skills": skills or {},
            "certifications": certifications or [],
            "projects": []
        }
        
        # 2. Phân tích GitHub repos để tạo projects
        if github_repos:
            print("🔍 Đang phân tích GitHub repositories...")
            projects = self._analyze_github_repos(github_repos)
            cv_data["projects"] = projects
            
            # Cập nhật skills từ GitHub repos
            cv_data["skills"] = self._merge_skills_from_repos(cv_data["skills"], projects)
        
        # 3. Tạo summary tự động
        cv_data["summary"] = self._generate_summary(cv_data, template)
        
        # 4. Tối ưu CV theo Job Description (nếu có)
        if job_description and self.llm:
            print("🤖 Đang tối ưu CV theo Job Description...")
            cv_data = self._optimize_for_job_description(cv_data, job_description)
        
        # 5. Generate CV
        print(f"📄 Đang tạo CV với template {template}...")
        html_content = self.cv_generator.generate_cv(
            template_name=template,
            cv_data=cv_data,
            output_path=output_path
        )
        
        return html_content
    
    def _analyze_github_repos(self, repo_urls: List[str]) -> List[Dict]:
        """Phân tích GitHub repos và chuyển đổi thành định dạng projects"""
        projects = []
        
        for repo_url in repo_urls:
            try:
                print(f"  📊 Phân tích: {repo_url}")
                analysis = analyze_repo(repo_url, token=self.github_token, include_ai_description=True)
                
                # Chuyển đổi sang định dạng project cho CV
                project = {
                    "name": analysis["info"]["name"],
                    "description": analysis.get("ai_description", analysis["info"].get("description", "")),
                    "tech_stack": analysis["frameworks"][:8],  # Giới hạn số lượng tech
                    "github_url": repo_url,
                    "highlights": self._generate_project_highlights(analysis)
                }
                
                # Thêm homepage nếu có
                if analysis["info"].get("homepage"):
                    project["live_url"] = analysis["info"]["homepage"]
                
                projects.append(project)
                
            except Exception as e:
                print(f"  ❌ Lỗi khi phân tích {repo_url}: {str(e)}")
                # Thêm project cơ bản nếu không phân tích được
                repo_name = repo_url.split("/")[-1]
                projects.append({
                    "name": repo_name,
                    "description": f"Dự án {repo_name}",
                    "tech_stack": [],
                    "github_url": repo_url,
                    "highlights": []
                })
        
        return projects
    
    def _generate_project_highlights(self, analysis: Dict) -> List[str]:
        """Tạo highlights cho project từ analysis"""
        highlights = []
        
        # Thêm thông tin về ngôn ngữ chính
        if analysis["languages"].get("primary"):
            primary_lang = analysis["languages"]["primary"]
            highlights.append(f"Phát triển bằng {primary_lang}")
        
        # Thêm thông tin về stars nếu > 5
        stars = analysis["info"].get("stars", 0)
        if stars > 5:
            highlights.append(f"Nhận được {stars} stars trên GitHub")
        
        # Thêm framework chính
        if analysis["frameworks"]:
            main_frameworks = analysis["frameworks"][:3]
            highlights.append(f"Sử dụng {', '.join(main_frameworks)}")
        
        return highlights[:3]  # Giới hạn 3 highlights
    
    def _merge_skills_from_repos(self, existing_skills: Dict, projects: List[Dict]) -> Dict:
        """Merge skills từ GitHub repos vào skills hiện có"""
        if not existing_skills:
            existing_skills = {
                "programming_languages": [],
                "Deep Learning and Machine Learning": [],
                "Generative Models": [],
                "Computer Vision": [],
                "databases": [],
                "tools": []
            }
        
        # Thu thập tất cả tech từ projects
        all_tech = []
        for project in projects:
            all_tech.extend(project.get("tech_stack", []))
        
        # Phân loại và thêm vào skills
        for tech in set(all_tech):
            tech_lower = tech.lower()
            
            # Programming languages
            if any(lang in tech_lower for lang in ['python', 'javascript', 'typescript', 'java', 'go', 'rust', 'php', 'ruby', 'dart']):
                if tech not in existing_skills["programming_languages"]:
                    existing_skills["programming_languages"].append(tech)
            
            # Frontend
            elif any(fe in tech_lower for fe in ['react', 'vue', 'angular', 'svelte', 'next', 'nuxt', 'gatsby']):
                if tech not in existing_skills["frontend"]:
                    existing_skills["frontend"].append(tech)
            
            # Backend
            elif any(be in tech_lower for be in ['express', 'fastapi', 'django', 'flask', 'spring', 'gin', 'rails']):
                if tech not in existing_skills["backend"]:
                    existing_skills["backend"].append(tech)
            
            # Databases
            elif any(db in tech_lower for db in ['mongodb', 'postgresql', 'mysql', 'redis', 'sqlite']):
                if tech not in existing_skills["databases"]:
                    existing_skills["databases"].append(tech)
            
            # Tools
            else:
                if tech not in existing_skills["tools"]:
                    existing_skills["tools"].append(tech)
        
        return existing_skills
    
    def _generate_summary(self, cv_data: Dict, template: str) -> str:
        """Tạo summary tự động dựa trên template và dữ liệu"""
        name = cv_data["personal_info"].get("name", "Ứng viên")
        title = cv_data["personal_info"].get("title", "Developer")
        
        # Lấy kinh nghiệm
        years_exp = len(cv_data.get("experience", []))
        
        # Lấy ngôn ngữ chính từ skills
        main_languages = cv_data.get("skills", {}).get("programming_languages", [])[:3]
        
        # Lấy số lượng projects
        num_projects = len(cv_data.get("projects", []))
        
        if template == "tech":
            summary = f"Code-driven {title} với passion cho clean architecture và cutting-edge technology. "
            if main_languages:
                summary += f"Chuyên về {', '.join(main_languages)}. "
            if num_projects > 0:
                summary += f"Đã phát triển {num_projects}+ dự án với focus vào performance và user experience."
        
        elif template == "minimal":
            summary = f"Experienced {title} với focus vào scalable applications và system optimization. "
            if years_exp > 0:
                summary += f"Có {years_exp}+ năm kinh nghiệm trong việc "
            summary += "lead technical teams và deliver high-quality solutions."
        
        else:  # modern
            summary = f"Passionate {title} "
            if years_exp > 0:
                summary += f"với {years_exp}+ năm kinh nghiệm "
            summary += "phát triển ứng dụng hiện đại. "
            if main_languages:
                summary += f"Sử dụng {', '.join(main_languages[:2])} và các công nghệ tiên tiến. "
            summary += "Đam mê về clean code và user experience."
        
        return summary
    
    def _optimize_for_job_description(self, cv_data: Dict, job_description: str) -> Dict:
        """Tối ưu CV theo Job Description sử dụng Gemini"""
        if not self.llm:
            return cv_data
        
        system_prompt = """Bạn là chuyên gia tối ưu CV. Hãy điều chỉnh CV data để phù hợp hơn với Job Description được cung cấp.

Yêu cầu:
1. Điều chỉnh summary để highlight các kỹ năng phù hợp với JD
2. Reorder và emphasize skills phù hợp
3. Điều chỉnh project descriptions để align với requirements
4. Giữ nguyên thông tin factual, chỉ điều chỉnh cách diễn đạt
5. Return JSON format chính xác như input

Chỉ điều chỉnh: summary, skills order, project descriptions. KHÔNG thay đổi personal_info, experience, education."""
        
        user_prompt = f"""
Job Description:
{job_description}

Current CV Data:
{json.dumps(cv_data, ensure_ascii=False, indent=2)}

Hãy tối ưu CV data để phù hợp với JD. Return JSON:"""

        try:
            messages = [
                ("system", system_prompt),
                ("human", user_prompt)
            ]
            response = self.llm.invoke(messages)
            
            # Parse JSON response
            optimized_data = json.loads(response.content.strip())
            return optimized_data
            
        except Exception as e:
            print(f"⚠️ Lỗi khi tối ưu CV theo JD: {str(e)}")
            return cv_data

# Example usage function
def create_cv_example():
    """Ví dụ sử dụng CVSystem"""
    cv_system = CVSystem()
    
    # Thông tin cá nhân
    personal_info = {
        "name": "Nguyễn Trần Minh Tâm",
        "title": "AI Engineering",
        "email": "tam.nguyentranminh04@hcmut.edu.vn",
        "phone": "0899781007",
        "location": "TP. Hồ Chí Minh, Việt Nam",
        "website": "http://alotamne.id.vn",
        "linkedin": "linkedin.com/in/minh-tâm-nguyễn-trần-73073820b",
        "github": "https://github.com/taamnguyeen04"
    }
    
    # GitHub repositories
    github_repos = [
        "https://github.com/taamnguyeen04/Scan-CV",
        "https://github.com/taamnguyeen04/MangoLeaf",
        "https://github.com/Ripefog/retreival_backend"

    ]
    
    # Kinh nghiệm
    experience = [
        {
            "title": "AI Engineering Intern",
            "company": "Upskill Academy",
            "location": "TP.HCM",
            "duration": "01/2025 - Present",
            "achievements": [
                "Built an AI-powered CV scanning system allowing users to upload CV and job description (JD) in both PDF and image formats."
            ]
        }
    ]
    
    # Skills cơ bản
    skills = {
        "programming_languages": ["Python", "C/CPP"],
        "Deep Learning and Machine Learning": ["PyTorch", "scikit-learn", "OpenCV", "Numpy", "Pandas"],
        "Generative Models": ["GANs", "VAEs", "Diffusion Model"],
        "Computer Vision": ["YOLO", "RCNN", "Fast RCNN", "Faster RCNN", "DeepLab", "Co-DETR"],
        "databases": ["MySQL", "MongoDB", "Elasticsearch", "Milvus"],
        "backend": ["Fast API"],
        "tools": ["Git", "Docker"]
    }
    # THÊM PHẦN HỌC VẤN TẠI ĐÂY
    education = [
        {
            "degree": "Cử nhân Khoa học Máy tính",
            "school": "Đại học Bách Khoa TP.HCM",
            "duration": "2022 - 2026",
            "gpa": "8.5/10"
        }
        # Có thể thêm nhiều bậc học khác nếu cần
        # {
        #     "degree": "Thạc sĩ Trí tuệ Nhân tạo",
        #     "school": "Đại học ABC",
        #     "duration": "2026 - 2028",
        #     "gpa": "9.0/10"
        # }
    ]

    # Chứng chỉ (nếu có)
    certifications = [
        {
            "name": "Deep Learning Specialization",
            "issuer": "Coursera - Andrew Ng",
            "date": "2024"
        },
        {
            "name": "Computer Vision Certificate",
            "issuer": "Stanford Online",
            "date": "2024"
        }
    ]
    # Job Description (optional)
    job_description = """
    Tuyển dụng AI Engineer - Computer Vision & Image Processing
    - Kinh nghiệm với Deep Learning frameworks: PyTorch, TensorFlow
    - Xử lý ảnh và Computer Vision: OpenCV, PIL, scikit-image
    - Phát triển các mô hình CNN, Object Detection, Image Segmentation
    - Kiến thức về Generative Models: GANs, VAEs, Diffusion Models
    - Làm việc với datasets lớn và data preprocessing
    - Deploy AI models vào production environment
    - Hiểu biết về MLOps và model monitoring
    - Kỹ năng Python programming mạnh
    - Kinh nghiệm với cloud platforms (AWS, GCP) là một plus
    - Khả năng research và implement state-of-the-art algorithms
    - Teamwork và communication skills
    """
    
    # Tạo CV
    html_content = cv_system.create_cv_from_input(
        personal_info=personal_info,
        github_repos=github_repos,
        experience=experience,
        education=education,  # ← Thêm education
        certifications=certifications,  # ← Thêm certifications  
        skills=skills,
        job_description=job_description,
        template="modern",
        output_path="generated_cv.html"
    )
    
    print("✅ CV đã được tạo thành công!")
    return html_content

if __name__ == "__main__":
    create_cv_example()

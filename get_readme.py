import re, requests, json
from urllib.parse import urlparse
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

load_dotenv()

# Load environment variables
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

API_HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}
RAW_HEADERS = {"Accept": "application/vnd.github.raw"}

# Expanded framework patterns with more comprehensive detection
FRAMEWORK_PATTERNS = {
    # Python Web Frameworks
    "fastapi": ("Python", "FastAPI"),
    "django": ("Python", "Django"),
    "flask": ("Python", "Flask"),
    "starlette": ("Python", "Starlette"),
    "tornado": ("Python", "Tornado"),
    "pyramid": ("Python", "Pyramid"),
    "bottle": ("Python", "Bottle"),
    "cherrypy": ("Python", "CherryPy"),

    # Python Data Science & ML
    "tensorflow": ("Python", "TensorFlow"),
    "torch": ("Python", "PyTorch"),
    "sklearn": ("Python", "Scikit-learn"),
    "pandas": ("Python", "Pandas"),
    "numpy": ("Python", "NumPy"),
    "matplotlib": ("Python", "Matplotlib"),
    "seaborn": ("Python", "Seaborn"),
    "plotly": ("Python", "Plotly"),
    "streamlit": ("Python", "Streamlit"),
    "gradio": ("Python", "Gradio"),
    "jupyter": ("Python", "Jupyter"),
    "opencv": ("Python", "OpenCV"),
    "pillow": ("Python", "PIL/Pillow"),

    # Python Others
    "celery": ("Python", "Celery"),
    "sqlalchemy": ("Python", "SQLAlchemy"),
    "pydantic": ("Python", "Pydantic"),
    "pytest": ("Python", "PyTest"),

    # JavaScript/TypeScript Frontend
    "react": ("JavaScript/TypeScript", "React"),
    "next": ("JavaScript/TypeScript", "Next.js"),
    "vue": ("JavaScript/TypeScript", "Vue.js"),
    "nuxt": ("JavaScript/TypeScript", "Nuxt.js"),
    "svelte": ("JavaScript/TypeScript", "Svelte"),
    "sveltekit": ("JavaScript/TypeScript", "SvelteKit"),
    "angular": ("JavaScript/TypeScript", "Angular"),
    "astro": ("JavaScript/TypeScript", "Astro"),
    "remix": ("JavaScript/TypeScript", "Remix"),
    "gatsby": ("JavaScript/TypeScript", "Gatsby"),
    "vite": ("JavaScript/TypeScript", "Vite"),
    "webpack": ("JavaScript/TypeScript", "Webpack"),
    "parcel": ("JavaScript/TypeScript", "Parcel"),

    # JavaScript/TypeScript Backend
    "express": ("JavaScript/TypeScript", "Express.js"),
    "nest": ("JavaScript/TypeScript", "NestJS"),
    "koa": ("JavaScript/TypeScript", "Koa"),
    "fastify": ("JavaScript/TypeScript", "Fastify"),
    "hapi": ("JavaScript/TypeScript", "Hapi"),
    "socket.io": ("JavaScript/TypeScript", "Socket.IO"),

    # JavaScript Testing & Tools
    "jest": ("JavaScript/TypeScript", "Jest"),
    "mocha": ("JavaScript/TypeScript", "Mocha"),
    "cypress": ("JavaScript/TypeScript", "Cypress"),
    "playwright": ("JavaScript/TypeScript", "Playwright"),
    "eslint": ("JavaScript/TypeScript", "ESLint"),
    "prettier": ("JavaScript/TypeScript", "Prettier"),

    # CSS Frameworks
    "tailwindcss": ("CSS", "Tailwind CSS"),
    "bootstrap": ("CSS", "Bootstrap"),
    "bulma": ("CSS", "Bulma"),
    "chakra-ui": ("CSS", "Chakra UI"),
    "material-ui": ("CSS", "Material-UI"),
    "ant-design": ("CSS", "Ant Design"),
    "styled-components": ("CSS", "Styled Components"),

    # Mobile Development
    "react-native": ("Mobile", "React Native"),
    "expo": ("Mobile", "Expo"),
    "flutter": ("Dart/Mobile", "Flutter"),
    "ionic": ("Mobile", "Ionic"),

    # Database & ORM
    "mongoose": ("Database", "MongoDB/Mongoose"),
    "sequelize": ("Database", "Sequelize"),
    "typeorm": ("Database", "TypeORM"),
    "prisma": ("Database", "Prisma"),
    "knex": ("Database", "Knex.js"),

    # Java
    "spring-boot": ("Java", "Spring Boot"),
    "spring": ("Java", "Spring Framework"),
    "hibernate": ("Java", "Hibernate"),
    "maven": ("Java", "Maven"),
    "gradle": ("Java", "Gradle"),
    "junit": ("Java", "JUnit"),

    # PHP
    "laravel": ("PHP", "Laravel"),
    "symfony": ("PHP", "Symfony"),
    "codeigniter": ("PHP", "CodeIgniter"),
    "cakephp": ("PHP", "CakePHP"),
    "composer": ("PHP", "Composer"),
    "phpunit": ("PHP", "PHPUnit"),

    # Ruby
    "rails": ("Ruby", "Ruby on Rails"),
    "sinatra": ("Ruby", "Sinatra"),
    "rspec": ("Ruby", "RSpec"),
    "bundler": ("Ruby", "Bundler"),

    # Go
    "github.com/gin-gonic/gin": ("Go", "Gin"),
    "github.com/gofiber/fiber": ("Go", "Fiber"),
    "github.com/gorilla/mux": ("Go", "Gorilla Mux"),
    "github.com/labstack/echo": ("Go", "Echo"),
    "gorm.io/gorm": ("Go", "GORM"),

    # Rust
    "rocket": ("Rust", "Rocket"),
    "actix-web": ("Rust", "Actix Web"),
    "axum": ("Rust", "Axum"),
    "warp": ("Rust", "Warp"),
    "serde": ("Rust", "Serde"),

    # C#/.NET
    "aspnetcore": (".NET", "ASP.NET Core"),
    "entityframework": (".NET", "Entity Framework"),
    "newtonsoft.json": (".NET", "Newtonsoft.Json"),

    # DevOps & Cloud
    "docker": ("DevOps", "Docker"),
    "kubernetes": ("DevOps", "Kubernetes"),
    "terraform": ("DevOps", "Terraform"),
    "ansible": ("DevOps", "Ansible"),
    "github.com/aws/aws-sdk": ("Cloud", "AWS SDK"),
    "azure": ("Cloud", "Azure"),
    "googleapis": ("Cloud", "Google Cloud"),

    # Databases
    "redis": ("Database", "Redis"),
    "mongodb": ("Database", "MongoDB"),
    "postgresql": ("Database", "PostgreSQL"),
    "mysql": ("Database", "MySQL"),
    "sqlite": ("Database", "SQLite"),
}

# File patterns to check for additional technology detection
FILE_PATTERNS = {
    "dockerfile": ("DevOps", "Docker"),
    "docker-compose.yml": ("DevOps", "Docker Compose"),
    "docker-compose.yaml": ("DevOps", "Docker Compose"),
    "kubernetes.yml": ("DevOps", "Kubernetes"),
    "kubernetes.yaml": ("DevOps", "Kubernetes"),
    ".github/workflows": ("DevOps", "GitHub Actions"),
    "terraform.tf": ("DevOps", "Terraform"),
    "ansible.yml": ("DevOps", "Ansible"),
    "ansible.yaml": ("DevOps", "Ansible"),
    "makefile": ("Build", "Make"),
    "cmake.txt": ("Build", "CMake"),
    "webpack.config.js": ("JavaScript/TypeScript", "Webpack"),
    "vite.config.js": ("JavaScript/TypeScript", "Vite"),
    "rollup.config.js": ("JavaScript/TypeScript", "Rollup"),
    "next.config.js": ("JavaScript/TypeScript", "Next.js"),
    "nuxt.config.js": ("JavaScript/TypeScript", "Nuxt.js"),
    "svelte.config.js": ("JavaScript/TypeScript", "Svelte"),
    "tailwind.config.js": ("CSS", "Tailwind CSS"),
    ".env": ("Config", "Environment Variables"),
    "vercel.json": ("Deployment", "Vercel"),
    "netlify.toml": ("Deployment", "Netlify"),
}


def parse_owner_repo(repo_url: str):
    u = urlparse(repo_url)
    m = re.match(r"^/([^/]+)/([^/]+)", u.path.rstrip("/"))
    if not m:
        raise ValueError("URL không hợp lệ")
    owner, repo = m.group(1), m.group(2).removesuffix(".git")
    return owner, repo


def get_default_branch(owner, repo, token: str | None = None):
    headers = API_HEADERS.copy()
    if token: headers["Authorization"] = f"Bearer {token}"
    r = requests.get(f"https://api.github.com/repos/{owner}/{repo}", headers=headers, timeout=20)
    r.raise_for_status()
    return r.json().get("default_branch", "main")


def get_languages(owner, repo, token: str | None = None):
    headers = API_HEADERS.copy()
    if token: headers["Authorization"] = f"Bearer {token}"
    r = requests.get(f"https://api.github.com/repos/{owner}/{repo}/languages", headers=headers, timeout=20)
    r.raise_for_status()
    data = r.json()
    total = sum(data.values()) or 1
    pct = {k: round(v * 100 / total, 2) for k, v in sorted(data.items(), key=lambda x: -x[1])}
    primary = next(iter(pct)) if pct else None
    return {"bytes": data, "percent": pct, "primary": primary}


def get_topics(owner, repo, token: str | None = None):
    headers = API_HEADERS.copy()
    if token: headers["Authorization"] = f"Bearer {token}"
    r = requests.get(f"https://api.github.com/repos/{owner}/{repo}/topics", headers=headers, timeout=20)
    if r.status_code == 404:
        return []
    r.raise_for_status()
    return r.json().get("names", [])


def get_repo_info(owner, repo, token: str | None = None):
    """Get basic repository information including description"""
    headers = API_HEADERS.copy()
    if token: headers["Authorization"] = f"Bearer {token}"
    r = requests.get(f"https://api.github.com/repos/{owner}/{repo}", headers=headers, timeout=20)
    r.raise_for_status()
    data = r.json()
    return {
        "name": data.get("name", ""),
        "description": data.get("description", ""),
        "homepage": data.get("homepage", ""),
        "stars": data.get("stargazers_count", 0),
        "forks": data.get("forks_count", 0),
        "language": data.get("language", ""),
        "created_at": data.get("created_at", ""),
        "updated_at": data.get("updated_at", "")
    }


def list_contents_recursive(owner, repo, ref: str, path: str = "", token: str | None = None, max_depth: int = 2,
                            current_depth: int = 0):
    """Recursively list repository contents with depth limit"""
    if current_depth >= max_depth:
        return []

    headers = API_HEADERS.copy()
    if token: headers["Authorization"] = f"Bearer {token}"

    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={ref}"
    r = requests.get(url, headers=headers, timeout=20)
    if r.status_code == 404:
        return []
    r.raise_for_status()

    items = r.json() if isinstance(r.json(), list) else [r.json()]
    all_items = []

    for item in items:
        all_items.append(item)
        if item.get("type") == "dir" and current_depth < max_depth - 1:
            sub_items = list_contents_recursive(owner, repo, ref, item["path"], token, max_depth, current_depth + 1)
            all_items.extend(sub_items)

    return all_items


def get_readme_content(owner, repo, ref: str, token: str | None = None):
    """Fetch README content"""
    readme_files = ["readme.md", "readme.txt", "readme", "readme.rst"]

    headers = RAW_HEADERS.copy()
    if token: headers["Authorization"] = f"Bearer {token}"

    for readme_name in readme_files:
        try:
            url = f"https://raw.githubusercontent.com/{owner}/{repo}/{ref}/{readme_name}"
            r = requests.get(url, headers=headers, timeout=20)
            if r.ok and r.text.strip():
                return r.text

            # Try uppercase
            url = f"https://raw.githubusercontent.com/{owner}/{repo}/{ref}/{readme_name.upper()}"
            r = requests.get(url, headers=headers, timeout=20)
            if r.ok and r.text.strip():
                return r.text
        except Exception:
            continue

    return None


def fetch_raw(download_url: str, token: str | None = None) -> str | None:
    headers = RAW_HEADERS.copy()
    if token: headers["Authorization"] = f"Bearer {token}"
    try:
        rr = requests.get(download_url, headers=headers, timeout=20)
        return rr.text if rr.ok else None
    except Exception:
        return None


def detect_frameworks(owner, repo, token: str | None = None):
    ref = get_default_branch(owner, repo, token)
    items = list_contents_recursive(owner, repo, ref, "", token, max_depth=3)

    found = set()
    evidence = {}
    category_summary = {}

    # Check file patterns first
    for item in items:
        if item.get("type") == "file":
            filename = item["name"].lower()
            filepath = item.get("path", "").lower()

            # Check file patterns
            for pattern, (category, tech) in FILE_PATTERNS.items():
                if pattern in filename or pattern in filepath:
                    if tech not in found:
                        found.add(tech)
                        evidence[tech] = f"File: {item['path']}"
                        category_summary[category] = category_summary.get(category, []) + [tech]

    # Check manifest files
    manifest_files = []
    for item in items:
        if item.get("type") == "file":
            filename = item["name"].lower()
            if filename in [
                "package.json", "requirements.txt", "pyproject.toml", "pipfile",
                "pom.xml", "build.gradle", "build.gradle.kts",
                "go.mod", "cargo.toml", "composer.json", "gemfile",
                "pubspec.yaml", "mix.exs"
            ] or filename.endswith(".csproj"):
                manifest_files.append(item)

    for item in manifest_files:
        if not item.get("download_url"):
            continue

        content = fetch_raw(item["download_url"], token)
        if not content:
            continue

        content_lower = content.lower()

        # JSON parsing for package.json
        if item["name"].lower() == "package.json":
            try:
                pkg = json.loads(content)
                all_deps = {}
                all_deps.update(pkg.get("dependencies", {}))
                all_deps.update(pkg.get("devDependencies", {}))
                all_deps.update(pkg.get("peerDependencies", {}))

                for dep_name in all_deps.keys():
                    dep_lower = dep_name.lower()
                    for pattern, (category, tech) in FRAMEWORK_PATTERNS.items():
                        if pattern in dep_lower and tech not in found:
                            found.add(tech)
                            evidence[tech] = f"{item['name']}: dependency '{dep_name}'"
                            category_summary[category] = category_summary.get(category, []) + [tech]
            except Exception:
                pass

        # Text-based detection for other files
        for pattern, (category, tech) in FRAMEWORK_PATTERNS.items():
            if pattern in content_lower and tech not in found:
                found.add(tech)
                evidence[tech] = f"{item['name']}: contains '{pattern}'"
                category_summary[category] = category_summary.get(category, []) + [tech]

    return {
        "frameworks": sorted(found),
        "evidence": evidence,
        "category_summary": category_summary,
        "ref": ref,
        "checked_files": [item["name"] for item in manifest_files]
    }


def generate_project_description(readme_content: str, repo_info: dict, frameworks: list, languages: dict, topics: list):
    """Use LLM to generate project description based on README and detected technologies"""

    # Initialize the LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0.3,
        max_tokens=1000,
        timeout=30,
        max_retries=2,
    )

    # Prepare the context
    tech_stack = ", ".join(frameworks) if frameworks else "Not detected"
    primary_language = languages.get("primary", "Unknown")
    language_breakdown = ", ".join([f"{lang} ({pct}%)" for lang, pct in list(languages.get("percent", {}).items())[:3]])
    topics_str = ", ".join(topics) if topics else "No topics"

    system_prompt = """Bạn là một chuyên gia phân tích dự án phần mềm. Hãy tạo ra một mô tả ngắn gọn và chuyên nghiệp về dự án dựa trên thông tin được cung cấp. 

Yêu cầu:
- Mô tả bằng tiếng Việt, phong cách chuyên nghiệp
- Độ dài 2-3 câu, tối đa 150 từ
- Tập trung vào mục đích, công nghệ chính và điểm nổi bật
- Phù hợp để đưa vào CV hoặc portfolio
- Không lặp lại thông tin không cần thiết"""

    user_prompt = f"""
    Thông tin dự án:
    - Tên dự án: {repo_info.get('name', 'Unknown')}
    - Mô tả gốc: {repo_info.get('description', 'Không có mô tả')}
    - Ngôn ngữ chính: {primary_language}
    - Phân bố ngôn ngữ: {language_breakdown}
    - Công nghệ/Framework: {tech_stack}
    - Topics: {topics_str}
    - Stars: {repo_info.get('stars', 0)}

    README content (trích đoạn đầu):
    {readme_content[:1000] if readme_content else "Không có README"}

    Hãy tạo mô tả dự án phù hợp cho CV:
    """

    try:
        messages = [
            ("system", system_prompt),
            ("human", user_prompt)
        ]
        response = llm.invoke(messages)
        return response.content.strip()
    except Exception as e:
        # Fallback description
        fallback = f"Dự án {repo_info.get('name', 'phần mềm')} được phát triển bằng {primary_language}"
        if frameworks:
            fallback += f" sử dụng {frameworks[0]}"
        if repo_info.get('description'):
            fallback += f". {repo_info['description']}"
        return fallback


def analyze_repo(repo_url: str, token: str | None = None, include_ai_description: bool = True):
    """Complete repository analysis with optional AI-generated description"""
    owner, repo = parse_owner_repo(repo_url)

    # Get all information
    repo_info = get_repo_info(owner, repo, token)
    langs = get_languages(owner, repo, token)
    topics = get_topics(owner, repo, token)
    fw_analysis = detect_frameworks(owner, repo, token)

    result = {
        "owner": owner,
        "repo": repo,
        "info": repo_info,
        "languages": langs,
        "topics": topics,
        "frameworks": fw_analysis["frameworks"],
        "framework_categories": fw_analysis["category_summary"],
        "evidence": fw_analysis["evidence"],
        "checked_files": fw_analysis["checked_files"],
        "default_branch": fw_analysis["ref"],
    }

    # Add AI-generated description if requested
    if include_ai_description:
        readme_content = get_readme_content(owner, repo, fw_analysis["ref"], token)
        ai_description = generate_project_description(
            readme_content, repo_info, fw_analysis["frameworks"], langs, topics
        )
        result["ai_description"] = ai_description
        result["readme_found"] = readme_content is not None

    return result


def print_analysis_report(analysis: dict):
    """Print a formatted analysis report"""
    print(f"\nPHÂN TÍCH DỰ ÁN: {analysis['info']['name']}")
    print("=" * 60)

    print(f"Repository: {analysis['owner']}/{analysis['repo']}")
    if analysis['info']['description']:
        print(f"Mô tả gốc: {analysis['info']['description']}")

    if analysis.get('ai_description'):
        print(f"Mô tả AI: {analysis['ai_description']}")

    print(f"Stars: {analysis['info']['stars']} | 🍴 Forks: {analysis['info']['forks']}")

    print(f"\nNGÔN NGỮ LẬP TRÌNH:")
    for lang, pct in list(analysis['languages']['percent'].items())[:5]:
        print(f"  • {lang}: {pct}%")

    print(f"\nCÔNG NGHỆ & FRAMEWORK:")
    if analysis['framework_categories']:
        for category, techs in analysis['framework_categories'].items():
            print(f"{category}: {', '.join(techs)}")
    else:
        print("  Không phát hiện framework nào")

    if analysis['topics']:
        print(f"\nTOPICS: {', '.join(analysis['topics'])}")

    print(f"\nFiles đã kiểm tra: {', '.join(analysis['checked_files'])}")


# Example usage
if __name__ == "__main__":
    # Test with a public repository
    repo_url = "https://github.com/ultralytics/ultralytics"  # Example
    
    # Check GitHub token
    if GITHUB_TOKEN:
        print("✅ Đã tìm thấy GitHub token - Rate limit: 5000 requests/hour")
    else:
        print("⚠️  Không tìm thấy GitHub token!")
        print("🔧 Để tăng rate limit (từ 60 lên 5000 requests/hour):")
        print("   1. Tạo GitHub token tại: https://github.com/settings/tokens")
        print("   2. Chọn scope: public_repo")
        print("   3. Thêm vào file .env: GITHUB_TOKEN=your_token_here")
        print("📡 Đang tiếp tục với rate limit thấp (60 requests/hour)...\n")
    
    try:
        analysis = analyze_repo(repo_url, token=GITHUB_TOKEN, include_ai_description=True)
        print_analysis_report(analysis)
    except Exception as e:
        print(f"❌ Error: {e}")
        if "rate limit" in str(e).lower():
            print("\n💡 Gợi ý: Thêm GitHub token vào file .env để tăng rate limit")
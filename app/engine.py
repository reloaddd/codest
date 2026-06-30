import time
import docker
import tarfile
import io

try:
    client = docker.from_env()
except Exception as e:
    client = None
    print(f"Docker is not running: {e}")

LANGUAGE_CONFIG = {
    "python": {
        "image": "python:3.11-alpine",
        "filename": "main.py",
        "command": 'sh -c "cat /workspace/input.txt | python /workspace/main.py"'
    },
    "cpp": {
        "image": "gcc:latest",
        "filename": "main.cpp",
        "command": 'sh -c "g++ -O2 /workspace/main.cpp -o /workspace/main.out && cat /workspace/input.txt | /workspace/main.out"'
    },
    "java": {
        "image": "openjdk:17-slim",
        "filename": "Main.java",
        "command": 'sh -c "javac /workspace/Main.java && cat /workspace/input.txt | java -cp /workspace Main"'
    }
}

def create_tar_stream(filename: str, code: str, input_data: str) -> io.BytesIO:
    """Packages the code and input files into an in-memory tarball."""
    file_out = io.BytesIO()
    with tarfile.open(fileobj=file_out, mode="w") as tar:
        # 1. Add Code File
        code_bytes = code.encode('utf-8')
        code_info = tarfile.TarInfo(name=filename)
        code_info.size = len(code_bytes)
        tar.addfile(code_info, io.BytesIO(code_bytes))
        
        # 2. Add Input File
        input_bytes = input_data.encode('utf-8')
        input_info = tarfile.TarInfo(name="input.txt")
        input_info.size = len(input_bytes)
        tar.addfile(input_info, io.BytesIO(input_bytes))
        
    file_out.seek(0)
    return file_out

def run_code(language: str, code: str, input_data: str, timeout_seconds: int = 5) -> dict:
    if not client:
        return {"status": "System Error", "output": "Docker daemon not running"}

    if language not in LANGUAGE_CONFIG:
        return {"status": "System Error", "output": f"Language '{language}' not supported."}

    config = LANGUAGE_CONFIG[language]

    try:
        # 1. CREATE container (do not start it yet, and NO VOLUMES!)
        container = client.containers.create(
            image=config["image"], 
            command=config["command"],
            working_dir='/workspace',
            mem_limit='256m',       
            network_disabled=True,  
            detach=True             
        )

        # 2. INJECT files directly into the container's file system
        tar_stream = create_tar_stream(config["filename"], code, input_data)
        container.put_archive('/workspace', tar_stream)

        # 3. START the container now that the files are inside
        container.start()

        start_time = time.time()
        while container.status in ['created', 'running']:
            if time.time() - start_time > timeout_seconds:
                container.kill() 
                return {"status": "Time Limit Exceeded", "output": ""}
            time.sleep(0.1)
            container.reload() 

        result = container.wait()
        logs = container.logs().decode('utf-8').strip()
        container.remove()

        if result['StatusCode'] != 0:
            print(f"\n[COMPILER ERROR]:\n{logs}\n")
            return {"status": "Compilation/Runtime Error", "output": logs}

        return {"status": "Success", "output": logs}

    except Exception as e:
        print(f"\n[SYSTEM ERROR]: {str(e)}\n")
        return {"status": "System Error", "output": str(e)}

def grade_submission(code: str, language: str, test_cases: list) -> str:
    for index, tc in enumerate(test_cases):
        result = run_code(language, code, tc.input_data)
        
        if result["status"] != "Success":
            return result["status"] 
            
        if result["output"] != tc.expected_output.strip():
            return f"Wrong Answer on Test Case {index + 1}"
            
    return "Accepted"